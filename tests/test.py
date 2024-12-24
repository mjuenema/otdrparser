#!/usr/bin/env python3

import sys
sys.path.append('..')
import otdrparser

with open(sys.argv[1], 'rb') as fp:
    otdrparser.parse(fp)
