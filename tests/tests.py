#!/usr/bin/env python3

import glob
import parameterized
import sys
sys.path.append('..')
import otdrparser

ALL_SOR_FILES = glob.glob('*.sor')
ISSUE9_SOR_FILE = ['issue9.sor']
ISSUE11_SOR_FILE = ['issue11.sor', 'issue9.sor']

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


@parameterized.parameterized(ALL_SOR_FILES)
def test_issue11(sor_file):
    """Spellcheck keys in the parsed data structure.

       This is really a one-off check to ensure that there are no
       other misspelled words in the data structure. It passes
       for one particular SOR file.

    """

    def recurse(data):

        if isinstance(data, str):
            if '_' in data:
                for part in data.split('_'):
                    recurse(part)
            elif len(data) > 2:
                assert data.lower() in words
        elif isinstance(data, list):
            for item in data:
                recurse(item)
        elif isinstance(data, dict):
            for key,value in data.items():
                recurse(key)
                if not isinstance(value, (str, int)):
                    recurse(value)

    with open('/usr/share/dict/words', 'rt') as fp:
        words = [line.strip().lower() for line in fp]
    words += ['numbytes', 'numblocks', 'genparams', 'supparams','fxdparams','keyevents',
              'datapts','spclproprietary', 'cksum', 'otdr', 'backscattering',
              'position2', 'length2', 'points2', 'chksum']


    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        recurse(blocks)


