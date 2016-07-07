
from __future__ import print_function

import sys
import os
import subprocess as sp
import shlex

def mkdir_p(path):
    """Create a new directory; ignore if it already exists."""
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


class MOM5Model:

    def __init__(self, name, mom_dir):
        self.name = name
        self.mom_dir = mom_dir
        self.site = 'raijin'

    def build(self, compiler, build, memory_type):
        """
        Build this model.
        """
        saved_path = os.getcwd()
        ret = 0

        # Build either ocean_only or ice and ocean.

        model_dir = get_model_build_dir(self.mom_dir, compiler, self.name,
                                        build, memory_type)
        mkdir_p(model_dir)
        os.chdir(model_dir)
        if self.name == 'ocean_only':
            command = _build_ocean_script.format(site=self.site, build=build,
                                                 compiler=compiler,
                                                 memory_type=memory_type)
        elif self.name == 'ice_ocean_SIS2':
            command = _build_ocean_ice_script.format(site=self.site, build=build,
                                                     compiler=compiler,
                                                     memory_type=memory_type)
        else:
            print('Unsupported model type', file=sys.stderr)
            assert False
        try:
            output = sp.check_output(command, stderr=sp.STDOUT, shell=True)
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        with open(os.path.join(model_dir, 'build.out'), 'w') as f:
            f.write(output)

        return ret
