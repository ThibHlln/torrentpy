import logging
import imp
from pandas import DataFrame
from itertools import izip
import argparse
from glob import glob

from CSFclasses import *
import CSFinout as csfC
import CSFfunctions as csfF


def main(catchment, outlet, slice_length, warm_up_in_days, root, in_fmt="csv", out_fmt="csv", is_single_run=False):
    # Format catchment and outlet names
    catchment = catchment.capitalize()
    outlet = outlet.upper()

    # Location of the different needed directories
    spec_directory = ''.join([root, "/scripts/specs/"])
    input_directory = ''.join([root, "/in/"])
    output_directory = ''.join([root, "/out/"])

    # Check if combination catchment/outlet is coherent by using the name of the input folder
    if not os.path.exists("{}{}_{}".format(input_directory, catchment, outlet)):
        raise Exception("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Set up the simulation (either with .simulation file or through the console)
    data_time_gap_in_min, data_datetime_start, data_datetime_end, \
        simu_time_gap_in_min, simu_datetime_start, simu_datetime_end, water_quality = \
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

    logger.warning("Starting simulation for {} {} [Slice-Up: {}, Warm-Up: {}].".format(
        catchment, outlet, slice_length, warm_up_in_days,))

    # Store information about arguments used to call the run
    my_df_info = pandas.DataFrame.from_dict(
        {'SliceUp': slice_length, 'WarmUp': warm_up_in_days}, orient='index')
    my_df_info.index.name = "Information"
    my_df_info.columns = ["Value"]
    my_df_info.to_csv('{}{}_{}.information'.format(output_folder, catchment, outlet), sep=',')

    logger.info("Initialising.")

    # Clean up the output folder for the desired file extensions
    for my_extension in [".information", ".parameters", ".node*", ".inputs*", ".outputs*", ".states*"]:
        my_files = glob("{}{}*{}".format(output_folder, catchment, my_extension))
        for my_file in my_files:
            os.remove(my_file)

    # Create a TimeFrame object for simulation run and warm-up run
    my__time_frame = TimeFrame(simu_datetime_start, simu_datetime_end,
                               int(data_time_gap_in_min), int(simu_time_gap_in_min), slice_length)
    my__time_frame_warm_up = TimeFrame(my__time_frame.start, my__time_frame.start +
                                       datetime.timedelta(days=warm_up_in_days - 1),
                                       int(data_time_gap_in_min), int(simu_time_gap_in_min), slice_length)

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, spec_directory, wq=water_quality)

    # Create Models for the links
    dict__ls_models, dict__c_models, dict__r_models, dict__l_models = \
        csfF.generate_models_for_links(my__network, spec_directory, input_folder, output_folder)

    # Create files to store simulation results
    csfC.create_simulation_files(my__network, dict__ls_models, catchment, out_fmt, output_folder)

    # Set the initial conditions ('blank' warm up run slice by slice) if required
    my_last_lines = dict()
    if not warm_up_in_days == 0:  # Warm-up run required
        logger.info("Determining initial conditions.")
        # Get meteo input data
        dict__nd_meteo = csfF.get_meteo_input_for_links(my__network, my__time_frame_warm_up,
                                                        my__time_frame_warm_up.series_data,
                                                        my__time_frame_warm_up.series_simu,
                                                        data_datetime_start, data_datetime_end,
                                                        in_fmt, input_folder)
        # Initialise dicts needed to link time slices together (use last time step of one as first for the other)
        for link in my__network.links:
            # For links, get a dict of the models states initial conditions from "educated guesses"
            my_last_lines[link] = dict()
            for model in dict__ls_models[link]:
                my_last_lines[link].update(model.initialise(my__network))
        for node in my__network.nodes:
            # For nodes, no states so no initial conditions, but instantiation of dict required
            my_last_lines[node] = dict()

        for my_simu_slice, my_data_slice in izip(my__time_frame_warm_up.slices_simu,
                                                 my__time_frame_warm_up.slices_data):
            logger.info("Running Warm-Up Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                                 my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
            # Initialise data structures
            dict__nd_data = csfF.generate_data_structures_for_links_and_nodes(my__network,
                                                                              my_simu_slice,
                                                                              dict__ls_models)

            # Get history of previous time slice last time step for initial conditions of current time slice
            for link in my__network.links:
                dict__nd_data[link][my_simu_slice[0]].update(my_last_lines[link])
            for node in my__network.nodes:
                dict__nd_data[node][my_simu_slice[0]].update(my_last_lines[node])

            # Get other input data
            dict__nd_loadings = \
                csfF.get_contaminant_input_for_links(my__network, my__time_frame_warm_up,
                                                     my_data_slice, my_simu_slice,
                                                     input_folder, spec_directory) if water_quality else {}

            # Simulate
            simulate(my__network, my__time_frame_warm_up, my_simu_slice,
                     dict__nd_data, dict__nd_meteo, dict__nd_loadings,
                     dict__c_models, dict__r_models, dict__l_models
                     )

            # Save history (last time step) for next slice
            for link in my__network.links:
                my_last_lines[link].update(dict__nd_data[link][my_simu_slice[-1]])
            for node in my__network.nodes:
                my_last_lines[node].update(dict__nd_data[node][my_simu_slice[-1]])

            # Garbage collection
            del dict__nd_data
            del dict__nd_loadings
    else:  # Warm-up run not required
        # Initialise dicts needed to link time slices together (use last time step of one as first for the other)
        for link in my__network.links:
            # For links, get a dict of the models states initial conditions from "educated guesses"
            my_last_lines[link] = dict()
            for model in dict__ls_models[link]:
                my_last_lines[link].update(model.initialise(my__network))
        for node in my__network.nodes:
            # For nodes, no states so no initial conditions, but instantiation of dict required
            my_last_lines[node] = dict()

    # Simulate (run slice by slice)
    logger.info("Starting the simulation.")
    # Get meteo input data
    dict__nd_meteo = csfF.get_meteo_input_for_links(my__network, my__time_frame,
                                                    my__time_frame.series_data, my__time_frame.series_simu,
                                                    data_datetime_start, data_datetime_end,
                                                    in_fmt, input_folder)
    for my_simu_slice, my_data_slice in izip(my__time_frame.slices_simu,
                                             my__time_frame.slices_data):

        logger.info("Running Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                     my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
        # Initialise data structures
        dict__nd_data = csfF.generate_data_structures_for_links_and_nodes(my__network,
                                                                          my_simu_slice,
                                                                          dict__ls_models)

        # Get history of previous time step for initial conditions of current time step
        for link in my__network.links:
            dict__nd_data[link][my_simu_slice[0]].update(my_last_lines[link])
        for node in my__network.nodes:
            dict__nd_data[node][my_simu_slice[0]].update(my_last_lines[node])

        # Get other input data
        dict__nd_loadings = csfF.get_contaminant_input_for_links(my__network, my__time_frame,
                                                                 my_data_slice, my_simu_slice,
                                                                 input_folder, spec_directory) if water_quality else {}

        # Simulate
        simulate(my__network, my__time_frame, my_simu_slice,
                 dict__nd_data, dict__nd_meteo, dict__nd_loadings,
                 dict__c_models, dict__r_models, dict__l_models
                 )

        # Write results in files
        csfC.update_simulation_files(my__network, my__time_frame, my_data_slice, my_simu_slice,
                                     dict__nd_data, dict__ls_models,
                                     catchment, out_fmt, output_folder, report='data_gap', method='summary')

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
    the console (except for water_quality that takes False as default, if not specified).

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
        water_quality: boolean for decision on water quality simulations (True for on, False for off)
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
        raise Exception(
            "The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_end_simu = my_answers_df.get_value('simu_end_datetime', 'ANSWER')
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception(
            "The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

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

    try:
        question_water_quality = my_answers_df.get_value('water_quality', 'ANSWER')
    except KeyError:
        question_water_quality = "off"  # default setting
    if question_water_quality == "on" or question_water_quality == "off":
        water_quality = True if question_water_quality == "on" else False
    else:
        raise Exception("The water quality choice is invalid. [not \'on\' nor \'off\']")

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
        # guarantees that both of the following statements are true:
        # i)  data_gap >= simu_gap
        # ii) data_gap is a multiple of simu_gap
        raise Exception("The data time gap is not a multiple of the simulation time gap.")

    return data_time_gap_in_min, datetime_start_data, datetime_end_data, \
        simu_time_gap_in_min, datetime_start_simu, datetime_end_simu, water_quality


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


def simulate(my__network, my__time_frame, my_simu_slice,
             dict__nd_data, dict__nd_meteo, dict__nd_loadings,
             dict__c_models, dict__r_models, dict__l_models):
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
    :param dict__nd_meteo: dictionary containing the nested dictionaries for the links for meteorological inputs
        { key = link: value = nested_dictionary(index=datetime,column=meteo_input) }
    :type dict__nd_meteo: dict
    :param dict__nd_loadings: dictionary containing the nested dictionaries for the links for contaminant inputs
        { key = link: value = nested_dictionary(index=datetime,column=contaminant_input) }
    :type dict__nd_loadings: dict
    :param dict__c_models: dictionary containing the catchment models for each link
        { key = link: value = Model objects }
    :type dict__c_models: dict
    :param dict__r_models: dictionary containing the river models for each link
        { key = link: value = Model objects }
    :type dict__r_models: dict
    :param dict__l_models: dictionary containing the lake models for each link
        { key = link: value = Model objects }
    :type dict__l_models: dict
    :return: NOTHING, only updates the nested dictionaries for data
    """
    logger = logging.getLogger('SingleRun.main')
    logger.info("> Simulating.")
    my_dict_variables = dict()
    logger_simu = logging.getLogger('SingleRun.simulate')
    for variable in my__network.variables:
        my_dict_variables[variable] = 0.0
    for step in my_simu_slice[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate water (and contaminant) runoff from catchment for each link
        for link in my__network.links:
            if link in dict__c_models:
                dict__c_models[link].run(my__network, link, dict__nd_data,
                                         dict__nd_meteo, dict__nd_loadings,
                                         step, my__time_frame.gap_simu,
                                         logger_simu)
        # Sum up everything coming towards each node
        delta = datetime.timedelta(minutes=my__time_frame.gap_simu)
        for node in my__network.nodes:
            # Sum up outputs for hydrology
            q_h2o = 0.0
            for variable in ["q_h2o"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step - delta]["".join(["r_out_", variable])]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step - delta]["".join(["r_out_", variable])]
                    elif my__network.categories[link] == "20":  # lake
                        my_dict_variables[variable] += dict__nd_data[link][step - delta]["".join(["l_out_", variable])]
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":  # headwater river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])]
                    elif my__network.categories[link] == "10":  # river
                        my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])]
                q_h2o += my_dict_variables[variable]
                dict__nd_data[node][step - delta][variable] = my_dict_variables[variable]
                my_dict_variables[variable] = 0.0
            # Sum up outputs for water quality
            if my__network.waterQuality:
                for variable in ["c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]:
                    for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                        if my__network.categories[link] == "11":  # headwater river
                            my_dict_variables[variable] += \
                                dict__nd_data[link][step - delta]["".join(["r_out_", variable])] * \
                                dict__nd_data[link][step - delta]["r_out_q_h2o"]
                        elif my__network.categories[link] == "10":  # river
                            my_dict_variables[variable] += \
                                dict__nd_data[link][step - delta]["".join(["r_out_", variable])] * \
                                dict__nd_data[link][step - delta]["r_out_q_h2o"]
                        elif my__network.categories[link] == "20":  # lake
                            my_dict_variables[variable] += \
                                dict__nd_data[link][step - delta]["".join(["l_out_", variable])] * \
                                dict__nd_data[link][step - delta]["l_out_q_h2o"]
                    for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                        if my__network.categories[link] == "11":  # headwater river
                            my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])] * \
                                                           dict__nd_data[link][step]["c_out_q_h2o"]
                        elif my__network.categories[link] == "10":  # river
                            my_dict_variables[variable] += dict__nd_data[link][step]["".join(["c_out_", variable])] * \
                                                           dict__nd_data[link][step]["c_out_q_h2o"]
                    if q_h2o > 0.0:
                        dict__nd_data[node][step - delta][variable] = my_dict_variables[variable] / q_h2o
                    my_dict_variables[variable] = 0.0
        # Calculate water (and contaminant) routing in river reach for each link
        for link in my__network.links:
            if link in dict__r_models:
                dict__r_models[link].run(my__network, link, dict__nd_data,
                                         dict__nd_meteo, dict__nd_loadings,
                                         step, my__time_frame.gap_simu,
                                         logger_simu)
        # Calculate water (and contaminant) routing in lake for each link
        for link in my__network.links:
            if link in dict__l_models:
                dict__l_models[link].run(my__network, link, dict__nd_data,
                                         dict__nd_meteo, dict__nd_loadings,
                                         step, my__time_frame.gap_simu,
                                         logger_simu)

    # Sum up everything that was routed towards each node at penultimate time step
    step = my_simu_slice[-1]
    for node in my__network.nodes:
        # Sum up outputs for hydrology
        q_h2o = 0.0
        for variable in ["q_h2o"]:
            for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                if my__network.categories[link] == "11":  # headwater river
                    my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])]
                elif my__network.categories[link] == "10":  # river
                    my_dict_variables[variable] += dict__nd_data[link][step]["".join(["r_out_", variable])]
                elif my__network.categories[link] == "20":  # lake
                    my_dict_variables[variable] += dict__nd_data[link][step]["".join(["l_out_", variable])]
            q_h2o += my_dict_variables[variable]
            dict__nd_data[node][step][variable] = my_dict_variables[variable]
            my_dict_variables[variable] = 0.0
        # Sum up output for water quality
        if my__network.waterQuality:
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
                if q_h2o > 0.0:
                    dict__nd_data[node][step][variable] = my_dict_variables[variable] / q_h2o
                my_dict_variables[variable] = 0.0


def valid_file_format(fmt):
    if fmt.lower() == "netcdf":
        try:
            imp.find_module('netCDF4')
            return "netcdf"
        except ImportError:
            raise argparse.ArgumentTypeError("NetCDF4 module is not installed, please choose another file format.")
    elif fmt.lower() == "csv":
        try:
            imp.find_module('csv')
            return "csv"
        except ImportError:
            raise argparse.ArgumentTypeError("CSV module is not installed, please choose another file format.")
    else:
        raise argparse.ArgumentTypeError("File format not recognised: '{0}'.".format(fmt))


if __name__ == "__main__":
    # Define the root of the CSF
    csf_root = os.path.realpath('..')  # move to parent directory of this current python file

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
    parser.add_argument('-i', '--in_format', type=valid_file_format, default='csv',
                        help="format of input data files [csv or netcdf]")
    parser.add_argument('-o', '--out_format', type=valid_file_format, default='csv',
                        help="format of output data files [csv or netcdf]")

    args = parser.parse_args()

    # Run the main() function
    main(args.catchment, args.outlet, args.slice_up, args.warm_up, csf_root,
         in_fmt=args.in_format, out_fmt=args.out_format, is_single_run=True)
