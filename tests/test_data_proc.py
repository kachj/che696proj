#!/usr/bin/env python3
"""
Unit and regression test for data_proc.py
"""

# Import package, test suite, and other packages as needed
import sys
import unittest
from contextlib import contextmanager
from io import StringIO
import errno
import os
import numpy as np
import pandas as pd
import logging
from centrifugation_expt.data_proc import main, csv_data_analysis, excel_data_analysis


logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

CURRENT_DIR = os.path.dirname(__file__)
MAIN_DIR = os.path.join(CURRENT_DIR, '..')
TEST_DATA_DIR = os.path.join(CURRENT_DIR, 'data_proc')
PROJ_DIR = os.path.join(MAIN_DIR, 'centrifugation_expt')
DATA_DIR = os.path.join(PROJ_DIR, 'data')
SAMPLE_CSV_DATA_FILE_LOC = os.path.join(TEST_DATA_DIR, 'sample_data.csv')
SAMPLE_EXCEL_DATA_FILE_LOC = os.path.join(TEST_DATA_DIR, 'sample_data.xlsx')

# Assumes running tests from the main directory
DEF_CSV_OUT = os.path.join(MAIN_DIR, 'sample_data_analysis.csv')
DEF_EXCEL_OUT = os.path.join(MAIN_DIR, 'sample_data_analysis.xlsx')
DEF_CSV_PNG_OUT = os.path.join(MAIN_DIR, 'sample_data_analysis_csv.png')
DEF_EXCEL_PNG_OUT = os.path.join(MAIN_DIR, 'sample_data_analysis_excel.png')


def silent_remove(filename, disable=False):
    """
    Removes the target file name, catching and ignoring errors that indicate that the
    file does not exist.
    @param filename: The file to remove.
    @param disable: boolean to flag if want to disable removal
    """
    if not disable:
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


class TestMain_csv(unittest.TestCase):
    # These tests make sure that the program can run properly from main
    def testSampleData(self):
        # Checks that runs with defaults and that files are created
        test_input = ["-c", SAMPLE_CSV_DATA_FILE_LOC]
        try:
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            # checks that the expected message is sent to standard out
            with capture_stdout(main, test_input) as output:
                self.assertTrue("sample_data_analysis.csv" in output)

            self.assertTrue(os.path.isfile("sample_data_analysis.csv"))
            self.assertTrue(os.path.isfile("sample_data_analysis_csv.png"))
        finally:
            silent_remove(DEF_CSV_OUT, disable=DISABLE_REMOVE)
            silent_remove(DEF_CSV_PNG_OUT, disable=DISABLE_REMOVE)


class TestMain_excel(unittest.TestCase):
    # These tests make sure that the program can run properly from main
    def testSampleData(self):
        # Checks that runs with defaults and that files are created
        test_input = ["-e", SAMPLE_EXCEL_DATA_FILE_LOC]
        try:
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            # checks that the expected message is sent to standard out
            with capture_stdout(main, test_input) as output:
                self.assertTrue("sample_data_analysis.xlsx" in output)

            self.assertTrue(os.path.isfile("sample_data_analysis.xlsx"))
            self.assertTrue(os.path.isfile("sample_data_analysis_excel.png"))
        finally:
            silent_remove(DEF_EXCEL_OUT, disable=DISABLE_REMOVE)
            silent_remove(DEF_EXCEL_PNG_OUT, disable=DISABLE_REMOVE)


class TestMainFailWell(unittest.TestCase):
    def testMissingFile(self):
        test_input = ["-c", "ghost.txt"]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("ghost.txt" in output)


class TestDataAnalysis_csv(unittest.TestCase):
    def testSampleData_csv(self):

        csv_analysis_results = csv_data_analysis(SAMPLE_CSV_DATA_FILE_LOC)
        csv_expected_results = pd.read_csv(filepath_or_buffer=os.path.join(TEST_DATA_DIR,
                                                                           "sample_data_results.csv"), header=None)
        self.assertTrue(np.allclose(csv_analysis_results.values, csv_expected_results.values))


class TestDataAnalysis_excel(unittest.TestCase):
    def testSampleData_excel(self):

        excel_analysis_results_whole = excel_data_analysis(SAMPLE_EXCEL_DATA_FILE_LOC)
        number = np.random.randint(0, int(len(excel_analysis_results_whole)/3))
        excel_analysis_results = excel_analysis_results_whole.iloc[:, 3*number:3*number+3].dropna()
        excel_expected_results = pd.read_excel(os.path.join(TEST_DATA_DIR, "sample_data_results.xlsx"), sheet_name=number)

        self.assertTrue(np.allclose(excel_analysis_results.values, excel_expected_results.values))


# Utility functions

# From http://schinckel.net/2013/04/15/capture-and-test-sys.stdout-sys.stderr-in-unittest.testcase/
@contextmanager
def capture_stdout(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


@contextmanager
def capture_stderr(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    err, sys.stderr = sys.stderr, StringIO()
    command(*args, **kwargs)
    sys.stderr.seek(0)
    yield sys.stderr.read()
    sys.stderr = err