#!/usr/bin/env python

"""Parse a *.sor file and print the content in YAML format.

      $ sor2yaml.py mytrace.sor

"""

import argparse
import yaml
import otdrparser


def main():
    parser = argparse.ArgumentParser(prog="sor2json")
    parser.add_argument("filename", help="Path to the SOR file")
    args = parser.parse_args()

    with open(args.filename, "rb") as fp:
        print(yaml.dump(otdrparser.parse(fp)))


if __name__ == "__main__":
    main()
