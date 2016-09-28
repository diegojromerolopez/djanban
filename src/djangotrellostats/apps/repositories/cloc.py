import os
import subprocess

from bs4 import BeautifulSoup


# Cloc wrapper
class Cloc(object):

    def __init__(self, file_path):
        self.file_path = file_path

    def run(self):

        cloc_command = "cloc {0} --xml".format(self.file_path)
        cloc_command_result = subprocess.Popen(cloc_command, shell=True, stdout=subprocess.PIPE)

        self.stdout = cloc_command_result.stdout.read()

        return ClocResult(self.file_path, self.stdout)

    # Asserts that cloc is installed in this system
    @staticmethod
    def assert_existence():
        try:
            subprocess.call(["cloc", "--version"])
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                raise AssertionError(
                    u"Cloc was not found in your system. Install cloc (https://github.com/AlDanial/cloc).")


# Result of a cloc execution
class ClocResult(object):
    def __init__(self, file_path, stdout):
        self.file_path = file_path
        self.stdout = stdout
        self._init_results()

    # Initialize results
    def _init_results(self):
        bs = BeautifulSoup(self.stdout, "html.parser")
        language_cloc = bs.find("language")
        self.data = {
            "path": self.file_path,
            "language": language_cloc["name"],
            "number_of_files": language_cloc["files_count"],
            "blank_lines": language_cloc["blank"],
            "commented_lines": language_cloc["comment"],
            "lines_of_code": language_cloc["code"],
        }

    def __getitem__(self, key):
        return self.data[key]

