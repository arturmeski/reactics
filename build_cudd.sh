#!/bin/sh

CUDD_VERSION=3.0.0
INSTALL_DIR="$PWD"

tar -zxvf dist/cudd-$CUDD_VERSION.tar.gz
cd cudd-$CUDD_VERSION
./configure --enable-shared --enable-obj --prefix=$INSTALL_DIR/cudd
make -j4
make install
cd ..
rm -rf cudd-$CUDD_VERSION

