import json
import os
import re
import subprocess
from djanban.apps.repositories.cloc import Cloc


# Pylinter for directories
class PythonDirectoryAnalyzer:

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        Cloc.assert_existence()
        results = []
        for root, subdirs, files in os.walk(self.dir_path):
            for filename in files:
                if PythonDirectoryAnalyzer.is_python_file(filename):
                    file_path = f"{root}/{filename}"
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
class Pylinter:

    def __init__(self, file_path):
        self.file_path = file_path
        self.stdout = None
        self.stderr = None

    def run(self):
        command = [
            'pylint',
            self.file_path,
            '--output-format=json'
        ]
        # In modern pylint, --reports=y is often default or handled differently but--output-format=json is key
        result = subprocess.run(command, capture_output=True, text=True)
        return PylinterResult(self.file_path, result.stdout, result.stderr)


# Stores pylint result
class PylinterResult:

    def __init__(self, file_path, stdout, stderr):
        self.file_path = file_path
        self.stdout = stdout
        self.stderr = stderr

        self._init_results()

    # Initialize results
    def _init_results(self):
        self.messages = []
        if self.stdout.strip() != "":
            try:
                self.messages = json.loads(self.stdout)
            except json.JSONDecodeError:
                self.messages = []
