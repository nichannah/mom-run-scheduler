
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


def get_code_hashes(mom_dir):

    latest_code_hashes = []

    dirs = [mom_dir]
    for m in ['MOM6', 'SIS2', 'icebergs']:
        dirs.append(os.path.join(mom_dir, 'src', m))

    orig_dir = os.getcwd()
    for d in dirs:
        os.chdir(d)
        rev = sh.git('rev-parse', 'HEAD').strip()
        latest_code_hashes.append((d, rev))
    os.chdir(orig_dir)

    return latest_code_hashes


def checkout_latest_code(mom_dir):

    dirs = []
    for m in ['MOM6', 'SIS2', 'icebergs']:
        dirs.append(os.path.join(mom_dir, 'src', m))

    orig_dir = os.getcwd()

    for d in dirs:
        os.chdir(d)
        sh.git('checkout', 'dev/master')
    os.chdir(orig_dir)


def get_input_data(dest_dir):
    """
    Set up input data.
    """

    sh.ln('-s', '/short/v45/nah599/more_home/Download/datasets', dest_dir)

    # FIXME: perhaps this would be better.
    #sh.aws('s3', 'cp', 's3://mom6/datasets.2015.04.24.tgz', mom_dir)
