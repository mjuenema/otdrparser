# otdrparser

**otdrparser** is a Python library for parsing OTDR traces in Telcordia SR-4731 Version 2 format (```*.sor``` files).

It is effectively a simplified re-implementation of the [pyOTDR](https://github.com/sid5432/pyOTDR) project. Its author, Hsin-Yu Sidney Li, together with several others deserve a lot of credit for [reverse-engineering](https://morethanfootnotes.blogspot.com/2015/07/the-otdr-optical-time-domain.html) 
the Telcordia SR-4731 standard as it is not freely available. 

The **otdrparser** library differs from the **pyOTDR** project in multiple ways.
* It's just a library with a single ``.parse()`` function.
* It only supports Version 2 of the Telcordia SR-4731 standard.
* It is assumed that the OTDR file contains only a single trace.
* The checksum block is read but not verified.
* No attempt is made to accomodate vendor specific "quirks" in standard blocks.
* I am certain **otdrparser** contains bugs. Please open a Github Issue if you find any.

The **otdrparser** library contains only a single public ``.parse()`` function which returns the "blocks" contained in the file as a list of dictionaries. 
```python
import otdrparser
with open('my_trace_file.sor', 'rb') as fp:
    blocks = otdrparser.parse(fp)
```
The output below shows the (abridged) content of ```blocks``` converted into JSON format for easier reading.
* Each "block" has a ```name``` attribute which describes its type.
* Data points are included as a list of (distance, dBm) pairs.
* Vendor proprietary blocks are included as raw bytes. There are none in the example below.
* Some data is interpreted. For example ```fibre_type=652``` is also interpreted as ```"ITU-T G.652 (standard single-mode fiber)"```
```json
[
  { "name": "Map",
    "version": "2.0",
    "numbytes": 231,
    "numblocks": 13,
    "maps": [
      { "name": "GenParams",
        "version": "2.0",
        "numbytes": 92 },
      { "name": "SupParams",
        "version": "2.0",
        "numbytes": 56 },
      { "name": "FxdParams",
        "version": "2.0",
        "numbytes": 92 },
      { "name": "DataPts",
        "version": "2.0",
        "numbytes": 127064 },
      { "name": "KeyEvents",
        "version": "2.0",
        "numbytes": 342 },
     {  "name": "Cksum",
        "version": "2.0",
        "numbytes": 8 },
  { "name": "GenParams",
    "cable_id": "FR96c from A to B",
    "fiber_id": "FR96c",
    "fiber_type": 652,
    "wavelength": 1310,
    "location_a": "Location A",
    "location_b": "Location B",
    "cable_code": "",
    "build_condition": "CC",
    "user_offset": 0,
    "user_offset_distance": 0,
    "operator": "BC",
    "comments": "Example for Github",
    "fiber_type_description": "ITU-T G.652 (standard single-mode fiber)",
    "build_condition_description": "as-current" },
  { "name": "SupParams",
    "supplier_name": "Acterna",
    "otdr_name": "MTS 6000",
    "otdr_serial_number": "1111",
    "module_name": "8156 SRL",
    "module_serial_number": "652",
    "software_version": "7.22",
    "other": "" },
  { "name": "FxdParams",
    "date_time": 1644849308,
    "units": "km",
    "wavelength": 1310.0,
    "acqusition_offset": 0,
    "acqusition_offset_distance": 0,
    "number_of_pulse_width_entries": 1,
    "pulse_width": 30,
    "sample_spacing": 312500,
    "number_of_data_points": 63522,
    "index_of_refraction": 1.4732,
    "backscattering_coefficient": 790,
    "number_of_averages": 12873,
    "averaging_time": 420,
    "range": 2000000,
    "acquisition_range_distance": 406,
    "front_panel_offset": 0,
    "noise_floor_level": 55000,
    "noise_floor_scaling_factor": 1000,
    "power_offset_first_point": 35522,
    "loss_threshold": 65526,
    "reflection_threshold": 15000,
    "end_of_transmission_threshold": 0,
    "trace_type": "ST",
    "x1": 0,
    "y1": 0,
    "x2": 0,
    "y2": 0,
    "trace_type_description": "standard trace" },
  { "name": "DataPts",
    "number_of_data_points": 63522,
    "number_of_traces": 1,
    "number_of_data_points2": 63522,
    "scaling_factor": 1470,
    "data_points": [
      [ 0.0, -49.67865 ],
      [ 0.93685143125, -44.19996 ],
      ...
      [ 23623.6456904, -55.10883 ],
      [ 23624.58254183125, -55.26906 ]
    ]
  },
  { "name": "KeyEvents",
    "number_of_events": 7,
    "events": [
      { "event_number": 1,
        "time_of_travel": 4821.900000000001,
        "slope": 0.18,
        "splice_loss": 0.138,
        "reflection_loss": 0.0,
        "event_type": "0F9999LS",
        "end_of_previous_event": 0,
        "beginning_of_current_event": 0,
        "end_of_current_event": 0,
        "beginning_of_next_event": 0,
        "peak_point": 0,
        "comment": "",
        "distance_of_travel": 981.2444021383383,
        "event_type_details": {
          "event": "non-reflective",
          "note": "found-by-software",
          "landmark_number": 9999,
          "loss_measurement_technique": "least-square"
      },
        ...
      { "event_number": 7,
        "time_of_travel": 114321.90000000001,
        "slope": 0.0,
        "splice_loss": 0.0,
        "reflection_loss": -40.01,
        "event_type": "2F99992P",
        "end_of_previous_event": 0,
        "beginning_of_current_event": 0,
        "end_of_current_event": 0,
        "beginning_of_next_event": 0,
        "peak_point": 0,
        "comment": "",
        "distance_of_travel": 23264.216266786723,
        "event_type_details": {
          "event": "saturated-reflective",
          "note": "found-by-software",
          "landmark_number": 9999,
          "loss_measurement_technique": "two-point" }
      }
    ],
    "total_loss": 4.339,
    "fiber_start_position": 0,
    "fiber_length": 571563,
    "optical_return_loss": 0.0,
    "fiber_start_position2": 0,
    "fiber_length2": 0 },
  { "name": "Cksum",
    "chksum": "e474"
  }
]
```
