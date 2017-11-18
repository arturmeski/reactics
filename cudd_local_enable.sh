#!/bin/sh

cd cudd_local
make
cd obj
make
cd ../../
ln -s cudd_local cudd
