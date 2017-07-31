import csv
import os
import sys
import datetime
import pandas
from math import ceil

import simuModels as sM
import simuFunctions as sFn


class Network:
    """
    This class defines all the constituting parts of a catchment structures as a node-link network, as well as the
    different relationships between the nodes and the links, and the characteristics of the links.
    """
    def __init__(self, catchment, outlet, input_folder, specs_folder):
        # name of the catchment
        self.name = catchment.capitalize()
        # european code of the outlet
        self.code = outlet.upper()
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
        # adding for nodes = basin surrounding the link that has the given node upstream
        self.adding = Network.get_network_attributes(self)["adding"]
        # routing for nodes = list of the streams upstream that pour into the given node
        self.routing = Network.get_network_attributes(self)["routing"]
        # categories for links = code to identify the type of catchment (river or lake, headwater or not)
        self.categories = Network.get_waterbodies_attributes(self)
        # descriptors for the links = physical descriptors characteristic of a given catchment
        self.descriptors = Network.get_catchments_descriptors(self)
        # list of the variables to be propagated through the node-link network
        self.variables = Network.get_one_list(specs_folder, "variables")

    def get_network_attributes(self):
        """
        This method reads all the information contained in the network file in order to get the list of the nodes and
        the links as well as the connections, and the links adding to the nodes and routed by the nodes.
        :return: dictionary containing nodes, links, connections, routing, and adding
        """
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
            sys.exit("No link-node network file found for {}.".format(self.name))

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
        try:
            with open(self.waterBodiesFile) as my_file:
                my_reader = csv.DictReader(my_file)
                my_categories = dict()
                for row in my_reader:
                    my_categories[row['WaterBody']] = row['WaterBodyTypeCode'] + row['HeadwaterStatus']

        except IOError:
            sys.exit("No waterbodies file found for {}.".format(self.name))

        return my_categories

    def get_catchments_descriptors(self):
        """
        This method reads the catchment descriptors from the descriptors file.
        :return: nested dictionary {key: link, value: {key: descriptor_name, value: descriptor_value}}
        """
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
                    sys.exit("The following waterbodies are not in the descriptors file: {}.".format(missing))

        except IOError:
            sys.exit("No descriptors file found for {}.".format(self.name))

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
                    sys.exit("There is no {} specifications line in {}SIMULATOR.spec.".format(specs_type, specs_folder))
                elif count > 1:
                    sys.exit("There is more than one {} specifications line in {}SIMULATOR.spec.".format(specs_type,
                                                                                                         specs_folder))
                my_list.extend(my_string.split(";"))

        except IOError:
            sys.exit("There is no specifications file for SIMULATOR in {}.".format(specs_folder))

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
                        sys.exit("There is no {} specifications line in {}{}.spec.".format(specs_type, specs_folder,
                                                                                           component))
                    elif count > 1:
                        sys.exit("There is more than one {} specifications line in {}{}.".format(specs_type,
                                                                                                 specs_folder,
                                                                                                 component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                sys.exit("There is no specifications file for {} in {}.".format(component, specs_folder))

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
                        sys.exit("There is no {} specifications line in {}{}.spec.".format(specs_type, specs_folder,
                                                                                           component))
                    elif count > 1:
                        sys.exit("There is more than one {} specifications line in {}{}.".format(specs_type,
                                                                                                 specs_folder,
                                                                                                 component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                sys.exit("There is no specifications file for {} in {}.".format(component, specs_folder))

            if my_list:
                try:
                    my_file = "{}{}.{}".format(specs_folder, component, specs_type)
                    my_df = pandas.read_csv(my_file, index_col=0)
                    for name in my_list:
                        try:
                            my_dict[name] = float(my_df.get_value(name, 'value'))
                        except KeyError:
                            sys.exit("The {} {} is not available for {}.".format(specs_type[:-1], name, component))

                except IOError:
                    sys.exit("{}{}.{} does not exist.".format(specs_folder, component, specs_type))

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
                        sys.exit("There is no {} specifications line in {}{}.spec.".format(specs_type, specs_folder,
                                                                                           component))
                    elif count > 1:
                        sys.exit("There is more than one {} specifications line in {}{}.".format(specs_type,
                                                                                                 specs_folder,
                                                                                                 component))
                    if not my_string == '':
                        my_list.extend(my_string.split(";"))

            except IOError:
                sys.exit("There is no specifications file for {} in {}.".format(component, specs_folder))

            if my_list:
                dict_for_file = dict()
                try:
                    my_file = "{}{}_{}.{}.{}".format(input_folder, network.name, network.code, component, specs_type)
                    my_df = pandas.read_csv(my_file, index_col=0)
                    for name in my_list:
                        try:
                            dict_for_file[name] = float(my_df.get_value(self.link, name))
                        except KeyError:
                            sys.exit("The {} {} {} is not available for {}.".format(component, specs_type[:-1],
                                                                                    name, self.link))
                except IOError:
                    dict_for_file = sFn.infer_parameters_from_descriptors(network.descriptors[self.link], component)

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
            datetime_time_step, time_gap, logger):
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
        :param datetime_time_step:
        :param time_gap: duration of the gap between two simulation time steps
        :param time_gap: float
        :param logger: reference to the logger to be used
        :type logger: Logger
        :return: NOTHING
        """
        if self.category == "CATCHMENT":
            sM.catchment_model(self.identifier, waterbody, dict_nd_data,
                               obj_network.descriptors, self.parameters, self.constants,
                               dict_nd_meteo, dict_nd_loadings,
                               datetime_time_step, time_gap,
                               logger)
        elif self.category == "RIVER":
            sM.river_model(self.identifier, obj_network, waterbody, dict_nd_data,
                           self.parameters, self.constants, dict_nd_meteo,
                           datetime_time_step, time_gap,
                           logger)
        elif self.category == "LAKE":
            sM.lake_model(self.identifier, waterbody, dict_nd_data,
                          obj_network.descriptors, self.parameters, dict_nd_meteo,
                          datetime_time_step, time_gap,
                          logger)


class TimeFrame:
    """

    """
    def __init__(self, datetime_start, datetime_end,
                 data_increment_in_minutes, simu_increment_in_minutes,
                 expected_simu_slice_length):
        self.start = datetime_start
        self.end = datetime_end
        self.step_data = data_increment_in_minutes
        self.step_simu = simu_increment_in_minutes
        self.series_data = TimeFrame.get_list_datetime(self, 'data')
        self.series_simu = TimeFrame.get_list_datetime(self, 'simu')
        self.slices_simu, self.slices_data = \
            TimeFrame.slice_list_datetime(self, expected_simu_slice_length)

    def get_list_datetime(self, option):
        gap = self.end - self.start
        options = {'data': self.step_data, 'simu': self.step_simu}

        start_index = int(self.step_data / options[option])
        end_index = int(gap.total_seconds() // (options[option] * 60)) + 1

        my_list_datetime = list()
        for factor in xrange(-start_index, end_index, 1):  # add one datetime before start
            my_datetime = self.start + datetime.timedelta(minutes=factor * options[option])
            my_list_datetime.append(my_datetime)

        return my_list_datetime

    def slice_list_datetime(self, expected_length):
        divisor = self.step_data / self.step_simu

        # Adjust the length to make sure that it slices exactly between two steps of the data
        simu_length = (expected_length * self.step_simu) // self.step_data * divisor
        data_length = simu_length / divisor

        my_simu_slices = list()
        my_data_slices = list()

        if simu_length > 0:  # the expected length is longer than one data time step
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
