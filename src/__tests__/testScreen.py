# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from __future__ import print_function

import sys
sys.path.insert(0, '../')
import unittest
import os

import screenTestRunner

EXPECTED_DIR = './expected/'
screenTestCases = [{
    'name': 'simpleLoadAndQuit',
}, {
    'name': 'tallLoadAndQuit',
    'screenConfig': {
        'maxX': 140,
        'maxY': 60,
    },
}, {
    'name': 'selectFirst',
    'inputs': ['f'],
}, {
    'name': 'selectDownSelect',
    'inputs': ['f', 'j', 'f'],
}, {
    'name': 'selectDownSelectInverse',
    'inputs': ['f', 'j', 'f', 'A'],
}, {
    'name': 'selectTwoCommandMode',
    'input': 'absoluteGitDiff.txt',
    'inputs': ['f', 'j', 'f', 'c'],
    'pastScreen': 1
}, {
    'name': 'selectCommandWithPassedCommand',
    'input': 'absoluteGitDiff.txt',
    # the last key "a" is so we quit from command mode
    # after seeing the warning
    'inputs': ['f', 'c', 'a'],
    'pastScreen': 1,
    'args': ["-c 'git add'"]
}, {
    'name': 'simpleWithAttributes',
    'withAttributes': True
}, {
    'name': 'simpleSelectWithAttributes',
    'withAttributes': True,
    'inputs': ['f', 'j'],
}, {
    'name': 'simpleSelectWithColor',
    'input': 'gitDiffColor.txt',
    'withAttributes': True,
    'inputs': ['f', 'j'],
    'screenConfig': {
        'maxX': 200,
        'maxY': 40,
    },
}, {
    'name': 'gitDiffWithScroll',
    'input': 'gitDiffNoStat.txt',
    'inputs': ['f', 'j'],
}, {
    'name': 'gitDiffWithScrollUp',
    'input': 'gitLongDiff.txt',
    'inputs': ['k', 'k'],
}, {
    'name': 'gitDiffWithPageDown',
    'input': 'gitLongDiff.txt',
    'inputs': [' ', ' '],
}, {
    'name': 'gitDiffWithPageDownColor',
    'input': 'gitLongDiffColor.txt',
    'inputs': [' ', ' '],
    'withAttributes': True,
}, {
    'name': 'gitDiffWithValidation',
    'input': 'gitDiffSomeExist.txt',
    'validateFileExists': True,
    'withAttributes': True,
}]


class TestScreenLogic(unittest.TestCase):

    def testScreenInputs(self):
        seenCases = {}
        for testCase in screenTestCases:
            # make sure its not copy pasta-ed
            testName = testCase['name']
            self.assertFalse(
                seenCases.get(testName, False), 'Already seen %s ' % testName)
            seenCases[testName] = True

            charInputs = ['q']  # we always quit at the end
            charInputs = testCase.get('inputs', []) + charInputs

            screenData = screenTestRunner.getRowsFromScreenRun(
                inputFile=testCase.get('input', 'gitDiff.txt'),
                charInputs=charInputs,
                screenConfig=testCase.get('screenConfig', {}),
                printScreen=False,
                pastScreen=testCase.get('pastScreen', None),
                args=testCase.get('args', []),
                validateFileExists=testCase.get('validateFileExists', False)
            )

            self.compareToExpected(testCase, testName, screenData)
            print('Tested %s ' % testName)

    def compareToExpected(self, testCase, testName, screenData):
        TestScreenLogic.maybeMakeExpectedDir()
        (actualLines, actualAttributes) = screenData

        if testCase.get('withAttributes', False):
            self.compareLinesAndAttributesToExpected(testName, screenData)
        else:
            self.compareLinesToExpected(testName, actualLines)

    def compareLinesAndAttributesToExpected(self, testName, screenData):
        (actualLines, actualAttributes) = screenData
        actualMergedLines = []
        for actualLine, attributeLine in zip(actualLines, actualAttributes):
            actualMergedLines.append(actualLine)
            actualMergedLines.append(attributeLine)

        self.outputIfNotFile(testName, '\n'.join(actualMergedLines))
        file = open(TestScreenLogic.getExpectedFile(testName))
        expectedMergedLines = file.read().split('\n')
        file.close()

        self.assertEqualLines(testName, actualMergedLines, expectedMergedLines)

    def compareLinesToExpected(self, testName, actualLines):
        self.outputIfNotFile(testName, '\n'.join(actualLines))

        file = open(TestScreenLogic.getExpectedFile(testName))
        expectedLines = file.read().split('\n')
        file.close()

        self.assertEqualLines(testName, actualLines, expectedLines)

    def outputIfNotFile(self, testName, output):
        expectedFile = TestScreenLogic.getExpectedFile(testName)
        if os.path.isfile(expectedFile):
            return

        print('Could not find file %s so outputting...' % expectedFile)
        file = open(expectedFile, 'w')
        file.write(output)
        file.close()
        self.fail(
            'File outputted, please inspect %s for correctness' % expectedFile)

    def assertEqualNumLines(self, testName, actualLines, expectedLines):
        self.assertEqual(
            len(actualLines),
            len(expectedLines),
            '%s test: Actual lines was %d but expected lines was %d' % (
                testName, len(actualLines), len(expectedLines)),
        )

    def assertEqualLines(self, testName, actualLines, expectedLines):
        self.assertEqualNumLines(testName, actualLines, expectedLines)
        expectedFile = TestScreenLogic.getExpectedFile(testName)
        for index, expectedLine in enumerate(expectedLines):
            actualLine = actualLines[index]
            self.assertEqual(
                expectedLine,
                actualLine,
                'Lines did not match for test %s:\n\nExpected:%s\nActual:%s' % (
                    expectedFile, expectedLine, actualLine),
            )

    @staticmethod
    def getExpectedFile(testName):
        return os.path.join(EXPECTED_DIR, testName + '.txt')

    @staticmethod
    def maybeMakeExpectedDir():
        if not os.path.isdir(EXPECTED_DIR):
            os.makedirs(EXPECTED_DIR)

if __name__ == '__main__':
    unittest.main()
