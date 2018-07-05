from setuptools import setup


long_desc = \
    """
    TORRENTpy is an open-source framework for water, solutes, and particles transport through lumped and 
    semi-distributed catchments in Python. It is licensed under GNU GPL-3.0 (see license file provided). 
    The framework simulates the hydrological fluxes using top-down catchment models that can be applied 
    at the catchment scale or at the sub-catchment scale. Water quality models can complement the catchment 
    models to simulate the water-borne contaminants (both solutes and particles) at the scale where the 
    catchment models are applied (i.e. catchment scale or sub-catchment scale).
    """

setup(
    name='torrentpy',

    version='0.1.0',

    description='TORRENTpy: a tool for TranspORt thRough the catchmEnt NeTwork',
    long_description=long_desc,

    url='https://github.com/ThibHlln/torrentpy',

    author='Thibault Hallouin, Michael Bruen, and Eva Mockler',
    author_email='thibault.hallouin@ucdconnect.ie',

    license='GPLv3',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Natural Language :: English',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Hydrological Sciences',

        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',


        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],

    packages=['torrentpy', 'examples'],

    install_requires=[
        'numpy'
    ],

    extras_require={
        'with_netcdf': ['netCDF4'],
        'with_graphviz': ['graphviz']
    }
)
