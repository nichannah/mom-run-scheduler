from __future__ import print_function

import time

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
        assert key is not None
        start_idx, nnodes = key
        self.free_space_map[start_idx:start_idx+nnodes] = [True]*nnodes

    def max_available_nodes(self):
        return len(self.free_space_map)


class Scheduler:

    def __init__(self, runs, pbs):

        self.in_progress_runs = []
        self.completed_runs = []
        self.pbs = pbs

        self.allocator = NodeAllocator(pbs.get_node_ids())

        # Remove any runs which can't be run.
        self.queued_runs = []
        for r in runs:
            if r.nnodes > self.allocator.max_available_nodes():
                r.set_wont_run('Insuffient nodes')
                self.completed_runs.append(r)
            else:
                self.queued_runs.append(r)

        # Put valgrind runs first because they take so long.
        self.queued_runs.sort(key=lambda r : r.analyzer == 'valgrind', reverse=True)
        # Now sort according to size.
        self.queued_runs.sort(key=lambda r : r.nnodes, reverse=True)


    def print_report(self, filename):

        end_time = time.time()
        self.completed_runs.sort(key=lambda r : r.runtime, reverse=True)

        f = open(filename, 'w')
        for r in self.completed_runs:
            print('Completed run {} took {:.2} mins on {} CPUs.'. \
                  format(r.name, r.runtime / 60.0, r.ncpus), file=f)
        for r in self.in_progress_runs:
            runtime = (end_time - r.start_time) / 60.0
            print('Unfinished run {} took {:.2} mins on {} CPUs.'. \
                   format(r.name, runtime, r.ncpus), file=f)
        for r in self.queued_runs:
            print('Not started run {}'.format(r.name), file=f)
        f.close()
        with open(filename) as f:
            print(f.read())


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
            run.update_status()
            if run.status == 'FINISHED':
                self.in_progress_runs.remove(run)
                self.completed_runs.append(run)
                self.allocator.dealloc(run.alloc_key)
                run.alloc_key = None
                return True
            else:
                return False

        start_time = time.time()

        while len(self.queued_runs) > 0:

            # Cycle through all queued runs trying to start a new one.
            try_size = -1
            for i in range(len(self.queued_runs)):
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
            tmp_list = self.in_progress_runs[:]
            for run in tmp_list:
                update_run_status(run)

            if not self.pbs.check_session_alive():
                break

            time.sleep(1)

        while len(self.in_progress_runs) > 0:
            tmp_list = self.in_progress_runs[:]
            for run in tmp_list:
                finished = update_run_status(run)

            if not self.pbs.check_session_alive():
                break
            time.sleep(5)

        self.print_report('MOM6_test_runtimes.txt')

        return len(self.in_progress_runs) + len(self.queued_runs)
