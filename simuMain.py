import os
import logging
from pandas import DataFrame

from simuClasses import *
import simuFiles as sF
import simuFunctions as sFn


def main():

    # User-defined parameters
    catchment = "Morell"
    outlet = "IE_EA_09M010300"

    my_simu_start = (2007, 1, 1, 9, 0, 0)
    my_simu_end = (2007, 1, 10, 9, 0, 0)
    time_step_in_minutes = 1440.0

    # Location of the different needed folders
    root = os.path.realpath('..')  # move to parent directory of this current python file
    os.chdir(root)  # define parent directory as root in order to use only relative paths after this
    specifications_folder = "specs/"
    input_folder = "in/"
    output_folder = "out/"

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

    # Convert all time information in datetime format, and create a TimeFrame object
    datetime_start = datetime.datetime(my_simu_start[0], my_simu_start[1], my_simu_start[2],
                                       my_simu_start[3], my_simu_start[4], my_simu_start[5])
    datetime_end = datetime.datetime(my_simu_end[0], my_simu_end[1], my_simu_end[2],
                                     my_simu_end[3], my_simu_end[4], my_simu_end[5])
    time_steps = TimeFrame(datetime_start, datetime_end, int(time_step_in_minutes)).get_list_datetime()

    # Declare all the dictionaries that will be needed, all using the waterbody code as a key
    dict__models = dict()  # key: waterbody, value: list of model objects
    dict_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)
    dict_storage = dict()  # key: waterbody, value: data frame (x: time step, y: data type)

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder)

    # Initiate everything needed for the nodes
    my_variables = ["q_h2o", "c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]
    for node in my__network.nodes:
        dict_storage[node] = DataFrame(index=time_steps, columns=my_variables).fillna(0.0)  # filled with zeros

    # Initiate everything needed for the links (Model objects, DataFrame objects)
    # And collect meteorological data for the links (Meteo dictionary)
    for link in my__network.links:
        # Declare Model objects and get meteo DataFrame
        if my__network.categories[link] == "11":  # river headwater
            dict__models[link] = [Model("CATCHMENT", "SMART", specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "10":  # river
            dict__models[link] = [Model("CATCHMENT", "SMART", specifications_folder),
                                  Model("RIVER", "LINRES", specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "20":  # lake
            dict__models[link] = [Model("LAKE", "BATHTUB", specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            sys.exit("Waterbody {}: {} is not a registered type of waterbody.".format(link,
                                                                                      my__network.categories[link]))
        # Declare DataFrame objects
        my_headers = list()
        for model in dict__models[link]:
            my_headers += model.input_names + model.state_names + model.output_names
        dict_storage[link] = DataFrame(index=time_steps, columns=my_headers).fillna(0.0)  # filled with zeros

    # Read the parameters, or read the descriptors file and generate the parameters
    if os.path.isfile('{}{}_{}.parameters'.format(input_folder, catchment, outlet)):
        dict_param = sF.get_dict_parameters_from_file(catchment, outlet, my__network, dict__models, input_folder)
        dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, input_folder)
    elif os.path.isfile('{}{}_{}.descriptors'.format(input_folder, catchment, outlet)):
        dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, input_folder)
        dict_param = sFn.infer_parameters_from_descriptors(my__network, dict_desc, logger)
        df_param = DataFrame.from_dict(dict_param, orient='index')
        df_param.to_csv('{}{}_{}.parameters'.format(output_folder, catchment.capitalize(), outlet))
    else:
        sys.exit("Parameters are not available from files.")

    # Read in loadings file
    dict_annual_loads = sF.get_dict_floats_from_file("loadings", catchment, outlet, my__network, input_folder)
    dict_applications = sF.get_dict_strings_from_file("applications", catchment, outlet, my__network, input_folder)
    dict_loadings = sFn.distribute_loadings_across_year(my__network, dict_annual_loads, dict_applications,
                                                        time_steps, specifications_folder)

    # Read the constants in .const file
    dict_const = dict()
    dict_const["SMART"] = sF.get_dict_constants_from_file("SMART", specifications_folder)

    # Initial for reservoirs
    # # TO BE DEFINED

    # Run the simulation
    my_dict_variables = dict()
    for variable in my_variables:
        my_dict_variables[variable] = 0.0

    for step in time_steps[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__models[link]:
                model.run(my__network, link, dict_storage,
                          dict_desc, dict_param, dict_const, dict_meteo, dict_loadings,
                          step, time_step_in_minutes,
                          logger)
        # Sum up everything coming from upstream for each node
        for node in my__network.nodes:
            if my__network.additions.get(node):  # ignore the node up for headwaters
                for variable in ["q_h2o"]:
                    for link in my__network.additions[node]:
                        if my__network.categories[link] == "11":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "c_out_" + variable]
                        elif my__network.categories[link] == "10":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "r_out_" + variable]
                            my_dict_variables[variable] += dict_storage[link].loc[step, "c_out_" + variable]
                        elif my__network.categories[link] == "20":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "l_out_" + variable]
                    dict_storage[node].set_value(step, variable,
                                                 my_dict_variables[variable])
                    my_dict_variables[variable] = 0.0
                for variable in ["c_no3", "c_nh4", "c_dph", "c_pph", "c_sed"]:
                    for link in my__network.additions[node]:
                        if my__network.categories[link] == "11":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "c_out_" + variable] * \
                                dict_storage[link].loc[step, "c_out_q_h2o"]
                        elif my__network.categories[link] == "10":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "r_out_" + variable] * \
                                dict_storage[link].loc[step, "r_out_q_h2o"]
                            my_dict_variables[variable] += dict_storage[link].loc[step, "c_out_" + variable] * \
                                dict_storage[link].loc[step, "c_out_q_h2o"]
                        elif my__network.categories[link] == "20":
                            my_dict_variables[variable] += dict_storage[link].loc[step, "l_out_" + variable] * \
                                dict_storage[link].loc[step, "l_out_q_h2o"]
                    if my_dict_variables["q_h2o"] > 0.0:
                        dict_storage[node].set_value(step, variable,
                                                     my_dict_variables[variable] / my_dict_variables["q_h2o"])
                    my_dict_variables[variable] = 0.0

    for link in my__network.links:
        my_inputs = list()
        my_states = list()
        my_outputs = list()
        for model in dict__models[link]:
            my_inputs += model.input_names
            my_states += model.state_names
            my_outputs += model.output_names
        dict_storage[link].to_csv('{}{}_{}.inputs'.format(output_folder, catchment.capitalize(), link),
                                  columns=my_inputs, float_format='%e')
        dict_storage[link].to_csv('{}{}_{}.states'.format(output_folder, catchment.capitalize(), link),
                                  columns=my_states, float_format='%e')
        dict_storage[link].to_csv('{}{}_{}.outputs'.format(output_folder, catchment.capitalize(), link),
                                  columns=my_outputs, float_format='%e')
    for node in my__network.nodes:
        dict_storage[node].to_csv('{}{}_{}.node'.format(output_folder, catchment.capitalize(), node),
                                  float_format='%e')


if __name__ == "__main__":
    main()
