# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bs4 import BeautifulSoup
import os
import re
import subprocess


# PHP-md for directories
from djangotrellostats.apps.repositories.cloc import Cloc


class PhpDirectoryAnalyzer(object):

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        Cloc.assert_existence()
        results = []
        for root, subdirs, files in os.walk(self.dir_path):
            for filename in files:
                if PhpDirectoryAnalyzer.is_php_file(filename):
                    file_path = u"{0}/{1}".format(root, filename)
                    # Check if file is not empty
                    if not PhpDirectoryAnalyzer.file_is_empty(file_path):
                        # Count of lines of code
                        cloc = Cloc(file_path)
                        cloc_result = cloc.run()

                        # Assessment of code quality
                        phpmd_analyzer = PhpMdAnalyzer(file_path)
                        phpmd_result = phpmd_analyzer.run()

                        # Add cloc results
                        phpmd_result.cloc_result = cloc_result

                        results.append(phpmd_result)

        return results

    @staticmethod
    def is_php_file(filename):
        return re.match(r"^[^\.]+\.php$", filename)

    @staticmethod
    def file_is_empty(file_path):
        return os.path.getsize(file_path) == 0


# Runs PHP-md on a file
class PhpMdAnalyzer(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.stdout = None
        self.stderr = None

    def run(self):
        PhpMdAnalyzer.assert_existence()

        php_md_command = "phpmd {0} xml cleancode,codesize,controversial,design,naming,unusedcode".format(self.file_path)
        phpmd_call_results = subprocess.Popen(php_md_command, shell=True, stdout=subprocess.PIPE)

        self.stdout = phpmd_call_results.stdout.read()
        self.stderr = ""

        if phpmd_call_results.stderr:
            self.stderr = phpmd_call_results.stderr.read()

        return PhpMdAnalysisResult(self.file_path, self.stdout, self.stderr)

    # Asserts that phpmd is installed in this system
    @staticmethod
    def assert_existence():
        try:
            subprocess.call(["phpmd", "--version"])
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                raise AssertionError(
                    u"PHPMD was not found in your system. Please install it to assess PHP code (https://phpmd.org/)."
                )


# Stores php-md result
class PhpMdAnalysisResult(object):

    def __init__(self, file_path, stdout, stderr):
        self.file_path = file_path
        self.stdout = stdout
        self.stderr = stderr

        self._init_results()

    # Initialize results
    def _init_results(self):
        bs = BeautifulSoup(self.stdout, "html.parser")
        self.filename = bs.find("file")
        self.messages = []
        for violation in bs.find_all("violation"):
            message = {
                "path": self.filename["name"],
                "begin_line": violation["beginline"],
                "end_line": violation["endline"],
                "rule": violation["rule"],
                "ruleset": violation["ruleset"],
                "message": violation.string
            }
            self.messages.append(message)

        return self.messages

