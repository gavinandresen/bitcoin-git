#!/usr/bin/env python

# Test save/restore memory pool functionality


import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python-bitcoinrpc"))

import json
import shutil
import subprocess
import tempfile
import traceback

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from util import *


def run_test(nodes, test_dir):
    # Three transactions for the memory pools. Each node gets a send-to-self
    # (which only they care about, and will restore to memory pool from wallet
    # at startup) and sends back-and-forth:
    txid1 = nodes[0].sendtoaddress(nodes[0].getnewaddress(), 0.11)
    txid2 = nodes[1].sendtoaddress(nodes[1].getnewaddress(), 0.21)
    txid3 = nodes[0].sendtoaddress(nodes[1].getnewaddress(), 0.31)
    txid4 = nodes[1].sendtoaddress(nodes[0].getnewaddress(), 0.41)

    # wait for mempools to sync
    sync_mempools(nodes)
    assert_equal(len(nodes[0].getrawmempool()), 4)
    assert_equal(len(nodes[1].getrawmempool()), 4)
    
    # restart nodes; their memory pools should restore on restart.
    stop_nodes(nodes)
    wait_bitcoinds()
    nodes[:] = start_nodes(2, test_dir)
    assert_equal(len(nodes[0].getrawmempool()), 4)
    assert_equal(len(nodes[1].getrawmempool()), 4)

def main():
    import optparse

    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option("--nocleanup", dest="nocleanup", default=False, action="store_true",
                      help="Leave bitcoinds and test.* datadir on exit or error")
    parser.add_option("--srcdir", dest="srcdir", default="../../src",
                      help="Source directory containing bitcoind/bitcoin-cli (default: %default%)")
    parser.add_option("--tmpdir", dest="tmpdir", default=tempfile.mkdtemp(prefix="test"),
                      help="Root directory for datadirs")
    (options, args) = parser.parse_args()

    os.environ['PATH'] = options.srcdir+":"+os.environ['PATH']

    check_json_precision()

    success = False
    nodes = []
    try:
        print("Initializing test directory "+options.tmpdir)
        if not os.path.isdir(options.tmpdir):
            os.makedirs(options.tmpdir)
        initialize_chain(options.tmpdir)

        nodes = start_nodes(2, options.tmpdir)
        connect_nodes(nodes[1], 0)
        wait_peers(nodes[0], 1)
        wait_peers(nodes[1], 1)
        sync_blocks(nodes)

        run_test(nodes, options.tmpdir)

        success = True

    except AssertionError as e:
        print("Assertion failed: "+e.message)
    except Exception as e:
        print("Unexpected exception caught during testing: "+str(e))
        traceback.print_tb(sys.exc_info()[2])

    if not options.nocleanup:
        print("Cleaning up")
        stop_nodes(nodes)
        wait_bitcoinds()
        shutil.rmtree(options.tmpdir)

    if success:
        print("Tests successful")
        sys.exit(0)
    else:
        print("Failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
