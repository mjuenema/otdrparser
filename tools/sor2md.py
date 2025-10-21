#!/usr/bin/env python3

"""Read one or multiple traces and create a detailed report 
   in Markdown syntax. The generated markdown file can then
   be converted into other formats using the 'pandoc' tool.

"""

import argparse
import tempfile
import os
import datetime
import otdrparser
import jinja2


## # OTDR Report
#
### Overview
#
#|File |Wavelength [nm]|Distance [m]|Loss [dB]|Loss/Km [dB]|Events|
#| :------------ |------------ |------------ |--- |--- |
#|25250-1-1_1310.sor |1310|2300|7.5|1.2|5|
#|25250-1-1_1550.sor|1550|2300|7.3|1.0|5|
#|25250-1-1_1625.sor|1625|2300|6.9|0.9|4|
#
## 25250-1-1_1310
#
# **File name:** 25250-1-1_1310.sor
# **Date/Time:**  10/10/2025 / 14:33:27
# **Cable ID:** FR96c from A to B
# **Fiber ID:** FR96C
# **Fiber Type:** ITU-T G.652 (standard single-mode fiber)
# **Operator**: MJ
# **Comments:** Example for Github
# **OTDR:** Acterna MTS 6000 (8156 SRL)
# **Serial #:** 1111 / 652
# **Software version:** 7.22
# **Location A:**
# # **Location B:**
# **Wavelength:** 1310
# **Index of refraction:** 1.47
# 
# GRAPH
# 
# **Length:** 2300 m
# **Loss:** 2.34 dB
# **Loss/Km:** 1.01 dB
# 
# |Event|No|Position [km]|Loss [dB]|Reflectance [dB]|Cumulative Loss [dB]
# |:---|---|---:|---:|---:|---:|
# |Non-Reflective|1|0.526|0.339|**-54.4**|0.339|


# Jinja 2 templates
#

HEADER_TEMPLATE = """
# OTDR Report
**Created on {{ created }}
"""

OVERVIEW_TEMPLATE = """
## Overview

|File |Wavelength [nm]|Distance [m]|Loss [dB]|Loss/Km [dB]|Events|
| :------------ |------------ |------------ |--- |--- |
{%- for 
|25250-1-1_1310.sor |1310|2300|7.5|1.2|5|
{%- endfor %}
"""



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infiles", help="Path to the SOR file(s)", nargs='*')
    args = parser.parse_args()


    with tempfile.TemporaryDirectory(prefix='sor2md', delete=False) as tmpdir:
        os.chdir(tmpdir.name)

        # Write the header
        #
        with open('00-header', 'wt') as fp:
            fp.write(f"# OTDR Report"
                    "**Created: {datetime.datetime.now()}")


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
