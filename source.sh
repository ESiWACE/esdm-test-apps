#!/bin/bash
echo "This file should be sourced"
ESDM_INSTALL_DIR=/home/kunkel/ur-git/esiwace/ESD-Middleware/install/
export PATH=$ESDM_INSTALL_DIR/bin:$PATH

alias mkesdm="mkfs.esdm -g -l --create  --remove --ignore-errors"
LDFLAGS="-Wl,--rpath=$ESDM_INSTALL_DIR/lib -L$ESDM_INSTALL_DIR/lib"
CFLAGS="-I$ESDM_INSTALL_DIR/include"

function checkCFG(){
  if [[ -e esdm.conf ]] ; then
    echo Using existing esdm.conf
  else
    echo "Copying ../esdm.conf"
    cp ../esdm.conf .
  fi
}
