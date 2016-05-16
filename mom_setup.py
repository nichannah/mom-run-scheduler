
import sh
import os

def get_code(mom_dir):
    """
    Download model code and build configs.
    """
    sh.git('clone', '--recursive',
            'https://github.com/NOAA-GFDL/MOM6-examples.git', mom_dir)
    sh.git('clone', 'https://github.com/nicjhan/mkmf.git',
                os.path.join(mom_dir, 'mkmf'))

def get_input_data(dest_dir):
    """
    Set up input data.
    """

    sh.ln('-s', '$HOME/more_home/Download/datasets', dest_dir)

    # FIXME: perhaps this would be better.
    #sh.aws('s3', 'cp', 's3://mom6/datasets.2015.04.24.tgz', mom_dir)
