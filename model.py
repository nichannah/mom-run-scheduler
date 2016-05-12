
from __future__ import print_function

import sys
import os
import subprocess as sp
import shlex

_file_dir = os.path.dirname(os.path.abspath(__file__))
_build_dir = os.path.normpath(os.path.join(_file_dir, '../../build'))

_build_fms_script = """
../../../../mkmf/bin/list_paths ../../../../src/FMS &&
../../../../mkmf/bin/mkmf -t ../../../../mkmf/templates/{site}-{compiler}.mk -p libfms.a -c "-Duse_libMPI -Duse_netCDF -DSPMD" path_names &&
source ../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 libfms.a -j
"""

_build_ocean_script = """
pwd &&
../../../../mkmf/bin/list_paths ./ ../../../../src/MOM6/{{config_src/dynamic_symmetric,config_src/solo_driver,src/{{*,*/*}}}}/
../../../../mkmf/bin/mkmf -t ../../../../mkmf/templates/{site}-{compiler}.mk -o '-I../../shared/{build}' -p 'MOM6 -L../../shared/{build} -lfms' -c "-Duse_libMPI -Duse_netCDF -DSPMD" path_names &&
source ../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 MOM6 -j
"""

_build_ocean_ice_script = """
pwd &&
../../../../mkmf/bin/list_paths ./ ../../../../src/MOM6/config_src/{{dynamic_symmetric,coupled_driver}} ../../../../src/MOM6/src/{{*,*/*}}/ ../../../../src/{{atmos_null,coupler,land_null,ice_param,SIS2,FMS/coupler,FMS/include}} &&
../../../../mkmf/bin/mkmf -t ../../../../mkmf/templates/{site}-{compiler}.mk -o '-I../../shared/{build}' -p 'MOM6 -L../../shared/{build} -lfms' -c '-Duse_libMPI -Duse_netCDF -DSPMD -DUSE_LOG_DIAG_FIELD_INFO' path_names &&
source ../../../../mkmf/env/{site}-{compiler}.env && make NETCDF=3 {build}=1 MOM6 -j
"""

def mkdir_p(path):
    """Create a new directory; ignore if it already exists."""
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

class Model:

    def __init__(self, name):
        self.name = name
        self.site = 'raijin'

    def build(self, build_kind, compiler):
        """
        Build this model.
        """
        saved_path = os.getcwd()
        ret = 0

        # Build FMS
        shared_dir = os.path.join(_build_dir, compiler, 'shared', build_kind)
        mkdir_p(shared_dir)
        os.chdir(shared_dir)
        command = _build_fms_script.format(site=self.site, build=build_kind,
                                           compiler=compiler)
        try:
            output = sp.check_output(command, stderr=sp.STDOUT, shell=True)
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        if ret != 0:
            return ret

        # Build either ocean_only or ice and ocean.
        model_dir = os.path.join(_build_dir, compiler, self.name, build_kind)
        mkdir_p(model_dir)
        os.chdir(model_dir)
        if self.name == 'ocean_only':
            command = _build_ocean_script.format(site=self.site, build=build_kind,
                                                 compiler=compiler)
        else:
            command = _build_ocean_ice_script.format(site=self.site, build=build_kind,
                                                     compiler=compiler)
        try:
            output = sp.check_output(command, stderr=sp.STDOUT, shell=True)
        except sp.CalledProcessError as e:
            ret = e.returncode
            print(e.output, file=sys.stderr)
        finally:
            os.chdir(saved_path)

        return ret
