import logging
from pandas import DataFrame
from itertools import izip
import argparse
from glob import glob

from simuClasses import *
import simuFiles as sF
import simuFunctions as sFn


def main(catchment, outlet, slice_length, warm_up_in_days, adding_up, is_single_run=False):
    # Location of the different needed directories
    root = "C:/PycharmProjects/Python/CatchmentSimulationFramework/"
    os.chdir(root)  # define root
    spec_directory = "scripts/specs/"
    input_directory = "in/"
    output_directory = "out/"

    # Check if combination catchment/outlet is coherent by using the name of the input folder
    if not os.path.exists("{}{}_{}".format(input_directory, catchment, outlet)):
        raise Exception("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Set up the simulation (either with .simulation file or through the console)
    data_time_gap_in_min, data_datetime_start, data_datetime_end, \
        simu_time_gap_in_min, simu_datetime_start, simu_datetime_end = \
        setup_simulation(catchment, outlet, input_directory)

    # Precise the specific folders to use in the directories
    input_folder = "{}{}_{}/".format(input_directory, catchment, outlet)
    output_folder = "{}{}_{}_{}_{}/".format(output_directory, catchment, outlet,
                                            simu_datetime_start.strftime("%Y%m%d"),
                                            simu_datetime_end.strftime("%Y%m%d"))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create logger and handler
    setup_logger(catchment, outlet, 'SingleRun.main', 'simu', output_folder, is_single_run)
    logger = logging.getLogger('SingleRun.main')

    logger.warning("Starting simulation for {} {} [Slice-Up: {}, Warm-Up: {}, Adding-Up: {}].".format(
        catchment, outlet, slice_length, warm_up_in_days, adding_up))

    # Store information about arguments used to call the run
    my_df_info = pandas.DataFrame.from_dict(
        {'SliceUp': slice_length, 'WarmUp': warm_up_in_days, 'AddUp': adding_up}, orient='index')
    my_df_info.index.name = "Information"
    my_df_info.columns = ["Value"]
    my_df_info.to_csv('{}{}_{}.information'.format(output_folder, catchment, outlet), sep=',')

    logger.info("Initialising.")

    # Clean up the output folder for the desired file extensions
    for my_extension in ["*.parameters", "*.node", "*.inputs", "*.outputs", "*.states"]:
        my_files = glob("{}/{}{}{}".format(root, output_folder, catchment, my_extension))
        for my_file in my_files:
            os.remove(my_file)

    # Create a TimeFrame object for simulation run and warm-up run
    my__time_frame = TimeFrame(simu_datetime_start, simu_datetime_end,
                               int(data_time_gap_in_min), int(simu_time_gap_in_min), slice_length)
    my__time_frame_warm_up = TimeFrame(my__time_frame.start, my__time_frame.start +
                                       datetime.timedelta(days=warm_up_in_days - 1),
                                       int(data_time_gap_in_min), int(simu_time_gap_in_min), slice_length)

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, spec_directory, adding_up=adding_up)

    # Create Models for the links
    dict__ls_models = generate_models_for_links(my__network, spec_directory, input_folder, output_folder)

    # Create files to store simulation results
    create_simulation_files(my__network, dict__ls_models, catchment, output_folder)

    # Set the initial conditions ('blank' warm up run slice by slice) if required
    my_last_lines = dict()
    if not warm_up_in_days == 0.0:  # Warm-up run required
        logger.info("Determining initial conditions.")
        # Get meteo input data
        dict__nd_meteo = get_meteo_input_from_file(my__network, my__time_frame_warm_up,
                                                   my__time_frame_warm_up.series_data,
                                                   my__time_frame_warm_up.series_simu,
                                                   data_datetime_start, data_datetime_end,
                                                   input_folder)
        # Initialise dicts to link time slices together (use last time step of one as first for the other)
        for link in my__network.links:
            my_last_lines[link] = dict()
        for node in my__network.nodes:
            my_last_lines[node] = dict()

        for my_simu_slice, my_data_slice in izip(my__time_frame_warm_up.slices_simu,
                                                 my__time_frame_warm_up.slices_data):
            logger.info("Running Warm-Up Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                                 my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
            # Initialise data structures
            dict__nd_data = generate_data_structures_for_links_and_nodes(my__network,
                                                                         my_simu_slice,
                                                                         dict__ls_models)

            # Get history of previous time slice last time step for initial conditions of current time slice
            for link in my__network.links:
                dict__nd_data[link][my_simu_slice[0]].update(my_last_lines[link])
            for node in my__network.nodes:
                dict__nd_data[node][my_simu_slice[0]].update(my_last_lines[node])

            # Get other input data
            dict__nd_loadings = get_contaminant_input_from_file(my__network, my__time_frame_warm_up,
                                                                my_data_slice, my_simu_slice,
                                                                input_folder, spec_directory)
            # Simulate
            simulate(my__network, my__time_frame_warm_up, my_simu_slice,
                     dict__nd_data, dict__ls_models,
                     dict__nd_meteo, dict__nd_loadings)

            # Save history (last time step) for next slice
            for link in my__network.links:
                my_last_lines[link].update(dict__nd_data[link][my_simu_slice[-1]])
            for node in my__network.nodes:
                my_last_lines[node].update(dict__nd_data[node][my_simu_slice[-1]])

            # Garbage collection
            del dict__nd_data
            del dict__nd_loadings
    else:  # Warm-up run not required
        # Initialise dicts to link time slices together (use last time step of one as first for the other)
        for link in my__network.links:
            my_last_lines[link] = dict()
        for node in my__network.nodes:
            my_last_lines[node] = dict()

    # Simulate (run slice by slice)
    logger.info("Starting the simulation.")
    # Get meteo input data
    dict__nd_meteo = get_meteo_input_from_file(my__network, my__time_frame,
                                               my__time_frame.series_data, my__time_frame.series_simu,
                                               data_datetime_start, data_datetime_end,
                                               input_folder)
    for my_simu_slice, my_data_slice in izip(my__time_frame.slices_simu,
                                             my__time_frame.slices_data):

        logger.info("Running Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                     my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
        # Initialise data structures
        dict__nd_data = generate_data_structures_for_links_and_nodes(my__network,
                                                                     my_simu_slice,
                                                                     dict__ls_models)

        # Get history of previous time step for initial conditions of current time step
        for link in my__network.links:
            dict__nd_data[link][my_simu_slice[0]].update(my_last_lines[link])
        for node in my__network.nodes:
            dict__nd_data[node][my_simu_slice[0]].update(my_last_lines[node])

        # Get other input data
        dict__nd_loadings = get_contaminant_input_from_file(my__network, my__time_frame,
                                                            my_data_slice, my_simu_slice,
                                                            input_folder, spec_directory)
        # Simulate
        simulate(my__network, my__time_frame, my_simu_slice,
                 dict__nd_data, dict__ls_models,
                 dict__nd_meteo, dict__nd_loadings)

        # Write results in files
        update_simulation_files(my__network, my__time_frame, my_data_slice, my_simu_slice,
                                dict__nd_data, dict__ls_models,
                                catchment, output_folder, report='data_gap', method='summary')

        # Save history (last time step) for next slice
        for link in my__network.links:
            my_last_lines[link].update(dict__nd_data[link][my_simu_slice[-1]])
        for node in my__network.nodes:
            my_last_lines[node].update(dict__nd_data[node][my_simu_slice[-1]])

        # Garbage collection
        del dict__nd_data
        del dict__nd_loadings

    logger.warning("Ending simulation for {} {}.".format(catchment, outlet))


def setup_simulation(catchment, outlet, input_dir):
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
    :param input_dir: path of the directory where the input files are located
    :type input_dir: str
    :return:
        data_time_gap_in_min: time increment in minutes in the input files
        datetime_start_data: datetime for the start date in the input files
        datetime_end_data: datetime for the end date in the input files
        simu_time_gap_in_min: time increment in minutes for the simulation
        datetime_start_simu: datetime for the start date of the simulation
        datetime_end_simu: datetime for the end date of the simulation
        warm_up_in_days: number of days to run in order to determine the initial conditions for the states of the links
    """
    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}/{}_{}.simulation".format(input_dir, catchment, outlet,
                                                                          catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()

    # Get the set-up information either from the file, or from console
    try:
        question_start_data = my_answers_df.get_value('data_start_datetime', 'ANSWER')
    except KeyError:
        question_start_data = raw_input('Starting date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_data = my_answers_df.get_value('data_end_datetime', 'ANSWER')
    except KeyError:
        question_end_data = raw_input('Ending date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_start_simu = my_answers_df.get_value('simu_start_datetime', 'ANSWER')
    except KeyError:
        question_start_simu = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_simu = datetime.datetime.strptime(question_start_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_simu = my_answers_df.get_value('simu_end_datetime', 'ANSWER')
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_data_time_gap = my_answers_df.get_value('data_time_gap_min', 'ANSWER')
    except KeyError:
        question_data_time_gap = raw_input('Time gap for data? [integer in minutes] ')
    try:
        data_time_gap_in_min = float(int(question_data_time_gap))
    except ValueError:
        raise Exception("The data time gap is invalid. [not an integer]")
    try:
        question_simu_time_gap = my_answers_df.get_value('simu_time_gap_min', 'ANSWER')
    except KeyError:
        question_simu_time_gap = raw_input('Time gap for simulation? [integer in minutes] ')
    try:
        simu_time_gap_in_min = float(int(question_simu_time_gap))
    except ValueError:
        raise Exception("The simulation time gap is invalid. [not an integer]")

    # Check if temporal information is consistent
    if datetime_start_data > datetime_end_data:
        raise Exception("The data time frame is inconsistent.")

    if datetime_start_simu > datetime_end_simu:
        raise Exception("The simulation time frame is inconsistent.")

    if datetime_start_simu < datetime_start_data:
        raise Exception("The simulation start is earlier than the data start.")
    if datetime_end_simu > datetime_end_data:
        raise Exception("The simulation end is later than the data end.")

    if data_time_gap_in_min % simu_time_gap_in_min != 0.0:
        raise Exception("The data time gap is not a multiple of the simulation time gap.")

    return data_time_gap_in_min, datetime_start_data, datetime_end_data, \
        simu_time_gap_in_min, datetime_start_simu, datetime_end_simu


def setup_logger(catchment, outlet, name, prefix, output_folder, is_single_run):
    """
    This function creates a logger in order to print in console as well as to save in .log file information
    about the simulation. The level of detail displayed is the console is customisable using the is_single_run
    parameter. If it is True, more information will be displayed (logging.INFO) than if it is False
    (logging.WARNING only).

    :param catchment: name of the catchment
    :param outlet: European code of the catchment
    :param name: name of the logger to identify it
    :param prefix: prefix of the extension .log to specify what type of log file it is
    :param output_folder: path of the output folder where to save the log file
    :param is_single_run: boolean to determine if the logger is created is a single run session
    :return: logger
    :rtype: Logger
    """
    # Create Logger [ levels: debug < info < warning < error < critical ]
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Create FileHandler
    if os.path.isfile('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix)):  # del file if already exists
        os.remove('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix))
    f_handler = logging.FileHandler('{}{}_{}.{}.log'.format(output_folder, catchment, outlet, prefix))
    f_handler.setLevel(logging.INFO)
    # Create StreamHandler
    s_handler = logging.StreamHandler()
    if is_single_run:  # specify level of detail depending if it is used in a singleRun or multiRun session
        s_handler.setLevel(logging.INFO)
    else:
        s_handler.setLevel(logging.WARNING)
    # Create Formatter
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt="%d/%m/%Y - %H:%M:%S")
    # Apply Formatter and Handler
    f_handler.setFormatter(formatter)
    s_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    logger.addHandler(s_handler)


def generate_models_for_links(my__network, specifications_folder, input_folder, output_folder):
    """
    This function creates the Model objects for all the links in the network. Each link can have several models
    (e.g. a catchment model and a reach model).

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param specifications_folder:
    :param input_folder: path to the output folder where to save the simulation files
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :return: dictionary containing all the Model objects generated
        {key: link, value: list of Model objects}
    :rtype: dict
    """
    dict__ls_models = dict()  # key: waterbody, value: list of model objects
    for link in my__network.links:
        # Declare Model objects
        if my__network.categories[link] == "11":  # river headwater
            dict__ls_models[link] = [Model("CATCHMENT", "SMART_INCAL", my__network, link,
                                           specifications_folder, input_folder, output_folder),
                                     Model("RIVER", "LINRES_INCAS", my__network, link,
                                           specifications_folder, input_folder, output_folder)]
        elif my__network.categories[link] == "10":  # river
            dict__ls_models[link] = [Model("CATCHMENT", "SMART_INCAL", my__network, link,
                                           specifications_folder, input_folder, output_folder),
                                     Model("RIVER", "LINRES_INCAS", my__network, link,
                                           specifications_folder, input_folder, output_folder)]
        elif my__network.categories[link] == "20":  # lake
            dict__ls_models[link] = [Model("LAKE", "BATHTUB", my__network, link,
                                           specifications_folder, input_folder, output_folder)]
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            raise Exception("Waterbody {}: {} is not a registered type of waterbody.".format(
                link, my__network.categories[link]))

    return dict__ls_models


def generate_data_structures_for_links_and_nodes(my__network, my_simu_slice, dict__ls_models):
    """
    This function generates a nested dictionary for each node and for each link and stores them in a single dictionary
    that is returned. Each nested dictionary has the dimension of the simulation time slice times the number of
    variables (inputs, states, and outputs) for all the models of the link.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my_simu_slice: list of DateTime to be simulated
    :type my_simu_slice: list
    :param dict__ls_models: dictionary containing the list of models for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict
    :return: dictionary containing the nested dictionaries
        { key = link: value = nested_dictionary(index=datetime,column=model_variables) }
    :rtype: dict
    """
    logger = logging.getLogger('SingleRun.main')
    logger.info("> Generating data structures.")
    dict__nd_data = dict()  # key: waterbody, value: data frame (x: time step, y: data type)
    # Create NestedDicts for the nodes
    for node in my__network.nodes:
        my_dict_with_variables = {c: 0.0 for c in my__network.variables}
        dict__nd_data[node] = \
            {i: dict(my_dict_with_variables) for i in my_simu_slice}
    # Create NestedDicts for the links
    for link in my__network.links:
        # Create NestedDicts for the links
        my_headers = list()
        for model in dict__ls_models[link]:
            my_headers += model.input_names + model.state_names + model.output_names
        my_dict_with_headers = {c: 0.0 for c in my_headers}
        dict__nd_data[link] = \
            {i: dict(my_dict_with_headers) for i in my_simu_slice}

    return dict__nd_data


def get_meteo_input_from_file(my__network, my__time_frame, my_data_slice, my_simu_slice,
                              datetime_start_data, datetime_end_data,
                              input_folder):
    """
    This function generates a nested dictionary for each link and stores them in a single dictionary that is returned.
    Each nested dictionary has the dimension of the simulation time slice times the number of meteorological variables.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param my_data_slice: list of DateTime corresponding to the simulation slice (separated by the data time gap)
    :type my_data_slice: list()
    :param my_simu_slice: list of DateTime to be simulated (separated by the simulation time gap)
    :type my_simu_slice: list()
    :param datetime_start_data: datetime of the first data in the meteorological files (used in file name)
    :type datetime_start_data: Datetime.Datetime
    :param datetime_end_data: datetime of the last data in the meteorological files (used in file name)
    :type datetime_end_data: Datetime.Datetime
    :param input_folder: path to the input folder where to find the meteorological files
    :type input_folder: str()
    :return: dictionary containing the nested dictionaries
        { key = link: value = nested_dictionary(index=datetime,column=meteo_variables) }
    :rtype: dict
    """
    logger = logging.getLogger('SingleRun.main')
    # Read the meteorological input files
    logger.info("> Reading meteorological files.")
    dict__nd_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)
    for link in my__network.links:
        dict__nd_meteo[link] = sF.get_nd_meteo_data_from_file(my__network.name, link, my__time_frame,
                                                              my_data_slice, my_simu_slice,
                                                              datetime_start_data, datetime_end_data, input_folder)

    return dict__nd_meteo


def get_contaminant_input_from_file(my__network, my__time_frame, my_data_slice, my_simu_slice,
                                    input_folder, specifications_folder):
    """
    This function generates a nested dictionary for each link and stores them in a single dictionary that is returned.
    Each nested dictionary has the dimension of the simulation time slice times the number of contaminant inputs.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param my_data_slice: list of DateTime corresponding to the simulation slice (separated by the data time gap)
    :type my_data_slice: list()
    :param my_simu_slice: list of DateTime to be simulated (separated by the simulation time gap)
    :type my_simu_slice: list()
    :param input_folder: path to the input folder where to find the loadings file and the applications file
    :type input_folder: str()
    :param specifications_folder: path to the specification folder where to find the distributions file
    :type specifications_folder: str()
    :return: dictionary containing the nested dictionaries
        { key = link: value = nested_dictionary(index=datetime,column=contaminant_inputs) }
    :rtype: dict
    """
    logger = logging.getLogger('SingleRun.main')
    # Read the annual loadings file and the application files to distribute the loadings for each time step
    logger.info("> Reading loadings files.")
    dict__nd_loadings = dict()
    dict_annual_loads = sF.get_nd_from_file(my__network, input_folder, extension='loadings', var_type=float)
    dict_applications = sF.get_nd_from_file(my__network, input_folder, extension='applications', var_type=str)
    nd_distributions = sF.get_nd_distributions_from_file(specifications_folder)
    for link in my__network.links:
        dict__nd_loadings[link] = sFn.distribute_loadings_across_year(dict_annual_loads, dict_applications,
                                                                      nd_distributions, link,
                                                                      my__time_frame, my_data_slice, my_simu_slice)

    return dict__nd_loadings


def simulate(my__network, my__time_frame, my_simu_slice,
             dict__nd_data, dict__ls_models, dict__nd_meteo, dict__nd_loadings):
    """
    This function runs the simulations for a given catchment (defined by a Network object) and given time period
    (defined by the time slice). For each time step, it first runs the models associated with the links (defined as
    Model objects), then it sums up all of what is arriving at each node.

    N.B. The first time step in the time slice is ignored because it is for the initial or previous conditions that
    are needed for the models to get the previous states of the links.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param my_simu_slice: list of DateTime to be simulated
    :type my_simu_slice: list()
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
    :return: NOTHING, only updates the nested dictionaries for data
    """
    logger = logging.getLogger('SingleRun.main')
    logger.info("> Simulating.")
    my_dict_variables = dict()
    logger_simu = logging.getLogger('SingleRun.simulate')
    for variable in my__network.variables:
        my_dict_variables[variable] = 0.0
    for step in my_simu_slice[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__ls_models[link]:
                model.run(my__network, link, dict__nd_data,
                          dict__nd_meteo, dict__nd_loadings,
                          step, my__time_frame.gap_simu,
                          logger_simu)
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
                if q_h2o > 0.0:
                    dict__nd_data[node][step][variable] = my_dict_variables[variable] / q_h2o
                my_dict_variables[variable] = 0.0


def create_simulation_files(my__network, dict__ls_models,
                            catchment, output_folder):
    """
    This function creates a CSV file for each node and for each link and it adds the relevant headers for the
    inputs, the states, and the outputs.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param dict__ls_models: dictionary containing the list of models for each link
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


def update_simulation_files(my__network, my__tf, my_data_slice, my_simu_slice,
                            dict__nd_data, dict__ls_models,
                            catchment, output_folder, report='data_gap', method='raw'):
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
    :param my_data_slice: list of datetime for the period simulated (separated by data time gap)
    :type my_data_slice: list()
    :param my_simu_slice: list of datetime for the period simulated (separated by simulated time gap)
    :type my_simu_slice: list()
    :param dict__nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
        { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
    :type dict__nd_data: dict()
    :param dict__ls_models: dictionary containing the list of models for each link
        { key = link: value = list of Model objects }
    :type dict__ls_models: dict()
    :param catchment: name of the catchment needed to name the simulation files
    :type catchment: str()
    :param output_folder: path to the output folder where to save the simulation files
    :type output_folder: str()
    :param report: choice on the time gap to report simulation variables :
     'simu_gap' = at the simulation gap / 'data_gap' = only at the data gap
    :type report: str()
    :param method: choice on the technique to process simulation variables when reporting time gap > simu time gap :
     'summary' = sums for inputs and averages for the rest / 'raw' = last values only for all
    :type method: str()
    :return: NOTHING, only updates the files in the output folder
    """
    logger = logging.getLogger('SingleRun.main')

    logger.info("> Updating results in files.")

    # Select the relevant list of DateTime given the argument used during function call
    if report == 'data_gap':
        my_list_datetime = my_data_slice  # list of reporting time steps
        simu_steps_per_reporting_step = my__tf.gap_data / my__tf.gap_simu
    elif report == 'simu_gap':
        my_list_datetime = my_simu_slice  # list of reporting time steps
        simu_steps_per_reporting_step = 1
    else:
        raise Exception('Unknown reporting time gap for updating simulations files.')

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
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_list = list()
                    for my_input in my_inputs:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_reporting_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.gap_simu)][my_input])
                        my_list.append('%e' % sum(my_values))
                    my_writer.writerow([step] + my_list)

            with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_list = list()
                    for my_state in my_states:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_reporting_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.gap_simu)][my_state])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

            with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_list = list()
                    for my_output in my_outputs:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_reporting_step, -1):
                            my_values.append(
                                dict__nd_data[link][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.gap_simu)][my_output])
                        my_list.append('%e' % (sum(my_values) / len(my_values)))
                    my_writer.writerow([step] + my_list)

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_list = list()
                    for my_variable in my__network.variables:
                        my_values = list()
                        for my_sub_step in xrange(0, -simu_steps_per_reporting_step, -1):
                            my_values.append(
                                dict__nd_data[node][
                                    step + datetime.timedelta(minutes=my_sub_step * my__tf.gap_simu)][my_variable])
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
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_input]
                                                 for my_input in my_inputs])
            with open('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_state]
                                                 for my_state in my_states])
            with open('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[link][step][my_output]
                                                 for my_output in my_outputs])

        # Save the Nested Dicts for the nodes
        for node in my__network.nodes:
            with open('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node), 'ab') as my_file:
                my_writer = csv.writer(my_file, delimiter=',')
                for step in my_list_datetime[1:]:
                    my_writer.writerow([step] + ['%e' % dict__nd_data[node][step][my_variable]
                                                 for my_variable in my__network.variables])

    else:
        raise Exception("Unknown method for updating simulations files.")


if __name__ == "__main__":
    # Collect the arguments of the program call
    parser = argparse.ArgumentParser(description="simulate hydrology and water quality "
                                                 "for one catchment and one time period")
    parser.add_argument('catchment', type=str,
                        help="name of the catchment")
    parser.add_argument('outlet', type=str,
                        help="european code of the catchment outlet [format IE_XX_##X######]")
    parser.add_argument('-s', '--slice_up', type=int, default=0,
                        help="length of simulation period slice-up in time steps")
    parser.add_argument('-w', '--warm_up', type=int, default=0,
                        help="warm-up duration in days")
    parser.add_argument('-u', '--add_up', dest='add_up', action='store_true',
                        help="add the catchment run-off to its upstream node ")
    parser.add_argument('-d', '--add_down', dest='add_up', action='store_false',
                        help="add the catchment run-off to its downstream node ")
    parser.set_defaults(add_up=True)

    args = parser.parse_args()

    # Run the main() function
    main(args.catchment.capitalize(), args.outlet.upper(), args.slice_up, args.warm_up, args.add_up,
         is_single_run=True)
