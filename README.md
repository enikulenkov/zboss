[![Build Status](https://travis-ci.org/enikulenkov/zboss.svg?branch=master)](https://travis-ci.org/enikulenkov/zboss)

Short build instructions
========================

a) Linux
* ln -s build-configurations/Platform-linux Platform
* ln -s build-configurations/Options-linux-debug Options
* make rebuild
* make tags

b) 8051 using SDCC
* ln -s build-configurations/Platform-8051 Platform
* ln -s build-configurations/Options-8051-sim-debug Options
* make rebuild
* make tags

c) Linux/ARM
* ln -s build-configurations/Platform-linux-arm Platform
* ln -s build-configurations/Options-linux-arm-debug Options

Call doxygen from the root to generate documentation.

