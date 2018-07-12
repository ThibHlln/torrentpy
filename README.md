[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI Version](https://badge.fury.io/py/torrentpy.svg)](https://pypi.python.org/pypi/torrentpy)

# TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork

TORRENTpy is an open-source framework in Python for water, solutes, and particules transport through catchments discretised in lumped and semi-distributed manners. It is licensed under GNU GPL-3.0 (see [licence file](LICENCE.md) provided). The framework simulates the hydrological fluxes using top-down catchment models that can be applied at the catchment scale (lumped manner) or at the sub-catchment scale (semi-distributed manner). Water quality models can complement the catchment models to simulate the water-borne contaminants (both solutes and particles) at the scale where the catchment models are applied (*i.e.* catchment scale or sub-catchment scale).

## How to Install

TORRENTpy is available on PyPI, so you can simply use pip:
    python -m pip install torrentpy

Alternatively, you can download the source code (*i.e.* this repository) and use the command:
    python setup.py install

## Dependencies

TORRENTpy requires the popular Python package `numpy` to be installed on the Python implementation where `torrentpy` is installed. For Python 2 and 3 compatibilities, the package `future` is also required.
Additional optional dependencies include `netCDF4` if one wishes to use NetCDF files as input and/or output, `graphviz` if one wishes to use the utility `connectivity.py` and plot the network it generates, and `smartcpp` if one wishes to use an accelerator module for the `SMART` model (it gives access to a C++ extension for the SMART model).

## List of Models currently available in TORRENTpy

* Rainfall-Runoff Models:
	* `SMART` model (catchment runoff + river routing)

* Water Quality Models:
	* `INCA` model (catchment runoff + river routing)

## Input/Output File Formats

TORRENTpy is designed to read CSV (Comma-Separated Values) files and NetCDF (Network Common Data Form) files. However, the use of NetCDF files requires the Python package `netCDF4` to be installed on the Python implementation where this package is installed (specific requirements for the installation of `netCDF4` exist and can be found at [unidata.github.io/netcdf4-python](http://unidata.github.io/netcdf4-python/).

## Version History

* 0.2.0 [12 Jul 2018]: Operational version of TORRENTpy, with Python 3 compatibility
	* Fixes relative module import issues that made v0.1.0 unusable out of the box
	* Adds clean up function for output folder to avoid appending to files from previous simulations
	* Makes all scripts Python 3 compatible by using `builtins` and `io` packages
	* Corrects check on class instance for user-defined models added to KnowledgeBase
* 0.1.0 [05 Jul 2018]: First version of TORRENTpy
	* Attention, this version is not functional due to relative module import issues.

## Acknowledgment

This tool was developed with the financial support of Ireland's Environmental Protection Agency (Grant Number 2014-W-LS-5).
