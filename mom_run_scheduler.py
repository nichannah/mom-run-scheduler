#!/usr/bin/env python

from __future__ import print_function

import os, sys, shutil
import argparse
import math
import pexpect
import itertools
import multiprocessing as mp
import re

"""
Do as many MOM6 runs as quickly as possible. Ideally we need ~100 runs in less
than an hour.

Given a specification of a large number of MOM(6) runs this program will start
a single large PBS session and schedule all runs within that session. The runs
will be executed in parallel as much as possible.
"""

class Experiment:

    def __init__(self, path, model):
        self.path = path
        self.model = model


class NodeAllocator:

    def __init__(self, node_ids):
        self.node_ids = node_ids
        self.free_space_map = [True]*len(self.node_ids)

    def alloc(self, nnodes):
        """
        Allocate nnodes nodes, return a key to be used for deallocation.
        """

        if sum(self.free_space_map) < nnodes:
            return None

        start_idx = None
        num_found = 0

        for i, v in enumerate(free_space_map):
            if v:
                if start_idx is None:
                    start_idx = i
                num_found += 1

                if num_found == nnodes:
                    break
            else:
                start_idx = None
                num_found = 0

        if num_found == nnodes:
            self.free_space_map[start_idx:start_idx+nnodes] = False
            key = (start_idx, nnodes)
            allocated_nodes = self.node_ids[start_idx:start_idx+nnodes]
            return key, allocated_nodes
        else:
            return None

    def dealloc(self, key):
        start_idx, nnodes = key
        self.free_space_map[start_idx:start_idx+nnodes] = True


class Run:

    def __init__(self, mom_dir, compiler, build, memory_type, analyzer, model, exp):
        self.compiler = compiler
        self.build = build
        self.memory_type = memory_type
        self.analyzer = analyzer
        self.exp= exp
        self.ncpus = 8
        self.nnodes = int(math.ceil(self.ncpus / 16.))

        self.output = ''
        self.status = 'NOT_RUN'
        self.alloc_key = None

        dir = '_'.join([compiler, build, memory_type, analyzer, exp.path])
        self.my_dir = os.path.join(mom_dir, dir)
        self.exe = os.path.join(mom_dir, 'build', compiler, exp.model, build, 'MOM6')
        self.output_file = os.path.join(self.my_dir, 'mom.out')
        self.exe_cmd = '(mpirun --hosts {} -np {} {} &> {} ; echo {}) &'

    def get_exe_cmd(self, node_ids)

        hosts = ','.join(node_ids)
        cmd = self.my_exe_cmd.format(hosts, self.ncpus, self.exe,
                                        self.output_file, 'Run complete')
        return cmd

    def update_status(self, output):
        self.output = output
        if 'Run complete' in output:
            self.status = 'FINISHED'

class Pbs:

    def __init__(self, ncpus):
        self.ncpus = ncpus
        self.cmd = 'qsub -I -P v45 -q express -l ncpus={},mem={}Gb,walltime=1:00:00'.format(ncpus, ncpus*2)
        self.pobj = None

    def start_session(self, submit_qsub=True):

        if submit_qsub:
            self.p_obj = pexpect.spawn(self.cmd, timeout=None)
            self.p_obj.expect('\[.+\]\$ ')
        else:
            self.p_obj = pexpect.spawn('bash')
            self.p_obj.expect('\[.+\]\$ ')

        self.p_obj.sendline('module load openmpi/1.8.4')
        self.p_obj.expect('\[.+\]\$ ')
        self.p_obj.sendline('cat $PBS_NODEFILE')
        self.p_obj.expect('\[.+\]\$ ')
        nodes = self.parse_nodefile(self.p_obj.before)

        return nodes


    def start_run(self, run, nodes):
        """
        Start a run on a particular node
        """

        run.status = 'IN_PROGRESS'

        self.p_obj.sendline('cd {}'.format(run.my_dir))
        self.p_obj.expect('\[.+\]\$ ')
        self.p_obj.sendline(run.get_exe_cmd(nodes))
        self.p_obj.expect('\[.+\]\$ ')


    def update_run_status(self, run):
        """
        Update the stdout, stderr of a current run.
        """

        self.p_obj.sendline('cat ' + run.output_file)
        self.p_obj.expect('\[.+\]\$ ')
        run.update_status(self.p_obj.before)


    def parse_nodefile(self, string):

        matches = re.findall('r\d+', string, flags=re.MULTILINE)
        return list(set(matches))

class Scheduler:

    def __init__(self, runs, pbs, allocator):

        self.queued_runs = sorted(runs, key=lambda x : x.nnodes, reverse=True)
        self.in_progress_runs = []
        self.completed_runs = []

    def find_largest_queued_run_smaller_than(self, try_size):
        if try_size == -1:
            return self.queued_runs[0]
        else:
            for r in self.queued_runs:
                if r.nnodes < try_size:
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
                key, nodes = allocator.alloc(run.nnodes)
                if key:
                    in_progress_runs.append(run)
                    queued_runs.remove(run)
                    run.alloc_key = key
                    pbs.start_run(run, nodes)
                    break
                else:
                    try_size = run.nnodes

            # Cycle through all in progress runs seeing if any have finished.
            for run in in_progress_runs:
                pbs.update_run_status(run)
                if run.status == 'FINISHED':
                    in_progress_runs.remove(run)
                    completed_runs.append(run)
                    allocator.dealloc(run.alloc_key)

            time.sleep(1)


def create_runs(mom_dir, exps, configs):
    """
    Return a list of all run objs
    """

    runs = []
    for args in itertools.product(*configs):
        runs.append(Run(mom_dir, *args))

    return runs


def init_run_dirs(configs, mom_dir):
    """
    Assume that code has been downlowded. Setup run directories.
    """

    for args in itertools.product(*configs):
        new_dir = os.path.join(mom_dir, '_'.join(args).strip('_') + \
                    '_ocean_only')
        if not os.path.exists(new_dir):
            shutil.copytree(os.path.join(mom_dir, 'ocean_only'), new_dir,
                                symlinks=True)
        new_dir = os.path.join(mom_dir, '_'.join(args).strip('_') + \
                    '_ice_ocean_SIS2')
        if not os.path.exists(new_dir):
            shutil.copytree(os.path.join(mom_dir, 'ice_ocean_SIS2'), new_dir,
                                symlinks=True)


def build_model(args)

    model, compiler, build, memory_type = args
    model.build(compiler, build, memory_type)

def build_models(models, compilers, builds, memory_types):

    args = []
    for config in itertools.product([models, compilers, builds, memory_types]):
        args.append(config)

    mp.map(build_model, args)


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
                model = None
                if 'ocean_only' in path:
                    model = 'ocean_only'
                if 'ice_ocean_sis2' in path:
                    model = 'ice_ocean_sis2'

                if model:
                    e = Experiment(fix_exp_path(path, mom_dir), model)
                    exps.append(e)
    return exps


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('mom_dir', help='Path to MOM6-examples')
    parser.add_argument('--ncpus', default=16, type=int)
    parser.add_argument('--already_in_pbs', action='store_true', default=False)
    args = parser.parse_args()

    args.mom_dir = os.path.realpath(args.mom_dir)

    compilers = ['intel', 'gnu']
    builds = ['debug', 'repro']
    memory_types = ['dynamic_symmetric']
    analyzers = ['', 'valgrind']
    exps = discover_experiments(args.mom_dir)
    configs = (compilers, builds, memory_types, analyzers, exps)

    ocean_model = Model('ocean_model', args.mom_dir)
    ice_ocean_SIS2 = Model('ice_ocean_SIS2', args.mom_dir)
    models = [ocean_model, ice_ocean_SIS2]
    build_models(models, compilers, builds, memory_types)

    runs = create_runs(args.mom_dir, configs)
    init_run_dirs(configs[:-1], args.mom_dir)

    pbs = Pbs(args.ncpus)
    node_ids = pbs.start_session(submit_qsub=(not args.already_in_pbs))
    allocator = NodeAllocator(node_ids)
    scheduler = Scheduler(runs, pbs, allocator)

    scheduler.loop(runs, pbs, allocator)

if __name__ == '__main__':
    sys.exit(main())
