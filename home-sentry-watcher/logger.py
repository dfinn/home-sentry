class Logger:

    def __init__(self, name, is_verbose_mode):
        self.name = name
        self.is_verbose_mode = is_verbose_mode

    def verbose(self, msg):
        """
        Logs the message only if verbose mode is active.
        """
        if self.is_verbose_mode:
            print(f'[{self.name}] {msg}')

    def info(self, msg):
        """
        Logs the message provided.
        """
        print(f'[{self.name}] {msg}')

