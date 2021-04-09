from enum import Enum


class LogLevel(Enum):
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class Logger:
    def __init__(self):
        self.format = "HL* ({})\t{}"
        pass

    def info(self, msg):
        print(self.format.format(LogLevel.INFO.value, msg))
