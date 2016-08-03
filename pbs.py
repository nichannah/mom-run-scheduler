import os
import re
import pexpect
import time

class Pbs:

    def __init__(self, ncpus):
        self.ncpus = ncpus
        self.pobj = None
        self.prompt = '\[{}@.+\]\$ '.format(os.environ['USER'])
        self.nodes = []

        queue = 'normal'
        if ncpus <= 32:
            queue = 'express'
        self.cmd = 'qsub -I -P e14 -q {} -l ncpus={},mem={}Gb,walltime=5:00:00,jobfs=100GB'.format(queue, ncpus, ncpus*2)


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
        self.nodes = self.parse_nodefile(self.p_obj.before)

    def get_node_ids(self):
        return self.nodes

    def get_tmpdir(self):
        """
        Get tmpdir within PBS session
        """

        if not self.check_session_alive():
            return None

        try:
            self.p_obj.sendline('echo $TMPDIR')
            self.p_obj.expect(self.prompt)
            tmpdir = self.parse_tmpdir(self.p_obj.before)
        except pexpect.EOF:
            tmpdir = None

        return tmpdir


    def check_session_alive(self):
        """
        Check whether the PBS session is still alive.
        """

        try:
            self.p_obj.sendline('echo $PBS_JOBID')
            self.p_obj.expect(self.prompt)
            pbs_jobid = self.parse_jobid(self.p_obj.before)
        except pexpect.EOF:
            pbs_jobid = None

        if pbs_jobid:
            return True
        else:
            return False


    def start_run(self, run, nodes):
        """
        Start a run on a particular node
        """

        try:
            self.p_obj.sendline('cd {}'.format(run.run_dir))
            self.p_obj.expect(self.prompt)
            self.p_obj.sendline('mkdir -p RESTART')
            self.p_obj.expect(self.prompt)
            print('executing: {}'.format(run.get_exe_cmd(nodes)))
            self.p_obj.sendline(run.get_exe_cmd(nodes))
            self.p_obj.expect(self.prompt)

            run.status = 'IN_PROGRESS'
            run.start_time = time.time()
            return True
        except pexpect.EOF:
            return False


    def parse_nodefile(self, string):

        matches = re.findall('r\d+', string, flags=re.MULTILINE)
        return list(set(matches))


    def parse_jobid(self, string):

        m = re.search('\d+\.r-man2', string)
        if m:
            return m.group(0)
        else:
            return None


    def parse_tmpdir(self, string):

        m = re.search('^.+\d+\.r-man2', string, flags=re.MULTILINE)

        if m:
            return m.group(0)
        else:
            return None


