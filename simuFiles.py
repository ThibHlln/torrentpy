from pandas import DataFrame
import pandas
import sys
import csv


def get_data_frame_for_daily_meteo_data(catchment, link, time_steps, in_folder):

    my_start = '%04d' % time_steps[1].year + '%02d' % time_steps[1].month + '%02d' % time_steps[1].day
    # use 1, not 0 because 0 was artificially created in TimeFrame object for initial conditions
    my_end = '%04d' % time_steps[-1].year + '%02d' % time_steps[-1].month + '%02d' % time_steps[-1].day

    my_meteo_data_types = ["rain", "peva", "temp"]

    my__data_frame = DataFrame(index=time_steps, columns=my_meteo_data_types).fillna(0.0)

    for meteo_type in my_meteo_data_types:
        try:
            my_meteo_df = pandas.read_csv("{}{}_{}_{}_{}.{}".format(in_folder, catchment,
                                                                    link, my_start, my_end, meteo_type),
                                          index_col=0)

            for my_datetime in time_steps[1:]:  # ignore first value which is for the initial conditions
                try:
                    my_value = my_meteo_df.loc[my_datetime.strftime("%Y-%m-%d %H:%M:%S"), meteo_type.upper()]
                    my__data_frame.set_value(my_datetime, meteo_type, float(my_value))
                except KeyError:  # could only be raised for .loc[], when index or column does not exist
                    sys.exit("{}{}_{}_{}_{}.{} does not "
                             "contain any value for {}.".format(in_folder, catchment, link, my_start, my_end,
                                                                meteo_type, my_datetime.strftime("%Y-%m-%d %H:%M:%S")))
                except ValueError:  # could only be raised for float(), when my_value is not a number
                    sys.exit("{}{}_{}_{}_{}.{} contains "
                             "an invalid value for {}.".format(in_folder, catchment, link, my_start, my_end,
                                                               meteo_type, my_datetime.strftime("%Y-%m-%d %H:%M:%S")))

        except IOError:
            sys.exit("{}{}_{}_{}_{}.{} does not exist.".format(in_folder, catchment,
                                                               link, my_start, my_end, meteo_type))

    return my__data_frame


def get_dict_parameters_from_file(catchment, outlet, obj_network, dict__model, in_folder):

    try:
        with open("{}{}_{}.parameters".format(in_folder, catchment, outlet)) as my_file:
            my_dict_param = dict()
            my_reader = csv.DictReader(my_file)
            found = list()
            for row in my_reader:
                if row["EU_CD"] in obj_network.links:
                    my_dict = dict()
                    for model in dict__model[row["EU_CD"]]:
                        for param in model.parameter_names:
                            try:
                                my_dict[param] = float(row[param])
                            except KeyError:
                                sys.exit("The parameter {} is not available for {}.".format(param, row["EU_CD"]))
                    my_dict_param[row["EU_CD"]] = my_dict
                    found.append(row["EU_CD"])
                else:
                    print "The waterbody {} in the parameter file is not in the network file.".format(row["EU_CD"])

            missing = [elem for elem in obj_network.links if elem not in found]
            if missing:
                sys.exit("The following waterbodies are not in the parameter file: {}.".format(missing))

        return my_dict_param

    except IOError:
        sys.exit("{}{}_{}.parameters does not exist.".format(in_folder, catchment, outlet))


def get_dict_constants_from_file(model, specs_folder):

    try:
        with open("{}{}.const".format(specs_folder, model.upper())) as my_file:
            my_dict_cst = dict()
            my_reader = csv.reader(my_file)
            for row in my_reader:
                my_dict_cst[row[0]] = float(row[1])

        return my_dict_cst

    except IOError:
        sys.exit("{}{}.const".format(specs_folder, model.upper()))


def get_dict_floats_from_file(variables, catchment, outlet, obj_network, folder):

    try:
        with open("{}{}_{}.{}".format(folder, catchment, outlet, variables)) as my_file:
            my_dict_variables = dict()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            fields.remove("EU_CD")
            found = list()
            for row in my_reader:
                if row["EU_CD"] in obj_network.links:
                    my_dict = dict()
                    for field in fields:
                        my_dict[field] = float(row[field])
                    my_dict_variables[row["EU_CD"]] = my_dict
                    found.append(row["EU_CD"])
                else:
                    print "The waterbody {} in the {} file is not in the network file.".format(row["EU_CD"], variables)

            missing = [elem for elem in obj_network.links if elem not in found]
            if missing:
                sys.exit("The following waterbodies are not in the {} file: {}.".format(missing, variables))

        return my_dict_variables

    except IOError:
        sys.exit("{}{}_{}.{} does not exist.".format(folder, catchment, outlet, variables))


def get_dict_strings_from_file(variables, catchment, outlet, obj_network, folder):

    try:
        with open("{}{}_{}.{}".format(folder, catchment, outlet, variables)) as my_file:
            my_dict_variables = dict()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            fields.remove("EU_CD")
            found = list()
            for row in my_reader:
                if row["EU_CD"] in obj_network.links:
                    my_dict = dict()
                    for field in fields:
                        my_dict[field] = str(row[field])
                    my_dict_variables[row["EU_CD"]] = my_dict
                    found.append(row["EU_CD"])
                else:
                    print "The waterbody {} in the {} file is not in the network file.".format(row["EU_CD"], variables)

            missing = [elem for elem in obj_network.links if elem not in found]
            if missing:
                sys.exit("The following waterbodies are not in the {} file: {}.".format(missing, variables))

        return my_dict_variables

    except IOError:
        sys.exit("{}{}_{}.{} does not exist.".format(folder, catchment, outlet, variables))


def get_df_distributions_from_file(specs_folder):

    try:
        my_file = '{}LOADINGS.dist'.format(specs_folder)
        my_df_distributions = pandas.read_csv(my_file, index_col=0)
        return my_df_distributions

    except IOError:
        sys.exit("{}LOADINGS.dist does not exist.".format(specs_folder))
