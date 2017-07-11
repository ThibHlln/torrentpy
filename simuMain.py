import os
import logging
import pandas
from pandas import DataFrame

from simuClasses import *
import simuFiles as sF
import simuFunctions as sFn


def main():
    # Location of the different needed folders
    root = os.path.realpath('..')  # move to parent directory of this current python file
    os.chdir(root)  # define parent directory as root in order to use only relative paths after this
    specifications_folder = "specs/"
    input_folder = "in/"
    output_folder = "out/"

    # Ask user for information on simulation
    question_catch = raw_input('Name of the catchment? ')
    catchment = question_catch.capitalize()

    question_outlet = raw_input('European Code (EU_CD) of the catchment? [format IE_XX_##X######] ')
    outlet = question_outlet.upper()

    if not os.path.isfile('{}{}_{}.network'.format(input_folder, catchment, outlet)):
        # Check if combination catchment/outlet is coherent by using the name of the network file
        sys.exit("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Create a logger
    logger = get_logger(catchment, outlet, 'simu', output_folder)

    # Set up the simulation (either with .simulation file or through the console)
    data_time_step_in_min, datetime_start_data, datetime_end_data, \
        simu_time_step_in_min, datetime_start_simu, datetime_end_simu, \
        warm_up_in_days = set_up_simulation(catchment, outlet, input_folder, logger)

    # Create a TimeFrame object
    my__time_frame = TimeFrame(datetime_start_simu, datetime_end_simu,
                               int(data_time_step_in_min), int(simu_time_step_in_min))
    my__time_frame_warm_up = TimeFrame(my__time_frame.start, my__time_frame.start +
                                       datetime.timedelta(days=warm_up_in_days - 1),
                                       int(data_time_step_in_min), int(simu_time_step_in_min))

    # Declare all the dictionaries that will be needed, all using the waterbody code as a key
    dict__ls_models = dict()  # key: waterbody, value: list of model objects
    dict__nd_data = dict()  # key: waterbody, value: data frame (x: time step, y: data type)
    dict__nd_data_warm_up = dict()

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, specifications_folder)

    # Create NestedDicts for the nodes
    for node in my__network.nodes:
        my_dict_with_variables = {c: 0.0 for c in my__network.variables}
        dict__nd_data[node] = \
            {i: dict(my_dict_with_variables) for i in my__time_frame.series_simu}
        if not warm_up_in_days == 0.0:
            dict__nd_data_warm_up[node] = \
                {i: dict(my_dict_with_variables) for i in my__time_frame_warm_up.series_simu}

    # Create Models and NestedDicts for the links
    for link in my__network.links:
        # Declare Model objects
        if my__network.categories[link] == "11":  # river headwater
            dict__ls_models[link] = [Model("CATCHMENT", "SMART_INCAL", specifications_folder),
                                     Model("RIVER", "LINRES_INCAS", specifications_folder)]
        elif my__network.categories[link] == "10":  # river
            dict__ls_models[link] = [Model("CATCHMENT", "SMART_INCAL", specifications_folder),
                                     Model("RIVER", "LINRES_INCAS", specifications_folder)]
        elif my__network.categories[link] == "20":  # lake
            dict__ls_models[link] = [Model("LAKE", "BATHTUB", specifications_folder)]
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            sys.exit("Waterbody {}: {} is not a registered type of waterbody.".format(link,
                                                                                      my__network.categories[link]))

        # Create NestedDicts for the links
        my_headers = list()
        for model in dict__ls_models[link]:
            my_headers += model.input_names + model.state_names + model.output_names
        my_dict_with_headers = {c: 0.0 for c in my_headers}
        dict__nd_data[link] = \
            {i: dict(my_dict_with_headers) for i in my__time_frame.series_simu}
        if not warm_up_in_days == 0.0:
            dict__nd_data_warm_up[link] = \
                {i: dict(my_dict_with_headers) for i in my__time_frame_warm_up.series_simu}

    # Read the parameters file, or read the descriptors file, generate the parameters, and generate the parameters file
    logger.info("{} # Parameterising.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    dict_desc = sF.get_nd_from_file('descriptors', 'float', catchment, outlet, my__network, input_folder)
    dict_param = dict()
    my_dict_for_file = dict()
    for link in my__network.links:
        dict_param[link] = dict()
        for models in dict__ls_models[link]:
            for model_name in models.identifier.split('_'):
                try:
                    my_dict_for_file[model_name]
                except KeyError:
                    my_dict_for_file[model_name] = dict()
                if os.path.isfile('{}{}_{}.{}.parameters'.format(input_folder, catchment, outlet, model_name)):
                    my__model = Model("SPECIMEN", model_name, specifications_folder)
                    dict_param[link][model_name] = sF.get_dict_parameters_from_file(catchment, outlet, link, my__model,
                                                                                    input_folder)
                    my_dict_for_file[model_name].update({link: dict_param[link][model_name]})
                else:
                    dict_param[link][model_name] = sFn.infer_parameters_from_descriptors(dict_desc[link], model_name)
                    my_dict_for_file[model_name].update({link: dict_param[link][model_name]})

    for model_name in my_dict_for_file:
        df_param = DataFrame.from_dict(my_dict_for_file[model_name], orient='index')
        df_param.to_csv('{}{}_{}.{}.parameters'.format(output_folder, catchment.capitalize(),
                                                       outlet, model_name), index_label='EU_CD')

    # Read the constants files if model has constants
    dict_const = dict()
    logger.info("{} # Reading constants files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    for model_name in ["SMART", "LINRES", "INCAS", "INCAL"]:
        my__model = Model("SPECIMEN", model_name, specifications_folder)
        dict_const[model_name] = sF.get_dict_constants_from_file(my__model, specifications_folder)

    # Read the meteorological input files
    logger.info("{} # Reading meteorological files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    dict__nd_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)
    for link in my__network.links:
        dict__nd_meteo[link] = sF.get_nd_meteo_data_from_file(catchment, link, my__time_frame,
                                                              datetime_start_data, datetime_end_data, input_folder)

    # Read the annual loadings file and the application files to distribute the loadings for each time step
    logger.info("{} # Reading loadings files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    dict__nd_loadings = dict()
    dict_annual_loads = sF.get_nd_from_file('loadings', 'float', catchment, outlet, my__network, input_folder)
    dict_applications = sF.get_nd_from_file('applications', 'str', catchment, outlet, my__network, input_folder)
    df_distributions = sF.get_df_distributions_from_file(specifications_folder)
    for link in my__network.links:
        dict__nd_loadings[link] = sFn.distribute_loadings_across_year(dict_annual_loads, dict_applications,
                                                                      df_distributions, link, my__time_frame)

    # Set the initial conditions ('blank' warm up run)
    if not warm_up_in_days == 0.0:
        logger.info("{} # Determining initial conditions.".format(datetime.datetime.now().strftime('%d/%m/%Y '
                                                                                                   '%H:%M:%S')))
        simulate(my__network, my__time_frame_warm_up,
                 dict__nd_data_warm_up, dict__ls_models,
                 dict__nd_meteo, dict__nd_loadings, dict_desc, dict_param, dict_const,
                 logger)

        for link in my__network.links:  # set last values of warm up as initial conditions for actual simulation
            dict__nd_data[link].iloc[0] = dict__nd_data_warm_up[link].iloc[-1]

        with open('{}{}_{}.log'.format(output_folder, catchment, outlet), 'w'):
            # empty the log file because lines in it only due to warm up run
            pass

    # Simulate
    logger.info("{} # Simulating.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    simulate(my__network, my__time_frame,
             dict__nd_data, dict__ls_models,
             dict__nd_meteo, dict__nd_loadings, dict_desc, dict_param, dict_const,
             logger)

    # Save the DataFrames for the links and nodes (separating inputs, states, and outputs)
    save_simulation_files(my__network, my__time_frame, dict__nd_data, dict__ls_models,
                          catchment, output_folder, logger)

    # Generate gauged flow file in output folder (could be identical to input file if date ranges identical)
    sF.get_df_flow_data_from_file(
        catchment, outlet, my__time_frame,
        datetime_start_data, datetime_end_data, input_folder).to_csv('{}{}_{}.flow'.format(output_folder,
                                                                                           catchment.capitalize(),
                                                                                           outlet),
                                                                     header='FLOW',
                                                                     float_format='%e',
                                                                     index_label='DateTime')

    logger.info("{} # Ending.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))


def get_logger(catchment, outlet, prefix, output_folder):
    """
    This function creates a logger in order to print in console as well as to save in .log file information
    about the simulation.

    :param catchment: name of the catchment
    :param outlet: European code of the catchment
    :param prefix: prefix of the extension .log to specify what type of log file it is
    :param output_folder: path of the output folder where to save the log file
    :return: logger
    :rtype: Logger
    """
    # # Logger levels: debug < info < warning < error < critical
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create a file handler
    if os.path.isfile('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix)):
        os.remove('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix))
    handler = logging.FileHandler('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def set_up_simulation(catchment, outlet, input_folder, logger):
    """
    This function generates the various inputs required to set up the simulation objects and files. It will first check
    if there is a .simulation file available in the input folder, and then check in the file if each required input is
    available. If there is no file available, it will ask for everything to be typed by the user in the console. If
    there is a file available but some inputs are missing, it will ask for the missing ones to be typed by the user in
    the console.

    :param catchment: name of the catchment to simulate
    :type catchment: str
    :param outlet: European code of the outlet of the catchment to simulate
    :type outlet: str
    :param input_folder: path of the folder where the input files are located
    :type input_folder: str
    :param logger: reference to the logger to be used
    :type logger: Logger
    :return:
        data_time_step_in_min: time step in minutes in the input files
        datetime_start_data: datetime for the start date in the input files
        datetime_end_data: datetime for the end date in the input files
        simu_time_step_in_min: time step in minutes for the simulation
        datetime_start_simu: datetime for the start date of the simulation
        datetime_end_simu: datetime for the end date of the simulation
        warm_up_in_days: number of days to run in order to determine the initial conditions for the states of the links
    """

    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}.simulation".format(input_folder, catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()
        logger.info("There is not {}{}_{}.simulation available.".format(input_folder, catchment, outlet))

    # Get the set-up information either from the file, or from console
    try:
        question_start_data = my_answers_df.get_value('start_datetime_data', 'ANSWER')
    except KeyError:
        question_start_data = raw_input('Starting date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_data = my_answers_df.get_value('end_datetime_data', 'ANSWER')
    except KeyError:
        question_end_data = raw_input('Ending date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_start_simu = my_answers_df.get_value('start_datetime_simu', 'ANSWER')
    except KeyError:
        question_start_simu = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_simu = datetime.datetime.strptime(question_start_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_simu = my_answers_df.get_value('end_datetime_simu', 'ANSWER')
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_data_time_step = my_answers_df.get_value('data_time_step_min', 'ANSWER')
    except KeyError:
        question_data_time_step = raw_input('Time step for data? [integer in minutes] ')
    try:
        data_time_step_in_min = float(int(question_data_time_step))
    except ValueError:
        sys.exit("The data time step is invalid. [not an integer]")
    try:
        question_simu_time_step = my_answers_df.get_value('simu_time_step_min', 'ANSWER')
    except KeyError:
        question_simu_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        simu_time_step_in_min = float(int(question_simu_time_step))
    except ValueError:
        sys.exit("The simulation time step is invalid. [not an integer]")
    try:
        question_warm_up_duration = my_answers_df.get_value('warm_up_days', 'ANSWER')
    except KeyError:
        question_warm_up_duration = raw_input('Warm-up duration? [integer in days] ')
    try:
        warm_up_in_days = float(int(question_warm_up_duration))
    except ValueError:
        sys.exit("The warm-up duration is invalid. [not an integer]")
    logger.info("{} # Initialising.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    # Check if temporal information is consistent
    if datetime_start_simu < datetime_start_data:
        sys.exit("The simulation start is earlier than the data start.")
    if datetime_end_simu > datetime_end_data:
        sys.exit("The simulation end is later than the data end.")
    if data_time_step_in_min % simu_time_step_in_min != 0.0:
        sys.exit("The data time step is not a multiple of the simulation time step.")

    return data_time_step_in_min, datetime_start_data, datetime_end_data, \
        simu_time_step_in_min, datetime_start_simu, datetime_end_simu, \
        warm_up_in_days


def simulate(my__network, my__time_frame,
             dict__nd_data, dict__ls_models, dict__nd_meteo, dict__nd_loadings,
             nd_desc, nd_param, nd_const,
             logger):
    """
    This function runs the simulations for a given catchment (defined by a Network object) and given time period
    (defined by a TimeFrame object). For each time step, it first runs the models associated with the links (defined as
    Model objects), then it sums up all of what is arriving at each node.

    N.B. The first time step in the TimeFrame is ignored because it is for the initial conditions that are needed for
    the models to get the previous states of the links.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param dict__nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type dict__nd_data: dict
    :param dict__ls_models: dictionary containing the list of models for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict
    :param dict__nd_meteo: dictionary containing the nested dictionaries for the links for meteorological inputs
        { key = link: value = nested_dictionary(index=datetime,column=meteo_input) }
    :type dict__nd_meteo: dict
    :param dict__nd_loadings: dictionary containing the nested dictionaries for the links for contaminant inputs
        { key = link: value = nested_dictionary(index=datetime,column=contaminant_input) }
    :type dict__nd_loadings: dict
    :param nd_desc: nested dictionary containing the catchment descriptors for the links
        { key = link: value = { key = descriptor_name, value = descriptor_value } }
    :type nd_desc: dict
    :param nd_param: nested dictionary containing the catchment parameters for the links
        { key = link: value = { key = parameter_name, value = parameter_value } }
    :type nd_param: dict
    :param nd_const: nested dictionary containing the model constants for the models
        { key = model_identifier: value = { key = constant_name, value = constant_value } }
    :param logger: reference to the logger to be used
    :type logger: Logger
    :return: NOTHING, only updates the nested dictionaries for data
    """
    my_dict_variables = dict()
    for variable in my__network.variables:
        my_dict_variables[variable] = 0.0
    for step in my__time_frame.series_simu[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__ls_models[link]:
                model.run(my__network, link, dict__nd_data,
                          nd_desc, nd_param, nd_const, dict__nd_meteo, dict__nd_loadings,
                          step, my__time_frame.step_simu,
                          logger)
        # Sum up everything coming towards each node
        for node in my__network.nodes:
            # Sum up the flows
            q_h2o = 0.0
            for variable in ["q_h2o"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])]
                    elif my__network.categories[link] == "20":  # lake
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["l_out_", variable])]
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])]
                q_h2o += my_dict_variables[variable]
                dict__nd_data[node][step][variable] = my_dict_variables[variable]
                my_dict_variables[variable] = 0.0
            # Sum up the contaminants
            for variable in ["c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])] * \
                                                       dict__nd_data[link][step]["r_out_q_h2o"]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])] * \
                                                       dict__nd_data[link][step]["r_out_q_h2o"]
                    elif my__network.categories[link] == "20":  # lake
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["l_out_", variable])] * \
                                                       dict__nd_data[link][step]["l_out_q_h2o"]
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])] * \
                                                       dict__nd_data[link][step]["c_out_q_h2o"]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])] * \
                                                       dict__nd_data[link][step]["c_out_q_h2o"]
                if q_h2o >= 0.01:
                    dict__nd_data[node][step][variable] = my_dict_variables[variable] / q_h2o
                my_dict_variables[variable] = 0.0


def save_simulation_files(my__network, my__time_frame,
                          dict__nd_data, dict__ls_models,
                          catchment, output_folder,
                          logger):
    """
    This function saves the simulated data into CSV files. It creates one file per link and per node in the network.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param dict__nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type dict__nd_data: dict
    :param dict__ls_models: dictionary containing the list of models for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str
    :param logger: reference to the logger to be used
    :type logger: Logger
    :return: NOTHING, only creates the files in the output folder
    """
    # Save the Nested Dicts for the links (separating inputs, states, and outputs)
    logger.info("{} # Saving results in files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
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
            for step in my__time_frame.series_data[1:]:
                my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_input]
                                             for my_input in my_inputs])
        with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_states)
            for step in my__time_frame.series_data[1:]:
                my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_state]
                                             for my_state in my_states])
        with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my_outputs)
            for step in my__time_frame.series_data[1:]:
                my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_output]
                                             for my_output in my_outputs])

    # Save the Nested Dicts for the nodes
    for node in my__network.nodes:
        with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'wb') as my_file:
            my_writer = csv.writer(my_file, delimiter=',')
            my_writer.writerow(['DateTime'] + my__network.variables)
            for step in my__time_frame.series_data[1:]:
                my_writer.writerow([step] + ['%e' % dict__nd_data[node][step][my_variable]
                                             for my_variable in my__network.variables])


if __name__ == "__main__":
    main()
