
import os
import pytest
from itertools import product

from model import get_model_build_dir
from mom_run_scheduler import get_config_run_dir

def pytest_addoption(parser):
    parser.addoption('--mom_dir', default='./MOM6-examples',
                     help="Path to the MOM top-level dir.")
    parser.addoption('--exp', default='ocean_only-double_gyre')
    parser.addoption('--compiler', default='intel')
    parser.addoption('--build', default='DEBUG')
    parser.addoption('--memory_type', default='dynamic')
    parser.addoption('--analyzer', default='none')


def get_run_dirs(mom_dir, model_names, exp_paths, configs):

    config_run_dirs = [get_config_run_dir(*a) for a in \
                        product([mom_dir], model_names, *configs)]

    run_dirs = []
    for e in exp_paths:
        for r in config_run_dirs:
            for m in model_names:
                if m in e and m in r:
                    en = e.split(m)[1].strip('/')
                    run_dirs.append(os.path.join(r, en))

    return run_dirs


def pytest_generate_tests(metafunc):
    """
    Parameterize tests, just pass the command line options to the test.
    """

    mom_dir = metafunc.config.option.mom_dir
    mom_dir = './MOM6-examples'
    exps = [metafunc.config.option.exp]
    exp_paths = [e.replace('-', '/') for e in exps]

    model_names = list(set([e.split('-')[0] for e in exps]))

    compilers = [metafunc.config.option.compiler]
    builds = [metafunc.config.option.build]
    memory_types = [metafunc.config.option.memory_type]
    analyzers = [metafunc.config.option.analyzer]
    configs = (compilers, builds, memory_types, analyzers)
    run_dirs = get_run_dirs(mom_dir, model_names, exp_paths, configs)

    if 'exp' in metafunc.funcargnames:
        metafunc.parametrize('exp', [exp_paths])
    if 'build' in metafunc.funcargnames:
        metafunc.parametrize('build', [build])
    if 'compiler' in metafunc.funcargnames:
        metafunc.parametrize('compiler', [compiler])
    if 'memory' in metafunc.funcargnames:
        metafunc.parametrize('memory', [memory])
    if 'analyzer' in metafunc.funcargnames:
        metafunc.parametrize('analyzer', [analyzer])

    if 'build_dir' in metafunc.funcargnames:
        args = product([mom_dir], compilers, model_names, builds, memory_types)

        build_dirs = []
        for a in args:
            build_dirs.append(get_model_build_dir(*a))

        metafunc.parametrize('build_dir', build_dirs)

    if 'run_dir' in metafunc.funcargnames:
        metafunc.parametrize('run_dir', run_dirs)

    if 'analyzer_run_dir' in metafunc.funcargnames:
        metafunc.parametrize('analyzer_run_dir',
                                filter(lambda x : 'valgrind' in x, run_dirs))
