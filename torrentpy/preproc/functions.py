import logging

import inout as prp_io
import resolution as prp_tm


def get_meteo_input_for_links(my__network, my__time_frame,
                              input_format, input_folder):
    """
    This function generates a nested dictionary for each link and stores them in a single dictionary that is returned.
    Each nested dictionary has the dimension of the simulation time slice times the number of meteorological variables.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
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
        dict__nd_meteo[link] = prp_io.get_nd_meteo_data_from_file(my__network.name, link, my__time_frame,
                                                                  input_format, input_folder)

    return dict__nd_meteo


def get_contaminant_input_for_links(my__network, my__time_frame, my_save_slice, my_simu_slice,
                                    input_folder, specifications_folder):
    """
    This function generates a nested dictionary for each link and stores them in a single dictionary that is returned.
    Each nested dictionary has the dimension of the simulation time slice times the number of contaminant inputs.

    :param my__network: Network object for the simulated catchment
    :type my__network: Network
    :param my__time_frame: TimeFrame object for the simulation period
    :type my__time_frame: TimeFrame
    :param my_save_slice: list of DateTime corresponding to the simulation slice (separated by the save time gap)
    :type my_save_slice: list()
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
    dict_annual_loads = prp_io.get_nd_from_file(my__network, input_folder, extension='loadings', var_type=float)
    dict_applications = prp_io.get_nd_from_file(my__network, input_folder, extension='applications', var_type=str)
    nd_distributions = prp_io.get_nd_distributions_from_file(specifications_folder)
    for link in my__network.links:
        dict__nd_loadings[link] = prp_tm.distribute_loadings_across_year(dict_annual_loads, dict_applications,
                                                                         nd_distributions, link,
                                                                         my__time_frame, my_save_slice, my_simu_slice)

    return dict__nd_loadings
