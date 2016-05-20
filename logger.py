import sys
import datetime


# logging level
ERROR = "ERROR"
INFO = "INFO"
DEBUG = "DEBUG"


class Logger:
    def __init__(self, log_file_path, ignore_debug=True):
        self.logfile = open(log_file_path, "a")
        self.ignore_debug = ignore_debug

    def _log(self, msg, level):
        if level == DEBUG and self.ignore_debug:
            return

        log_content = "[{}][{}] {}\n".format(level, datetime.datetime.now().strftime("%m-%d %H:%M:%S %f"), msg)

        self.logfile.write(log_content)
        if level == ERROR:
            sys.stderr.write(log_content)
        else:
            sys.stdout.write(log_content)

    def info(self, msg):
        self._log(msg, INFO)

    def debug(self, msg):
        self._log(msg, DEBUG)

    def error(self, msg):
        self._log(msg, ERROR)

    def flush(self):
        self.logfile.flush()
