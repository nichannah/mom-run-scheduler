class Experiment:

    def __init__(self, path, model):
        self.orig_path = path
        self.model = model
        self.name = path.split(model.name)[-1].strip('/')
        self.min_cpus = exp_resources.min_cpus.get(self.name, None)


mom6_exps = [
    {'name' : 'global_ALE/z', 'ncpus' : 256},
    {'name' : 'global_ALE/layer', 'ncpus' : 256},
    {'name' : 'global_ALE/SLight', 'ncpus' : 256},
    {'name' : 'global_ALE/hycom', 'ncpus' : 256},
    {'name' : 'nonBous_global', 'ncpus' : 256},
    {'name' : 'global', 'ncpus' : 256},
    {'name' : 'benchmark', 'ncpus' : 128},
    {'name' : 'MESO_025_63L', 'ncpus' : 288},
    {'name' : 'MESO_025_23L', 'ncpus' : 288},
    {'name' : 'OM4_025', 'ncpus' : 480},
    {'name' : 'single_column/BML', 'ncpus' : 1},
    {'name' : 'single_column/KPP', 'ncpus' : 1},
    {'name' : 'single_column/EPBL', 'ncpus' : 1},
    {'name' : 'resting/z', 'ncpus' : 8},
    {'name' : 'resting/layer', 'ncpus' : 8},
    {'name' : 'SCM_idealized_hurricane', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/mech_only/BML', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/mech_only/KPP', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/mech_only/EPBL', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/wind_only/BML', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/wind_only/KPP', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/wind_only/EPBL', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/cooling_only/BML', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/cooling_only/KPP', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/cooling_only/EPBL', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/skin_warming_wind/BML', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/skin_warming_wind/KPP', 'ncpus' : 1},
    {'name' : 'CVmix_SCM_tests/skin_warming_wind/EPBL', 'ncpus' : 1},
    {'name' : 'SIS2_icebergs', 'ncpus' : 128},
    {'name' : 'SIS2', 'ncpus' : 128},
    {'name' : 'SIS2_bergs_cgrid', 'ncpus' : 128},
    {'name' : 'SIS2_cgrid', 'ncpus' : 128}
]
