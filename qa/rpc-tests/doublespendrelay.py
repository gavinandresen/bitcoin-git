#!/usr/bin/env python

#
# Test double-spend-relay and notification code
#

from test_framework import BitcoinTestFramework
from decimal import Decimal
from util import *

class DoubleSpendRelay(BitcoinTestFramework):

    #
    # Create a 4-node network; roles for the nodes are:
    # [0] : double-spender, creates transactions
    # [1] : second-spend-sender
    # [2] : relay node
    # [3] : receiver, should detect/notify of double-spends
    #
    # Node connectivity is:
    # [0,1] <--> [2] <--> [3]
    #
    def setup_network(self, test_dir):
        nodes = []
        for i in range(0,4):
            nodes.append(start_node(i, test_dir))
        connect_nodes(nodes[0], 2)
        connect_nodes(nodes[1], 2)
        connect_nodes(nodes[3], 2)
        sync_blocks(nodes)
        return nodes

    def run_test(self, nodes):
        # Test 1:
        # shutdown nodes[1] so it is not aware of the first spend
        # and will be willing to broadcast the second spend
        stop_node(nodes[1], 1)
        # First spend: nodes[0] -> nodes[3]
        amount = Decimal("48")
        fee = Decimal("0.01")
        (total_in, inputs) = gather_inputs(nodes[0], amount+fee)
        change_outputs = make_change(nodes[0], total_in, amount, fee)
        outputs = dict(change_outputs)
        outputs[nodes[3].getnewaddress()] = amount
        signed1 = nodes[0].signrawtransaction(nodes[0].createrawtransaction(inputs, outputs))
        txid1 = nodes[0].sendrawtransaction(signed1["hex"], True)
        sync_mempools([nodes[0], nodes[3]])
        
        txid1_info = nodes[3].gettransaction(txid1)
        assert_equal(txid1_info["respendsobserved"], [])

        # Restart nodes[1]
        nodes[1] = start_node(1, self.options.tmpdir)
        connect_nodes(nodes[1], 2)
        # Second spend: nodes[0] -> nodes[1]
        outputs = dict(change_outputs)
        outputs[nodes[1].getnewaddress()] = amount
        signed2 = nodes[0].signrawtransaction(nodes[0].createrawtransaction(inputs, outputs))
        txid2 = nodes[1].sendrawtransaction(signed2["hex"], True)
        # Wait until txid2 is relayed to nodes[3] (but don't wait forever):
        # Note we can't use sync_mempools, because the respend isn't added to
        # the mempool.
        for i in range(1,5):
            txid1_info2 = nodes[3].gettransaction(txid1)
            if txid1_info2["respendsobserved"] != []:
                break
            time.sleep(0.1 * i**2) # exponential back-off
        assert_equal(txid1_info2["respendsobserved"], [txid2])

if __name__ == '__main__':
    DoubleSpendRelay().main()
