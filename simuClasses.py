import csv
import sys
import datetime

from scripts import simuModels as sM


class Network:
    """"""
    def __init__(self, catchment, input_folder):
        self.name = catchment.capitalize()
        self.networkFile = "{}{}_networkLinksNodes".format(input_folder, catchment)
        self.waterBodiesFile = "{}{}_waterBodies".format(input_folder, catchment)
        self.nodes = Network.get_network_attributes(self)["nodes"]
        self.links = Network.get_network_attributes(self)["links"]
        self.connections = Network.get_network_attributes(self)["connections"]
        self.additions = Network.get_network_attributes(self)["additions"]
        self.categories = Network.get_water_bodies_attributes(self)

    def get_network_attributes(self):
        try:
            with open(self.networkFile) as my_file:
                my_reader = csv.DictReader(my_file)
                my_nodes = list()
                my_links = list()
                my_connections = dict()
                my_additions = dict()
                for row in my_reader:
                    my_nodes.append(row['NodeDown'])
                    my_nodes.append(row['NodeUp'])
                    my_links.append(row['WaterBody'])
                    my_connections[row['WaterBody']] = (row['NodeDown'], row['NodeUp'])
                my_nodes = list(set(my_nodes))
                for node in my_nodes:
                    my_additions[node] = list()
                for link in my_connections:
                    my_additions[my_connections[0]].append(link)

        except EnvironmentError:
            sys.exit("No link-node network file found for {}.".format(self.name))

        return {
            "nodes": my_nodes,
            "links": my_links,
            "connections": my_connections,
            "additions": my_additions
        }

    def get_water_bodies_attributes(self):
        try:
            with open(self.waterBodiesFile) as my_file:
                my_reader = csv.DictReader(my_file)
                my_categories = dict()
                for row in my_reader:
                    my_categories[row['WaterBody']] = row['WaterBodyTypeCode'] + row['HeadwaterStatus']

        except EnvironmentError:
            sys.exit("No link-node network file found for {}.".format(self.name))

        return my_categories


class WaterBody:
    """"""
    def __init__(self, category, code, node_up, node_down):
        self.category = category
        self.code = code
        self.nodeUp = node_up
        self.nodeDown = node_down


class Model:
    """"""
    def __init__(self, identifier, specs_folder):
        self.identifier = identifier.upper()
        self.input_names = Model.get_one_list(self, specs_folder, "inputs")
        self.parameter_names = Model.get_one_list(self, specs_folder, "parameters")
        self.state_names = Model.get_one_list(self, specs_folder, "states")
        self.output_names = Model.get_one_list(self, specs_folder, "outputs")

    def get_one_list(self, specs_folder, specs_type):
        try:
            with open(specs_folder + self.identifier + ".spec") as my_file:
                my_reader = csv.reader(my_file)
                my_string = list()
                count = 0
                for row in my_reader:
                    if row[0] == specs_type:
                        my_string = row[1]
                        count += 1
                if count == 0:
                    sys.exit("There is no {} specifications line in {}{}".format(specs_type, specs_folder,
                                                                                 self.identifier))
                elif count > 1:
                    sys.exit("There is more than one input specifications line in {}{}".format(specs_type, specs_folder,
                                                                                               self.identifier))
        except EnvironmentError:
            sys.exit("There is no specifications file for {} in {} model.".format(self.identifier, specs_folder))
        return my_string.split(";")

    def run(self, obj_network, obj_waterbody, dict_data_frame, dict_meteo, datetime_time_step):
        if self.identifier == "SMART":
            sM.smart(obj_network, obj_waterbody, dict_data_frame, dict_meteo, datetime_time_step)
        elif self.identifier == "LINRES":
            sM.linres(obj_network, obj_waterbody, dict_data_frame, dict_meteo, datetime_time_step)
        elif self.identifier == "BATHTUB":
            sM.bathtub(obj_network, obj_waterbody, dict_data_frame, dict_meteo, datetime_time_step)


class TimeFrame:
    """"""
    def __init__(self, datetime_start, datetime_end, increment_in_minutes):
        self.start = datetime_start
        self.end = datetime_end
        self.step = increment_in_minutes

    def get_list_datetime(self):
        gap = self.end - self.end
        gap_in_minutes = int(gap.total_seconds()) // 60
        my_list_datetime = list()
        for time_step in range(0, gap_in_minutes + 1, 1):
            my_datetime = self.start + datetime.timedelta(minutes=time_step)
            my_list_datetime.append(my_datetime)

        return my_list_datetime
