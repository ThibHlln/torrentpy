from collections import OrderedDict
from csv import DictReader, writer
from numpy import float64
from datetime import datetime, timedelta
from netCDF4 import Dataset

import popCSFfunctions as popF


def create_subset_flow_file(catchment, link, catchment_area, gauge, gauged_area,
                            my_tf, plot_dt_start, plot_dt_end,
                            in_folder, out_folder, logger):

    flow_label = 'flow'

    my_dt_series = [step for step in my_tf.save_series if (step >= plot_dt_start) and (step <= plot_dt_end)]

    if not gauged_area == -999.00:  # i.e. the gauged area is known
        try:
            my_original_flow_file = "{}{}_{}_{}.{}".format(in_folder, catchment, link, gauge, flow_label)
            my_subset_flow_file = "{}{}_{}_{}.{}".format(out_folder, catchment, link, gauge, flow_label)

            my_dict_flows = get_dict_discharge_series(my_original_flow_file,
                                                      plot_dt_start, plot_dt_end,
                                                      catchment_area, gauged_area)

            write_flow_file_from_dict(my_subset_flow_file, my_dict_flows, my_dt_series)

        except IOError:
            logger.info("{}{}_{}_{}.{} does not exist.".format(in_folder, catchment, link, gauge, flow_label))
    else:
        logger.info("Gauged area of {} for {}_{} is unknown.".format(gauge, catchment, link))


def get_dict_discharge_series(file_location, start_report, end_report, catchment_area, gauged_area):
    data_flow = read_flow_file(file_location)

    scaling_factor = catchment_area / gauged_area

    start_date = (start_report - timedelta(days=2)).date()
    end_date = (end_report + timedelta(days=1)).date()

    dict_flow = OrderedDict()
    for dt in data_flow.iterkeys():
        d = dt.date()
        if (start_date <= d) and (d <= end_date):
            dict_flow[dt] = data_flow[dt] * scaling_factor

    return popF.rescale_time_resolution_of_irregular_mean_data(dict_flow, start_report, end_report,
                                                               timedelta(days=1), timedelta(hours=1))


def read_netcdf_timeseries(netcdf_file, time_variable):
    try:
        with Dataset(netcdf_file, "r") as my_file:
            my_file.set_auto_mask(False)
            my_nd_variables = dict()
            fields = my_file.variables.keys()
            try:
                fields.remove(time_variable)
            except KeyError:
                raise Exception('Field {} does not exist in {}.'.format(time_variable, netcdf_file))

            for field in fields:
                if not len(my_file.variables[time_variable]) == len(my_file.variables[field]):
                    raise Exception(
                        'Fields {} and {} do not have the same length in {}.'.format(field, time_variable, netcdf_file))

            list_dt = [datetime.utcfromtimestamp(tstamp) for tstamp in my_file.variables[time_variable][:]]
            list_st_dt = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in list_dt]
            list_vals = {field: my_file.variables[field][:] for field in fields}

            for field in fields:
                my_nd_variables[str(field)] = dict()

            for idx, dt in enumerate(list_st_dt):
                for field in fields:
                    my_nd_variables[str(field)][dt] = float(list_vals[field][idx])

        return my_nd_variables

    except IOError:
        raise Exception('File {} could not be found.'.format(netcdf_file))


def read_flow_file(file_location):
    return read_csv_time_series_with_missing_check(file_location, key_header='DATETIME', val_header='FLOW')


def read_csv_time_series_with_missing_check(csv_file, key_header, val_header):
    try:
        with open(csv_file, 'rb') as my_file:
            my_dict_data = OrderedDict()
            my_reader = DictReader(my_file)
            try:
                for row in my_reader:
                    try:
                        if row[val_header] != '':  # not an empty string (that would mean missing data)
                            if float64(row[val_header]) != -99.0:  # flag for missing data
                                my_dict_data[datetime.strptime(row[key_header], "%Y-%m-%d %H:%M:%S")] = \
                                    float64(row[val_header])
                    except ValueError:
                        raise Exception('Field {} in {} cannot be converted to float '
                                        'at {}.'.format(val_header, csv_file, row[key_header]))
            except KeyError:
                raise Exception('Field {} or {} does not exist in {}.'.format(key_header, val_header, csv_file))
        return my_dict_data
    except IOError:
        raise Exception('File {} could not be found.'.format(csv_file))


def write_flow_file_from_dict(csv_file, discharge, timeseries):
    with open(csv_file, 'wb') as my_file:
        my_writer = writer(my_file, delimiter=',')
        my_writer.writerow(['DateTime', 'flow'])
        for my_dt in timeseries:
            try:
                my_writer.writerow([my_dt, '%e' % discharge[my_dt]])
            except KeyError:
                my_writer.writerow([my_dt, '%e' % -99.0])
