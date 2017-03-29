import sys
from pandas import DataFrame

from simuClasses import *
import simuFunctions as sF


def main():
    print "Hello"

    catchment = ""

    model_specifications_folder = ""
    input_folder = ""

    dict_wb = {"a": (2, 1, 2),
               "b": (3, 2, 3),
               "c": (1, 3, 4)}

    dict__water_body = dict()
    dict__model = dict()
    dict__data_frame = dict()
    dict_meteo = dict()

    my_simu_start = (2006, 1, 1, 9, 0, 0)
    my_simu_end = (2012, 1, 1, 9, 0, 0)

    time_step_in_minutes = 60

    datetime_start = datetime.datetime(my_simu_start[0], my_simu_start[1], my_simu_start[2],
                                       my_simu_start[3], my_simu_start[4], my_simu_start[5])
    datetime_end = datetime.datetime(my_simu_end[0], my_simu_end[1], my_simu_end[2],
                                     my_simu_end[3], my_simu_end[4], my_simu_end[5])

    time_steps = TimeFrame(datetime_start, datetime_end, time_step_in_minutes).get_list_datetime()

    my__network = Network(catchment, input_folder)  # to replace dict_wb eventually

    # Initiate everything needed for the nodes
    my_variables = ["q", "cNO3", "cNH4", "cDP", "cPP", "cSED"]
    for node in my__network.nodes:
        dict__data_frame[node] = DataFrame(index=time_steps, columns=my_variables).fillna(0.0)

    # Initiate everything needed for the links
    for link in my__network.links:
        # Declare WaterBody objects
        dict__water_body[link] = WaterBody(link, my__network.categories[link],
                                           my__network.connections[link][0], my__network.connections[link][1])
        # Declare Model objects and get meteo DataFrame
        if my__network.categories[link] == "11":  # river headwater
            dict__model[link] = [Model("SMART", model_specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "10":  # river
            dict__model[link] = [Model("SMART", model_specifications_folder),
                                 Model("LINRES", model_specifications_folder)]
            dict_meteo[link] = sF.get_data_frame_for_daily_meteo_data(catchment, link, time_steps, input_folder)
        elif my__network.categories[link] == "20":  # lake
            dict__model[link] = [Model("BATHTUB", model_specifications_folder)]
            # For now, no direct rainfall on open water in model
            # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
        else:  # unknown (e.g. 21 would be a lake headwater)
            sys.exit("Waterbody {}: {} is not a registered type of waterbody.".format(link, dict_wb[link][0]))
        # Declare DataFrame objects
        my_headers = list()
        for model in dict__model[link]:
            my_headers.append(model.input_names + model.state_names + model.parameter_names + model.output_names)
        dict__data_frame[link] = DataFrame(index=time_steps, columns=my_headers).fillna(0.0)  # filled with zeros

    # Initial for nodes
    # # TO BE DEFINED

    # Run the simulation
    my_dict_variables = dict()
    for variable in my_variables:
        my_dict_variables[variable] = 0.0

    for step in time_steps:
        # Calculate runoff and concentrations for each link
        for link in my__network.links:
            for model in dict__model[link]:
                model.run(my__network, dict__water_body[link], dict__data_frame, dict_meteo, step)
        # Sum up everything coming from upstream for each node
        for node in my__network.nodes:
            if my__network.additions.get(node):  # ignore the node up for headwaters
                for variable in my_dict_variables:
                    for link in my__network.additions[node]:
                        try:
                            my_dict_variables[variable] += dict__data_frame[link].loc[step, variable]
                            my_dict_variables[variable] += dict__data_frame[link].loc[step, "r_" + variable]
                        except KeyError:
                            my_dict_variables[variable] += dict__data_frame[link].loc[step, variable]
                    dict__data_frame[node].set_value(step, variable, my_dict_variables[variable])
                    my_dict_variables[variable] = 0.0


if __name__ == "__main__":
    main()
