import os, sys, shutil
import math
import re
import fileinput

_valgrind_cmd = '-x TMPDIR={} -x LD_PRELOAD=/home/599/nah599/more_home/usr/local/lib/valgrind/libmpiwrap-amd64-linux.so /home/599/nah599/more_home/usr/local/bin//valgrind --main-stacksize=200000000 --max-stackframe=200000000 --error-limit=no --track-origins=yes --freelist-vol=10000000 --gen-suppressions=all --suppressions=/short/v45/nah599/more_home/valgrind_suppressions.txt'

class Run:

    def __init__(self, exp, build, analyzer, mom_dir, tmp_dir):
        self.exp = exp
        self.build = build
        self.analyzer = analyzer
        self.mom_dir = mom_dir
        self.tmp_dir = tmp_dir

        self.nnodes = int(math.ceil(exp.ncpus / 16.))

        self.analyzer_cmd = ''
        if analyzer == 'valgrind':
            self.analyzer_cmd = _valgrind_cmd.format(tmp_dir)

        self.output = ''
        self.status = 'NOT_RUN'
        self.alloc_key = None

        self.start_time = None
        self.runtime = 0

        self.my_dir = os.path.join(mom_dir, 'work', exp.name)
        self.output_file = os.path.join(self.my_dir, 'mom.out')
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        self.exe_cmd = '(mpiexec --host {} -np {} ' + self.analyzer_cmd + \
                         ' {} &> {} ; echo {} $? >> {}) &'

    def get_exe_cmd(self, node_ids):

        hosts = ','.join(node_ids)
        cmd = self.exe_cmd.format(hosts, self.ncpus, self.build.exe,
                                  self.output_file,
                                  'Run complete, exit code: ',
                                  self.output_file)
        return cmd


    def update_status(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                output = f.read()
                if 'Run complete' in output:
                    self.status = 'FINISHED'
                    self.runtime = time.time() - self.start_time


    def set_wont_run(self, reason):
        with open(self.output_file, 'w') as f:
            f.write("Can't run, insuffient nodes.\n")

