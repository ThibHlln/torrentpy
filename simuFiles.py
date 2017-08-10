from pandas import DataFrame
import datetime
import pandas
import csv


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


def get_nd_meteo_data_from_file(catchment, link, my_tf, series_data, series_simu,
                                dt_start_data, dt_end_data, in_folder):

    my_start = dt_start_data.strftime("%Y%m%d")
    my_end = dt_end_data.strftime("%Y%m%d")

    my_meteo_data_types = ["rain", "peva", "airt", "soit"]

    my_dbl_dict = {i: {c: 0.0 for c in my_meteo_data_types} for i in series_simu}

    divisor = my_tf.step_data / my_tf.step_simu

    for meteo_type in my_meteo_data_types:
        try:
            my_meteo_df = pandas.read_csv("{}{}_{}_{}_{}.{}".format(in_folder, catchment,
                                                                    link, my_start, my_end, meteo_type),
                                          index_col=0)

            for my_dt_data in series_data[1:]:  # ignore first value which is for the initial conditions
                try:
                    my_value = my_meteo_df.get_value(my_dt_data.strftime("%Y-%m-%d %H:%M:%S"), meteo_type.upper())
                    my_portion = float(my_value) / divisor
                except KeyError:  # could only be raised for .get_value(), when index or column does not exist
                    raise Exception("{}{}_{}_{}_{}.{} does not contain any value for {}.".format(
                        in_folder, catchment, link, my_start, my_end, meteo_type,
                        my_dt_data.strftime("%Y-%m-%d %H:%M:%S")))
                except ValueError:  # could only be raised for float(), when my_value is not a number
                    raise Exception("{}{}_{}_{}_{}.{} contains an invalid value for {}.".format(
                        in_folder, catchment, link, my_start, my_end, meteo_type,
                        my_dt_data.strftime("%Y-%m-%d %H:%M:%S")))
                for my_sub_step in xrange(0, -divisor, -1):
                    my_dt_simu = my_dt_data + datetime.timedelta(minutes=my_sub_step * my_tf.step_simu)
                    if (meteo_type == 'rain') or (meteo_type == 'peva'):
                        my_dbl_dict[my_dt_simu][meteo_type] = float(my_portion)
                    else:
                        my_dbl_dict[my_dt_simu][meteo_type] = float(my_value)

        except IOError:
            raise Exception("{}{}_{}_{}_{}.{} does not exist.".format(
                in_folder, catchment, link, my_start, my_end, meteo_type))

        del my_meteo_df

    return my_dbl_dict


def get_df_flow_data_from_file(catchment, link, my_tf,
                               dt_start_data, dt_end_data, in_folder, logger):

    my_start = dt_start_data.strftime("%Y%m%d")
    my_end = dt_end_data.strftime("%Y%m%d")

    flow_label = 'flow'

    my__data_frame = DataFrame(index=my_tf.series_data, columns=[flow_label]).fillna(0.0)

    try:
        my_flow_df = pandas.read_csv("{}{}_{}_{}_{}.{}".format(in_folder, catchment,
                                                               link, my_start, my_end, flow_label),
                                     index_col=0)

        for my_dt_data in my_tf.series_data[1:]:  # ignore first value which is for the initial conditions
            try:
                my_value = my_flow_df.get_value(my_dt_data.strftime("%Y-%m-%d %H:%M:%S"), flow_label.upper())
                my__data_frame.set_value(my_dt_data, flow_label, float(my_value))
            except KeyError:  # could only be raised for .get_value(), when index or column does not exist
                raise Exception("{}{}_{}_{}_{}.{} does not contain any value for {}.".format(
                    in_folder, catchment, link, my_start, my_end, flow_label, my_dt_data.strftime("%Y-%m-%d %H:%M:%S")))
            except ValueError:  # could only be raised for float(), when my_value is not a number
                raise Exception("{}{}_{}_{}_{}.{} contains an invalid value for {}.".format(
                    in_folder, catchment, link, my_start, my_end, flow_label, my_dt_data.strftime("%Y-%m-%d %H:%M:%S")))

    except IOError:
        logger.info("{}{}_{}_{}_{}.{} does not exist.".format(in_folder, catchment, link, my_start, my_end, flow_label))

    return my__data_frame


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
