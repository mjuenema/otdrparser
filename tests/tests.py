#!/usr/bin/env python3

import glob
import parameterized
import sys
sys.path.append('..')
import otdrparser

ALL_SOR_FILES = glob.glob('*.sor')
ISSUE9_SOR_FILE = ['issue9.sor']

@parameterized.parameterized(ALL_SOR_FILES)
def test_parsing(sor_file):
    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)


@parameterized.parameterized(ALL_SOR_FILES)
def test_datapoints(sor_file):

    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        for block in blocks:
            if block['name'] == 'DataPts':
                assert 'data_points' in block


@parameterized.parameterized(ISSUE9_SOR_FILE)
def test_issue9(sor_file):
    """Consider index of refraction when calculating speed of light
       in fibre optic cables.

       In versions prior of 0.1.4 the distances were calculated
       incorrectly as the index of refraction was not considered.

       This test verifies that the distances are calculated correctly
       using traces with known distances.

    """

    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        for block in blocks:
            if block['name'] == 'DataPts':
                assert block['data_points'][-1] == (2501.387576623927, -60.749)


