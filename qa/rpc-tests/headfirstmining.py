#!/usr/bin/env python2
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#

import binascii
from copy import deepcopy

from test_framework.mininode import *
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.blocktools import create_block, create_coinbase, create_transaction

'''
HeadFirstMining.py

Test some unlikely scenarios involving valid-proof-of-work
but invalid-something-else full blocks.

'''

class BaseNode(NodeConnCB):
    def __init__(self):
        NodeConnCB.__init__(self)
        self.connection = None
        self.last_inv = None
        self.last_headers = None
        self.last_block = None
        self.ping_counter = 1
        self.last_pong = msg_pong(0)
        self.last_getdata = None
        self.sleep_time = 0.05
        self.block_announced = False

    def add_connection(self, conn):
        self.connection = conn

    # Wrapper for the NodeConn's send_message function
    def send_message(self, message):
        self.connection.send_message(message)

    def on_inv(self, conn, message):
        self.last_inv = message
        self.block_announced = True

    def on_headers(self, conn, message):
        self.last_headers = message
        self.block_announced = True

    def on_block(self, conn, message):
        self.last_block = message.block
        self.last_block.calc_sha256()

    def on_getdata(self, conn, message):
        self.last_getdata = message

    def on_pong(self, conn, message):
        self.last_pong = message

    # Syncing helpers
    def sync(self, test_function, timeout=60):
        while timeout > 0:
            with mininode_lock:
                if test_function():
                    return
            time.sleep(self.sleep_time)
            timeout -= self.sleep_time
        raise AssertionError("Sync failed to complete")
        
    def sync_with_ping(self, timeout=60):
        self.send_message(msg_ping(nonce=self.ping_counter))
        test_function = lambda: self.last_pong.nonce == self.ping_counter
        self.sync(test_function, timeout)
        self.ping_counter += 1
        return

    def wait_for_block(self, blockhash, timeout=60):
        test_function = lambda: self.last_block != None and self.last_block.sha256 == blockhash
        self.sync(test_function, timeout)
        return

    def wait_for_getdata(self, hash_list, timeout=60):
        if hash_list == []:
            return

        test_function = lambda: self.last_getdata != None and [x.hash for x in self.last_getdata.inv] == hash_list
        self.sync(test_function, timeout)
        return

    def send_header_for_blocks(self, new_blocks):
        headers_message = msg_headers()
        headers_message.headers = [ CBlockHeader(b) for b in new_blocks ]
        self.send_message(headers_message)

# TestNode: This peer is the one we use for most of the testing.
class TestNode(BaseNode):
    def __init__(self):
        BaseNode.__init__(self)

class HeadFirstMineTest(BitcoinTestFramework):
    def setup_chain(self):
        initialize_chain_clean(self.options.tmpdir, 4)

    def setup_network(self):
        self.nodes = []
        self.nodes = start_nodes(4, self.options.tmpdir, [["-debug=net", "-banscore=999999", "-logtimemicros=1"]]*4)
        connect_nodes(self.nodes[0], 1)
        connect_nodes(self.nodes[1], 2)
        connect_nodes(self.nodes[2], 3) # 0 -> 1 -> 2 -> 3 connected in a chain

    def create_valid_block(self, tip):
        height = self.nodes[0].getblockcount()
        block_time = max(int(time.time()), self.nodes[0].getblock(self.nodes[0].getbestblockhash())['time']+1)
        new_block = create_block(tip, create_coinbase(height+1), block_time)
        new_block.solve()
        return new_block

    def create_invalid_block(self, tip):
        height = self.nodes[0].getblockcount()
        block_time = max(int(time.time()), self.nodes[0].getblock(self.nodes[0].getbestblockhash())['time']+1)
        new_block = create_block(tip, create_coinbase(height+1), block_time)
        new_block.vtx.append(create_transaction(new_block.vtx[0], 0, chr(81), 50))
        new_block.hashMerkleRoot = new_block.calc_merkle_root()
        new_block.rehash()
        new_block.solve()
        return new_block

    def wait_for(self, test_function, wait=1, timeout=30):
        while not test_function():
            time.sleep(wait)
            timeout -= wait;
            if timeout < 0:
                raise AssertionError("Unexpected wait_for timeout")

    def run_test(self):
        # Setup the p2p connections and start up the network thread.
        test_node = TestNode()

        self.p2p_connections = [test_node]

        connections = []
        connections.append(NodeConn('127.0.0.1', p2p_port(0), self.nodes[0], test_node))
        test_node.add_connection(connections[0])

        NetworkThread().start() # Start up network handling in another thread

        test_node.wait_for_verack()
        test_node.send_message(msg_sendheaders())

        # Network initialized, ready to start testing.

        # test_node.send_header_for_blocks is used to send headers first,
        # and behavior is tested before and after the full block is sent
        # with .send_message(msg_block)

        self.nodes[0].generate(1)
        sync_blocks(self.nodes) # make sure all the nodes are out of initial-download state
        tip = int(self.nodes[0].getbestblockhash(), 16)

        # 1. Create a block, send header to peer,
        #    it should mine on that header
        new_block = self.create_valid_block(tip)
        test_node.send_header_for_blocks([new_block])
        test_node.wait_for_getdata([new_block.sha256], timeout=5)
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(new_block.sha256, int(block_template['previousblockhash'], 16))

        # ... all the nodes will mine on that header:
        self.wait_for(lambda: int(self.nodes[3].getblocktemplate()['previousblockhash'], 16) == new_block.sha256)

        # 2. If node[0] generates a new block, should build on that:
        new_tip = int(self.nodes[0].generate(1)[0], 16)
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(new_tip, int(block_template['previousblockhash'], 16))

        test_node.send_message(msg_block(new_block))
        self.wait_for(lambda: int(self.nodes[3].getblocktemplate()['previousblockhash'], 16) == new_tip)

        tip = new_tip

        # 3. Create a block with valid POW but containing an invalid transaction
        new_block = self.create_invalid_block(tip)
        test_node.send_header_for_blocks([new_block])
        test_node.wait_for_getdata([new_block.sha256], timeout=5)
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(new_block.sha256, int(block_template['previousblockhash'], 16)) # Should build on the invalid block
        
        # ... once full invalid block received: shouldn't build on it:
        test_node.send_message(msg_block(new_block))
        test_node.sync_with_ping()
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(tip, int(block_template['previousblockhash'], 16))

        # 4. Test submitblock when mining on top of header:
        invalid_parent = self.create_invalid_block(tip)
        test_node.send_header_for_blocks([invalid_parent])
        test_node.wait_for_getdata([invalid_parent.sha256], timeout=5)
        valid_child = self.create_valid_block(invalid_parent.sha256)
        data = valid_child.serialize()
        result = self.nodes[0].submitblock(binascii.hexlify(data))
        block_template = self.nodes[0].getblocktemplate()
        # Mining on valid_child:
        assert_equal(valid_child.sha256, int(block_template['previousblockhash'], 16))
        # .. but best block is still tip:
        assert_equal(tip, int(self.nodes[0].getbestblockhash(), 16))

        # 5. Invalid parent validated: switch to mining on tip
        test_node.send_message(msg_block(invalid_parent))
        test_node.sync_with_ping()
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(tip, int(block_template['previousblockhash'], 16))

        # ... news of the invalid block should propagate before the 30-second timeout:
        self.wait_for(lambda: int(self.nodes[3].getblocktemplate()['previousblockhash'], 16) == tip, timeout=10)

        # 6. Valid block header sent, then try to send an 'invalidblock' with tweaked
        # transaction data. 'invalidblock' message should be ignored.
        new_block = self.create_valid_block(tip)
        test_node.send_header_for_blocks([new_block])
        test_node.sync_with_ping()
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(new_block.sha256, int(block_template['previousblockhash'], 16))
        tweaked_block = deepcopy(new_block)
        tweaked_block.vtx[0].nLockTime = 11 # invalidates merkleroot
        test_node.send_message(msg_invalidblock(tweaked_block)) # should be ignored
        test_node.sync_with_ping()
        block_template = self.nodes[0].getblocktemplate()
        assert_equal(new_block.sha256, int(block_template['previousblockhash'], 16))
        test_node.send_message(msg_block(new_block))
        test_node.sync_with_ping()
        assert_equal(new_block.sha256, int(self.nodes[0].getbestblockhash(), 16))

        tip = new_block.sha256

        # 7. Send valid block as 'invalidblock' message, should propagate as a normal
        # block and become everybody's best block:
        new_block = self.create_valid_block(tip)
        test_node.send_header_for_blocks([new_block])
        test_node.sync_with_ping()
        test_node.send_message(msg_invalidblock(new_block)) # valid block sent in invalidblock message
        test_node.sync_with_ping()
        assert_equal(new_block.sha256, int(self.nodes[0].getbestblockhash(), 16))
        self.wait_for(lambda: int(self.nodes[3].getbestblockhash(), 16) == new_block.sha256, timeout=10)

        tip = new_block.sha256


if __name__ == '__main__':
    HeadFirstMineTest().main()
