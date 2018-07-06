[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/torrentpy.png)](https://pypi.python.org/pypi/torrentpy)
[![PyPI Version](https://img.shields.io/pypi/v/torrentpy.png)](https://pypi.python.org/pypi/torrentpy)

# TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork

TORRENTpy is an open-source framework for water, solutes, and particules transport through lumped and semi-distributed catchments in Python. It is licensed under GNU GPL-3.0 (see [licence file](LICENCE.md) provided). The framework simulates the hydrological fluxes using top-down catchment models that can be applied at the catchment scale or at the sub-catchment scale. Water quality models can complement the catchment models to simulate the water-borne contaminants (both solutes and particles) at the scale where the catchment models are applied (*i.e.* catchment scale or sub-catchment scale).

## List of Models currently available in TORRENTpy

* Rainfall-Runoff Models:
	* `SMART` model (catchment runoff + river routing)

* Water Quality Models:
	* `INCA` model (catchment runoff + river routing)

## Input/Output File Formats

TORRENTpy is designed to read CSV (Comma-Separated Values) files and NetCDF (Network Common Data Form) files. However, the use of NetCDF files requires the Python package `netCDF4` to be installed on the Python implementation where this package is installed.

## Version History

* 0.1.0 [08 Jul 2018]: First version of TORRENTpy

### Ackownlegments

This tool was developed with the financial support of Ireland's Environmental Protection Agency (Grant Number 2014-W-LS-5).
