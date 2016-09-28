# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import os
import re
from pylint import epylint as lint
from djangotrellostats.apps.repositories.cloc import Cloc


# Pylinter for directories
class PythonDirectoryAnalyzer(object):

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        Cloc.assert_existence()
        results = []
        for root, subdirs, files in os.walk(self.dir_path):
            for filename in files:
                if PythonDirectoryAnalyzer.is_python_file(filename):
                    file_path = u"{0}/{1}".format(root, filename)
                    if not PythonDirectoryAnalyzer.file_is_empty(file_path):
                        # Count of lines of code
                        cloc = Cloc(file_path)
                        cloc_result = cloc.run()
                        pylinter = Pylinter(file_path)
                        pylinter_result = pylinter.run()
                        pylinter_result.cloc_result = cloc_result
                        results.append(pylinter_result)
        return results

    @staticmethod
    def is_python_file(filename):
        return filename != "__init__.py" and re.match(r"^[^\.]+\.py$", filename)

    @staticmethod
    def file_is_empty(file_path):
        file_size = os.path.getsize(file_path)
        return file_size == 0


# Runs pylint on a file
class Pylinter(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.stdout = None
        self.stderr = None

    def run(self):
        command_options = u"{0} --output-format=json --reports=y".format(self.file_path)
        (stdout, stderr) = lint.py_run(command_options, return_std=True)
        return PylinterResult(self.file_path, stdout, stderr)


# Stores pylint result
class PylinterResult(object):

    def __init__(self, file_path, stdout, stderr):
        self.file_path = file_path
        self.stdout = stdout.getvalue()
        self.stderr = stderr.getvalue()

        self._init_results()

    # Initialize results
    def _init_results(self):
        self.messages = []
        if self.stdout != "":
            self.messages = json.loads(self.stdout)

