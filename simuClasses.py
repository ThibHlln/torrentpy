import csv
import os
from logging import getLogger
import datetime
import pandas
from math import ceil

import simuModels as sM


class Network:
    """
    This class defines all the constituting parts of a catchment structures as a node-link network, as well as the
    different relationships between the nodes and the links, and the characteristics of the links. The optional
    parameter 'adding_up' allows to specify where the catchment runoff is routed to: if True runoff is routed to the
    node upstream of the link, if False runoff is routed to the node downstream of the link, Default is set as False.
    """
    def __init__(self, catchment, outlet, input_folder, specs_folder, wq=False):
        # name of the catchment
        self.name = catchment.capitalize()
        # european code of the outlet
        self.code = outlet.upper()
        # boolean for water quality simulations
        self.waterQuality = wq
        # path of the files necessary to generate the Network object
        self.networkFile = "{}{}_{}.network".format(input_folder, catchment, outlet)
        self.waterBodiesFile = "{}{}_{}.waterbodies".format(input_folder, catchment, outlet)
        self.descriptorsFile = "{}{}_{}.descriptors".format(input_folder, catchment, outlet)
        # list of the nodes contained in the Network
        self.nodes = Network.get_network_attributes(self)["nodes"]
        # list of the links contained in the Network
        self.links = Network.get_network_attributes(self)["links"]
        # connections for links = nodes upstream and downstream of a given link
        self.connections = Network.get_network_attributes(self)["connections"]
        # adding for nodes = list of links whose catchments are pouring into the node
        self.adding = Network.get_network_attributes(self)["adding"]
        # routing for nodes = list of links whose reaches are pouring into the node
        self.routing = Network.get_network_attributes(self)["routing"]
        # categories for links = code to identify the type of catchment (river or lake, headwater or not)
        self.categories = Network.get_waterbodies_attributes(self)
        # descriptors for the links = physical descriptors characteristic of a given catchment
        self.descriptors = Network.get_catchments_descriptors(self)
        # list of the variables to be propagated through the node-link network
        self.variables_h = Network.get_one_list(specs_folder, "variables_h")
        self.variables_q = Network.get_one_list(specs_folder, "variables_q") if wq else []
        self.variables = self.variables_h + self.variables_q

    def get_network_attributes(self):
        """
        This method reads all the information contained in the network file in order to get the list of the nodes and
        the links as well as the connections, and the links adding to the nodes and routed by the nodes.
        :return: dictionary containing nodes, links, connections, routing, and adding
        """
        logger = getLogger('SingleRun.Network')
        try:
            with open(self.networkFile) as my_file:
                my_reader = csv.DictReader(my_file)
                my_nodes = list()  # list of all nodes
                my_links = list()  # list of all links (i.e. waterbodies)
                my_connections = dict()  # key: waterbody, value: 2-element list (node down, node up)
                my_routing = dict()  # key: node, value: list of streams pouring into node
                my_adding = dict()  # key: node, value: basin pouring into node
                for row in my_reader:
                    my_nodes.append(row['NodeDown'])
                    my_nodes.append(row['NodeUp'])
                    my_links.append(row['WaterBody'])
                    my_connections[row['WaterBody']] = (row['NodeDown'], row['NodeUp'])
                my_nodes = list(set(my_nodes))  # get rid of the duplicates
                for node in my_nodes:
                    my_routing[node] = list()
                    my_adding[node] = list()
                for link in my_connections:
                    my_routing[my_connections[link][0]].append(link)
                    my_adding[my_connections[link][1]].append(link)

        except IOError:
            logger.error("No link-node network file found for {}.".format(self.name))
            raise Exception("No link-node network file found for {}.".format(self.name))

        return {
            "nodes": my_nodes,
            "links": my_links,
            "connections": my_connections,
            "routing": my_routing,
            "adding": my_adding
        }

    def get_waterbodies_attributes(self):
        """
        This method reads the attributes of the links from the waterBodies file. It associates the waterbody type code
        (1 for river, 2 for lake) and the headwater status (1 if headwater, 0 if not) to create a 2-digit code.
        :return: dictionary {key: link, value: category as a 2-digit code}
        """
        logger = getLogger('SingleRun.Network')
        try:
            with open(self.waterBodiesFile) as my_file:
                my_reader = csv.DictReader(my_file)
                my_categories = dict()
                for row in my_reader:
                    my_categories[row['WaterBody']] = row['WaterBodyTypeCode'] + row['HeadwaterStatus']

        except IOError:
            logger.error("No waterbodies file found for {}.".format(self.name))
            raise Exception("No waterbodies file found for {}.".format(self.name))

        return my_categories

    def get_catchments_descriptors(self):
        """
        This method reads the catchment descriptors from the descriptors file.
        :return: nested dictionary {key: link, value: {key: descriptor_name, value: descriptor_value}}
        """
        logger = getLogger('SingleRun.Network')
        try:
            with open(self.descriptorsFile) as my_file:
                my_descriptors = dict()
                my_reader = csv.DictReader(my_file)
                fields = my_reader.fieldnames[:]
                fields.remove("EU_CD")
                found = list()
                for row in my_reader:
                    my_dict = dict()
                    for field in fields:
                        my_dict[field] = float(row[field])
                    my_descriptors[row["EU_CD"]] = my_dict
                    found.append(row["EU_CD"])

                missing = [elem for elem in self.links if elem not in found]
                if missing:
                    logger.error("The following waterbodies are not in the descriptors file: {}.".format(missing))
                    raise Exception("The following waterbodies are not in the descriptors file: {}.".format(missing))

        except IOError:
            logger.error("No descriptors file found for {}.".format(self.name))
            raise Exception("No descriptors file found for {}.".format(self.name))

        return my_descriptors

    @staticmethod
    def get_one_list(specs_folder, specs_type):
        """
        This method reads the list of variables for the specification type given as a parameter from the file of
        specifications in the specification folder.
        :param specs_folder: path to the specification folder where to find the specifications file
        :param specs_type: name of the specification type
        :return: a list of the names of the variables for the given specification
        """
        logger = getLogger('SingleRun.Network')
        my_list = list()
        try:
            with open(specs_folder + "SIMULATOR.spec") as my_file:
                my_reader = csv.reader(my_file)
                my_string = list()
                count = 0
                for row in my_reader:
                    if row[0] == specs_type:
                        my_string = row[1]
                        count += 1
                if count == 0:
                    logger.error("There is no {} specifications line in {}SIMULATOR.spec.".format(
                        specs_type, specs_folder))
                    raise Exception("There is no {} specifications line in {}SIMULATOR.spec.".format(
                        specs_type, specs_folder))
                elif count > 1:
                    logger.error("There is more than one {} specifications line in {}SIMULATOR.spec.".format(
                        specs_type, specs_folder))
                    raise Exception("There is more than one {} specifications line in {}SIMULATOR.spec.".format(
                        specs_type, specs_folder))
                my_list.extend(my_string.split(";"))

        except IOError:
            logger.error("There is no specifications file for SIMULATOR in {}.".format(specs_folder))
            raise Exception("There is no specifications file for SIMULATOR in {}.".format(specs_folder))

        return my_list


class Model:
    """
    This class defines a model associated to a link in the Network object. It contains the names of the inputs, states,
    parameters, and outputs as well as the values of the parameters and the constants.
    """
    def __init__(self, category, identifier, my__network, link, specs_folder, input_folder, output_folder):
        # category of the Model (catchment, river, or lake)
        self.category = category.upper()
        # name of the Model within the category
        self.identifier = identifier.upper()
        # european code of the link associated to the Model
        self.link = link.upper()
        # list of the names for the inputs of the Model
        self.input_names = Model.get_list_names(self, specs_folder, "inputs")
        # list of the names for the parameters of the Model
        self.parameter_names = Model.get_list_names(self, specs_folder, "parameters")
        # list of the names for the states of the Model
        self.state_names = Model.get_list_names(self, specs_folder, "states")
        # list of the names for the outputs of the Model
        self.output_names = Model.get_list_names(self, specs_folder, "outputs")
        # values for the parameters of the Model
        self.parameters = Model.get_dict_parameters(self, my__network, specs_folder, input_folder, output_folder)
        # values for the constants of the Model
        self.constants = Model.get_dict_constants(self, specs_folder)

    def get_list_names(self, specs_folder, specs_type):
        """
        This method reads the list of variables names for the specification type given as a parameter from the file of
        specifications in the specification folder.
        :param specs_folder: path to the specification folder where to find the specifications file
        :param specs_type: name of the specification type
        :return: a list of the names of the variables for the given specification
        """
        logger = getLogger('SingleRun.Model')
        components = self.identifier.split('_')
        my_list = list()
        for component in components:
            try:
                with open("{}{}.spec".format(specs_folder, component)) as my_file:
                    my_reader = csv.reader(my_file)
                    my_string = list()
                    count = 0
                    for row in my_reader:
                        if row[0] == specs_type:
                            my_string = row[1]
                            count += 1
                    if count == 0:
                        logger.error("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                    elif count > 1:
                        logger.error("There is more than one {} specifications line in {}{}.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is more than one {} specifications line in {}{}.".format(
                            specs_type, specs_folder, component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                logger.error("There is no specifications file for {} in {}.".format(component, specs_folder))
                raise Exception("There is no specifications file for {} in {}.".format(component, specs_folder))

        return my_list

    def get_dict_constants(self, specs_folder):
        """
        This method get the list of the names for the constants of the Model in its specification file in the
        specifications folder. Then, the methods reads the constants values in the constant file for the Model located
        in the specifications folder.

        :param specs_folder: path to the specification folder where to find the specifications file
        :return: dictionary containing the constants names and values
            {key: constant_name, value: constant_value}
        """
        logger = getLogger('SingleRun.Model')
        specs_type = "constants"
        components = self.identifier.split('_')
        my_list = list()
        my_dict = dict()
        for component in components:
            try:
                with open("{}{}.spec".format(specs_folder, component)) as my_file:
                    my_reader = csv.reader(my_file)
                    my_string = list()
                    count = 0
                    for row in my_reader:
                        if row[0] == specs_type:
                            my_string = row[1]
                            count += 1
                    if count == 0:
                        logger.error("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                    elif count > 1:
                        logger.error("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is more than one {} specifications line in {}{}.".format(
                            specs_type, specs_folder, component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                logger.error("There is no specifications file for {} in {}.".format(component, specs_folder))
                raise Exception("There is no specifications file for {} in {}.".format(component, specs_folder))

            if my_list:
                try:
                    my_file = "{}{}.{}".format(specs_folder, component, specs_type)
                    my_df = pandas.read_csv(my_file, index_col=0)
                    for name in my_list:
                        try:
                            my_dict[name] = float(my_df.get_value(name, 'value'))
                        except KeyError:
                            logger.error("The {} {} is not available for {}.".format(
                                specs_type[:-1], name, component))
                            raise Exception("The {} {} is not available for {}.".format(
                                specs_type[:-1], name, component))

                except IOError:
                    logger.error("{}{}.{} does not exist.".format(specs_folder, component, specs_type))
                    raise Exception("{}{}.{} does not exist.".format(specs_folder, component, specs_type))

        return my_dict

    def get_dict_parameters(self, network, specs_folder, input_folder, output_folder):
        """
        This method get the list of the names for the parameters of the Model in its specification file in the
        specifications folder. Then, the methods reads the parameters values in the parameter file for the Model located
        in the input folder. If this file does not exist, it uses the descriptors of the catchment that owns the Model
        in order to infer the parameters from the descriptors. In any case, it saves the parameters used in a file in
        the output folder.

        :param network: Network object for the simulated catchment
        :param specs_folder: path to the specification folder where to find the specifications file
        :param input_folder: path to the specification folder where to find the parameter file
        :param output_folder: path to the specification folder where to save the parameter file
        :return: dictionary containing the constants names and values
            {key: parameter_name, value: parameter_value}
        """
        logger = getLogger('SingleRun.Model')
        specs_type = "parameters"
        components = self.identifier.split('_')
        my_list = list()
        my_dict = dict()
        for component in components:
            try:
                with open("{}{}.spec".format(specs_folder, component), 'rb') as my_file:
                    my_reader = csv.reader(my_file)
                    my_string = list()
                    count = 0
                    for row in my_reader:
                        if row[0] == specs_type:
                            my_string = row[1]
                            count += 1
                    if count == 0:
                        logger.error("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is no {} specifications line in {}{}.spec.".format(
                            specs_type, specs_folder, component))
                    elif count > 1:
                        logger.error("There is more than one {} specifications line in {}{}.".format(
                            specs_type, specs_folder, component))
                        raise Exception("There is more than one {} specifications line in {}{}.".format(
                            specs_type, specs_folder, component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                logger.error("There is no specifications file for {} in {}.".format(component, specs_folder))
                raise Exception("There is no specifications file for {} in {}.".format(component, specs_folder))

            if my_list:
                dict_for_file = dict()
                try:
                    my_file = "{}{}_{}.{}.{}".format(input_folder, network.name, network.code, component, specs_type)
                    my_df = pandas.read_csv(my_file, index_col=0)
                    for name in my_list:
                        try:
                            dict_for_file[name] = float(my_df.get_value(self.link, name))
                        except KeyError:
                            logger.error("The {} {} {} is not available for {}.".format(
                                component, specs_type[:-1], name, self.link))
                            raise Exception("The {} {} {} is not available for {}.".format(
                                component, specs_type[:-1], name, self.link))
                except IOError:
                    dict_for_file = sM.infer_parameters_from_descriptors(network.descriptors[self.link], component)

                my_dict.update(dict_for_file)
                dict_for_file["EU_CD"] = self.link

                if os.path.isfile('{}{}_{}.{}.{}'.format(output_folder, network.name, network.code,
                                                         component, specs_type)):
                    with open('{}{}_{}.{}.{}'.format(output_folder, network.name, network.code,
                                                     component, specs_type), 'ab') as my_file:
                        header = ["EU_CD"] + my_list
                        my_writer = csv.DictWriter(my_file, fieldnames=header)
                        my_writer.writerow(dict_for_file)
                else:
                    with open('{}{}_{}.{}.{}'.format(output_folder, network.name, network.code,
                                                     component, specs_type), 'wb') as my_file:
                        header = ["EU_CD"] + my_list
                        my_writer = csv.DictWriter(my_file, fieldnames=header)
                        my_writer.writeheader()
                        my_writer.writerow(dict_for_file)

            del my_list[:]

        return my_dict

    def run(self, obj_network, waterbody, dict_nd_data,
            dict_nd_meteo, dict_nd_loadings,
            datetime_time_step, time_gap,
            logger):
        """
        This method runs the Model simulations for one time step.

        :param obj_network: Network object for the simulated catchment
        :param waterbody: code of the link that owns the model
        :param dict_nd_data: dictionary containing the nested dictionaries for the nodes and the links for variables
            { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
        :type dict_nd_data: dict
        :param dict_nd_meteo: dictionary containing the nested dictionaries for the links for meteorological inputs
            { key = link: value = nested_dictionary(index=datetime,column=meteo_input) }
        :type dict_nd_meteo: dict
        :param dict_nd_loadings: dictionary containing the nested dictionaries for the links for contaminant inputs
            { key = link: value = nested_dictionary(index=datetime,column=contaminant_input) }
        :param datetime_time_step: DateTime of the time step to be simulated
        :type datetime_time_step: datetime.datetime
        :param time_gap: duration of the gap between two simulation time steps
        :type time_gap: float
        :param logger: reference to the logger to be used to inform on simulation
        :type logger: Logger
        :return: NOTHING
        """
        if self.category == "CATCHMENT":
            sM.run_catchment_model(self.identifier, waterbody, dict_nd_data,
                                   obj_network.descriptors, self.parameters, self.constants,
                                   dict_nd_meteo, dict_nd_loadings,
                                   datetime_time_step, time_gap,
                                   logger)
        elif self.category == "RIVER":
            sM.run_river_model(self.identifier, obj_network, waterbody, dict_nd_data,
                               self.parameters, self.constants, dict_nd_meteo,
                               datetime_time_step, time_gap,
                               logger)
        elif self.category == "LAKE":
            sM.run_lake_model(self.identifier, waterbody)

    def initialise(self, obj_network):
        """
        This method returns the initial conditions for the states of the model.

        :param obj_network: Network object for the simulated catchment
        :return: dictionary containing states that have non-zero initial values
        """
        dict_init = dict()
        if self.category == "CATCHMENT":
            dict_init.update(
                sM.initialise_catchment_model(self.identifier, obj_network.descriptors[self.link], self.parameters))
        elif self.category == "RIVER":
            dict_init.update(
                sM.initialise_river_model(self.identifier, obj_network.descriptors[self.link], self.parameters))
        elif self.category == "LAKE":
            dict_init.update(
                sM.initialise_lake_model(self.identifier))

        return dict_init


class TimeFrame:
    """
    This class defines the temporal attributes of the simulation period. It contains the start and the end of the
    simulation as well as the lists of DateTime series for the simulation time steps and the data time steps (that
    can be identical or nested). It also breaks down the series into slices in order to reduce the memory demand during
    the simulation.

    N.B. 1: The simulation gap needs to be a multiple if the data gap and the simulation gap can be greater than
    or equal to the data gap
    N.B. 2: The start and the end of the simulation are defined by the user, the class always adds one data step
    prior to the start date in order to set the initial conditions, one or more simulation steps are added in
    consequence depending if the simulation step in a multiple of the data step or not (i.e. equal)
    """
    def __init__(self, datetime_start, datetime_end,
                 data_increment_in_minutes, simu_increment_in_minutes,
                 expected_simu_slice_length):
        # DateTime of the start of the time period simulated
        self.start = datetime_start
        # DateTime of the end of the time period simulated
        self.end = datetime_end
        # Time gap of the data used for simulation
        self.gap_data = data_increment_in_minutes
        # Time gap of the simulation
        self.gap_simu = simu_increment_in_minutes
        # List of DateTime for the data (i.e. list of time steps)
        self.series_data = TimeFrame.get_list_datetime(self, 'data')
        # List of DateTime for the simulation (i.e. list of time steps)
        self.series_simu = TimeFrame.get_list_datetime(self, 'simu')
        # List of Lists of DateTime for simulation and for data, respectively
        self.slices_simu, self.slices_data = \
            TimeFrame.slice_list_datetime(self, expected_simu_slice_length)

    def get_list_datetime(self, option):
        """
        This function returns a list of DateTime by using the start and the end of the simulation and the time gap
        (either the data time gap or the simulation time gap, using the option parameter to specify which one).

        N.B. For the initial conditions, the function always adds:
            - [if 'data' option] one data step prior to the data start date
            - [if 'simu' option] one (or more if data gap > simulation gap) simulation step(s)
            prior to the simulation start date

        :param option: choice to specify if function should work on data or on simulation series
        :type option: str()
        :return: a list of DateTime
        :rtype: list()
        """
        extent = self.end - self.start
        options = {'data': self.gap_data, 'simu': self.gap_simu}

        start_index = int(self.gap_data / options[option])
        end_index = int(extent.total_seconds() // (options[option] * 60)) + 1

        my_list_datetime = list()
        for factor in xrange(-start_index, end_index, 1):  # add one or more datetime before start
            my_datetime = self.start + datetime.timedelta(minutes=factor * options[option])
            my_list_datetime.append(my_datetime)

        return my_list_datetime

    def slice_list_datetime(self, expected_length):
        """
        This function returns two lists of lists of DateTime for simulation and data, respectively. It uses the two
        DateTime series and the expected length of the simulation time slice. A time slice is a subset of a time
        series as follows : [ series ] = [ slice 1 ] + [ slice 2 ] + ... + [ slice n ]
        The function adjusts the expected length to make sure that the slicing is done between two data
        time steps.

        N.B. the last slice is usually shorter than the others, unless the input time series is a multiple
        of the adjusted length

        :param expected_length: number of time steps desired per time slice
        :type expected_length: int()
        :return: two lists of time slices for simulation and data, respectively
        :rtype: list(), list()
        """
        simu_steps_per_data_step = self.gap_data / self.gap_simu

        # Adjust the length to make sure that it slices exactly between two steps of the data
        simu_length = (expected_length * self.gap_simu) // self.gap_data * simu_steps_per_data_step
        data_length = simu_length / simu_steps_per_data_step

        my_simu_slices = list()
        my_data_slices = list()

        if simu_length > 0:  # the expected length is longer than one data time gap
            stop_index = int(ceil(float(len(self.series_simu)) / float(simu_length)))
            for i in xrange(0, stop_index, 1):
                start_index = i * simu_length
                end_index = ((i + 1) * simu_length) + 1
                my_simu_slices.append(self.series_simu[start_index:end_index])
            stop_index = int(ceil(float(len(self.series_data)) / float(data_length)))
            for i in xrange(0, stop_index, 1):
                start_index = i * data_length
                end_index = ((i + 1) * data_length) + 1
                my_data_slices.append(self.series_data[start_index:end_index])
        else:  # no need to slice, return the original lists as one slice
            my_simu_slices.append(self.series_simu[:])
            my_data_slices.append(self.series_data[:])

        return my_simu_slices, my_data_slices
