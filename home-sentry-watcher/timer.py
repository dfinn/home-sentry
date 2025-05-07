import time


class Timer:

    def __init__(self, description):
        self.start = None
        self.description = description

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start
        print(f'{self.description} [elapsed time: {elapsed:0.4f} seconds]')
