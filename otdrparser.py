#!/usr/bin/env python

"""Parse OTDR traces in *.sor format.

   "I stand on the shoulder of giants": This OTDR parser is heavily based on 
   'pyOTDR' [1] and its authors efforts in reverse-engineering the Telcordia SR-4731
   standard for OTDR data [2][3]. Additional information has been extracted from
   the 'otdrs' project [4].

   My motiviation for writing yet another OTDR parser was that I wanted something
   that is intended to be used as a Python library instead of a full application.

   Limitations:

   - Only version 2 of the Telcordia SR-4731 is supported.
   - It is assumed that the SOR file contains only a single trace.
   - The checksum is just read as 2 bytes but neither calculated nor verified.


   References:

   [1] https://github.com/sid5432/pyOTDR
   [2] https://morethanfootnotes.blogspot.com/2015/07/the-otdr-optical-time-domain.html
   [3] https://telecom-info.njdepot.ericsson.net/site-cgi/ido/docs.cgi?ID=SEARCH&DOCUMENT=SR-4731&
   [4] https://github.com/JamesHarrison/otdrs
   [5] https://github.com/sid5432/pyOTDR/issues/40

"""

import struct
import sys
import io

FIBER_TYPES = {
    651: "ITU-T G.651 (multi-mode fiber)",
    652: "ITU-T G.652 (standard single-mode fiber)",
    653: "ITU-T G.653 (dispersion-shifted fiber)",
    654: "ITU-T G.654 (1550nm loss-minimzed fiber)",
    655: "ITU-T G.655 (nonzero dispersion-shifted fiber)",
}

BUILD_CONDITIONS = {
    "BC": "as-built",
    "CC": "as-current",
    "RC": "as-repaired",
    "OT": "other",
}

TRACE_TYPES = {
    "ST": "standard trace",
    "RT": "reverse trace",
    "DT": "difference trace",
    "RF": "reference",
}


EVENT_MAP = {
    "0": "non-reflective",
    "1": "reflective",
    "2": "saturated-reflective",
}


EVENT_NOTE_MAP = {
    "A": "added-by-user",
    "M": "moved-by-user",
    "E": "end-of-fiber",
    "F": "found-by-software",
    "O": "out-of-range",
    "D": "modified-end-of-fiber",
}


LOSS_MEASUREMENT_MAP = {
    "LS": "least-square",
    "2P": "two-point",
}


C_KM = 0.299792458
"""Speed of light in km/usec."""

C_M = C_KM * 1000
"""Speed of light in m/usec."""


def read_zero_terminated_string(fp):
    """Read until \0 and return as unicode string.

    Args:
        fp (file): File object of the opened SOR file.

    Returns:
        unicode: Read unicode string, stripped off leading and trailing white space.
    """

    s = b""
    while True:
        c = fp.read(1)

        if c == b"\x00":
            return s.decode().strip()
        s += c


def read_fixed_length_string(fp, n):
    """Read fixed number of bytes and return as unicode string.

    Args:
        fp (file): File object of the opened SOR file.
        n (int): Number of bytes to read.

    Returns:
        unicode: Read unicode string, stripped off leading and trailing white space.
    """

    return fp.read(n).decode().strip()


def read_unsigned2(fp):
    """Read 2 bytes and return a little-endian unsigned integer.

    Args:
        fp (file): File object of the opened SOR file.

    Returns:
        int: The bytes read interpreted as an unsigned integer.
    """

    return struct.unpack("<H", fp.read(2))[0]


def read_unsigned4(fp):
    """Read 4 bytes and return a little-endian unsigned integer.

    Args:
        fp (file): File object of the opened SOR file.

    Returns:
        int: The bytes read interpreted as an unsigned integer.
    """

    return struct.unpack("<I", fp.read(4))[0]


def read_signed2(fp):
    """Read 2 bytes and return a little-endian signed integer.

    Args:
        fp (file): File object of the opened SOR file.

    Returns:
        int: The bytes read interpreted as a signed integer.
    """

    return struct.unpack("<h", fp.read(2))[0]


def read_signed4(fp):
    """Read 4 bytes and return a little-endian unsigned integer.

    Args:
        fp (file): File object of the opened SOR file.

    Returns:
        int: The bytes read interpreted as a signed integer.
    """

    return struct.unpack("<i", fp.read(4))[0]


def interpret_event_type(event_type):
    """Interpret the event type string.

       Adapted from [2] the event type is represented as a string
       of the following format 'nx0000yy', where

       n=0 - Non-reflective event
       n=1 - Reflective event
       n=2 - Saturated reflective event

       x=A - Added by user.
       x=M - Moved by user.
       x=E - End of fiber.
       x=F - Found by software.
       x=O - Out of range.
       x=D - Modified end of fiber.

       0000 - Landmark number or '9999' if not used.

       yy=LS - Least-Square loss measurement technique.
       yy=2P - Two-point loss measurement technique.

    Args:
        event_type (unicode): Event type field of an event.

    Returns:
        dict: Dictionary with interpretation of the event type.
    """

    return {
        "event": EVENT_MAP.get(event_type[0]),
        "note": EVENT_NOTE_MAP.get(event_type[1]),  # I don't like this key
        "landmark_number": int(event_type[2:6]),
        "loss_measurement_technique": LOSS_MEASUREMENT_MAP.get(event_type[-2:]),
    }


def parse_map_block(fp):
    """Parse the Map block.

    Below is an example of a dictionary this function may return.

    ```
    {'name': 'Map',
     'numblocks': 13,
     'numbytes': 231,
     'version': '2.0'}]
     'maps': [{'name': 'GenParams', 'numbytes': 92, 'version': '2.0'},
              {'name': 'SupParams', 'numbytes': 56, 'version': '2.0'},
              {'name': 'FxdParams', 'numbytes': 92, 'version': '2.0'},
              {'name': 'DataPts', 'numbytes': 127064, 'version': '2.0'},
              {'name': 'KeyEvents', 'numbytes': 342, 'version': '2.0'},
              {'name': 'WaveMTSParams', 'numbytes': 658, 'version': '2.0'},
              {'name': 'WavetekTwoMTS', 'numbytes': 378, 'version': '2.0'},
              {'name': 'WavetekThreeMTS', 'numbytes': 20, 'version': '2.0'},
              {'name': 'ActernaConfig', 'numbytes': 6888, 'version': '2.0'},
              {'name': 'ActernaMiniCurve', 'numbytes': 849, 'version': '2.0'},
              {'name': 'JDSUEvenementsMTS', 'numbytes': 1956, 'version': '2.0'},
              {'name': 'Cksum', 'numbytes': 8, 'version': '2.0'},
              {'name': 'GenParams', 'numbytes': 543372857, 'version': '210.62'}]
     ```
    """

    data = {
        "name": read_zero_terminated_string(fp),
        "version": str(read_unsigned2(fp) / 100),
        "numbytes": read_unsigned4(fp),
        "numblocks": read_unsigned2(fp),
        "maps": [],
    }

    for _ in range(1, data["numblocks"]):
        data["maps"].append(
            {
                "name": read_zero_terminated_string(fp),
                "version": str(read_unsigned2(fp) / 100),
                "numbytes": read_unsigned4(fp),
            }
        )

    return data


def parse_genparams_block(fp, block_numbytes):
    """Parse a General parameters block."""

    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "cable_id": read_zero_terminated_string(block_fp),
        "fiber_id": read_zero_terminated_string(block_fp),
        "fiber_type": read_unsigned2(block_fp),
        "wavelength": read_unsigned2(block_fp),
        "location_a": read_zero_terminated_string(block_fp),
        "location_b": read_zero_terminated_string(block_fp),
        "cable_code": read_zero_terminated_string(block_fp),
        "build_condition": read_fixed_length_string(block_fp, 2),
        "user_offset": read_unsigned4(block_fp),
        "user_offset_distance": read_unsigned4(block_fp),
        "operator": read_zero_terminated_string(block_fp),
        "comments": read_zero_terminated_string(block_fp),
    }

    block_fp.close()

    data["fiber_type_description"] = FIBER_TYPES.get(data["fiber_type"])
    data["build_condition_description"] = BUILD_CONDITIONS.get(data["build_condition"])

    return data


def parse_supparams_block(fp, block_numbytes):
    """Parse a Supplier parameters block."""

    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "supplier_name": read_zero_terminated_string(block_fp),
        "otdr_name": read_zero_terminated_string(block_fp),
        "otdr_serial_number": read_zero_terminated_string(block_fp),
        "module_name": read_zero_terminated_string(block_fp),
        "module_serial_number": read_zero_terminated_string(block_fp),
        "software_version": read_zero_terminated_string(block_fp),
        "other": read_zero_terminated_string(block_fp),
    }

    block_fp.close()

    return data


def parse_fxdparams_block(fp, block_numbytes):
    """Parse a Fixed Parameters block.

    A limitation of this function is that only a single pulse width
    entry (i.e. a single trace) will be parsed. Apparently nobody
    has ever seen a *.sor file with multiple traces so I decided
    to assume that *.sor files never contain motre than one trace.

    """

    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "date_time": read_unsigned4(block_fp),
        "units": read_fixed_length_string(block_fp, 2),
        "wavelength": read_unsigned2(block_fp) / 10,
        "acquisition_offset": read_signed4(block_fp),
        "acquisition_offset_distance": read_signed4(block_fp),
        "number_of_pulse_width_entries": read_unsigned2(block_fp),
        "pulse_width": read_unsigned2(block_fp),
        "sample_spacing": read_unsigned4(block_fp),
        "number_of_data_points": read_unsigned4(block_fp),
        "index_of_refraction": read_unsigned4(block_fp) / 100000,
        "backscattering_coefficient": read_unsigned2(block_fp) * -0.1,
        "number_of_averages": read_unsigned4(block_fp),
        "averaging_time": read_unsigned2(block_fp),
        "range": read_unsigned4(block_fp) * 2 * 10**5,
        "acquisition_range_distance": read_signed4(block_fp),
        "front_panel_offset": read_signed4(block_fp),
        "noise_floor_level": read_unsigned2(block_fp),
        "noise_floor_scaling_factor": read_signed2(block_fp),
        "power_offset_first_point": read_unsigned2(block_fp),
        "loss_threshold": read_unsigned2(block_fp) * 0.001,
        "reflection_threshold": read_unsigned2(block_fp) * 0.001,
        "end_of_transmission_threshold": read_unsigned2(block_fp) * -0.001,
        "trace_type": read_fixed_length_string(block_fp, 2),
        "x1": read_signed4(block_fp),
        "y1": read_signed4(block_fp),
        "x2": read_signed4(block_fp),
        "y2": read_signed4(block_fp),
    }

    block_fp.close()

    data["trace_type_description"] = TRACE_TYPES.get(data["trace_type"])

    return data


def parse_datapts_block(fp, block_numbytes, sample_spacing, index_of_refraction):
    """Parse Data Points block."""

    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "number_of_data_points": read_unsigned4(block_fp),
        "number_of_traces": read_unsigned2(block_fp),
        "number_of_data_points2": read_unsigned4(block_fp),
        "scaling_factor": read_unsigned2(block_fp),
        "data_points": [],
    }

    for n in range(0, data["number_of_data_points"]):
        data["data_points"].append(
            (
                n * sample_spacing / 100000000 * C_M / index_of_refraction,
                read_unsigned2(block_fp) * -data["scaling_factor"] / 1000000,
            )
        )

    block_fp.close()

    return data


def parse_keyevents_block(fp, block_numbytes, index_of_refraction):
    """Parse Key Events block."""

    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "number_of_events": read_unsigned2(block_fp),
        "events": [],
    }

    for _ in range(0, data["number_of_events"]):
        event = {
            "event_number": read_unsigned2(block_fp),
            "time_of_travel": read_unsigned4(block_fp) * 0.1,
            "slope": read_signed2(block_fp) * 0.001,
            "splice_loss": read_signed2(block_fp) * 0.001,
            "reflection_loss": read_signed4(block_fp) * 0.001,
            "event_type": read_fixed_length_string(block_fp, 8),
            "end_of_previous_event": read_unsigned4(block_fp),
            "beginning_of_current_event": read_unsigned4(block_fp),
            "end_of_current_event": read_unsigned4(block_fp),
            "beginning_of_next_event": read_unsigned4(block_fp),
            "peak_point": read_unsigned4(block_fp),
            "comment": read_zero_terminated_string(block_fp),
        }

        event["distance_of_travel"] = (
            event["time_of_travel"] / 1000 * C_M / index_of_refraction
        )

        event["event_type_details"] = interpret_event_type(event["event_type"])

        data["events"].append(event)

    data.update(
        {
            "total_loss": read_signed4(block_fp) * 0.001,
            "fiber_start_position": read_signed4(block_fp),
            "fiber_length": read_unsigned4(block_fp),
            "optical_return_loss": read_unsigned2(block_fp) * 0.001,
            "fiber_start_position2": read_signed4(block_fp),
            "fiber_length2": read_unsigned4(block_fp),
        }
    )

    block_fp.close()

    return data


def parse_chksum_block(fp, block_numbytes):
    """Parse Chksum block."""


    block_fp = io.BytesIO(fp.read(block_numbytes))

    data = {
        "name": read_zero_terminated_string(block_fp),
        "chksum": f"{read_unsigned2(block_fp):04x}",
    }

    block_fp.close()

    return data


def parse_unknown_block(fp, block_numbytes):
    """Read an unknown block.

       Only the `name` is parsed and the rest of the block is returned
       as is.

    Args:
        fp (file): File object of the opened SOR file.
        n (int): The size of the block, including its name.
    """

    block_fp = io.BytesIO(fp.read(block_numbytes))

    name = read_zero_terminated_string(block_fp)

    data = {"name": name, "content": block_fp.read(block_numbytes - len(name) - 1)}

    block_fp.close()

    return data




def parse(fp):
    """The ``parse()`` function is the public interface of this library."""

    # The Map block is always the first block in the file.
    #
    blocks = [parse_map_block(fp)]

    # We need to remember some values for processing. They will
    # be updated in the big if/elif/else block below but I list
    # them already here for clarity.
    #
    # pulse_width = None
    sample_spacing = None
    index_of_refraction = None

    # Parse the other blocks.
    #
    for entry in blocks[0]["maps"]:
        block_name = entry["name"]
        block_version = entry['version']
        block_numbytes = entry['numbytes']

        if block_name == "GenParams":
            blocks += [parse_genparams_block(fp, block_numbytes)]
        elif block_name == "SupParams":
            blocks += [parse_supparams_block(fp, block_numbytes)]
        elif block_name == "FxdParams":
            blocks += [parse_fxdparams_block(fp, block_numbytes)]
            # pulse_width = blocks[-1]["pulse_width"]
            sample_spacing = blocks[-1]["sample_spacing"]
            index_of_refraction = blocks[-1]["index_of_refraction"]
        elif block_name == "DataPts":
            blocks += [parse_datapts_block(fp, block_numbytes, sample_spacing, index_of_refraction)]
        elif block_name == "KeyEvents":
            blocks += [parse_keyevents_block(fp, block_numbytes, index_of_refraction)]
        elif block_name == "Cksum":
            blocks += [parse_chksum_block(fp, block_numbytes)]
        else:
            blocks += [parse_unknown_block(fp, block_numbytes)]

    return blocks



if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fp:
        blocks = parse(fp)

    for block in blocks:
        print(block['name'])


