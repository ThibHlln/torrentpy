import datetime
import logging
import csv
import numpy as np
from netCDF4 import Dataset


def create_simulation_files(my__network, dict__ls_models,
                            catchment, out_file_format, output_folder):
    if out_file_format == 'netcdf':
        create_simulation_files_netcdf(my__network, dict__ls_models,
                                       catchment, output_folder)
    else:
        create_simulation_files_csv(my__network, dict__ls_models,
                                    catchment, output_folder)


def create_simulation_files_csv(my__network, dict__ls_models,
                                catchment, output_folder):
    """
    This function creates a CSV file for each node and for each link and it adds the relevant headers for the
    inputs, the states, and the outputs.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param dict__ls_models: dictionary containing the list of structures for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict()
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str()
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :return: NOTHING, only creates the files in the output folder
    """
    logger = logging.getLogger('SingleRun.main')
    logger.info("Creating files for results.")
    # Create the CSV files with headers for the nodes (separating inputs, states, and outputs)
    for link in my__network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()

        for model in dict__ls_models[link]:
            my_inputs += model.input_names
            my_states += model.state_names
            my_outputs += model.output_names

        with open('{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_inputs)

        with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_states)

        with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_outputs)

    # Create the CSV files with headers for the nodes
    for node in my__network.nodes:
        with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my__network.variables)


def create_simulation_files_netcdf(my__network, dict__ls_models,
                                   catchment, output_folder):
    """
    This function creates a NetCDF4 file for each node and for each link and it adds the relevant headers for the
    inputs, the states, and the outputs.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param dict__ls_models: dictionary containing the list of structures for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict()
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str()
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :return: NOTHING, only creates the files in the output folder
    """
    logger = logging.getLogger('SingleRun.main')
    logger.info("Creating files for results.")
    # Create the NetCDF4 files with headers for the nodes (separating inputs, states, and outputs)
    for link in my__network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()

        for model in dict__ls_models[link]:
            my_inputs += model.input_names
            my_states += model.state_names
            my_outputs += model.output_names

        with Dataset('{}{}_{}.inputs.nc'.format(output_folder, catchment.capitalize(), link), 'w') as my_file:
            my_file.createDimension("DateTime", None)
            t = my_file.createVariable("DateTime", np.float64, ("DateTime",), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_input in my_inputs:
                my_file.createVariable(my_input, np.float64, ("DateTime",), zlib=True, complevel=1)

        with Dataset('{}{}_{}.states.nc'.format(output_folder, catchment.capitalize(), link), 'w') as my_file:
            my_file.createDimension("DateTime", None)
            t = my_file.createVariable("DateTime", np.float64, ("DateTime",), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_state in my_states:
                my_file.createVariable(my_state, np.float64, ("DateTime",), zlib=True, complevel=1)

        with Dataset('{}{}_{}.outputs.nc'.format(output_folder, catchment.capitalize(), link), 'w') as my_file:
            my_file.createDimension("DateTime", None)
            t = my_file.createVariable("DateTime", np.float64, ("DateTime",), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_output in my_outputs:
                my_file.createVariable(my_output, np.float64, ("DateTime",), zlib=True, complevel=1)

    # Create the NetCDF4 files with headers for the nodes
    for node in my__network.nodes:
        with Dataset('{}{}_{}.node.nc'.format(output_folder, catchment.capitalize(), node), 'w') as my_file:
            my_file.createDimension("DateTime", None)
            t = my_file.createVariable("DateTime", np.float64, ("DateTime",), zlib=True)
            t.units = 'seconds since 1970-01-01 00:00:00.0'
            for my_variable in my__network.variables:
                my_file.createVariable(my_variable, np.float64, ("DateTime",), zlib=True, complevel=1)


def update_simulation_files(my__network, my__tf, my_data_slice,
                            dict__nd_data, dict__ls_models,
                            catchment, out_file_format, output_folder, method='raw'):
    if out_file_format == 'netcdf':
        update_simulation_files_netcdf(my__network, my__tf, my_data_slice,
                                       dict__nd_data, dict__ls_models,
                                       catchment, output_folder, method=method)
    else:
        update_simulation_files_csv(my__network, my__tf, my_data_slice,
                                    dict__nd_data, dict__ls_models,
                                    catchment, output_folder, method=method)


def update_simulation_files_csv(my__network, my__tf, my_save_slice,
                                dict__nd_data, dict__ls_models,
                                catchment, output_folder, method='raw'):
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

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__tf: TimeFrame object for the simulation period
    :type my__tf: TimeFrame
    :param my_save_slice: list of datetime that need to be reported on
    :type my_save_slice: list()
    :param dict__nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type dict__nd_data: dict()
    :param dict__ls_models: dictionary containing the list of structures for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict()
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str()
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :param method: choice on the technique to process simulation variables when reporting time gap > simu time gap :
     'summary' = sums for inputs and averages for the rest / 'raw' = last values only for all
    :type method: str()
    :return: NOTHING, only updates the files in the output folder
    """
    logger = logging.getLogger('SingleRun.main')

    logger.info("> Updating results in files.")

    # Determine number of simulation steps to consider for reporting
    simu_steps_per_save_step = my__tf.save_gap / my__tf.simu_gap
    
    if method == 'summary':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in my__network.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in dict__ls_models[link]:
                my_inputs += model.input_names
                my_states += model.state_names
                my_outputs += model.output_names

            with open('{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_list = list()
                    for my_input in my_inputs:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_input])
                        my_list.append('%e' % sum(my_values))
                    my_writer.writerow([step] + my_list)

            with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_list = list()
                    for my_state in my_states:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_state])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

            with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_list = list()
                    for my_output in my_outputs:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_output])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_list = list()
                    for my_variable in my__network.variables:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                dict__nd_data[node][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_variable])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

    elif method == 'raw':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in my__network.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in dict__ls_models[link]:
                my_inputs += model.input_names
                my_states += model.state_names
                my_outputs += model.output_names

            with open('{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_list = list()
                    for my_input in my_inputs:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_input])
                        my_list.append('%e' % sum(my_values))
                    my_writer.writerow([step] + my_list)

            with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_state]
                                                 for my_state in my_states])

            with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_output]
                                                 for my_output in my_outputs])

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_save_slice[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[node][step][my_variable]
                                                 for my_variable in my__network.variables])

    else:
        raise Exception("Unknown method for updating simulations files.")


def update_simulation_files_netcdf(my__network, my__tf, my_save_slice,
                                   dict__nd_data, dict__ls_models,
                                   catchment, output_folder, method='raw'):
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

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__tf: TimeFrame object for the simulation period
    :type my__tf: TimeFrame
    :param my_save_slice: list of datetime that need to be reported on
    :type my_save_slice: list()
    :param dict__nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type dict__nd_data: dict()
    :param dict__ls_models: dictionary containing the list of structures for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict()
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str()
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :param method: choice on the technique to process simulation variables when reporting time gap > simu time gap :
     'summary' = sums for inputs and averages for the rest / 'raw' = last values only for all
    :type method: str()
    :return: NOTHING, only updates the files in the output folder
    """
    logger = logging.getLogger('SingleRun.main')

    logger.info("> Updating results in files.")

    my_stamps = \
        (np.asarray(my_save_slice[1:], dtype='datetime64[us]') - np.datetime64('1970-01-01T00:00:00Z')) / \
        np.timedelta64(1, 's')

    # Determine number of simulation steps to consider for reporting
    simu_steps_per_save_step = my__tf.save_gap / my__tf.simu_gap

    if method == 'summary':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in my__network.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in dict__ls_models[link]:
                my_inputs += model.input_names
                my_states += model.state_names
                my_outputs += model.output_names

            with Dataset('{}{}_{}.inputs.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_values = {my_input: list() for my_input in my_inputs}
                for step in my_save_slice[1:]:
                    for my_input in my_inputs:
                        my_value = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_input])
                        my_values[my_input].append(sum(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_input in my_inputs:
                    my_file.variables[my_input][start_idx:end_idx] = my_values[my_input]

            with Dataset('{}{}_{}.states.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                my_values = {my_state: list() for my_state in my_states}
                for step in my_save_slice[1:]:
                    for my_state in my_states:
                        my_value = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_state])
                        my_values[my_state].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_state in my_states:
                    my_file.variables[my_state][start_idx:end_idx] = my_values[my_state]

            with Dataset('{}{}_{}.outputs.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                my_values = {my_output: list() for my_output in my_outputs}
                for step in my_save_slice[1:]:
                    for my_output in my_outputs:
                        my_value = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_output])
                        my_values[my_output].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_output in my_outputs:
                    my_file.variables[my_output][start_idx:end_idx] = my_values[my_output]

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with Dataset('{}{}_{}.node.nc'.format(output_folder, catchment.capitalize(), node), 'a') as my_file:
                my_values = {my_variable: list() for my_variable in my__network.variables}
                for step in my_save_slice[1:]:
                    for my_variable in my__network.variables:
                        my_value = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                dict__nd_data[node][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_variable])
                        my_values[my_variable].append(sum(my_value) / len(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_variable in my__network.variables:
                    my_file.variables[my_variable][start_idx:end_idx] = my_values[my_variable]

    elif method == 'raw':
        # Save the Nested Dicts for the links (separating inputs, states, and outputs)
        for link in my__network.links:
            my_inputs = list()
            my_states = list()
            my_outputs = list()

            for model in dict__ls_models[link]:
                my_inputs += model.input_names
                my_states += model.state_names
                my_outputs += model.output_names

            with Dataset('{}{}_{}.inputs.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                # for inputs, 'raw' and 'summary report the same values because they are cumulative values
                my_values = {my_input: list() for my_input in my_inputs}
                for step in my_save_slice[1:]:
                    for my_input in my_inputs:
                        my_value = list()
                        for my_sub_step in xrange(0, -simu_steps_per_save_step, -1):
                            my_value.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.simu_gap)][my_input])
                        my_values[my_input].append(sum(my_value))
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_input in my_inputs:
                    my_file.variables[my_input][start_idx:end_idx] = my_values[my_input]

            with Dataset('{}{}_{}.states.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                my_values = {my_state: list() for my_state in my_states}
                for step in my_save_slice[1:]:
                    for my_state in my_states:
                        my_values[my_state].append(dict__nd_data[link][step][my_state])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_state in my_states:
                    my_file.variables[my_state][start_idx:end_idx] = my_values[my_state]

            with Dataset('{}{}_{}.outputs.nc'.format(output_folder, catchment.capitalize(), link), 'a') as my_file:
                my_values = {my_output: list() for my_output in my_outputs}
                for step in my_save_slice[1:]:
                    for my_output in my_outputs:
                        my_values[my_output].append(dict__nd_data[link][step][my_output])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_output in my_outputs:
                    my_file.variables[my_output][start_idx:end_idx] = my_values[my_output]

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with Dataset('{}{}_{}.node.nc'.format(output_folder, catchment.capitalize(), node), 'a') as my_file:
                my_values = {my_variable: list() for my_variable in my__network.variables}
                for step in my_save_slice[1:]:
                    for my_variable in my__network.variables:
                        my_values[my_variable].append(dict__nd_data[node][step][my_variable])
                start_idx, end_idx = \
                    len(my_file.variables['DateTime']), len(my_file.variables['DateTime']) + len(my_stamps)
                my_file.variables['DateTime'][start_idx:end_idx] = my_stamps
                for my_variable in my__network.variables:
                    my_file.variables[my_variable][start_idx:end_idx] = my_values[my_variable]

    else:
        raise Exception("Unknown method for updating simulations files.")
