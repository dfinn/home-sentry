class Logger:

    def __init__(self, name, is_verbose_mode):
        self.name = name
        self.is_verbose_mode = is_verbose_mode

    def verbose(self, msg):
        if self.is_verbose_mode:
            print(f'[{self.name}] {msg}')

    def info(self, msg):
        print(f'[{self.name}] {msg}')

