# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
from pylint import epylint as lint


# Pylinter for directories
class DirPylinter(object):

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        results = []
        for root, subdirs, files in os.walk(self.dir_path):
            for filename in files:
                if DirPylinter.is_python_file(filename):
                    file_path = u"{0}/{1}".format(root, filename)
                    pylinter = Pylinter(file_path)
                    pylinter_result = pylinter.run()
                    results.append(pylinter_result)
        return results

    @staticmethod
    def is_python_file(filename):
        return re.match(r"^[^\.]+\.py$", filename)


# Runs pylint on a file
class Pylinter(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.stdout = None
        self.stderr = None

    def run(self):
        (stdout, stderr) = lint.py_run(self.file_path, return_std=True)
        return PylinterResult(self.file_path, stdout, stderr)


# Stores pylint result
class PylinterResult(object):

    def __init__(self, file_path, stdout, stderr):
        self.file_path = file_path
        self.stdout = stdout.getvalue()
        self.stderr = stderr.getvalue()
