#!/usr/bin/env python

import sys
import pexpect as pe

pbs = pe.spawnu('ssh raijin')
pbs.expect('\[.+\]\$ ')
pbs.sendline('echo "asdflkjsdf" >> hello.txt')
pbs.expect('\[.+\]\$ ')
pbs.sendline('/bin/cat hello.txt')
pbs.expect('\[.+\]\$ ')
print(pbs.before)
#print(fout.readlines())

"""
pbs = pe.spawnu('ls')
pbs.expect(pe.EOF)
#pbs.expect('.+\$ ')
print(pbs.before)

#pbs = pe.spawn('/bin/ls')
#pbs.expect(pe.EOF)
#print(pbs.before)
"""
