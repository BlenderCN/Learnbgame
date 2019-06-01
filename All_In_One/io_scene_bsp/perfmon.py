import time

class PerformanceMonitor:
    """Simple class for timing addon performance. Adapted from the official
    Blender FBX addon.

    Example:
        pmon = PerformanceMonitor('Demo')
        pmon.push_scope('Starting')

        pmon.step('Step 1: A single measurement')
        # Do work

        pmon.push_scope('Step 2: A measurement with four tasks')

        for i in range(4):
            # Do work
            pmon.step(f'Task{i} completed')

        pmon.pop()
        pmon.pop('Finished')

    """

    def __init__(self, identifier=''):
        self.level = -1
        self.reference_time = []
        self.identifier = identifier

    def push_scope(self, message=''):
        self.level += 1
        self.reference_time.append(None)

        if message:
            print(f'{"   " * self.level}{self.identifier}: {message}')

    def pop_scope(self, message=''):
        if not self.reference_time:
            if message:
                print(message)

            return

        reference_time = self.reference_time[self.level]
        delta = time.process_time() - reference_time if reference_time else 0
        print(f'{"   " * (self.level + 1)}Done ({delta} sec)\n')

        if message:
            print(f'{"   " * self.level}{self.identifier}: {message}')

        del self.reference_time[self.level]
        self.level -= 1

    def step(self, message=''):
        reference_time = self.reference_time[self.level] or 0
        current_time = time.process_time()

        delta = current_time - reference_time
        if reference_time:
            print(f'{"   " * (self.level + 1)}Done ({delta} sec)\n')

        self.reference_time[self.level] = current_time

        if message:
            print(f'{"   " * self.level}{self.identifier}: {message}')

    def __del__(self):
        while self.level >= 0:
            self.pop_scope()
