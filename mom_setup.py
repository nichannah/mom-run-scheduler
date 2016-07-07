
import sh
import os

def get_code(mom_dir, model):
    """
    Download model code and build configs.
    """

    if model == 'MOM6':
        sh.git('clone', '--recursive',
              'https://github.com/NOAA-GFDL/MOM6-examples.git', mom_dir)
        sh.git('clone', 'https://github.com/nicjhan/mkmf.git',
                  os.path.join(mom_dir, 'mkmf'))
    else:
        assert(mode == 'MOM5')
        sh.git('clone',
              'https://github.com/BreakawayLabs/mom.git', mom_dir)


def checkout_latest_code(mom_dir, model):

    orig_dir = os.getcwd()

    if model == 'MOM6':
      dirs = []
      for m in ['MOM6', 'SIS2', 'icebergs']:
          dirs.append(os.path.join(mom_dir, 'src', m))

      for d in dirs:
          os.chdir(d)
          sh.git('checkout', 'dev/master')
    else:
        assert(mode == 'MOM5')
        os.chdir(mom_dir)
        sh.git('checkout', 'master')

    os.chdir(orig_dir)


def get_input_data(mom_dir, model):
    """
    Set up input data.
    """

    if model == 'MOM6':
        if not os.path.exists(os.path.join(mom_dir, '.datasets')):
            sh.ln('-s', '/short/v45/nah599/more_home/Download/datasets', dest_dir)
    else:
        assert(mode == 'MOM5')
        data_dir = os.path.join(mom_dir, 'data', 'archives')
        try:
            os.mkdir(data_dir)
        except OSError as e:
            if e.args[1] != 'File exists'
                raise e
        sh.rsync('/home/599/nah599/more_home/MOM5/data/archives/*.tar.gz', data_dir)

    # FIXME: perhaps this would be better.
    #sh.aws('s3', 'cp', 's3://mom6/datasets.2015.04.24.tgz', mom_dir)
