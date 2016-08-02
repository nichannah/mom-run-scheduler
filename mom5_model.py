
from __future__ import print_function

import os
import sys
import subprocess as sp
import shlex

model_names = ['MOM_SIS', 'EBM', 'CM2M', 'ICCM', 'ESM2M']

_build_cmd = "{mom_dir}/exp/MOM_compile.csh --platform nci --type {model_name} {debug}"

class Model:

    def __init__(self, mom_dir, name):
        self.mom_dir = mom_dir
        self.name = name

    def build(self, build_type, compiler):

        assert(compiler.lower() == 'intel')

        saved_dir = os.getcwd()
        script_dir = os.path.join(self.mom_dir, 'exp')
        os.chdir(script_dir)

        debug = ''
        if build_type.lower() == 'debug':
            debug = '--debug'

        build_cmd = _build_cmd.format(mom_dir=self.mom_dir,
                                      model_name=self.name, debug=debug)
        # Build the model.
        ret = sp.call(shlex.split(build_cmd))
        os.chdir(saved_dir)

        return ret
