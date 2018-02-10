#!/bin/sh

CUDD_VERSION=3.0.0
INSTALL_DIR="$PWD"

cd cudd-$CUDD_VERSION
./configure --enable-shared --enable-obj --prefix=$INSTALL_DIR/cudd
make
make install
