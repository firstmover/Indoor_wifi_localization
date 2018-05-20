#!/bin/bash

ifconfig wlp3s0 down
iwconfig wlp3s0 mode managed
ifconfig wlp3s0 up
service network-manager start
