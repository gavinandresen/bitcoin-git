#include <boost/foreach.hpp>
#include <stdio.h>
#include "config/bitcoin-config.h"

#include "chain.h"
#include "chainparams.h"
#include "coins.h"
#include "txdb.h"
#include "util.h"

//
// Generate a "megablocks" blockchain from the main
// bitcoin network's blockchain.
//


static CCoinsViewDB *pcoinsdbview = NULL;

bool CheckRegTestWork(const CBlock& block)
{
    arith_uint256 h = UintToArith256(block.GetHash());
    arith_uint256 bnTarget;
    bnTarget.SetCompact(block.nBits);
    return (h <= bnTarget);
}

void StreamToDisk(const CBlock& block, const std::string& directory)
{
    static int nFile = 0;
    static int64_t nBytesWritten = 0;
    static FILE* fp = NULL;

    if (fp == NULL || nBytesWritten > 1.5e9) { // 1.5GB max
        if (fp != NULL) fclose(fp);
        std::string filename = strprintf("%s/blk%.5d.dat", directory.c_str(), nFile);
        fp = fopen(filename.c_str(), "wb");
        if (fp == NULL) {
            fprintf(stderr, "Couldn't open %s\n", filename.c_str());
            exit(1);
        }
        ++nFile;
        nBytesWritten = 0;
    }
    CAutoFile fileout(fp, SER_DISK, CLIENT_VERSION);
    unsigned int nSize = fileout.GetSerializeSize(block);
    fileout << FLATDATA(Params(CBaseChainParams::REGTEST).MessageStart()) << nSize;
    fileout << block;
    nBytesWritten += 8+nSize;
    fileout.release();
}

int main(int argc, char* argv[])
{
    SetupEnvironment();
    ParseParameters(argc, argv);
    ReadConfigFile(mapArgs, mapMultiArgs);

    bool fQuiet = GetBoolArg("-q", false);

    bool fParseErr = false;

    // Having two different params to control
    // how big blocks are is a hack, but convenient
    // for creating chains with varying blocksize
    // (use -n and the size variation will be like
    // the main chain) or consistent block sizes
    // (use -size).
    int nToCombine = static_cast<int>(GetArg("-n", 0));
    unsigned int nSizeTarget = static_cast<unsigned int>(GetArg("-size", 0));
    if (nToCombine <= 0 && nSizeTarget <= 0) fParseErr = true;
    else if (nToCombine <= 0 && nSizeTarget > 0){
        // ... keep combining until block is bigger than nSizeTarget:
        nToCombine = std::numeric_limits<int>::max();
    }
    else if (nToCombine > 0 && nSizeTarget <= 0) {
        // ... combine nToCombine, no matter how big blocks get:
        nSizeTarget = std::numeric_limits<unsigned int>::max();
    }
    std::string writeDir = GetArg("-d", "");
    if (writeDir.empty()) fParseErr = true;

    std::set<uint256> skipTxids;
    int nSkipped = 0;
    for (unsigned int i = 0; i < mapMultiArgs.count("-skiptx"); i++)
    {
        const std::string& txidHex = mapMultiArgs["-skiptx"][i];
        if (!IsHex(txidHex))
        {
            fParseErr = true;
            break;
        }
        uint256 txid;
        txid.SetHex(txidHex);
        skipTxids.insert(txid);
    }

    if (fParseErr) {
        fprintf(stderr, "Usage: %s -n=11 -size=1000000 -d=/path/to/megachain -skiptx=HEX_TX_ID -to=n\n", argv[0]);
        fprintf(stderr, "Writes blk*.dat to -d path; run a megablocks-compiled\n");
        fprintf(stderr, "bitcoind with -loadblock=/path/to/blk*.dat to load\n");
        fprintf(stderr, "Also writes a coinbasetx.dat file; copy or link that\n");
        fprintf(stderr, "into the -datadir, so coinbase transaction spends\n");
        fprintf(stderr, "from the main chain that are not in the megablocks\n");
        fprintf(stderr, "chain are allowed\n");
        fprintf(stderr, "If one or more -skiptx txids are given, skip those\n");
        fprintf(stderr, "transactions (and their descendants; useful for\n");
        fprintf(stderr, "re-org testing)\n");
        fprintf(stderr, "Either bundles up -n blocks at a time, or creates blocks that\n");
        fprintf(stderr," are at least -size bytes big.\n");
        fprintf(stderr, "Dumps all blocks, unless -to=n option given (dumps through block height n)\n");
        return 1;
    }

    SelectParamsFromCommandLine();

    CChain chainActive;

    pblocktree = new CBlockTreeDB(100<<8, false, false);
    pcoinsdbview = new CCoinsViewDB(100<<8, false, false);
    pcoinsTip = new CCoinsViewCache(pcoinsdbview);

    LoadBlockIndex();
    InitBlockIndex();

    BlockMap::iterator it = mapBlockIndex.find(pcoinsTip->GetBestBlock());
    if (it != mapBlockIndex.end())
        chainActive.SetTip(it->second);

    int nHeight = (int)GetArg("-to", chainActive.Height());
    if (nHeight > chainActive.Height())
        nHeight = chainActive.Height();

    // First block is -regtest genesis block:
    StreamToDisk(Params(CBaseChainParams::REGTEST).GenesisBlock(), writeDir);
    uint256 hashPrevBlock = Params(CBaseChainParams::REGTEST).HashGenesisBlock();

    if (!fQuiet) printf("\nBlock height is %d; combining into %s\n", chainActive.Height(), writeDir.c_str());
    std::string coinbaseFile = writeDir+"/"+"coinbasetx.dat";
    CAutoFile coinbaseStream(fopen(coinbaseFile.c_str(), "wb"), SER_DISK, CLIENT_VERSION);
    int writeBlockHeight = 1;
    int h = 1;
    while (h <= nHeight) {
        CBlock megablock;

        // Create a coinbase transaction
        CMutableTransaction tx;
        tx.vin.resize(1);
        tx.vin[0].prevout.SetNull();
        std::string s("MEGABLOCKS");
        tx.vin[0].scriptSig = CScript() << writeBlockHeight << std::vector<unsigned char>(s.begin(), s.end());
        tx.vout.resize(1);
        tx.vout[0].nValue = 0; // These coinbases are never spent, so OK to be 0-value.
        tx.vout[0].scriptPubKey = CScript() << OP_TRUE;
        megablock.vtx.push_back(tx);

        // Now add transactions from rest of blocks to megablock:
        unsigned int nMaxCombine = h+nToCombine;
        while (h < nMaxCombine && ::GetSerializeSize(megablock, SER_DISK, CLIENT_VERSION) < nSizeTarget) {
            CBlock b;
            if (!ReadBlockFromDisk(b, chainActive[h])) {
                fprintf(stderr, "Couldn't read block %d, skipping\n", h);
                return 1;
            }
            // main-chain blocks 91842 and 91880 are weird; skip their
            // coinbase transactions, they're duplicates and not spendable anyway:
            if (h != 91842 && h != 91880) {
                // coinbaseStream is list of:
                //  height in new blockchain where transaction should become live
                //  full coinbase transaction
                coinbaseStream << writeBlockHeight << b.vtx[0];
            }

            // All tx except for coinbase:
            for (size_t k = 1; k < b.vtx.size(); k++) {
                const CTransaction& tx = b.vtx[k];
                uint256 txid = tx.GetHash();
                // Add to skip list if any inputs in skip list:
                BOOST_FOREACH(const CTxIn& txin, tx.vin) {
                    if (skipTxids.count(txin.prevout.hash)) 
                    {
                        skipTxids.insert(txid);
                        break;
                    }
                }
                if (skipTxids.count(txid) == 0)
                    megablock.vtx.push_back(tx);
                else
                    ++nSkipped;
            }

            if (!fQuiet && h%10000 == 0) { printf("%d ", h); fflush(stdout); }
            ++h;
        }
        bool fBadMerkle = false;
        megablock.hashMerkleRoot = megablock.BuildMerkleTree(&fBadMerkle);
        if (fBadMerkle) {
            fprintf(stderr, "Bad merkle, blocks %d to %d\n", h, h+nToCombine-1);
        }
        megablock.nTime = Params(CBaseChainParams::REGTEST).GenesisBlock().nTime+h;
        megablock.nBits = 0x207fffff;
        megablock.hashPrevBlock = hashPrevBlock;
        // Increment block nonce until it passes the -regtest proof of work
        while (!CheckRegTestWork(megablock)) ++megablock.nNonce;

        hashPrevBlock = megablock.GetHash();

        // Write to disk
        StreamToDisk(megablock, writeDir);
        ++writeBlockHeight;
    }
    // coinbasestream ends with -1, null tx:
    coinbaseStream << -1 << CTransaction();

    if (fQuiet) {
        printf("%d\n", writeBlockHeight-1);
    }
    else {
        if (mapMultiArgs.count("-skiptx") > 0)
        {
            printf("\nSkipped %d transactions", nSkipped);
        }
        printf("\nFinished, new chain is %d blocks long.\n", writeBlockHeight-1);
    }

    return 0;
}

