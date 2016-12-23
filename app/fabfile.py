#!/usr/bin/env python
# coding=utf-8

from fabric.operations import (
    local
)

def hello(who="world"):
    print "hello {}".format(who)

def whoami():
    print local("echo `whoami`")

