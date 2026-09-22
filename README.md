# otdrparser

**otdrparser** is a Python library for parsing OTDR traces in Telcordia SR-4731 Version 2 format (```*.sor``` files).

It is a simplified re-implementation of the [pyOTDR](https://github.com/sid5432/pyOTDR) project. Its author, Hsin-Yu Sidney Li, together with several others deserve a lot of credit for [reverse-engineering](https://morethanfootnotes.blogspot.com/2015/07/the-otdr-optical-time-domain.html) 
the Telcordia SR-4731 standard as it is not freely available. 

The **otdrparser** library differs from the **pyOTDR** project in multiple ways.
* It's a small module with a ``parse2()`` function (and a now legacy ``parse()`` function).
* It only supports Version 2 of the Telcordia SR-4731 standard.
* Only single-trace OTDR files are supported. Multi-trace input is rejected explicitly.
* The checksum block is read but not verified.
* No attempt is made to accomodate vendor specific blocks.
* I am certain **otdrparser** contains bugs. Please open a Github Issue if you find any.

Both parser functions accept any binary file-like object, including an open file or an ``io.BytesIO`` instance.

```python
import io
import otdrparser

with open('my_trace_file.sor', 'rb') as fp:
    blocks = otdrparser.parse2(fp)

blocks_from_memory = otdrparser.parse2(io.BytesIO(sor_bytes))
```

* Each "block" has a ```name``` attribute which describes its type.
* The ``parse2()`` function returns the parsed trace file as a dictionary, keyed by the name of the block.
* Data points are included as a list of (distance in metres, dB) pairs.
* Data-point and key-event distances are expressed in metres. The encoded
  ``FxdParams.range`` field follows the SOR convention and is expressed in
  kilometres.
* ``FxdParams.averaging_time`` is expressed in seconds.
* Vendor proprietary blocks are included as raw bytes.
* Some data is interpreted. For example ```fibre_type=652``` is also interpreted as ```"ITU-T G.652 (standard single-mode fiber)"```
* Truncated, malformed, and unsupported input raises ``OTDRParserError``.

Output of the ``.parse2()`` method converted into JSON: [example-parse2.json](https://github.com/mjuenema/otdrparser/blob/main/example-parse2.json).

The ``otdrparser.parse()`` function is now considered legacy. It returns the blocks as a list.

Output of the ``.parse()`` method converted into JSON: [example-parse.json](https://github.com/mjuenema/otdrparser/blob/main/example-parse.json)).
