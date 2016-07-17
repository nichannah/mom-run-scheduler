import os, sys, shutil
import f90nml
import math
import re
import fileinput

class Run:

    def __init__(self, mom_dir, exp, build, analyzer, tmp_dir):
        self.tmp_dir = tmp_dir
        self.build = build
        self.exp = exp
        self.ncpus = 16
        if exp.min_cpus:
            self.ncpus = exp.min_cpus
        self.nnodes = int(math.ceil(self.ncpus / 16.))

        self.analyzer = analyzer
        self.analyzer_cmd = ''
        if analyzer == 'valgrind':
            self.analyzer_cmd = _valgrind_cmd.format(tmp_dir)

        self.output = ''
        self.status = 'NOT_RUN'
        self.alloc_key = None

        self.start_time = None
        self.runtime = 0

        dir = '_'.join([compiler, build, memory_type, analyzer, exp.model.name])
        self.my_dir = os.path.join(mom_dir, dir, exp.name)
        self.exe = os.path.join(mom_dir, 'build', compiler, exp.model.name,
                                    build, memory_type, 'MOM6')
        self.output_file = os.path.join(self.my_dir, 'mom.out')
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        self.exe_cmd = '(mpiexec --host {} -np {} ' + self.analyzer_cmd + \
                         ' {} &> {} ; echo {} $? >> {}) &'


    def try_to_reduce_runtime(self):

        # Change runtime when it's in the input.nml
        changed = False
        input_nml = os.path.join(self.my_dir, 'input.nml')
        if os.path.exists(input_nml):
            nml = f90nml.read(input_nml)
            nml_sect = None
            if 'coupler_nml' in nml:
                nml_sect = nml['coupler_nml']
            elif 'ocean_solo_nml' in nml:
                nml_sect = nml['ocean_solo_nml']

            if nml_sect:
                if 'months' in nml_sect:
                    nml_sect['months'] = 0

                # Runs which were multiple days now run for 6 hours.
                if 'days' in nml_sect:
                    if nml_sect['days'] >= 1:
                        nml_sect['days'] = 0
                        nml_sect['hours'] = 6
                        changed = True

                # Runs which were multiple hours now run for 1 hour.
                if not changed and 'hours' in nml_sect:
                    if nml_sect['hours'] > 1:
                        nml_sect['hours'] = 1
                        changed = True

            if changed:
                tmp_input_nml = os.path.join(self.my_dir, 'tmp_input.nml')
                nml.write(tmp_input_nml)
                shutil.move(tmp_input_nml, input_nml)
                return

        # Change runtime when it's in the MOM_input
        mom_input = os.path.join(self.my_dir, 'MOM_input')
        if os.path.exists(mom_input):
            for l in fileinput.input([mom_input], inplace=1):
                line = re.sub('DAYMAX *= *.+', 'DAYMAX = 1.0', l)
                print(line, end='')
            fileinput.close()


    def get_exe_cmd(self, node_ids):

        hosts = ','.join(node_ids)
        cmd = self.exe_cmd.format(hosts, self.ncpus, self.exe,
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

