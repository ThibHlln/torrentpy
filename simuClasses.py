import csv
import os
import sys
import datetime
import pandas

import simuModels as sM
import simuFunctions as sFn


class Network:
    """"""
    def __init__(self, catchment, outlet, input_folder, specs_folder):
        self.name = catchment.capitalize()
        self.code = outlet.upper()
        self.networkFile = "{}{}_{}.network".format(input_folder, catchment, outlet)
        self.waterBodiesFile = "{}{}_{}.waterbodies".format(input_folder, catchment, outlet)
        self.descriptorsFile = "{}{}_{}.descriptors".format(input_folder, catchment, outlet)
        self.nodes = Network.get_network_attributes(self)["nodes"]
        self.links = Network.get_network_attributes(self)["links"]
        self.connections = Network.get_network_attributes(self)["connections"]
        self.adding = Network.get_network_attributes(self)["adding"]
        self.routing = Network.get_network_attributes(self)["routing"]
        self.categories = Network.get_waterbodies_attributes(self)
        self.descriptors = Network.get_catchments_descriptors(self)
        self.variables = Network.get_one_list(specs_folder, "variables")

    def get_network_attributes(self):
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
    """"""
    def __init__(self, category, identifier, my__network, link, specs_folder, input_folder, output_folder):
        self.category = category.upper()
        self.identifier = identifier.upper()
        self.link = link.upper()
        self.input_names = Model.get_list_names(self, specs_folder, "inputs")
        self.parameter_names = Model.get_list_names(self, specs_folder, "parameters")
        self.state_names = Model.get_list_names(self, specs_folder, "states")
        self.output_names = Model.get_list_names(self, specs_folder, "outputs")
        self.parameters = Model.get_dict_parameters(self, my__network, specs_folder, input_folder, output_folder)
        self.constants = Model.get_dict_constants(self, specs_folder)

    def get_list_names(self, specs_folder, specs_type):
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

    def run(self, obj_network, waterbody, dict_data_frame,
            dict_meteo, dict_loads,
            datetime_time_step, time_gap, logger):
        if self.category == "CATCHMENT":
            sM.catchment_model(self.identifier, waterbody, dict_data_frame,
                               obj_network.descriptors, self.parameters, self.constants, dict_meteo, dict_loads,
                               datetime_time_step, time_gap,
                               logger)
        elif self.category == "RIVER":
            sM.river_model(self.identifier, obj_network, waterbody, dict_data_frame,
                           self.parameters, self.constants, dict_meteo,
                           datetime_time_step, time_gap,
                           logger)
        elif self.category == "LAKE":
            sM.lake_model(self.identifier, waterbody, dict_data_frame,
                          obj_network.descriptors, self.parameters, dict_meteo,
                          datetime_time_step, time_gap,
                          logger)


class TimeFrame:
    """"""
    def __init__(self, datetime_start, datetime_end, data_increment_in_minutes, simu_increment_in_minutes):
        self.start = datetime_start
        self.end = datetime_end
        self.step_data = data_increment_in_minutes
        self.step_simu = simu_increment_in_minutes
        self.series_data = TimeFrame.get_list_datetime(self, 'data')
        self.series_simu = TimeFrame.get_list_datetime(self, 'simu')

    def get_list_datetime(self, option):
        gap = self.end - self.start
        options = {'data': self.step_data, 'simu': self.step_simu}
        start_index = int(self.step_data / options[option])
        end_index = int(gap.total_seconds() // (options[option] * 60)) + 1
        my_list_datetime = list()
        for factor in range(-start_index, end_index, 1):  # add one datetime before start
            my_datetime = self.start + datetime.timedelta(minutes=factor * options[option])
            my_list_datetime.append(my_datetime)

        return my_list_datetime
