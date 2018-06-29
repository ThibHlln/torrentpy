from datetime import datetime, timedelta
import csv
from os import path
from netCDF4 import Dataset

import resolution as prp_rs


def read_csv(csv_file, var_type, ind_type, col4index):
    try:
        with open(csv_file, 'rb') as my_file:
            my_nd_variables = dict()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            try:
                fields.remove(col4index)
            except KeyError:
                raise Exception('Field {} does not exist in {}.'.format(col4index, csv_file))
            for row in my_reader:
                my_dict = dict()
                for field in fields:
                    my_dict[field] = var_type(row[field])
                my_nd_variables[ind_type(row[col4index])] = my_dict

        return my_nd_variables

    except IOError:
        raise Exception('File {} could not be found.'.format(csv_file))


def read_csv_timeseries_with_data_checks(csv_file, tf):
    try:
        with open(csv_file, 'rb') as my_file:
            my_nd_variables = dict()
            my_list_dt = list()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            try:
                fields.remove('DATETIME')
            except KeyError:
                raise Exception('Field {} does not exist in {}.'.format('DATETIME', csv_file))

            for field in fields:
                my_nd_variables[field] = dict()

            for row in my_reader:
                my_dt = datetime.strptime(row['DATETIME'], "%Y-%m-%d %H:%M:%S")
                for field in fields:
                    my_nd_variables[field][my_dt] = float(row[field])
                my_list_dt.append(my_dt)

        start_data, end_data, interval = prp_rs.check_interval_in_list(my_list_dt, csv_file)
        if not tf.data_start == start_data:
            raise Exception(
                'Data Start provided does not comply with Data available in {}.'.format(csv_file))
        if not tf.data_end == end_data:
            raise Exception('Data End provided does not comply with Data available in {}.'.format(csv_file))
        if not timedelta(minutes=tf.data_gap) == interval:
            raise Exception('Data Gap provided does not comply with Data available in {}.'.format(csv_file))

        return my_nd_variables

    except IOError:
        raise Exception('File {} could not be found.'.format(csv_file))


def read_netcdf_timeseries_with_data_checks(netcdf_file, tf):
    try:
        with Dataset(netcdf_file, "r") as my_file:
            my_file.set_auto_mask(False)
            my_nd_variables = dict()
            fields = my_file.variables.keys()
            try:
                fields.remove('DATETIME')
            except KeyError:
                raise Exception('Field {} does not exist in {}.'.format('DATETIME', netcdf_file))

            for field in fields:
                if not len(my_file.variables['DATETIME']) == len(my_file.variables[field]):
                    raise Exception(
                        'Fields {} and {} do not have the same length in {}.'.format(field, 'DATETIME', netcdf_file))

            list_dt = [datetime.utcfromtimestamp(tstamp) for tstamp in my_file.variables['DATETIME'][:]]
            list_vals = {field: my_file.variables[field][:] for field in fields}

            for field in fields:
                my_nd_variables[str(field)] = dict()

            for idx, dt in enumerate(list_dt):
                for field in fields:
                    my_nd_variables[str(field)][dt] = float(list_vals[field][idx])

            start_data, end_data, interval = prp_rs.check_interval_in_list(list_dt, netcdf_file)
            if not tf.data_start == start_data:
                raise Exception('Data Start provided does not comply with Data available in {}.'.format(netcdf_file))
            if not tf.data_end == end_data:
                raise Exception('Data End provided does not comply with Data available in {}.'.format(netcdf_file))
            if not timedelta(minutes=tf.data_gap) == interval:
                raise Exception('Data Gap provided does not comply with Data available in {}.'.format(netcdf_file))

        return my_nd_variables

    except IOError:
        raise Exception('File {} could not be found.'.format(netcdf_file))


def get_nd_meteo_data_from_file(catchment, link, my_tf, in_file_format, in_folder):
    if in_file_format == 'netcdf':
        return get_nd_meteo_data_from_netcdf_file(catchment, link, my_tf, in_folder)
    else:
        return get_nd_meteo_data_from_csv_file(catchment, link, my_tf, in_folder)


def get_nd_meteo_data_from_csv_file(catchment, link, my_tf, in_folder):

    my_meteo_data_types = ["rain", "peva", "airt", "soit"]

    nd_meteo_simu = {c: dict() for c in my_meteo_data_types}

    for meteo_type in my_meteo_data_types:
        my_meteo_file = None
        for dt_format in ['%Y', '%Y%m', '%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S']:
            if path.isfile(
                    "{}{}_{}_{}_{}.{}".format(in_folder, catchment, link, my_tf.data_start.strftime(dt_format),
                                              my_tf.data_end.strftime(dt_format), meteo_type)):
                my_meteo_file = \
                    "{}{}_{}_{}_{}.{}".format(in_folder, catchment, link, my_tf.data_start.strftime(dt_format),
                                              my_tf.data_end.strftime(dt_format), meteo_type)
        if not my_meteo_file:
            raise Exception("{}{}_{}_{}_{}.{} does not exist.".format(
                in_folder, catchment, link, '[DataStart]', '[DataEnd]', meteo_type))

        my_nd_meteo_data = read_csv_timeseries_with_data_checks(my_meteo_file, my_tf)

        time_delta_res = prp_rs.get_required_resolution(
            my_tf.data_needed_start, my_tf.simu_start,
            timedelta(minutes=my_tf.data_gap), timedelta(minutes=my_tf.simu_gap))

        if meteo_type in ["rain", "peva"]:
            nd_meteo_simu[meteo_type] = prp_rs.rescale_time_resolution_of_regular_cumulative_data(
                my_nd_meteo_data[meteo_type.upper()],
                my_tf.data_needed_start, my_tf.data_needed_end, timedelta(minutes=my_tf.data_gap),
                time_delta_res,
                my_tf.simu_start, my_tf.simu_end, timedelta(minutes=my_tf.simu_gap))
        else:  # i.e. meteo_type in ["airt", "soit"]
            nd_meteo_simu[meteo_type] = prp_rs.rescale_time_resolution_of_regular_mean_data(
                my_nd_meteo_data[meteo_type.upper()],
                my_tf.data_needed_start, my_tf.data_needed_end, timedelta(minutes=my_tf.data_gap),
                time_delta_res,
                my_tf.simu_start, my_tf.simu_end, timedelta(minutes=my_tf.simu_gap))

        del my_nd_meteo_data

    return nd_meteo_simu


def get_nd_meteo_data_from_netcdf_file(catchment, link, my_tf, in_folder):

    my_meteo_data_types = ["rain", "peva", "airt", "soit"]

    nd_meteo_simu = {c: dict() for c in my_meteo_data_types}

    for meteo_type in my_meteo_data_types:
        my_meteo_file = None
        for dt_format in ['%Y', '%Y%m', '%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S']:
            if path.isfile(
                    "{}{}_{}_{}_{}.{}.nc".format(in_folder, catchment, link, my_tf.data_start.strftime(dt_format),
                                                 my_tf.data_end.strftime(dt_format), meteo_type)):
                my_meteo_file = \
                    "{}{}_{}_{}_{}.{}.nc".format(in_folder, catchment, link, my_tf.data_start.strftime(dt_format),
                                                 my_tf.data_end.strftime(dt_format), meteo_type)
        if not my_meteo_file:
            raise Exception("{}{}_{}_{}_{}.{}.nc does not exist.".format(
                in_folder, catchment, link, 'StartDate', 'EndDate', meteo_type))

        my_nd_meteo_data = read_netcdf_timeseries_with_data_checks(my_meteo_file, my_tf)

        time_delta_res = prp_rs.get_required_resolution(
            my_tf.data_needed_start, my_tf.simu_start,
            timedelta(minutes=my_tf.data_gap), timedelta(minutes=my_tf.simu_gap))

        if meteo_type in ["rain", "peva"]:
            nd_meteo_simu[meteo_type] = prp_rs.rescale_time_resolution_of_regular_cumulative_data(
                my_nd_meteo_data[meteo_type.upper()],
                my_tf.data_needed_start, my_tf.data_needed_end, timedelta(minutes=my_tf.data_gap),
                time_delta_res,
                my_tf.simu_start, my_tf.simu_end, timedelta(minutes=my_tf.simu_gap))
        else:  # i.e. meteo_type in ["airt", "soit"]
            nd_meteo_simu[meteo_type] = prp_rs.rescale_time_resolution_of_regular_mean_data(
                my_nd_meteo_data[meteo_type.upper()],
                my_tf.data_needed_start, my_tf.data_needed_end, timedelta(minutes=my_tf.data_gap),
                time_delta_res,
                my_tf.simu_start, my_tf.simu_end, timedelta(minutes=my_tf.simu_gap))

        del my_nd_meteo_data

    return nd_meteo_simu


def get_nd_from_file(obj_network, folder, var_type, extension='csv'):

    try:
        with open("{}{}_{}.{}".format(folder, obj_network.name, obj_network.code, extension)) as my_file:
            my_dict_variables = dict()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            fields.remove("EU_CD")
            found = list()
            for row in my_reader:
                if row["EU_CD"] in obj_network.links:
                    my_dict = dict()
                    for field in fields:
                        my_dict[field] = var_type(row[field])
                    my_dict_variables[row["EU_CD"]] = my_dict
                    found.append(row["EU_CD"])
                else:
                    print "The waterbody {} in the {} file is not in the network file.".format(row["EU_CD"], extension)

            missing = [elem for elem in obj_network.links if elem not in found]
            if missing:
                raise Exception("The following waterbodies are not in the {} file: {}.".format(missing, extension))

        return my_dict_variables

    except IOError:
        raise Exception("{}{}_{}.{} does not exist.".format(folder, obj_network.name, obj_network.code, extension))


def get_nd_distributions_from_file(specs_folder):

    try:
        my_file = '{}LOADINGS.dist'.format(specs_folder)
        my_nd_distributions = read_csv(my_file, var_type=float, ind_type=int, col4index='day_no')
        return my_nd_distributions

    except IOError:
        raise Exception("{}LOADINGS.dist does not exist.".format(specs_folder))
