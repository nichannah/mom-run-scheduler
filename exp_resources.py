
# The minimum number of cpus needed to run a particular model

min_cpus = {
    'global_ALE/z' : 256,
    'global_ALE/layer' : 256,
    'global_ALE/SLight' : 256,
    'global_ALE/hycom' : 256,
    'nonBous_global' : 256,
    'global' : 256,
    'benchmark' : 128,
    'MESO_025_63L' : 288,
    'MESO_025_23L' : 288,
    'OM4_025' : 910,
    'OM4_05' : 128,
    'single_column/BML' : 1,
    'single_column/KPP' : 1,
    'single_column/EPBL' : 1,
    'resting/z' : 8,
    'resting/layer' : 8,
    'SCM_idealized_hurricane' : 1,
    'CVmix_SCM_tests/mech_only/BML' : 1,
    'CVmix_SCM_tests/mech_only/KPP' : 1,
    'CVmix_SCM_tests/mech_only/EPBL' : 1,
    'CVmix_SCM_tests/wind_only/BML' : 1,
    'CVmix_SCM_tests/wind_only/KPP' : 1,
    'CVmix_SCM_tests/wind_only/EPBL' : 1,
    'CVmix_SCM_tests/cooling_only/BML' : 1,
    'CVmix_SCM_tests/cooling_only/KPP' : 1,
    'CVmix_SCM_tests/cooling_only/EPBL' : 1,
    'CVmix_SCM_tests/skin_warming_wind/BML' : 1,
    'CVmix_SCM_tests/skin_warming_wind/KPP' : 1,
    'CVmix_SCM_tests/skin_warming_wind/EPBL' : 1,
    'SIS2_icebergs' : 128,
    'SIS2' : 128,
    'SIS2_bergs_cgrid' : 128,
    'SIS2_cgrid' : 128,
}

cpu_layout = {
    'OM4_025' : \
    """
    LAYOUT = 32,36
    IO_LAYOUT = 2,2
    MASKTABLE = "mask_table.242.32x36"
    """
}
