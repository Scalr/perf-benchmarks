#!/bin/bash

date; dd if=/dev/zero of=/mnt/persistent/5gig bs=512 count=10000000; sync; date


date; dd if=/mnt/persistent/5gig of=/dev/null bs=512; sync; date


