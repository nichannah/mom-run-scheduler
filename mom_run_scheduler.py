#!/usr/bin/env python

from __future__ import print_function

import os, sys, shutil
import time
import argparse
import math
import pexpect
from itertools import product, chain
import multiprocessing as mp
import re

from model import Model
from mom_setup import get_code, get_input_data
import exp_resources

"""
Do as many MOM6 runs as quickly as possible. Ideally we need ~100 runs in less
than an hour.

Given a specification of a large number of MOM(6) runs this program will start
a single large PBS session and schedule all runs within that session. The runs
will be executed in parallel as much as possible.
"""

_valgrind_cmd = '-x LD_PRELOAD=/home/599/nah599/more_home/usr/local/lib/valgrind//libmpiwrap-amd64-linux.so /home/599/nah599/more_home/usr/local/bin//valgrind --main-stacksize=2000000000 --max-stackframe=2000000000 --error-limit=no --track-origins=yes --gen-suppressions=all --suppressions=/short/v45/nah599/more_home/MOM6-examples/tools/tests/valgrind_suppressions.txt'

class Experiment:

    def __init__(self, path, model):
        self.orig_path = path
        self.model = model
        self.name = path.split(model.name)[-1].strip('/')
        self.min_cpus = exp_resources.min_cpus.get(self.name, None)


class NodeAllocator:

    def __init__(self, node_ids):
        self.node_ids = node_ids
        self.free_space_map = [True]*len(self.node_ids)

    def alloc(self, nnodes):
        """
        Allocate nnodes nodes, return a key to be used for deallocation.
        """

        if sum(self.free_space_map) < nnodes:
            return None, None

        start_idx = None
        num_found = 0

        for i, v in enumerate(self.free_space_map):
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
            self.free_space_map[start_idx:start_idx+nnodes] = [False]*nnodes
            key = (start_idx, nnodes)
            allocated_nodes = self.node_ids[start_idx:start_idx+nnodes]
            return key, allocated_nodes
        else:
            return None, None

    def dealloc(self, key):
        start_idx, nnodes = key
        self.free_space_map[start_idx:start_idx+nnodes] = [True]*nnodes

    def max_available_nodes(self):
        return len(self.free_space_map)


class Run:

    def __init__(self, mom_dir, compiler, build, memory_type, analyzer, exp):
        self.compiler = compiler
        self.build = build
        self.memory_type = memory_type
        self.exp= exp
        self.ncpus = 16
        if exp.min_cpus:
            self.ncpus = exp.min_cpus
        self.nnodes = int(math.ceil(self.ncpus / 16.))

        self.analyzer_cmd = ''
        if analyzer == 'valgrind':
            self.analyzer_cmd = _valgrind_cmd

        self.output = ''
        self.status = 'NOT_RUN'
        self.alloc_key = None

        dir = '_'.join([compiler, build, memory_type, analyzer, exp.model.name])
        self.my_dir = os.path.join(mom_dir, dir, exp.name)
        self.exe = os.path.join(mom_dir, 'build', compiler, exp.model.name,
                                    build, memory_type, 'MOM6')
        self.output_file = os.path.join(self.my_dir, 'mom.out')

        self.exe_cmd = '(mpiexec --host {} -np {} ' + self.analyzer_cmd + \
                         ' {} &> {} ; echo {} $? >> {}) &'


    def get_exe_cmd(self, node_ids):

        hosts = ','.join(node_ids)
        cmd = self.exe_cmd.format(hosts, self.ncpus, self.exe,
                                  self.output_file,
                                  'Run complete, exit code: ',
                                  self.output_file)
        return cmd

    def update_status(self, output):
        self.output = output
        if 'Run complete' in output:
            self.status = 'FINISHED'

    def set_wont_run(self, reason):
        with open(self.output_file, 'w') as f:
            f.write("Can't run, insuffient nodes.\n")


class Pbs:

    def __init__(self, ncpus):
        self.ncpus = ncpus
        self.cmd = 'qsub -I -P v45 -q express -l ncpus={},mem={}Gb,walltime=1:00:00'.format(ncpus, ncpus*2)
        self.pobj = None
        self.prompt = '\[{}@.+\]\$ '.format(os.environ['USER'])

    def start_session(self, submit_qsub=True):

        if submit_qsub:
            self.p_obj = pexpect.spawn(self.cmd, timeout=None)
            self.p_obj.expect(self.prompt)
        else:
            self.p_obj = pexpect.spawn('bash')
            self.p_obj.expect(self.prompt)

        self.p_obj.sendline('module load openmpi/1.8.4')
        self.p_obj.expect(self.prompt)
        self.p_obj.sendline('cat $PBS_NODEFILE')
        self.p_obj.expect(self.prompt)
        nodes = self.parse_nodefile(self.p_obj.before)

        return nodes


    def start_run(self, run, nodes):
        """
        Start a run on a particular node
        """

        run.status = 'IN_PROGRESS'

        self.p_obj.sendline('cd {}'.format(run.my_dir))
        self.p_obj.expect(self.prompt)
        self.p_obj.sendline('mkdir -p RESTART')
        self.p_obj.expect(self.prompt)
        print('executing: {}'.format(run.get_exe_cmd(nodes)))
        self.p_obj.sendline(run.get_exe_cmd(nodes))
        self.p_obj.expect(self.prompt)


    def update_run_status(self, run):
        """
        Update the stdout, stderr of a current run.
        """

        if os.path.exists(run.output_file):
            with open(run.output_file, 'r') as f:
                run.update_status(f.read())

    def parse_nodefile(self, string):

        matches = re.findall('r\d+', string, flags=re.MULTILINE)
        return list(set(matches))


class Scheduler:

    def __init__(self, runs, pbs, allocator):

        self.in_progress_runs = []
        self.completed_runs = []
        self.allocator = allocator
        self.pbs = pbs

        # Remove any runs which can't be run.
        self.queued_runs = []
        for r in runs:
            if r.nnodes > allocator.max_available_nodes():
                r.set_wont_run('Insuffient nodes')
                self.completed_runs.append(r)
            else:
                self.queued_runs.append(r)

        self.queued_runs.sort(key=lambda x : x.nnodes, reverse=True)


    def find_largest_queued_run_smaller_than(self, try_size):
        if try_size == -1:
            return self.queued_runs[0]
        else:
            for r in self.queued_runs:
                if r.nnodes < try_size:
                    return r

        return None

    def loop(self):

        def update_run_status(run):
            self.pbs.update_run_status(run)
            if run.status == 'FINISHED':
                self.in_progress_runs.remove(run)
                self.completed_runs.append(run)
                self.allocator.dealloc(run.alloc_key)

        while len(self.queued_runs) > 0:

            # Cycle through all queued runs trying to start a new one.
            try_size = -1
            for i, _ in enumerate(self.queued_runs):
                run = self.find_largest_queued_run_smaller_than(try_size)
                if run is None:
                    break
                key, nodes = self.allocator.alloc(run.nnodes)
                if key:
                    self.in_progress_runs.append(run)
                    self.queued_runs.remove(run)
                    run.alloc_key = key
                    self.pbs.start_run(run, nodes)
                    break
                else:
                    try_size = run.nnodes

            # Cycle through all in progress runs seeing if any have finished.
            for run in self.in_progress_runs:
                update_run_status(run)

            time.sleep(1)

        while len(self.in_progress_runs) > 0:
            for run in self.in_progress_runs:
                update_run_status(run)
            time.sleep(5)


def create_runs(mom_dir, configs):
    """
    Return a list of all run objs
    """

    runs = []
    for args in product(*configs):
        if 'valgrind' in args and 'REPRO' in args:
            continue
        runs.append(Run(mom_dir, *args))

    return runs


def init_run_dirs(configs, mom_dir):
    """
    Assume that code has been downlowded. Setup run directories.
    """

    for args in product(*configs):
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


def build_shared(args):
    model, compiler, build = args
    model.build_shared(compiler, build)

def build_model(args):
    model, compiler, build, memory_type = args
    model.build_model(compiler, build, memory_type)

def build_models(models, compilers, builds, memory_types):

    p = mp.Pool()
    p.map(build_shared, product([models[0]], compilers, builds))
    p.map(build_model, product(models, compilers, builds, memory_types))
    p.close()
    p.join()


def discover_experiments(mom_dir, models):
    """
    Return a list of all experiment paths relative to the top of the mom dir.
    """

    def fix_exp_path(path, mom_dir):
        path = os.path.normpath(path)
        path = path.replace(mom_dir, '')
        # Remove possible '/' from front and back.
        return path.strip('/')

    exps = []
    paths = [os.path.join(mom_dir, m.name) for m in models]
    for path, dirs, filenames in chain.from_iterable(os.walk(p) for p in paths):
        for fname in filenames:
            if fname == 'input.nml' and 'common' not in path:
                model = None
                for m in models:
                    if m.name in path:
                        model = m
                        break

                if model:
                    e = Experiment(fix_exp_path(path, mom_dir), model)
                    exps.append(e)
    return exps


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('mom_dir',
        help="Path to MOM6-examples, will be downloaded if it doesn't exist")
    parser.add_argument('--ncpus', default=16, type=int)
    parser.add_argument('--already_in_pbs', action='store_true', default=False)
    args = parser.parse_args()

    args.mom_dir = os.path.realpath(args.mom_dir)

    if not os.path.exists(args.mom_dir):
        get_code(args.mom_dir)

    if not os.path.exists(os.path.join(args.mom_dir, '.datasets')):
        get_input_data(os.path.join(args.mom_dir, '.datasets'))

    compilers = ['intel', 'gnu']
    builds = ['DEBUG', 'REPRO']
    memory_types = ['dynamic', 'dynamic_symmetric']
    analyzers = ['none', 'valgrind']
    ocean_only = Model('ocean_only', args.mom_dir)
    ice_ocean_SIS2 = Model('ice_ocean_SIS2', args.mom_dir)
    models = [ocean_only, ice_ocean_SIS2]

    exps = discover_experiments(args.mom_dir, models)
    configs = (compilers, builds, memory_types, analyzers, exps)

    build_models(models, compilers, builds, memory_types)

    runs = create_runs(args.mom_dir, configs)
    init_run_dirs(configs[:-1], args.mom_dir)

    pbs = Pbs(args.ncpus)
    node_ids = pbs.start_session(submit_qsub=(not args.already_in_pbs))
    allocator = NodeAllocator(node_ids)
    scheduler = Scheduler(runs, pbs, allocator)
    scheduler.loop()

if __name__ == '__main__':
    sys.exit(main())
