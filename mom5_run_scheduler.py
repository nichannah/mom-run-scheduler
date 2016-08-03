#!/usr/bin/env python

from __future__ import print_function

import os, sys
import time
import argparse
import pexpect
from itertools import product

from mom5_workspace import Workspace
from mom5_model import model_names, Model
from mom5_exp import exps
from mom5_run import Run
from build import Build
from scheduler import Scheduler
from pbs import Pbs

"""
Do as many MOM runs as quickly as possible. Ideally we need ~100 runs in less
than an hour.

Given a specification of a large number of MOM(6) runs this program will start
a single large PBS session and schedule all runs within that session. The runs
will be executed in parallel as much as possible.
"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('mom_dir',
        help="Path to MOM5 repo, will be downloaded if it doesn't exist")
    parser.add_argument('--ncpus', default=16, type=int)
    parser.add_argument('--already_in_pbs', action='store_true', default=False)
    parser.add_argument('--use_latest', action='store_true', default=False,
                        help='Checkout the latest MOM5')
    parser.add_argument('--fast', action='store_true', default=False,
                        help='Run a fast subset of tests.')
    args = parser.parse_args()

    ret = 0
    workspace = Workspace(os.path.realpath(args.mom_dir))
    workspace.download_code()
    for e in exps:
        workspace.download_input_data(e.name)

    analyzers = ['none', 'valgrind']
    models = [Model(workspace.mom_dir, n) for n in model_names]
    builds = [Build(*bargs) for bargs in \
                product([workspace.mom_dir], models, ['DEBUG'], ['intel'])]
    for b in builds:
        ret = b.build()
        assert(ret == 0)

    # Runs need to be created once we're in the PBS session because they need
    # to know the TMPDIR.
    pbs = Pbs(args.ncpus)
    pbs.start_session(submit_qsub=(not args.already_in_pbs))

    runs = [Run(*rargs) for rargs in \
            product(exps, builds, analyzers, \
                    [workspace.work_dir], [pbs.get_tmpdir()])]
    for r in runs:
        workspace.setup_run_dir(r.exp.name, r.run_dir)

    scheduler = Scheduler(runs, pbs)
    ret = scheduler.loop()

    return ret

if __name__ == '__main__':
    sys.exit(main())
