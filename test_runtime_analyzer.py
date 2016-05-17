
import os
import pytest

class TestRuntimeAnalyzer:

    def test_for_errors(self, analyzer_run_dir):

        run_log = os.path.join(analyzer_run_dir, 'mom.out')

        assert os.path.exists(analyzer_run_dir)
        assert os.path.exists(run_log)

        with open(run_log, 'r') as f:
            output = f.read()
            if not 'Run complete, exit code: 0' in output:
                print(output)

        assert 'Run complete, exit code: 0' in output
