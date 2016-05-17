
import os
import pytest

class TestBuild:

    def test_build_success(self, build_dir):

        exe = os.path.join(build_dir, 'MOM6')
        build_log = os.path.join(build_dir, 'build.out')

        assert os.path.exists(build_dir)
        assert os.path.exists(build_log)

        if not os.path.exists(exe):
            with open(build_log, 'r') as f:
                print(f.read())

        assert os.path.exists(exe)
