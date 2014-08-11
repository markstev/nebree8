#! /bin/bash

set -e

function install_once {
	sudo apt-get install python-smbus
	sudo apt-get install i2c-tools
}

function initialize {
  rmmod i2c-bcm2708 || echo 'failed to unload -- ignoring'
  rmmod i2c-dev || echo 'failed to unload -- ignoring'
  modprobe i2c-bcm2708
  modprobe i2c-dev
  lsmod | grep i2c
}

function test_config {
  i2cdetect -y 1
}

function all {
  install_once
  initialize
  test_config
}

function main {
  if [ "$#" -eq 0 ]; then
    all
    return $?
  fi
  while [ "$#" -gt 0 ]; do
    $1
    shift
  done
}

main "$@"
