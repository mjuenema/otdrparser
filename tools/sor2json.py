#!/usr/bin/env python

"""Parse a *.sor file and print the content in JSON format.

      $ sor2json.py mytrace.sor

"""

import argparse
import json
import otdrparser


class BytesEncoder(json.JSONEncoder):
    """Custom JSON Encoder that can handle bytes."""

    def default(self, o):
        if isinstance(o, bytes):
            return o.hex()
        return json.JSONEncoder.default(self, o)


def main():
    parser = argparse.ArgumentParser(prog="sor2json")
    parser.add_argument("filename", help="Path to the SOR file")
    args = parser.parse_args()

    with open(args.filename, "rb") as fp:
        print(json.dumps(otdrparser.parse(fp), cls=BytesEncoder, indent=2))


if __name__ == "__main__":
    main()
