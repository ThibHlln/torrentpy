import unittest
from datetime import datetime
import torrentpy
from torrentpy import inout


class TestReadInputs(unittest.TestCase):
    def setUp(self):
        self.input_file_csv = \
            "examples/in/CatchmentLumpedName_OutletName/CatchmentLumpedName_OutletName_20000101_20161231.meteorology"
        self.input_file_netcdf = \
            "examples/in/CatchmentLumpedName_OutletName/CatchmentLumpedName_OutletName_20000101_20161231.meteorology.nc"

        self.tf = torrentpy.TimeFrame(
            dt_data_start=datetime.strptime('01/01/2000 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_data_end=datetime.strptime('07/01/2000 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_save_start=datetime.strptime('01/01/2009 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_save_end=datetime.strptime('31/12/2010 09:00:00', '%d/%m/%Y %H:%M:%S'),
            data_increment_in_minutes=1440,
            save_increment_in_minutes=1440,
            simu_increment_in_minutes=1440,
            expected_simu_slice_length=0,
            warm_up_in_days=0
        )

        self.expected_outcome = {
            'rain': {
                datetime.strptime('2000-01-01 09:00:00', '%Y-%m-%d %H:%M:%S'): 8.620558e-01,
                datetime.strptime('2000-01-02 09:00:00', '%Y-%m-%d %H:%M:%S'): 8.247358e-01,
                datetime.strptime('2000-01-03 09:00:00', '%Y-%m-%d %H:%M:%S'): 3.283937e+00,
                datetime.strptime('2000-01-04 09:00:00', '%Y-%m-%d %H:%M:%S'): 8.649947e-02,
                datetime.strptime('2000-01-05 09:00:00', '%Y-%m-%d %H:%M:%S'): 3.660522e+00,
                datetime.strptime('2000-01-06 09:00:00', '%Y-%m-%d %H:%M:%S'): 2.177900e-01,
                datetime.strptime('2000-01-07 09:00:00', '%Y-%m-%d %H:%M:%S'): 2.730987e+00
            },
            'peva': {
                datetime.strptime('2000-01-01 09:00:00', '%Y-%m-%d %H:%M:%S'): 2.000000e-01,
                datetime.strptime('2000-01-02 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.000000e-01,
                datetime.strptime('2000-01-03 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.000000e-01,
                datetime.strptime('2000-01-04 09:00:00', '%Y-%m-%d %H:%M:%S'): 7.000000e-01,
                datetime.strptime('2000-01-05 09:00:00', '%Y-%m-%d %H:%M:%S'): 1.300000e+00,
                datetime.strptime('2000-01-06 09:00:00', '%Y-%m-%d %H:%M:%S'): 7.000000e-01,
                datetime.strptime('2000-01-07 09:00:00', '%Y-%m-%d %H:%M:%S'): 1.100000e+00
            },
            'airt': {
                datetime.strptime('2000-01-01 09:00:00', '%Y-%m-%d %H:%M:%S'): 4.000000e+00,
                datetime.strptime('2000-01-02 09:00:00', '%Y-%m-%d %H:%M:%S'): 8.250000e+00,
                datetime.strptime('2000-01-03 09:00:00', '%Y-%m-%d %H:%M:%S'): 6.100000e+00,
                datetime.strptime('2000-01-04 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.000000e+00,
                datetime.strptime('2000-01-05 09:00:00', '%Y-%m-%d %H:%M:%S'): 8.200000e+00,
                datetime.strptime('2000-01-06 09:00:00', '%Y-%m-%d %H:%M:%S'): 6.100000e+00,
                datetime.strptime('2000-01-07 09:00:00', '%Y-%m-%d %H:%M:%S'): 7.550000e+00
            },
            'soit': {
                datetime.strptime('2000-01-01 09:00:00', '%Y-%m-%d %H:%M:%S'): 4.650000e+00,
                datetime.strptime('2000-01-02 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.100000e+00,
                datetime.strptime('2000-01-03 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.575000e+00,
                datetime.strptime('2000-01-04 09:00:00', '%Y-%m-%d %H:%M:%S'): 4.450000e+00,
                datetime.strptime('2000-01-05 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.075000e+00,
                datetime.strptime('2000-01-06 09:00:00', '%Y-%m-%d %H:%M:%S'): 5.625000e+00,
                datetime.strptime('2000-01-07 09:00:00', '%Y-%m-%d %H:%M:%S'): 6.000000e+00
            }
        }

    def test_read_csv(self):
        # test the targeted read function on the example file
        read_nd = inout.read_csv_timeseries_with_data_checks(self.input_file_csv, self.tf)

        # extract a sample for comparison
        my_nd = dict()
        for var in self.expected_outcome:
            my_nd[var] = dict()
            for dt in self.expected_outcome[var]:
                my_nd[dt] = read_nd[var][dt]

        # compare
        self.assertEqual(
            self.expected_outcome,
            my_nd
        )

    def test_netcdf_csv(self):
        # test the targeted read function on the example file
        read_nd = inout.read_netcdf_timeseries_with_data_checks(self.input_file_csv, self.tf)

        # extract a sample for comparison
        my_nd = dict()
        for var in self.expected_outcome:
            my_nd[var] = dict()
            for dt in self.expected_outcome[var]:
                my_nd[dt] = read_nd[var][dt]

        # compare
        self.assertEqual(
            self.expected_outcome,
            my_nd
        )


if __name__ == '__main__':
    unittest.main()
