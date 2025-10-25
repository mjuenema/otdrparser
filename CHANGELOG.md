# Changelog
All notable changes to this project will be documented in this file.

## Future
* Add ``tools/`` scripts as I need them.
* Fix bugs.

## 0.2.0 - 2025-10-25
* Added ``parse2()`` method that returns the parsed trace file as a dictionary keyed by block name.

## 0.1.5 - 2025-10-14
* Fixed mis-spelled 'acquisition' (https://github.com/mjuenema/otdrparser/issues/11)

## 0.1.4 - 2025-10-10
* Fixed issue that index of refraction was not considered when calculating distances (https://github.com/mjuenema/otdrparser/issues/9)
* Added ``tools/sor2png.py`` script to plot OTDR traces as PNG file.

## 0.1.3 - 2025-05-10
* Read whole block first before parsing it instead of parsing the data while reading it.

## 0.1.2 - 2024-12-24
* Added basic tests.
* Merged "address otdrparser latin-1 handling issue" (https://github.com/mjuenema/otdrparser/pull/5)


## 0.1.1 - 2023-04-30
* Reference ``README.md`` in ``pyproject.toml`` so that there is a description on PyPi.

## 0.1.0 - 2023-04-30
* Initial release
