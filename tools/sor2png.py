#!/usr/bin/env python3

"""Plot one or multiple OTDR traces with Matplotlib



"""

import argparse
import otdrparser
import matplotlib.pyplot as plt



def main():
    parser = argparse.ArgumentParser(prog="sor2json")
    # TODO: Add title option
    parser.add_argument("outfile", help="Path to the PNG file")
    parser.add_argument("infiles", help="Path to the SOR file(s)", nargs='*')
    args = parser.parse_args()

    plt.xlabel("Distance [m]")
    plt.ylabel("Signal [dB]")


    for infile in args.infiles:
        with open(infile, "rb") as fp:

            datablock = otdrparser.parse(fp)[5]

            x_values = []
            y_values = []


            for datapoint in datablock['data_points']:
                x_values.append(datapoint[0])   # Distance
                y_values.append(datapoint[1])   # Signal

            plt.plot(x_values, y_values)

    plt.savefig(args.outfile)



if __name__ == "__main__":
    main()
