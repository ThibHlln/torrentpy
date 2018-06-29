import logging

from classes import *


def generate_models_for_links(my__network, specifications_folder, input_folder, output_folder):
    """
    This function creates the Model objects for all the links in the network. Each link can have several structures
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
    variables (inputs, states, and outputs) for all the structures of the link.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my_simu_slice: list of DateTime to be simulated
    :type my_simu_slice: list
    :param dict__ls_models: dictionary containing the list of structures for each link
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
