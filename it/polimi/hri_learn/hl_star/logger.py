from enum import Enum


class LogLevel(Enum):
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class Logger:
    def __init__(self):
        self.format = "\nHL* ({})\t{}"
        pass

    def info(self, msg):
        print(self.format.format(LogLevel.INFO.value, msg))

    def debug(self, msg):
        print(self.format.format(LogLevel.DEBUG.value, msg))

    def warn(self, msg):
        print(self.format.format(LogLevel.WARNING.value, msg))

    def error(self, msg):
        print(self.format.format(LogLevel.ERROR.value, msg))
