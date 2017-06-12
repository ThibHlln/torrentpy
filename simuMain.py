import os
import logging
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

    question_catch = raw_input('European Code (EU_CD) of the catchment? [format IE_XX_##X######] ')
    outlet = question_catch.upper()

    if not os.path.isfile('{}{}_{}.network'.format(input_folder, catchment, outlet)):
        # Check if combination catchment/outlet is coherent by using the name of the network file
        sys.exit("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    question_start = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start = datetime.datetime.strptime(question_start, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    question_end = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end = datetime.datetime.strptime(question_end, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    question_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        time_step_in_minutes = float(int(question_time_step))
    except ValueError:
        sys.exit("The time step is invalid. [not an integer]")

    question_warm_up_duration = raw_input('Warm-up duration? [integer in days] ')
    try:
        warm_up_in_days = float(int(question_warm_up_duration))
    except ValueError:
        sys.exit("The time step is invalid. [not an integer]")

    # Create a logger
    # # Logger levels: debug < info < warning < error < critical
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create a file handler
    if os.path.isfile('{}{}_{}.log'.format(output_folder, catchment, outlet)):
        os.remove('{}{}_{}.log'.format(output_folder, catchment, outlet))
    handler = logging.FileHandler('{}{}_{}.log'.format(output_folder, catchment, outlet))
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)

    # Create a TimeFrame object
    my__time_frame = TimeFrame(datetime_start, datetime_end, int(time_step_in_minutes))
    my__time_frame_warm_up = TimeFrame(my__time_frame.start, my__time_frame.start +
                                       datetime.timedelta(days=warm_up_in_days - 1), int(time_step_in_minutes))

    # Declare all the dictionaries that will be needed, all using the waterbody code as a key
    dict__models = dict()  # key: waterbody, value: list of model objects
    dict__data_frames = dict()  # key: waterbody, value: data frame (x: time step, y: data type)
    dict__data_frames_warm_up = dict()

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, specifications_folder)

    # Create DataFrames for the nodes
    for node in my__network.nodes:
        dict__data_frames[node] = \
            DataFrame(index=my__time_frame.series, columns=my__network.variables).fillna(0.0)
        dict__data_frames_warm_up[node] = \
            DataFrame(index=my__time_frame_warm_up.series, columns=my__network.variables).fillna(0.0)

    # Create Models for links
    # Collect meteorological data for the links
    dict_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)
    for link in my__network.links:
        # Declare Model objects and get meteo DataFrame
        if my__network.categories[link] == "11":  # river headwater
            dict__models[link] = [Model("CATCHMENT", "SMART_INCAL", specifications_folder),
                                  Model("RIVER", "LINRES_INCAS", specifications_folder)]
        elif my__network.categories[link] == "10":  # river
            dict__models[link] = [Model("CATCHMENT", "SMART_INCAL", specifications_folder),
                                  Model("RIVER", "LINRES_INCAS", specifications_folder)]
        elif my__network.categories[link] == "20":  # lake
            dict__models[link] = [Model("LAKE", "BATHTUB", specifications_folder)]
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            sys.exit("Waterbody {}: {} is not a registered type of waterbody.".format(link,
                                                                                      my__network.categories[link]))

        dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, my__time_frame.series, input_folder)

        # Create DataFrames for the links
        my_headers = list()
        for model in dict__models[link]:
            my_headers += model.input_names + model.state_names + model.output_names
        dict__data_frames[link] = DataFrame(index=my__time_frame.series, columns=my_headers).fillna(0.0)
        dict__data_frames_warm_up[link] = DataFrame(index=my__time_frame_warm_up.series, columns=my_headers).fillna(0.0)

    # Read the parameters file, or read the descriptors file, generate the parameters, and generate the parameters file
    if os.path.isfile('{}{}_{}.smart.parameters'.format(input_folder, catchment, outlet)):
        dict_param = sF.get_dict_parameters_from_file(catchment, outlet, my__network, dict__models, input_folder)
        dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, input_folder)
    elif os.path.isfile('{}{}_{}.descriptors'.format(input_folder, catchment, outlet)):
        dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, input_folder)
        dict_param = sFn.infer_parameters_from_descriptors(my__network, dict_desc, logger)
        df_param = DataFrame.from_dict(dict_param, orient='index')
        df_param.to_csv('{}{}_{}.smart.parameters'.format(output_folder, catchment.capitalize(), outlet))
    else:
        sys.exit("SMART parameters are not available from files.")

    # Read the annual loadings file and the application files to distribute the loadings for each time step
    dict_annual_loads = sF.get_dict_floats_from_file("loadings", catchment, outlet, my__network, input_folder)
    dict_applications = sF.get_dict_strings_from_file("applications", catchment, outlet, my__network, input_folder)
    dict_loadings = sFn.distribute_loadings_across_year(my__network, dict_annual_loads, dict_applications,
                                                        my__time_frame.series, specifications_folder)

    # Read the constants files
    dict_const = dict()
    dict_const["INCAL"] = sF.get_dict_constants_from_file("INCAL", specifications_folder)

    # Set the initial conditions
    simulate(my__network, my__time_frame_warm_up,
             dict__data_frames_warm_up, dict__models,
             dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
             logger)

    for link in my__network.links:  # set last values of warm up as initial conditions for actual simulation
        dict__data_frames[link].iloc[0] = dict__data_frames_warm_up[link].iloc[-1]

    with open('{}{}_{}.log'.format(output_folder, catchment, outlet), 'w'):  # empty the log file due to warm up
        pass

    # Simulate
    simulate(my__network, my__time_frame,
             dict__data_frames, dict__models,
             dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
             logger)

    # Save the DataFrames for the links (separating inputs, states, and outputs)
    for link in my__network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()
        for model in dict__models[link]:
            my_inputs += model.input_names
            my_states += model.state_names
            my_outputs += model.output_names
        dict__data_frames[link].to_csv('{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link),
                                       columns=my_inputs, float_format='%e', index_label='Date')
        dict__data_frames[link].to_csv('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link),
                                       columns=my_states, float_format='%e', index_label='Date')
        dict__data_frames[link].to_csv('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link),
                                       columns=my_outputs, float_format='%e', index_label='Date')

        dict__data_frames_warm_up[link].to_csv('{}{}_{}.inputs2'.format(output_folder, catchment.capitalize(), link),
                                               columns=my_inputs, float_format='%e', index_label='Date')
        dict__data_frames_warm_up[link].to_csv('{}{}_{}.states2'.format(output_folder, catchment.capitalize(), link),
                                               columns=my_states, float_format='%e', index_label='Date')
        dict__data_frames_warm_up[link].to_csv('{}{}_{}.outputs2'.format(output_folder, catchment.capitalize(), link),
                                               columns=my_outputs, float_format='%e', index_label='Date')

    # Save the DataFrames for the nodes
    for node in my__network.nodes:
        dict__data_frames[node].to_csv('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node),
                                       float_format='%e', index_label='Date')


def simulate(my__network, my__time_frame,
             dict__data_frames, dict__models,
             dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
             logger):
    my_dict_variables = dict()
    for variable in my__network.variables:
        my_dict_variables[variable] = 0.0
    for step in my__time_frame.series[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__models[link]:
                model.run(my__network, link, dict__data_frames,
                          dict_desc, dict_param, dict_const, dict_meteo, dict_loadings,
                          step, my__time_frame.step,
                          logger)
        # Sum up everything coming from upstream for each node
        for node in my__network.nodes:
            # Sum up the flows
            for variable in ["q_h2o"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "r_out_" + variable]
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "r_out_" + variable]
                    elif my__network.categories[link] == "20":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "l_out_" + variable]
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "c_out_" + variable]
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "c_out_" + variable]
                dict__data_frames[node].set_value(step, variable,
                                                  my_dict_variables[variable])
                my_dict_variables[variable] = 0.0
            # Sum up the contaminants
            for variable in ["c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "r_out_" + variable] * \
                                                       dict__data_frames[link].loc[step, "r_out_q_h2o"]
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "r_out_" + variable] * \
                                                       dict__data_frames[link].loc[step, "r_out_q_h2o"]
                    elif my__network.categories[link] == "20":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "l_out_" + variable] * \
                                                       dict__data_frames[link].loc[step, "l_out_q_h2o"]
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "c_out_" + variable] * \
                                                       dict__data_frames[link].loc[step, "c_out_q_h2o"]
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].loc[step, "c_out_" + variable] * \
                                                       dict__data_frames[link].loc[step, "c_out_q_h2o"]
                if my_dict_variables["q_h2o"] > 0.0:
                    dict__data_frames[node].set_value(step, variable,
                                                      my_dict_variables[variable] / my_dict_variables["q_h2o"])
                my_dict_variables[variable] = 0.0


if __name__ == "__main__":
    main()
