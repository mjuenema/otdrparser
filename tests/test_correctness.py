#!/usr/bin/env python3

import io
import pathlib
import sys
import unittest

sys.path.append("..")
import otdrparser


TEST_DIRECTORY = pathlib.Path(__file__).parent


class FixedParameterTests(unittest.TestCase):
    def parse_fixture(self, name):
        with (TEST_DIRECTORY / name).open("rb") as fp:
            return otdrparser.parse2(fp)

    def test_fixed_parameters_use_documented_units_and_signs(self):
        data = self.parse_fixture("example.sor")
        fixed = data["FxdParams"]

        self.assertEqual(fixed["averaging_time"], 1.5)
        self.assertAlmostEqual(fixed["range"], 1.4664)
        self.assertEqual(fixed["reflection_threshold"], -65.535)
        self.assertEqual(fixed["end_of_transmission_threshold"], 5.0)

    def test_distances_are_expressed_in_meters(self):
        data = self.parse_fixture("issue9.sor")

        self.assertAlmostEqual(
            data["DataPts"]["data_points"][-1][0],
            2501.387576623927,
        )
        self.assertAlmostEqual(data["FxdParams"]["range"], 1.4664)
        self.assertAlmostEqual(
            data["KeyEvents"]["events"][-1]["distance_of_travel"],
            1249.193115344144,
        )

    def test_key_event_marker_positions_are_signed(self):
        data = self.parse_fixture("example.sor")

        self.assertEqual(
            data["KeyEvents"]["events"][0]["end_of_previous_event"],
            -48875,
        )


class InvalidInputTests(unittest.TestCase):
    def test_latin_1_metadata_is_decoded(self):
        self.assertEqual(
            otdrparser.read_zero_terminated_string(io.BytesIO(b"caf\xe9\x00")),
            "café",
        )

    def test_empty_input_raises_instead_of_looping_forever(self):
        with self.assertRaisesRegex(
            otdrparser.OTDRParserError,
            "Unexpected end of file while reading a string",
        ):
            otdrparser.parse2(io.BytesIO(b""))

    def test_truncated_input_raises_descriptive_error(self):
        with (TEST_DIRECTORY / "example.sor").open("rb") as fp:
            truncated = fp.read(100)

        with self.assertRaises(otdrparser.OTDRParserError):
            otdrparser.parse2(io.BytesIO(truncated))

    def test_non_map_header_is_rejected(self):
        data = b"NotMap\x00" + b"\x00" * 20

        with self.assertRaisesRegex(
            otdrparser.OTDRParserError,
            "Unsupported file header",
        ):
            otdrparser.parse2(io.BytesIO(data))

    def test_unsupported_major_version_is_rejected(self):
        data = b"Map\x00" + (100).to_bytes(2, "little") + b"\x00" * 6

        with self.assertRaisesRegex(
            otdrparser.OTDRParserError,
            "Unsupported SOR version 1.0",
        ):
            otdrparser.parse2(io.BytesIO(data))

    def test_multiple_traces_are_rejected_instead_of_misparsed(self):
        data = b"DataPts\x00" + b"\x00" * 4 + (2).to_bytes(2, "little")

        with self.assertRaisesRegex(
            otdrparser.OTDRParserError,
            "Multiple traces are not supported",
        ):
            otdrparser.parse_datapts_block(
                io.BytesIO(data), len(data), sample_spacing=1, index_of_refraction=1
            )


if __name__ == "__main__":
    unittest.main()
