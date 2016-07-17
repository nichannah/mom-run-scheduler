
import sh
import os

class Workspace:

    def __init__(self, dir):
        self.dir = dir

    def get_code(self):
        """
        Download model code and build configs.
        """
        sh.git('clone', '--recursive',
                'https://github.com/NOAA-GFDL/MOM6-examples.git', self.dir)
        sh.git('clone', 'https://github.com/nicjhan/mkmf.git',
                    os.path.join(self.dir, 'mkmf'))


    def checkout_latest_code(self):

        dirs = []
        for m in ['MOM6', 'SIS2', 'icebergs']:
            dirs.append(os.path.join(self.dir, 'src', m))

        orig_dir = os.getcwd()

        for d in dirs:
            os.chdir(d)
            sh.git('checkout', 'dev/master')
        os.chdir(orig_dir)

    def download_input_data(self):
        """
        Set up input data.
        """

        dest_dir = os.path.join(self.dir, '.datasets')
        if not os.path.exists(dest_dir):
            sh.ln('-s', '/short/v45/nah599/more_home/Download/datasets', dest_dir)

        # FIXME: perhaps this would be better.
        #sh.aws('s3', 'cp', 's3://mom6/datasets.2015.04.24.tgz', mom_dir)
