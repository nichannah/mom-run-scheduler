
from __future__ import print_function

import os
import sys
import subprocess as sp
import shlex

model_names = ['MOM_SIS', 'EBM', 'CM2M', 'ICCM', 'ESM2M']

build_cmd = " {mom_dir}/exp/MOM_compile.csh --platform nci --type {model_name} {debug}"

class Model:

    def __init__(mom_dir, name):
        self.mom_dir = mom_dir
        self.name = name

    def build(self, build_type, compiler):

        assert(compiler.lower() == 'intel')

        debug = ''
        if build_type.lower() == 'debug':
            debug = 'debug'

        build_cmd = build_cmd.format(mom_dir=self.mom_dir,
                                        model_name=self.name, debug=debug)
        # Build the model.
        ret = sp.call(shlex.split(build_cmd))

        return ret
