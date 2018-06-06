import logging

from simuClasses import *
import simuFiles as sF


def distribute_loadings_across_year(dict_annual_loads, dict_applications, nd_distributions, link,
                                    my_tf, data_slice, simu_slice):
    """
    This function distributes the annual nutrient loadings across the year, using an application distribution.
    The annual amount is spread on every time step in the simulation time series.
    """
    my_nd_data = {i: {c: 0.0 for c in dict_applications[link]} for i in simu_slice}

    divisor = my_tf.gap_data / my_tf.gap_simu

    for contaminant in dict_applications[link]:
        for my_dt_data in data_slice[1:]:
            day_of_year = my_dt_data.timetuple().tm_yday
            my_value = dict_annual_loads[link][contaminant] * \
                nd_distributions[day_of_year][dict_applications[link][contaminant]]
            my_portion = float(my_value) / divisor
            for my_sub_step in xrange(0, -divisor, -1):
                my_dt_simu = my_dt_data + datetime.timedelta(minutes=my_sub_step * my_tf.gap_simu)
                my_nd_data[my_dt_simu][contaminant] = my_portion

    return my_nd_data


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
    dict__c_models = dict()  # key: waterbody, value: catchment model object
    dict__r_models = dict()  # key: waterbody, value: river model object
    dict__l_models = dict()  # key: waterbody, value: lake model object
    dict__ls_models = dict()   # key: waterbody, value: list of river model objects
    if my__network.waterQuality:
        for link in my__network.links:
            # Declare Model objects
            if my__network.categories[link] == "11":  # river headwater
                dict__c_models[link] = Model("CATCHMENT", "SMART_INCAL", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__r_models[link] = Model("RIVER", "LINRES_INCAS", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__c_models[link], dict__r_models[link]]
            elif my__network.categories[link] == "10":  # river
                dict__c_models[link] = Model("CATCHMENT", "SMART_INCAL", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__r_models[link] = Model("RIVER", "LINRES_INCAS", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__c_models[link], dict__r_models[link]]
            elif my__network.categories[link] == "20":  # lake
                dict__l_models[link] = Model("LAKE", "BATHTUB", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__l_models[link]]
                # For now, no direct rainfall on open water in model
                # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
            else:  # unknown (e.g. 21 would be a lake headwater)
                raise Exception("Waterbody {}: {} is not a registered type of waterbody.".format(
                    link, my__network.categories[link]))
    else:
        for link in my__network.links:
            # Declare Model objects
            if my__network.categories[link] == "11":  # river headwater
                dict__c_models[link] = Model("CATCHMENT", "SMART", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__r_models[link] = Model("RIVER", "LINRES", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__c_models[link], dict__r_models[link]]
            elif my__network.categories[link] == "10":  # river
                dict__c_models[link] = Model("CATCHMENT", "SMART", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__r_models[link] = Model("RIVER", "LINRES", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__c_models[link], dict__r_models[link]]
            elif my__network.categories[link] == "20":  # lake
                dict__l_models[link] = Model("LAKE", "BATHTUB", my__network, link,
                                             specifications_folder, input_folder, output_folder)
                dict__ls_models[link] = [dict__l_models[link]]
                # For now, no direct rainfall on open water in model
                # need to be changed, but to do so, need remove lake polygon from sub-basin polygon)
            else:  # unknown (e.g. 21 would be a lake headwater)
                raise Exception("Waterbody {}: {} is not a registered type of waterbody.".format(
                    link, my__network.categories[link]))

    return dict__ls_models, dict__c_models, dict__r_models, dict__l_models


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
            my_headers += model.input_names + model.state_names + model.process_names + model.output_names
        my_dict_with_headers = {c: 0.0 for c in my_headers}
        dict__nd_data[link] = \
            {i: dict(my_dict_with_headers) for i in my_simu_slice}

    return dict__nd_data


def get_meteo_input_for_links(my__network, my__time_frame, my_data_slice, my_simu_slice,
                              datetime_start_data, datetime_end_data,
                              input_format, input_folder):
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
    :param input_format: format to use to read in the meteorological files
    :type input_format: str()
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
                                                              datetime_start_data, datetime_end_data,
                                                              input_format, input_folder)

    return dict__nd_meteo


def get_contaminant_input_for_links(my__network, my__time_frame, my_data_slice, my_simu_slice,
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
        dict__nd_loadings[link] = distribute_loadings_across_year(dict_annual_loads, dict_applications,
                                                                  nd_distributions, link,
                                                                  my__time_frame, my_data_slice, my_simu_slice)

    return dict__nd_loadings

