#!/usr/bin/env python3

import glob
import parameterized
import sys
sys.path.append('..')
import otdrparser

SOR_FILES = glob.glob('*.sor')

@parameterized.parameterized(SOR_FILES)
def test_parsing(sor_file):
    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

@parameterized.parameterized(SOR_FILES)
def test_datapoints(sor_file):

    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        for block in blocks:
            if block['name'] == 'DataPts':
                assert 'data_points' in block
