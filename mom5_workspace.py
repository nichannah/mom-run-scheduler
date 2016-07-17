
import sh
import os

class Workspace:

    def __init__(self, dir):
        self.dir = dir

    def download_code(self):
        """
        Download model code and build configs.
        """

        if not os.path.exists(self.dir):
            sh.git('clone', 
                    'https://github.com/BreakawayLabs/mom.git', self.dir)

    def download_input_data(self, exp_name):
        """
        Download the experiment input data.
        """

        data_dir = os.path.join(self.dir, 'data')
        archive_dir = os.path.join(data_dir, 'archives')
        work_dir = os.path.join(self.dir, 'work', exp_name)

        filename = '{}.input.tar.gz'.format(exp_name)
        input = os.path.join(archive_dir, filename)

        ret = 0
        if not os.path.exists(input):
            cmd = '{} {}'.format(os.path.join(self.dir, 'data', 'get_exp_data.py'),
                                 filename)
            ret = sp.call(shlex.split(cmd))
        if ret != 0:
            return ret
        assert(os.path.exists(input))

        # Unzip into work directory.
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        if not os.path.exists(os.path.join(work_dir, filename)):
            shutil.copy(input, work_dir)

        if not os.path.exists(os.path.join(work_dir, exp_name)):
            cmd = '/bin/tar -C {} -xvf {}'.format(work_dir, input)
            ret += sp.call(shlex.split(cmd))

        return ret

