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
    # # Logger levels: debug < info < warning < error < critical
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create a file handler
    if os.path.isfile('{}{}_{}.simu.log'.format(output_folder, catchment, outlet)):
        os.remove('{}{}_{}.simu.log'.format(output_folder, catchment, outlet))
    handler = logging.FileHandler('{}{}_{}.simu.log'.format(output_folder, catchment, outlet))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}.simulation".format(input_folder, catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()
        logger.info("There is not {}{}_{}.simulation available.".format(input_folder, catchment, outlet))

    try:
        question_start_data = my_answers_df.loc['start_datetime_data', 'ANSWER']
    except KeyError:
        question_start_data = raw_input('Starting date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_end_data = my_answers_df.loc['end_datetime_data', 'ANSWER']
    except KeyError:
        question_end_data = raw_input('Ending date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_start_simu = my_answers_df.loc['start_datetime_simu', 'ANSWER']
    except KeyError:
        question_start_simu = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_simu = datetime.datetime.strptime(question_start_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_end_simu = my_answers_df.loc['end_datetime_simu', 'ANSWER']
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_data_time_step = my_answers_df.loc['data_time_step_min', 'ANSWER']
    except KeyError:
        question_data_time_step = raw_input('Time step for data? [integer in minutes] ')
    try:
        data_time_step_in_min = float(int(question_data_time_step))
    except ValueError:
        sys.exit("The data time step is invalid. [not an integer]")

    try:
        question_simu_time_step = my_answers_df.loc['simu_time_step_min', 'ANSWER']
    except KeyError:
        question_simu_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        simu_time_step_in_min = float(int(question_simu_time_step))
    except ValueError:
        sys.exit("The simulation time step is invalid. [not an integer]")

    try:
        question_warm_up_duration = my_answers_df.loc['warm_up_days', 'ANSWER']
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

    # Create a TimeFrame object
    my__time_frame = TimeFrame(datetime_start_simu, datetime_end_simu,
                               int(data_time_step_in_min), int(simu_time_step_in_min))
    my__time_frame_warm_up = TimeFrame(my__time_frame.start, my__time_frame.start +
                                       datetime.timedelta(days=warm_up_in_days - 1),
                                       int(data_time_step_in_min), int(simu_time_step_in_min))

    # Declare all the dictionaries that will be needed, all using the waterbody code as a key
    dict__models = dict()  # key: waterbody, value: list of model objects
    dict__data_frames = dict()  # key: waterbody, value: data frame (x: time step, y: data type)
    dict__data_frames_warm_up = dict()

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, specifications_folder)

    # Create DataFrames for the nodes
    for node in my__network.nodes:
        dict__data_frames[node] = \
            DataFrame(index=my__time_frame.series_simu, columns=my__network.variables).fillna(0.0)
        if not warm_up_in_days == 0.0:
            dict__data_frames_warm_up[node] = \
                DataFrame(index=my__time_frame_warm_up.series_simu, columns=my__network.variables).fillna(0.0)

    # Create Models and DataFrames for the links
    for link in my__network.links:
        # Declare Model objects
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

        # Create DataFrames for the links
        my_headers = list()
        for model in dict__models[link]:
            my_headers += model.input_names + model.state_names + model.output_names
        dict__data_frames[link] = DataFrame(index=my__time_frame.series_simu, columns=my_headers).fillna(0.0)
        if not warm_up_in_days == 0.0:
            dict__data_frames_warm_up[link] = DataFrame(index=my__time_frame_warm_up.series_simu,
                                                        columns=my_headers).fillna(0.0)

    # Read the parameters file, or read the descriptors file, generate the parameters, and generate the parameters file
    logger.info("{} # Parameterising.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, input_folder)
    dict_param = dict()
    my_dict_for_file = dict()
    for link in my__network.links:
        dict_param[link] = dict()
        for models in dict__models[link]:
            for model_name in models.identifier.split('_'):
                # For parameters
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
    dict_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)
    for link in my__network.links:
        dict_meteo[link] = sF.get_df_for_daily_meteo_data(catchment, link, my__time_frame,
                                                          datetime_start_data, datetime_end_data, input_folder)

    # Read the annual loadings file and the application files to distribute the loadings for each time step
    logger.info("{} # Reading loadings files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    dict_loadings = dict()
    dict_annual_loads = sF.get_dict_floats_from_file("loadings", catchment, outlet, my__network, input_folder)
    dict_applications = sF.get_dict_strings_from_file("applications", catchment, outlet, my__network, input_folder)
    df_distributions = sF.get_df_distributions_from_file(specifications_folder)
    for link in my__network.links:
        dict_loadings[link] = sFn.distribute_loadings_across_year(dict_annual_loads, dict_applications,
                                                                  df_distributions, link, my__time_frame)

    # Set the initial conditions ('blank' warm up run)
    if not warm_up_in_days == 0.0:
        logger.info("{} # Determining initial conditions.".format(datetime.datetime.now().strftime('%d/%m/%Y '
                                                                                                   '%H:%M:%S')))
        simulate(my__network, my__time_frame_warm_up,
                 dict__data_frames_warm_up, dict__models,
                 dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
                 logger)

        for link in my__network.links:  # set last values of warm up as initial conditions for actual simulation
            dict__data_frames[link].iloc[0] = dict__data_frames_warm_up[link].iloc[-1]

        with open('{}{}_{}.log'.format(output_folder, catchment, outlet), 'w'):
            # empty the log file because lines in it only due to warm up run
            pass

    # Simulate
    logger.info("{} # Simulating.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    simulate(my__network, my__time_frame,
             dict__data_frames, dict__models,
             dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
             logger)

    # Save the DataFrames for the links and nodes (separating inputs, states, and outputs)
    save_simulation_files(my__network, my__time_frame, catchment,
                          dict__data_frames, dict__models, output_folder, logger)

    # Generate gauged flow file in output folder (could be identical to input file if date ranges identical)
    sF.get_df_for_daily_flow_data(
        catchment, outlet, my__time_frame,
        datetime_start_data, datetime_end_data, input_folder).to_csv('{}{}_{}.flow'.format(output_folder,
                                                                                           catchment.capitalize(),
                                                                                           outlet),
                                                                     header='FLOW',
                                                                     float_format='%e',
                                                                     index_label='DateTime')

    logger.info("{} # Ending.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))


def simulate(my__network, my__time_frame,
             dict__data_frames, dict__models,
             dict_meteo, dict_loadings, dict_desc, dict_param, dict_const,
             logger):
    my_dict_variables = dict()
    for variable in my__network.variables:
        my_dict_variables[variable] = 0.0
    for step in my__time_frame.series_simu[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__models[link]:
                model.run(my__network, link, dict__data_frames,
                          dict_desc, dict_param, dict_const, dict_meteo, dict_loadings,
                          step, my__time_frame.step_simu,
                          logger)
        # Sum up everything coming from upstream for each node
        for node in my__network.nodes:
            # Sum up the flows
            for variable in ["q_h2o"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "r_out_" + variable)
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "r_out_" + variable)
                    elif my__network.categories[link] == "20":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "l_out_" + variable)
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "c_out_" + variable)
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "c_out_" + variable)
                dict__data_frames[node].set_value(step, variable,
                                                  my_dict_variables[variable])
                my_dict_variables[variable] = 0.0
            # Sum up the contaminants
            for variable in ["c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]:
                for link in my__network.routing.get(node):  # for the streams of the links upstream of the node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "r_out_" + variable) * \
                                                       dict__data_frames[link].get_value(step, "r_out_q_h2o")
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "r_out_" + variable) * \
                                                       dict__data_frames[link].get_value(step, "r_out_q_h2o")
                    elif my__network.categories[link] == "20":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "l_out_" + variable) * \
                                                       dict__data_frames[link].get_value(step, "l_out_q_h2o")
                for link in my__network.adding.get(node):  # for the catchment of the link downstream of this node
                    if my__network.categories[link] == "11":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "c_out_" + variable) * \
                                                       dict__data_frames[link].get_value(step, "c_out_q_h2o")
                    elif my__network.categories[link] == "10":
                        my_dict_variables[variable] += dict__data_frames[link].get_value(step, "c_out_" + variable) * \
                                                       dict__data_frames[link].get_value(step, "c_out_q_h2o")
                if my_dict_variables["q_h2o"] > 0.0:
                    dict__data_frames[node].set_value(step, variable,
                                                      my_dict_variables[variable] / my_dict_variables["q_h2o"])
                my_dict_variables[variable] = 0.0


def save_simulation_files(my__network, my__time_frame, catchment,
                          dict__data_frames, dict__models, output_folder, logger):
    # Save the DataFrames for the links (separating inputs, states, and outputs)
    logger.info("{} # Saving results in files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
    for link in my__network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()
        for model in dict__models[link]:
            my_inputs += model.input_names
            my_states += model.state_names
            my_outputs += model.output_names
        dict__data_frames[link].loc[my__time_frame.series_data[1:]].to_csv(
            '{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link),
            columns=my_inputs, float_format='%e', index_label='DateTime')
        dict__data_frames[link].loc[my__time_frame.series_data[1:]].to_csv(
            '{}{}_{}.states'.format(output_folder, catchment.capitalize(), link),
            columns=my_states, float_format='%e', index_label='DateTime')
        dict__data_frames[link].loc[my__time_frame.series_data[1:]].to_csv(
            '{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link),
            columns=my_outputs, float_format='%e', index_label='DateTime')

    # Save the DataFrames for the nodes
    for node in my__network.nodes:
        dict__data_frames[node].loc[my__time_frame.series_data[1:]].to_csv(
            '{}{}_{}.node'.format(output_folder, catchment.capitalize(), node),
            float_format='%e', index_label='DateTime')


if __name__ == "__main__":
    main()
