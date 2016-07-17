class Experiment:

    def __init__(self, name, model_name, ncpus):
        self.name = name
        self.model_name = model_name
        self.ncpus = ncpus

"""
exps = [{'name' : 'om3_core3', 'model_name' :'MOM_SIS', 'ncpus' : '24'},
        {'name' : 'om3_core1', 'model_name' : 'MOM_SIS', 'ncpus' : '24'},
        {'name' : 'atlantic1', 'model_name' : 'MOM_SIS', 'ncpus' : '24'},
        {'name' : 'mom4p1_ebm1', 'model_name' : 'EBM', 'ncpus' : '17'},
        {'name' : 'MOM_SIS_TOPAZ', 'model_name' : 'MOM_SIS', 'ncpus' : '24'},
        {'name' : 'MOM_SIS_BLING', 'model_name' : 'MOM_SIS', 'ncpus' : '24'},
        {'name' : 'CM2.1p1', 'model' : 'CM2M_name', 'ncpus' : '45'},
        {'name' : 'CM2M_coarse_BLING', 'model_name' : 'CM2M', 'ncpus' : '45'},
        {'name' : 'ICCMp1', 'model' : 'ICCM_name', 'ncpus' : '54'},
        {'name' : 'ESM2M_pi-control_C2', 'model_name' : 'ESM2M', 'ncpus' : '90'},
        {'name' : 'global_0.25_degree_NYF', 'model_name' : 'MOM_SIS', 'ncpus' : '960'}]
"""

exps = [Experiment('om3_core3', 'MOM_SIS', 24),
        Experiment('om3_core1', 'MOM_SIS', 24),
        Experiment('atlantic1', 'MOM_SIS', 24),
        Experiment('mom4p1_ebm1', 'EBM', 17),
        Experiment('MOM_SIS_TOPAZ', 'MOM_SIS', 24),
        Experiment('MOM_SIS_BLING', 'MOM_SIS', 24),
        Experiment('CM2.1p1', 'CM2M', 45),
        Experiment('CM2M_coarse_BLING', 'CM2M', 45),
        Experiment('ICCMp1', 'ICCM', 54),
        Experiment('ESM2M_pi-control_C2', 'ESM2M', 90),
        Experiment('global_0.25_degree_NYF', 'MOM_SIS', 960)]
