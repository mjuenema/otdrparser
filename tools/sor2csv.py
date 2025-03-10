#!/usr/bin/env python

"""Parse a *.sor file and print data points to CSV.

      $ sor2csv.py mytrace.sor

"""

import argparse
import csv
import sys
import otdrparser


def main():
    parser = argparse.ArgumentParser(prog="sor2csv")
    parser.add_argument("filename", help="Path to the SOR file")
    args = parser.parse_args()

    with open(args.filename, "rb") as fp:
        datablock = otdrparser.parse(fp)[5]

    writer = csv.writer(sys.stdout) 
    writer.writerow(['Distance [m]', 'Signal [dB]'])

    for datapoint in datablock['data_points']:
        writer.writerow(datapoint)




if __name__ == "__main__":
    main()
