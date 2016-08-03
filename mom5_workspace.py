
import sh
import os
import subprocess as sp
import shlex
import shutil

class Workspace:

    def __init__(self, mom_dir):
        self.mom_dir = mom_dir
        self.work_dir = os.path.join(self.mom_dir, 'work')
        self.archive_dir = os.path.join(self.mom_dir, 'data', 'archives')
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

        if not os.path.exists(self.archive_dir):
            os.mkdir(self.archive_dir)

    def setup_run_dir(self, exp_name, run_dir):

        filename = '{}.input.tar.gz'.format(exp_name)
        filename_full = os.path.join(self.archive_dir, filename)

        if not os.path.exists(os.path.join(self.work_dir, filename)):
            shutil.copy(filename_full, self.work_dir)

        ret = 0
        if not os.path.exists(run_dir):
            cmd = '/bin/tar -C {} -xvf {}'.format(self.work_dir, filename_full)
            ret += sp.call(shlex.split(cmd))
            shutil.move(os.path.join(self.work_dir, exp_name), run_dir)

        for f in ['diag_table', 'data_table', 'field_table', 'input.nml']:
            src = os.path.join(run_dir, 'INPUT', f)
            dest =  os.path.join(run_dir, f)
            shutil.copy(src, dest)

        prev_dir = os.getcwd()
        os.chdir(run_dir)
        ret += sp.call(['/bin/csh',
                        os.path.join(self.mom_dir, 'exp', 'preprocessing.csh')])
        os.chdir(prev_dir)

        return ret

    def download_code(self):
        """
        Download model code and build configs.
        """

        if not os.path.exists(self.mom_dir):
            sh.git('clone', 
                    'https://github.com/BreakawayLabs/mom.git', self.mom_dir)

    def download_input_data(self, exp_name):
        """
        Download the experiment input data.
        """

        filename = '{}.input.tar.gz'.format(exp_name)
        input = os.path.join(self.archive_dir, filename)

        ret = 0
        if not os.path.exists(input):
            cmd = '{} {}'.format(os.path.join(self.mom_dir, 'data', 'get_exp_data.py'),
                                 filename)
            ret = sp.call(shlex.split(cmd))
        if ret != 0:
            return ret
        assert(os.path.exists(input))

        return ret

