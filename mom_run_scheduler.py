#!/usr/bin/env python

from __future__ import print_function

import os, sys, shutil
import argparse
import math
import string
import itertools

"""
Do as many MOM6 runs as quickly as possible. Ideally we need ~100 runs in less
than an hour.

Given a specification of a large number of MOM(6) runs this program will start
a single large PBS session and schedule all runs within that session. The runs
will be executed in parallel as much as possible.
"""

class SlotAllocator:

    def __init__(self, slot_ids):
        self.slot_ids = slot_ids
        self.free_space_map = [True]*len(self.slot_ids)

    def alloc(self, nslots):
        """
        Allocate nslots, return a key to be used for deallocation.
        """

        if sum(self.free_space_map) < nslots:
            return None

        start_idx = None
        num_found = 0

        for i, v in enumerate(free_space_map):
            if v:
                if start_idx is None:
                    start_idx = i
                num_found += 1

                if num_found == nslots:
                    break
            else:
                start_idx = None
                num_found = 0

        if num_found == nslots:
            self.free_space_map[start_idx:start_idx+nslots] = False
            return (start_idx, nslots), self.slot_ids[start_idx]
        else:
            return None

    def dealloc(self, key):
        start_idx, nslots = key
        self.free_space_map[start_idx:start_idx+nslots] = True


class Run:

    def __init__(self, compiler, build, memory_type, analyzer, exp):
        self.compiler = compiler
        self.build = build
        self.memory_type = memory_type
        self.analyzer = analyzer
        self.exp= exp
        self.ncpus = 8
        self.nslots = int(math.ceil(self.ncpus / 16.))

        self.output = ''
        self.status = 'NOT_RUN'
        self.alloc_key = None



class Pbs:

    def __init__(self, ncpus):
        self.ncpus = ncpus
        self.cmd = 'qsub -I -P v45 -q express -l ncpus={},mem={}Gb,walltime=1:00:00'.format(ncpus, ncpus*2)
        self.pobj = None

    def start_session(self):

        self.p_obj = pexpect.spawn(self.cmd)
        self.p_obj.expect('\[.+\]\$ ')
        self.p_obj.sendline('cat $PBS_NODEFILE')
        self.p_obj.expect('\[.+\]\$ ')

        return slots

    def start_run(run, node):
        """
        Start a run on a particular node
        """

        run.status = 'IN_PROGRESS'
        return True


    def update_run_status(run):
        """
        Update the stdout, stderr of a current run.
        """

        run.output = ''
        if run.output[-12:]  == 'run finished':
            run.status = 'FINISHED'


class Scheduler:

    def __init__(self, runs, pbs, allocator):

        self.queued_runs = sorted(runs, key=lambda x : x.slots, reverse=True)
        self.in_progress_runs = []
        self.completed_runs = []

    def find_largest_queued_run_smaller_than(self, try_size):
        if try_size == -1:
            return self.queued_runs[0]
        else:
            for r in self.queued_runs:
                if r.slots < try_size:
                    return r

        return None

    def loop(self):

        while len(queue_runs) > 0:

            # Cycle through all queued runs trying to start a new one.
            try_size = -1
            for i, _ in enumerate(self.queued_runs):
                run = find_largest_queued_run_smaller_than(try_size)
                if run is None:
                    break
                key, node = allocator.alloc(run.slots)
                if key:
                    in_progress_runs.append(run)
                    queued_runs.remove(run)
                    run.alloc_key = key
                    pbs.start_run(run, node)
                    break
                else:
                    try_size = run.slots

            # Cycle through all in progress runs seeing if any have finished.
            for run in in_progress_runs:
                pbs.update_run_ouput(run)
                if run.status == 'FINISHED':
                    in_progress_runs.remove(run)
                    completed_runs.append(run)
                    allocator.dealloc(run.alloc_key)

            time.sleep(1)

def create_runs(mom_dir, configs):
    """
    Return a list of all run objs
    """

    runs = []
    for args in itertools.product(*configs):
        runs.append(Run(*args))


def init_run_dirs(configs, mom_dir):
    """
    Assume that code has been downlowded. Setup run directories, build the models.
    """

    for args in itertools.product(*configs):
        new_dir = os.path.join(mom_dir, '_'.join(args).strip('_') + \
                    '_ocean_only')
        shutil.copytree(os.path.join(mom_dir, 'ocean_only'), new_dir)
        new_dir = os.path.join(mom_dir, '_'.join(args).strip('_') + \
                    '_ocean_ice_SIS2')
        shutil.copytree(os.path.join(mom_dir, 'ocean_ice_SIS2'), new_dir)


def discover_experiments(mom_dir):
    """
    Return a list of all experiment paths relative to the top of the mom dir.
    """

    def fix_exp_path(path, mom_dir):
        path = os.path.normpath(path)
        path = path.replace(mom_dir, '')
        # Remove possible '/' from front and back.
        return path.strip('/')

    exps = []
    for path, dirs, filenames in os.walk(mom_dir):
        for fname in filenames:
            if fname == 'input.nml' and 'common' not in path:
                exps.append(fix_exp_path(path, mom_dir))
    return exps


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('mom_dir', help='Path to MOM6-examples')
    parser.add_argument('--ncpus', default=1280)
    args = parser.parse_args()

    compilers = ['intel', 'gnu']
    builds = ['debug', 'repro']
    memory_types = ['dynamic_symmetric']
    analyzers = ['', 'valgrind']
    exps = discover_experiments(args.mom_dir)
    configs = (compilers, builds, memory_types, analyzers, exps)

    runs = create_runs(args.mom_dir, configs)
    init_run_dirs(configs[:-1], args.mom_dir)

    pbs = Pbs(args.ncpus)
    slot_ids = pbs.start_session()
    allocator = SlotAllocator(slot_ids)
    scheduler = Scheduler(runs, pbs, allocator)

    scheduler.loop(runs, pbs, allocator)

if __name__ == '__main__':
    sys.exit(main())
