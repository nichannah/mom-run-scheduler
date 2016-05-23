
import os
import pytest

class TestRuntimeAnalyzer:

    def test_for_errors(self, analyzer_run_dir):

        run_log = os.path.join(analyzer_run_dir, 'mom.out')

        assert os.path.exists(analyzer_run_dir)
        assert os.path.exists(run_log)

        with open(run_log, 'r') as f:
            output = f.read()

        run_success = 'Run complete, exit code: 0' in output
        valgrind_success = 'ERROR SUMMARY: 0 errors from 0 contexts' in output

        if not run_success or not valgrind_success:
            print(output)

        assert run_success
        assert valgrind_success
