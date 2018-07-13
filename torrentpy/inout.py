# -*- coding: utf-8 -*-

# This file is part of TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork
# Copyright (C) 2018  Thibault Hallouin (1)
#
# (1) Dooge Centre for Water Resources Research, University College Dublin, Ireland
#
# TORRENTpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TORRENTpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TORRENTpy. If not, see <http://www.gnu.org/licenses/>.

from builtins import range
from datetime import datetime, timedelta
from logging import getLogger
import sys
import io
import csv
import numpy as np
try:
    from netCDF4 import Dataset
except ImportError:
    Dataset = None

from .timeframe import check_interval_in_list


def open_csv_rb(my_file):
    if sys.version_info[0] < 3:
        return io.open(my_file, 'rb')
    else:
        return io.open(my_file, 'r', encoding='utf8')


def open_csv_wb(my_file):
    if sys.version_info[0] < 3:
        return io.open(my_file, 'wb')
    else:
        return io.open(my_file, 'w', newline='', encoding='utf8')


def open_csv_ab(my_file):
    if sys.version_info[0] < 3:
        return io.open(my_file, 'ab')
    else:
        return io.open(my_file, 'a', newline='', encoding='utf8')


def read_csv_timeseries_with_data_checks(csv_file, tf):
    logger = getLogger('TORRENTpy.io')
    try:
        with open_csv_rb(csv_file) as my_file:
            my_nd_variables = dict()
            my_list_dt = list()
            my_reader = csv.DictReader(my_file)
            fields = my_reader.fieldnames[:]
            try:
                fields.remove('DateTime')
            except KeyError:
                logger.error("Field {} does not exist in {}.".format('DateTime', csv_file))
                raise Exception("Field {} does not exist in {}.".format('DateTime', csv_file))

            for field in fields:
                my_nd_variables[field] = dict()

            for row in my_reader:
                my_dt = datetime.strptime(row['DateTime'], '%Y-%m-%d %H:%M:%S')
                for field in fields:
                    my_nd_variables[field][my_dt] = float(row[field])
                my_list_dt.append(my_dt)

            start_data, end_data, interval = check_interval_in_list(my_list_dt, csv_file)
            if not start_data <= tf.needed_data_series[0]:
                logger.error("Data Start in {} is not sufficient for required TimeFrame.".format(csv_file))
                raise Exception("Data Start in {} is not sufficient for required TimeFrame.".format(csv_file))
            if not tf.needed_data_series[-1] <= end_data:
                logger.error("Data End in {} is not sufficient for required TimeFrame.".format(csv_file))
                raise Exception("Data End in {} is not sufficient for required TimeFrame.".format(csv_file))
            if not timedelta(minutes=tf.data_gap) == interval:
                logger.error("Data Gap in {} does not comply with required TimeFrame.".format(csv_file))
                raise Exception("Data Gap in {} does not comply with required TimeFrame.".format(csv_file))

        return my_nd_variables

    except IOError:
        raise Exception("File {} could not be found.".format(csv_file))


def read_netcdf_timeseries_with_data_checks(netcdf_file, tf):
    logger = getLogger('TORRENTpy.io')

    # check if netCDF4 is installed
    if not Dataset:
        logger.error("The use of 'netcdf' as the input file format requires the package 'netCDF4', "
                     "please install it and retry, or choose another file format.")
        raise Exception("The use of 'netcdf' as the input file format requires the package 'netCDF4', "
                        "please install it and retry, or choose another file format.")

    try:
        with Dataset(netcdf_file, "r") as my_file:
            my_file.set_auto_mask(False)
            my_nd_variables = dict()
            fields = list(my_file.variables.keys())
            try:
                fields.remove('DateTime')
            except KeyError:
                logger.error("Field {} does not exist in {}.".format('DateTime', netcdf_file))
                raise Exception("Field {} does not exist in {}.".format('DateTime', netcdf_file))

            for field in fields:
                if not len(my_file.variables['DateTime']) == len(my_file.variables[field]):
                    logger.error(
                        "Fields {} and {} do not have the same length in {}.".format(field, 'DateTime', netcdf_file))
                    raise Exception(
                        "Fields {} and {} do not have the same length in {}.".format(field, 'DateTime', netcdf_file))

            list_dt = [datetime.utcfromtimestamp(tstamp) for tstamp in my_file.variables['DateTime'][:]]
            list_vals = {field: my_file.variables[field][:] for field in fields}

            for field in fields:
                my_nd_variables[str(field)] = dict()

            for idx, dt in enumerate(list_dt):
                for field in fields:
                    my_nd_variables[str(field)][dt] = float(list_vals[field][idx])

            start_data, end_data, interval = check_interval_in_list(list_dt, netcdf_file)
            if not start_data <= tf.needed_data_series[0]:
                logger.error("Data Start in {} is not sufficient for required TimeFrame.".format(netcdf_file))
                raise Exception("Data Start in {} is not sufficient for required TimeFrame.".format(netcdf_file))
            if not tf.needed_data_series[-1] <= end_data:
                logger.error("Data End in {} is not sufficient for required TimeFrame.".format(netcdf_file))
                raise Exception("Data End in {} is not sufficient for required TimeFrame.".format(netcdf_file))
            if not timedelta(minutes=tf.data_gap) == interval:
                logger.error('Data Gap in {} does not comply with required TimeFrame.'.format(netcdf_file))
                raise Exception('Data Gap in {} does not comply with required TimeFrame.'.format(netcdf_file))

        return my_nd_variables

    except IOError:
        raise Exception("File {} could not be found.".format(netcdf_file))


def create_simulation_files(network, out_file_format):
    logger = getLogger('TORRENTpy.io')
    if out_file_format == 'netcdf':
        if Dataset:
            create_simulation_files_netcdf(network)
        else:
            logger.error("The use of 'netcdf' as the output file format requires the package 'netCDF4', "
                         "please install it and retry, or choose another file format.")
            raise Exception("The use of 'netcdf' as the output file format requires the package 'netCDF4', "
                            "please install it and retry, or choose another file format.")
    elif out_file_format == 'csv':
        create_simulation_files_csv(network)
    else:
        logger.error("The output format type \'{}\' cannot be read by TORRENTpy, "
                     "choose from: \'csv\', \'netcdf\'.".format(out_file_format))
        raise Exception("The output format type \'{}\' cannot be read by TORRENTpy, "
                        "choose from: \'csv\', \'netcdf\'.".format(out_file_format))


def create_simulation_files_csv(network):
    """
    This function creates a CSV file for each node and for each link and it adds the relevant headers for the
    inputs, the states, and the outputs.

    :param network: Network object for the simulated catchment
    :type network: Network
    """
    logger = getLogger('TORRENTpy.io')
    logger.info("Creating files for results.")
    # Create the CSV files with headers for the nodes (separating inputs, states, and outputs)
    for link in network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()

        for model in link.all_models:
            my_inputs += model.inputs_names
            my_states += model.states_names
            my_outputs += model.outputs_names

        with open_csv_wb('{}{}_{}.inputs'.format(network.out_fld, network.catchment, link.name)) as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_inputs)

        with open_csv_wb('{}{}_{}.states'.format(network.out_fld, network.catchment, link.name)) as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_states)

        with open_csv_wb('{}{}_{}.outputs'.format(network.out_fld, network.catchment, link.name)) as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_outputs)

    # Create the CSV files with headers for the nodes
    for node in network.nodes:
        with open_csv_wb('{}{}_{}.node'.format(network.out_fld, network.catchment, node.name)) as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + network.variables)


def create_simulation_files_netcdf(network):
    """
    This function creates a NetCDF4 file for each node and for each link and it adds the relevant headers for the
    inputs, the states, and the outputs.

    :param network: Network object for the simulated catchment
    :type network: Network
    """
    logger = getLogger('TORRENTpy.io')
    logger.info("Creating files for results.")
    # Create the NetCDF4 files with headers for the nodes (separating inputs, states, and outputs)
    for link in network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()

        for model in link.all_models:
            my_inputs += model.inputs_names
            my_states += model.states_names
            my_outputs += model.outputs_names

        with Dataset('{}{}_{}.inputs.nc'.format(network.out_fld, network.catchment, link.name), 'w') as my_file:
            my_file.createDimension('DateTime', None)
            t = my_file.createVariable("DateTime", np.float64, ('DateTime',), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_input in my_inputs:
                my_file.createVariable(my_input, np.float64, ('DateTime',), zlib=True, complevel=1)

        with Dataset('{}{}_{}.states.nc'.format(network.out_fld, network.catchment, link.name), 'w') as my_file:
            my_file.createDimension('DateTime', None)
            t = my_file.createVariable('DateTime', np.float64, ('DateTime',), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_state in my_states:
                my_file.createVariable(my_state, np.float64, ('DateTime',), zlib=True, complevel=1)

        with Dataset('{}{}_{}.outputs.nc'.format(network.out_fld, network.catchment, link.name), 'w') as my_file:
            my_file.createDimension('DateTime', None)
            t = my_file.createVariable('DateTime', np.float64, ('DateTime',), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_output in my_outputs:
                my_file.createVariable(my_output, np.float64, ('DateTime',), zlib=True, complevel=1)

    # Create the NetCDF4 files with headers for the nodes
    for node in network.nodes:
        with Dataset('{}{}_{}.node.nc'.format(network.out_fld, network.catchment, node.name), 'w') as my_file:
            my_file.createDimension('DateTime', None)
            t = my_file.createVariable('DateTime', np.float64, ("DateTime",), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_variable in network.variables:
                my_file.createVariable(my_variable, np.float64, ('DateTime',), zlib=True, complevel=1)


def update_simulation_files(network, timeframe, timeslice, database, out_file_format, method='raw'):
    logger = getLogger('TORRENTpy.io')
    if out_file_format == 'netcdf':  # it was already checked if netCDF4 was installed when creating the files
        update_simulation_files_netcdf(network, timeframe, timeslice,
                                       database, method=method)
    elif out_file_format == 'csv':
        update_simulation_files_csv(network, timeframe, timeslice,
                                    database, method=method)
    else:
        logger.error("The output format type \'{}\' cannot be read by TORRENTpy, "
                     "choose from: \'csv\', \'netcdf\'.".format(out_file_format))
        raise Exception("The output format type \'{}\' cannot be read by TORRENTpy, "
                        "choose from: \'csv\', \'netcdf\'.".format(out_file_format))


def update_simulation_files_csv(nw, tf, timeslice, db, method='raw'):
    """
    This function saves the simulation variables into the CSV files for the nodes and the links.
    It features two arguments:
     - "report" allows to choose which time gap to use to report the simulation variables ('data_gap' or 'simu_gap');
     - "method" allows to choose how to deal with the report of results at a coarser time scale than the simulated
      time gap:
        -> If 'summary' is chosen
         --> the inputs are summed up across all the simulation time steps included in the reporting gap
             (e.g. previous 24 hourly time steps summed up for each day when daily data simulated hourly)
         --> the states/outputs/nodes are averaged across all the simulation time steps included in the reporting gap
             (e.g. previous 24 hourly time steps averaged for each day when daily data simulated hourly)
        -> If 'raw' is chosen
         --> the inputs/states/outputs/nodes for the exact time steps corresponding to the data time gap end are
             reported (e.g. when daily data simulated hourly, only the value for the last hourly time step is
             reported for each day, the other 23 hourly time steps are not explicitly used)

    N.B. (report = 'simu_gap', method = 'raw') and (report = 'simu_gap', method = 'average') yield identical output
    files because the average is applied to only one data value.

    :param nw: Network object for the simulated catchment
    :type nw: Network
    :param tf: TimeFrame object for the simulation period
    :type tf: TimeFrame
    :param timeslice: list of datetime that need to be reported on
    :type timeslice: list()
    :param db: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type db: dict()
    :param method: choice on the technique to process simulation variables when reporting time gap > simu time gap :
     'summary' = sums for inputs and averages for the rest / 'raw' = last values only for all
    :type method: str()
    :return: NOTHING, only updates the files in the output folder
    """
    logger = getLogger('TORRENTpy.io')

    logger.info("> Updating results in files.")

    # Determine number of simulation steps to consider for reporting
    simu_steps_per_save_step = tf.save_gap // tf.simu_gap
    
    if method == 'summary':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in nw.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in link.all_models:
                my_inputs += model.inputs_names
                my_states += model.states_names
                my_outputs += model.outputs_names

            with open_csv_ab('{}{}_{}.inputs'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_list = list()
                    for my_input in my_inputs:
                        my_values = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_input])
                        my_list.append('%e' % sum(my_values))
                    my_writer.writerow([step] + my_list)

            with open_csv_ab('{}{}_{}.states'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_list = list()
                    for my_state in my_states:
                        my_values = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_state])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

            with open_csv_ab('{}{}_{}.outputs'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_list = list()
                    for my_output in my_outputs:
                        my_values = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_output])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

        # Save the Nested Dicts for the nodes
        for node in nw.nodes:
            with open_csv_ab('{}{}_{}.node'.format(nw.out_fld, nw.catchment, node.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_list = list()
                    for my_variable in nw.variables:
                        my_values = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                db.simulation[node.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_variable])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

    elif method == 'raw':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in nw.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in link.all_models:
                my_inputs += model.inputs_names
                my_states += model.states_names
                my_outputs += model.outputs_names

            with open_csv_ab('{}{}_{}.inputs'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_list = list()
                    for my_input in my_inputs:
                        my_values = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_input])
                        my_list.append('%e' % sum(my_values))
                    my_writer.writerow([step] + my_list)

            with open_csv_ab('{}{}_{}.states'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_writer.writerow([step] + ['%e' % db.simulation[link.name][step][my_state]
                                                 for my_state in my_states])

            with open_csv_ab('{}{}_{}.outputs'.format(nw.out_fld, nw.catchment, link.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_writer.writerow([step] + ['%e' % db.simulation[link.name][step][my_output]
                                                 for my_output in my_outputs])

        # Save the Nested Dicts for the nodes
        for node in nw.nodes:
            with open_csv_ab('{}{}_{}.node'.format(nw.out_fld, nw.catchment, node.name)) as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in timeslice[1:]:
                    my_writer.writerow([step] + ['%e' % db.simulation[node.name][step][my_variable]
                                                 for my_variable in nw.variables])

    else:
        logger.error("Unknown method for updating simulations files.")
        raise Exception("Unknown method for updating simulations files.")


def update_simulation_files_netcdf(nw, tf, timeslice, db, method='raw'):
    """
    This function saves the simulation variables into the CSV files for the nodes and the links.
    It features two arguments:
     - "report" allows to choose which time gap to use to report the simulation variables ('data_gap' or 'simu_gap');
     - "method" allows to choose how to deal with the report of results at a coarser time scale than the simulated
      time gap:
        -> If 'summary' is chosen
         --> the inputs are summed up across all the simulation time steps included in the reporting gap
             (e.g. previous 24 hourly time steps summed up for each day when daily data simulated hourly)
         --> the states/outputs/nodes are averaged across all the simulation time steps included in the reporting gap
             (e.g. previous 24 hourly time steps averaged for each day when daily data simulated hourly)
        -> If 'raw' is chosen
         --> the inputs/states/outputs/nodes for the exact time steps corresponding to the data time gap end are
             reported (e.g. when daily data simulated hourly, only the value for the last hourly time step is
             reported for each day, the other 23 hourly time steps are not explicitly used)

    N.B. (report = 'simu_gap', method = 'raw') and (report = 'simu_gap', method = 'average') yield identical output
    files because the average is applied to only one data value.

    :param nw: Network object for the simulated catchment
    :type nw: Network
    :param tf: TimeFrame object for the simulation period
    :type tf: TimeFrame
    :param timeslice: list of datetime that need to be reported on
    :type timeslice: list()
    :param db: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type db: dict()
    :param method: choice on the technique to process simulation variables when reporting time gap > simu time gap :
     'summary' = sums for inputs and averages for the rest / 'raw' = last values only for all
    :type method: str()
    :return: NOTHING, only updates the files in the output folder
    """
    logger = getLogger('TORRENTpy.io')

    logger.info("> Updating results in files.")

    my_stamps = \
        (np.asarray(timeslice[1:], dtype='datetime64[us]') - np.datetime64('1970-01-01T00:00:00Z')) / \
        np.timedelta64(1, 's')

    # Determine number of simulation steps to consider for reporting
    simu_steps_per_save_step = tf.save_gap // tf.simu_gap

    if method == 'summary':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in nw.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in link.all_models:
                my_inputs += model.inputs_names
                my_states += model.states_names
                my_outputs += model.outputs_names

            with Dataset('{}{}_{}.inputs.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_values = {my_input: list() for my_input in my_inputs}
                for step in timeslice[1:]:
                    for my_input in my_inputs:
                        my_value = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_input])
                        my_values[my_input].append(sum(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_input in my_inputs:
                    my_file.variables[my_input][start_idx:end_idx] = my_values[my_input]

            with Dataset('{}{}_{}.states.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                my_values = {my_state: list() for my_state in my_states}
                for step in timeslice[1:]:
                    for my_state in my_states:
                        my_value = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_state])
                        my_values[my_state].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_state in my_states:
                    my_file.variables[my_state][start_idx:end_idx] = my_values[my_state]

            with Dataset('{}{}_{}.outputs.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                my_values = {my_output: list() for my_output in my_outputs}
                for step in timeslice[1:]:
                    for my_output in my_outputs:
                        my_value = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_output])
                        my_values[my_output].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_output in my_outputs:
                    my_file.variables[my_output][start_idx:end_idx] = my_values[my_output]

        # Save the Nested Dicts for the nodes
        for node in nw.nodes:
            with Dataset('{}{}_{}.node.nc'.format(nw.out_fld, nw.catchment, node.name), 'a') as my_file:
                my_values = {my_variable: list() for my_variable in nw.variables}
                for step in timeslice[1:]:
                    for my_variable in nw.variables:
                        my_value = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                db.simulation[node.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_variable])
                        my_values[my_variable].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_variable in nw.variables:
                    my_file.variables[my_variable][start_idx:end_idx] = my_values[my_variable]

    elif method == 'raw':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in nw.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in link.all_models:
                my_inputs += model.inputs_names
                my_states += model.states_names
                my_outputs += model.outputs_names

            with Dataset('{}{}_{}.inputs.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_values = {my_input: list() for my_input in my_inputs}
                for step in timeslice[1:]:
                    for my_input in my_inputs:
                        my_value = list()
                        for my_sub_step in range(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                db.simulation[link.name][
                                    step + timedelta(minutes=my_sub_step * tf.simu_gap)][my_input])
                        my_values[my_input].append(sum(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_input in my_inputs:
                    my_file.variables[my_input][start_idx:end_idx] = my_values[my_input]

            with Dataset('{}{}_{}.states.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                my_values = {my_state: list() for my_state in my_states}
                for step in timeslice[1:]:
                    for my_state in my_states:
                        my_values[my_state].append(db.simulation[link.name][step][my_state])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_state in my_states:
                    my_file.variables[my_state][start_idx:end_idx] = my_values[my_state]

            with Dataset('{}{}_{}.outputs.nc'.format(nw.out_fld, nw.catchment, link.name), 'a') as my_file:
                my_values = {my_output: list() for my_output in my_outputs}
                for step in timeslice[1:]:
                    for my_output in my_outputs:
                        my_values[my_output].append(db.simulation[link.name][step][my_output])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_output in my_outputs:
                    my_file.variables[my_output][start_idx:end_idx] = my_values[my_output]

        # Save the Nested Dicts for the nodes
        for node in nw.nodes:
            with Dataset('{}{}_{}.node.nc'.format(nw.out_fld, nw.catchment, node.name), 'a') as my_file:
                my_values = {my_variable: list() for my_variable in nw.variables}
                for step in timeslice[1:]:
                    for my_variable in nw.variables:
                        my_values[my_variable].append(db.simulation[node.name][step][my_variable])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_variable in nw.variables:
                    my_file.variables[my_variable][start_idx:end_idx] = my_values[my_variable]

    else:
        logger.error("Unknown method for updating simulations files.")
        raise Exception("Unknown method for updating simulations files.")
