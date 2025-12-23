#!/usr/bin/env python3

import glob
import parameterized
import sys
sys.path.append('..')
import otdrparser

ALL_SOR_FILES = glob.glob('*.sor')

@parameterized.parameterized(ALL_SOR_FILES)
def test_parsing(sor_file):
    with open(sor_file, 'rb') as fp:
        otdrparser.parse(fp)


@parameterized.parameterized(ALL_SOR_FILES)
def test_datapoints(sor_file):

    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        for block in blocks:
            if block['name'] == 'DataPts':
                assert 'data_points' in block


ISSUE9_SOR_FILES = ['issue9.sor']

@parameterized.parameterized(ISSUE9_SOR_FILES)
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

    try:
        with open('/usr/share/dict/words', 'rt') as fp:
            words = [line.strip().lower() for line in fp]
        words += ['numbytes', 'numblocks', 'genparams', 'supparams','fxdparams','keyevents',
                  'datapts','spclproprietary', 'cksum', 'otdr', 'backscattering',
                  'position2', 'length2', 'points2', 'chksum']
    except FileNotFoundError:
        # No /usr/share/dict/words
        return


    with open(sor_file, 'rb') as fp:
        blocks = otdrparser.parse(fp)

        recurse(blocks)


ISSUE10_SOR_FILES = ['issue10a.sor']
@parameterized.parameterized(ISSUE10_SOR_FILES)
def test_issue10a(sor_file):

    with open(sor_file, 'rb') as fp:
        data = otdrparser.parse2(fp)
        assert data['KeyEvents']['fiber_start_position'] == -1002.3040072262725
        assert data['KeyEvents']['fiber_length'] == 619.8066597773387


ISSUE11_SOR_FILES = ALL_SOR_FILES
ISSUE11_SOR_FILES.remove('otdr7.sor')   # This trace does not contain KeyEvents

@parameterized.parameterized(ISSUE11_SOR_FILES)
def test_issue12(sor_file):
    """Return parsed data as dictionary.
    """

    with open(sor_file, 'rb') as fp:
        data = otdrparser.parse2(fp)
        assert 'Map' in data
        assert 'GenParams' in data
        assert 'SupParams' in data
        assert 'FxdParams' in data
        assert 'DataPts' in data
        assert 'KeyEvents' in data
        assert 'Cksum' in data

        assert 'maps' in data['Map']
        
@parameterized.parameterized(ALL_SOR_FILES)
def test_issue14(sor_file):
    with open(sor_file, 'rb') as fp:
        data = otdrparser.parse2(fp)
        assert "GenParams" in data
        assert data["GenParams"]["name"] == "GenParams"
