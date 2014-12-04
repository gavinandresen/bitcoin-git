#!/usr/bin/env bash

if [ $# -lt 3 ]; then
        echo "Usage: $0 datadir n outputdir"
        exit 1
fi

set -x

DATADIR=$1
N=$2
OUTDIR=$3

mkdir -p $OUTDIR/b
mkdir -p $OUTDIR/regtest

PORT=$(( 11000 + $RANDOM % 1000 ))
RPCPORT=$(( $PORT + 1 ))
cat > $OUTDIR/bitcoin.conf <<EOF
regtest=1
rpcpassword=t
port=$PORT
rpcport=$RPCPORT
keypool=1
EOF

H=$(./gen_megablocks -q -n=$N -d=$OUTDIR/b -datadir=$DATADIR)
cp $OUTDIR/b/coinbasetx.dat $OUTDIR/regtest/

CURRENT_HEIGHT=0
START_TIME=$(date +%s)

./bitcoind -daemon -datadir=$OUTDIR $(for i in $OUTDIR/b/blk*.dat ; do echo -n "-loadblock=$i "; done)

while [ $CURRENT_HEIGHT -lt $H ]; do
  CURRENT_HEIGHT=$(./bitcoin-cli -datadir=$OUTDIR -rpcwait getblockcount)
  sleep 60
done
./bitcoin-cli -datadir=$OUTDIR stop

END_TIME=$(date +%s)

rm -rf $OUTDIR/b

echo "Success, elapsed time " $(( $END_TIME-$START_TIME )) " seconds"
