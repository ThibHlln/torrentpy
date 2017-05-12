import os
from pandas import DataFrame

from simuClasses import *
import simuFunctions as sF


def main():

    # User-defined parameters
    catchment = "Test"
    outlet = "IE_SE_16A010800"

    root = os.path.realpath('..')
    os.chdir(root)

    model_specifications_folder = "specs/"
    input_folder = "in/"

    my_simu_start = (2011, 1, 1, 9, 0, 0)
    my_simu_end = (2011, 1, 10, 9, 0, 0)

    time_step_in_minutes = 1440

    # Convert all time information in datetime format, and create a TimeFrame object
    datetime_start = datetime.datetime(my_simu_start[0], my_simu_start[1], my_simu_start[2],
                                       my_simu_start[3], my_simu_start[4], my_simu_start[5])
    datetime_end = datetime.datetime(my_simu_end[0], my_simu_end[1], my_simu_end[2],
                                     my_simu_end[3], my_simu_end[4], my_simu_end[5])

    time_steps = TimeFrame(datetime_start, datetime_end, time_step_in_minutes).get_list_datetime()

    # Declare all the dictionaries that will be needed, all using the waterbody code as a key
    dict__model = dict()
    dict_meteo = dict()
    dict_storage = dict()

    # Create a Network object from networkNodesLinks and waterBodies files
    my__network = Network(catchment, outlet, input_folder)

    # Initiate everything needed for the nodes
    # my_variables = ["q", "cno3", "cnh4", "cdp", "cpp", "csed"]
    my_variables = ["q"]
    for node in my__network.nodes:
        dict_storage[node] = DataFrame(index=time_steps, columns=my_variables).fillna(0.0)  # filled with zeros

    # Initiate everything needed for the links (WaterBody object, Model objects, DataFrame objects
    for link in my__network.links:
        # Declare Model objects and get meteo DataFrame
        if my__network.categories[link] == "11":  # river headwater
            dict__model[link] = [Model("CATCHMENT", model_specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "10":  # river
            dict__model[link] = [Model("CATCHMENT", model_specifications_folder),
                                 Model("RIVER", model_specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "20":  # lake
            dict__model[link] = [Model("LAKE", model_specifications_folder)]
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            sys.exit("Waterbody {}: {} is not a registered type of waterbody.".format(link,
                                                                                      my__network.categories[link]))
        # Declare DataFrame objects
        my_headers = list()
        for model in dict__model[link]:
            my_headers += model.input_names + model.parameter_names + model.state_names + model.output_names
        dict_storage[link] = DataFrame(index=time_steps, columns=my_headers).fillna(0.0)  # filled with zeros

    # Read the parameters in .param file
    dict_param = sF.get_dict_parameters_from_file(catchment, outlet, my__network, dict__model, input_folder)

    # Initial for reservoirs
    # # TO BE DEFINED

    # Run the simulation
    my_dict_variables = dict()
    for variable in my_variables:
        my_dict_variables[variable] = 0.0

    for step in time_steps[1:]:  # ignore the index 0 because it is the initial conditions
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__model[link]:
                model.run(my__network, link, dict_storage, dict_param, dict_meteo, step, time_step_in_minutes)
        # Sum up everything coming from upstream for each node
        for node in my__network.nodes:
            if my__network.additions.get(node):  # ignore the node up for headwaters
                for variable in my_dict_variables:
                    for link in my__network.additions[node]:
                        try:  # when link is a river (SMART + LINRES)
                            my_dict_variables[variable] += dict_storage[link].loc[step, "r_" + variable]
                            my_dict_variables[variable] += dict_storage[link].loc[step, variable]
                        except KeyError:  # when link is a headwater river or a lake (SMART or BATHTUB)
                            my_dict_variables[variable] += dict_storage[link].loc[step, variable]
                    dict_storage[node].set_value(step, variable, my_dict_variables[variable])
                    my_dict_variables[variable] = 0.0


if __name__ == "__main__":
    main()
