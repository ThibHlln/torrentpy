import csv
import os
from logging import getLogger
from datetime import timedelta
import pandas
from math import ceil

import models as mod


class Network:
    """
    This class defines all the constituting parts of a catchment structures as a node-link network, as well as the
    different relationships between the nodes and the links, and the characteristics of the links.
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
            with open(specs_folder + "TORRENTPY.spec") as my_file:
                my_reader = csv.reader(my_file)
                my_string = list()
                count = 0
                for row in my_reader:
                    if row[0] == specs_type:
                        my_string = row[1]
                        count += 1
                if count == 0:
                    logger.error("There is no {} specifications line in {}TORRENTPY.spec.".format(
                        specs_type, specs_folder))
                    raise Exception("There is no {} specifications line in {}TORRENTPY.spec.".format(
                        specs_type, specs_folder))
                elif count > 1:
                    logger.error("There is more than one {} specifications line in {}TORRENTPY.spec.".format(
                        specs_type, specs_folder))
                    raise Exception("There is more than one {} specifications line in {}TORRENTPY.spec.".format(
                        specs_type, specs_folder))
                my_list.extend(my_string.split(";"))

        except IOError:
            logger.error("There is no specifications file for TORRENTPY in {}.".format(specs_folder))
            raise Exception("There is no specifications file for TORRENTPY in {}.".format(specs_folder))

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
        # list of the names for the processes of the Model
        self.process_names = Model.get_list_names(self, specs_folder, "processes")
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
                    dict_for_file = mod.infer_parameters_from_descriptors(network.descriptors[self.link], component)

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
            mod.run_catchment_model(self.identifier, waterbody, dict_nd_data,
                                    obj_network.descriptors, self.parameters, self.constants,
                                    dict_nd_meteo, dict_nd_loadings,
                                    datetime_time_step, time_gap,
                                    logger)
        elif self.category == "RIVER":
            mod.run_river_model(self.identifier, obj_network, waterbody, dict_nd_data,
                                self.parameters, self.constants, dict_nd_meteo,
                                datetime_time_step, time_gap,
                                logger)
        elif self.category == "LAKE":
            mod.run_lake_model(self.identifier, waterbody)

    def initialise(self, obj_network):
        """
        This method returns the initial conditions for the states of the model.

        :param obj_network: Network object for the simulated catchment
        :return: dictionary containing states that have non-zero initial values
        """
        dict_init = dict()
        if self.category == "CATCHMENT":
            dict_init.update(
                mod.initialise_catchment_model(self.identifier, obj_network.descriptors[self.link], self.parameters))
        elif self.category == "RIVER":
            dict_init.update(
                mod.initialise_river_model(self.identifier, obj_network.descriptors[self.link], self.parameters))
        elif self.category == "LAKE":
            dict_init.update(
                mod.initialise_lake_model(self.identifier))

        return dict_init


class TimeFrame:
    """
    This class gathers the temporal information provided by the user. Then, it defines the temporal attributes
    of the simulator.

    Three type of temporal attributes are considered: 'data' refers to the input to the simulator
    (e.g. meteorological variables in input files), 'simu' refers to the internal time used by the structures (i.e. model
    temporal discretisation), and 'save' refers to the output from the simulator (i.e. what will be written in the
    output files).

    For each type, three attributes (start, end, gap) are required to build timeseries. Then each timeseries will
    broken down into slices (to avoid flash memory limitations).

    In terms of starts/ends, the user is only required to provide them for 'data' and for 'save', start/end for 'simu'
    are inferred using 'save' start/end/gap and the 'simu' gap.

    In terms of timeseries, 'simu' and 'save' timeseries are built using their respective start/end/gap, however,
    the 'simu' timeseries will only be built if the data period specified provides enough information. For 'data',
    only a timeseries of needed_data is provided (i.e. a the minimum timeseries of data required to cover the 'simu'
    period). This is to avoid storing in flash memory an unnecessary long timeseries if 'simu' period is significantly
    shorter than 'data' period.
    To allow for initial conditions to be set up, one or more time steps are added prior the respective starts of
    'simu' and 'save'. The 'save' time is added one datetime before save_start, while the 'simu' is added one or more
    datetime if it requires several simu_gap to cover one data_gap.

    N.B. The 'save' gap is required to be a multiple of 'simu' gap because this simulator is not intended to
    interpolate on the simulation results, the simulator can only extract or summarise from simulation steps.
    Instead, the user is expected to adapt their simulation gap to match the required reporting gap.
    """
    def __init__(self, dt_data_start, dt_data_end, dt_save_start, dt_save_end,
                 data_increment_in_minutes, save_increment_in_minutes, simu_increment_in_minutes,
                 expected_simu_slice_length):
        # Time Attributes for Input Data (Read in Files)
        self.data_start = dt_data_start  # DateTime
        self.data_end = dt_data_end  # DateTime
        self.data_gap = data_increment_in_minutes  # Int [minutes]

        # Time Attributed for Output Data (Save/Write in Files)
        self.save_start = dt_save_start  # DateTime
        self.save_end = dt_save_end  # DateTime
        self.save_gap = save_increment_in_minutes  # Int [minutes]

        # Time Attributes for Simulation (Internal to the Simulator)
        self.simu_gap = simu_increment_in_minutes  # Int [minutes]
        self.simu_start_earliest, self.simu_end_latest = \
            TimeFrame.get_most_possible_extreme_simu_start_end(self)  # DateTime, DateTime
        self.simu_start, self.simu_end = \
            TimeFrame.get_simu_start_end_given_save_start_end(self)  # DateTime, DateTime

        # Time Attributes Only for Input Data Needed given Simulation Period
        self.data_needed_start, self.data_needed_end = \
            TimeFrame.get_data_start_end_given_simu_start_end(self)

        # DateTime Series for Data, Save, and Simulation
        self.needed_data_series = TimeFrame.get_list_data_needed_dt_without_initial_conditions(self)
        self.save_series = TimeFrame.get_list_save_dt_with_initial_conditions(self)
        self.simu_series = TimeFrame.get_list_simu_dt_with_initial_conditions(self)

        # Slices of DateTime Series for Save and Simulation
        self.save_slices, self.simu_slices = \
            TimeFrame.slice_datetime_series(self, expected_simu_slice_length)

    def get_most_possible_extreme_simu_start_end(self):

        # check whether data period makes sense on its own
        if not self.data_start <= self.data_end:
            raise Exception("Data Start is greater than Data End.")

        # determine the maximum possible simulation period given the period of data availability
        simu_start_earliest = self.data_start - timedelta(minutes=self.data_gap) + timedelta(minutes=self.simu_gap)
        simu_end_latest = self.data_end

        return simu_start_earliest, simu_end_latest

    def get_simu_start_end_given_save_start_end(self):

        # check whether saving/reporting period makes sense on its own
        if not self.save_start <= self.save_end:
            raise Exception("Save Start is greater than Save End.")

        # check whether the simulation time gap will allow to report on the saving/reporting time gap
        if not self.save_gap % self.simu_gap == 0:
            raise Exception("Save Gap is not greater and a multiple of Simulation Gap.")

        # determine the simulation period required to cover the whole saving/reporting period
        simu_start = self.save_start - timedelta(minutes=self.save_gap) + timedelta(minutes=self.simu_gap)
        simu_end = self.save_end

        # check if simu_start/simu_end period is contained in simu_start_earlier/simu_end_latest (i.e. available data)
        if not ((self.simu_start_earliest <= simu_start) and (simu_end <= self.simu_end_latest)):
            raise Exception("Input Data Period is insufficient to cover Save Period.")

        return simu_start, simu_end

    def get_data_start_end_given_simu_start_end(self):

        # check if Data Period is a multiple of Data Time Gap
        if not (self.data_end - self.data_start).total_seconds() % \
               timedelta(minutes=self.data_gap).total_seconds() == 0:
            raise Exception("Data Period does not contain a whole number of Data Time Gaps.")

        # increment from data_start until simu_start is just covered
        data_start_for_simu = self.data_start
        while data_start_for_simu < self.simu_start:
            data_start_for_simu += timedelta(minutes=self.data_gap)

        # decrement from data_end until end_start is just covered
        data_end_for_simu = self.data_end
        while data_end_for_simu >= self.simu_end:
            data_end_for_simu -= timedelta(minutes=self.data_gap)
        data_end_for_simu += timedelta(minutes=self.data_gap)

        return data_start_for_simu, data_end_for_simu

    def get_list_data_needed_dt_without_initial_conditions(self):

        # generate a list of DateTime for Data Period without initial conditions (not required)
        my_list_datetime = list()
        my_dt = self.data_needed_start
        while my_dt <= self.data_needed_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.data_gap)

        return my_list_datetime

    def get_list_save_dt_with_initial_conditions(self):

        # generate a list of DateTime for Saving/Reporting Period with one extra prior step for initial conditions
        my_list_datetime = list()
        my_dt = self.save_start - timedelta(minutes=self.save_gap)
        while my_dt <= self.save_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.save_gap)

        return my_list_datetime

    def get_list_simu_dt_with_initial_conditions(self):

        # generate a list of DateTime for Simulation Period with one extra prior step for initial conditions
        my_list_datetime = list()
        my_dt = self.simu_start - timedelta(minutes=self.simu_gap)
        while my_dt <= self.simu_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.simu_gap)

        return my_list_datetime

    def slice_datetime_series(self, expected_length):

        my_save_slices = list()
        my_simu_slices = list()

        if expected_length > 0:  # i.e. a slice length has been specified and is greater than 0
            if not (expected_length * self.simu_gap) >= self.save_gap:
                raise Exception('Expected Length for Slicing Up is smaller than the Saving Time Gap.')

            # Adjust the length to make sure that it slices exactly between two saving/reporting steps
            simu_slice_length = (expected_length * self.simu_gap) // self.save_gap * self.save_gap / self.simu_gap
            save_slice_length = simu_slice_length * self.simu_gap / self.save_gap

            if simu_slice_length > 0:  # the expected length is longer than one saving/reporting time gap
                stop_index = int(ceil(float(len(self.save_series)) / float(save_slice_length)))
                for i in xrange(0, stop_index, 1):
                    start_index = i * save_slice_length
                    end_index = ((i + 1) * save_slice_length) + 1
                    if len(self.save_series[start_index:end_index]) > 1:  # it would only be the initial conditions
                        my_save_slices.append(self.save_series[start_index:end_index])
                stop_index = int(ceil(float(len(self.simu_series)) / float(simu_slice_length)))
                for i in xrange(0, stop_index, 1):
                    start_index = i * simu_slice_length
                    end_index = ((i + 1) * simu_slice_length) + 1
                    if len(self.simu_series[start_index:end_index]) > 1:  # it would only be the initial conditions
                        my_simu_slices.append(self.simu_series[start_index:end_index])
            else:  # no need to slice, return the complete original lists (i.e. one slice for each)
                my_save_slices.append(self.save_series[:])
                my_simu_slices.append(self.simu_series[:])
        else:  # i.e. a slice length has not been specified or is equal to 0
            my_save_slices.append(self.save_series[:])
            my_simu_slices.append(self.simu_series[:])

        return my_save_slices, my_simu_slices
