#!/bin/bash

fio random-read-test.fio

fio random-write-test.fio

fio server-simulation.fio
