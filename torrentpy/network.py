import logging
from logging import getLogger
import os
import csv
from datetime import timedelta
from itertools import izip

import torrentpy.inout as io


class Network(object):
    """
    This class defines all the constituting parts of a catchment models as a node-link network, as well as the
    different relationships between the nodes and the links, and the characteristics of the links.
    """
    def __init__(self, catchment, outlet, in_fld, out_fld,
                 variable_h, variables_q=None, verbose=True, water_quality=False):
        # identifier for the catchment
        self.catchment = catchment
        # identifier for the catchment outlet
        self.outlet = outlet
        # path of the folders and files necessary to generate the Network object
        self.in_fld = in_fld
        self.out_fld = out_fld
        if not os.path.exists(out_fld):  # create the output folder if it does not already exist
            os.makedirs(out_fld)
        self.network_file = '{}{}_{}.network'.format(in_fld, catchment, outlet)
        self.waterbodies_file = '{}{}_{}.waterbodies'.format(in_fld, catchment, outlet)
        self.descriptors_file = '{}{}_{}.descriptors'.format(in_fld, catchment, outlet)
        # Logger to output in console and in log file
        self._set_logger(verbose)
        # Write the first logging message to inform of the start of the simulation for this catchment
        logger = getLogger('TORRENTpy.nw')
        logger.warning("Starting TORRENTpy session for {} at {}.".format(self.catchment, self.outlet))
        # boolean for water quality simulations
        self.water_quality = water_quality
        # list of the Nodes contained in the Network, mapping of Nodes to find them using their name
        # list of the Links contained in the Network, mapping of Links to find them using their name
        self.nodes, self.nodes_mapping, self.links, self.links_mapping = self._set_network_connectivity()
        # list of the different unique link categories in the network (rivers only or lakes and rivers)
        self.links_categories = None
        # set the categories for the links = code to identify the type of catchment (1 for river or 2 for lake)
        self._set_links_categories()
        # set the descriptors for the links = physical descriptors characteristic of a given catchment
        self._set_links_descriptors()
        # list of the variables to be propagated through the node-link network
        self.variable_h = variable_h
        self.variables_q = variables_q if water_quality and variables_q else []
        self.variables = [self.variable_h] + self.variables_q
        # boolean to state whether Links were assigned Models
        self.links_have_models = False

    def _set_logger(self, verbose):
        """
        This function creates a logger in order to print in console as well as to save in .log file information
        about the simulation. The level of detail displayed is the console is customisable using the 'verbose'
        parameter. If it is True, more information will be displayed (logging.INFO) than if it is False
        (logging.WARNING only).

        :param verbose: boolean to define the level of information the logger should report
        """
        # Create Logger [ levels: debug < info < warning < error < critical ]
        logger = logging.getLogger('TORRENTpy')
        logger.setLevel(logging.INFO)
        # Create FileHandler
        log_file = '{}{}_{}.simu.log'.format(self.out_fld, self.catchment, self.outlet)
        if os.path.isfile(log_file):  # del file if already exists
            os.remove(log_file)
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.INFO)
        # Create StreamHandler
        s_handler = logging.StreamHandler()
        if verbose:  # specify level of information required by the user
            s_handler.setLevel(logging.INFO)
        else:
            s_handler.setLevel(logging.WARNING)
        # Create Formatter
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%d/%m/%Y - %H:%M:%S')
        # Apply Formatter and Handler
        f_handler.setFormatter(formatter)
        s_handler.setFormatter(formatter)
        logger.addHandler(f_handler)
        logger.addHandler(s_handler)

    def _set_network_connectivity(self):
        """
        This method reads all the information contained in the network file in order to get the list of the nodes and
        the links as well as the connections, and the links adding to the nodes and routed by the nodes.
        :return: dictionary containing nodes, links, connections, routing, and adding
        """
        logger = getLogger('TORRENTpy.nw')
        try:
            with open(self.network_file) as my_file:
                my_reader = csv.DictReader(my_file)
                my_nodes = list()  # list of all nodes
                my_links = list()  # list of all links (i.e. waterbodies)
                my_connections = dict()  # key: waterbody, value: 2-element list (node down, node up)
                my_routing = dict()  # key: node, value: list of links whose reaches are pouring into the node
                my_adding = dict()  # key: node, value: list of links whose catchments are pouring into the node
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

                links = [Link(link, my_connections[link]) for link in my_links]
                links_mapping = {link.name: link for link in links}

                nodes = [Node(node,
                              [links_mapping[link] for link in my_routing[node]],
                              [links_mapping[link] for link in my_adding[node]])
                         for node in my_nodes]
                nodes_mapping = {node.name: node for node in nodes}

            return (
                nodes, nodes_mapping,
                links, links_mapping

            )

        except IOError:
            logger.error("No link-node network file found for {} at {}.".format(self.catchment, self.network_file))
            raise Exception("No link-node network file found for {} at {}.".format(self.catchment, self.network_file))

    def _set_links_categories(self):
        """
        This method reads the attributes of the links from the waterBodies file. It associates the waterbody type code
        (1 for river, 2 for lake) and the headwater status (1 if headwater, 0 if not) to create a 2-digit code.
        :return: dictionary {key: link, value: category as a 2-digit code}
        """
        logger = getLogger('TORRENTpy.nw')
        found = list()
        categories = list()
        try:
            with open(self.waterbodies_file) as my_file:
                my_reader = csv.DictReader(my_file)
                for row in my_reader:
                    if row['WaterBody'] in self.links_mapping:
                        self.links_mapping[row['WaterBody']].category = int(row['WaterBodyTypeCode'])
                        categories.append(int(row['WaterBodyTypeCode']))
                    else:
                        logger.error("{} is in the .waterbodies file but it is not "
                                     "in the .connectivity file.".format(row['WaterBody']))
                        raise Exception("{} is in the .waterbodies file but it is not "
                                        "in the .connectivity file.".format(row['WaterBody']))
                    found.append(row['WaterBody'])

            missing = [wb for wb in self.links_mapping if wb not in found]
            if missing:
                logger.error("The following waterbodies are not in the waterbodies file: {}.".format(missing))
                raise Exception("The following waterbodies are not in the waterbodies file: {}.".format(missing))

            self.links_categories = list(set(categories))

        except IOError:
            logger.error("No waterbodies file found for {}.".format(self.catchment))
            raise Exception("No waterbodies file found for {}.".format(self.catchment))

    def _set_links_descriptors(self):
        """
        This method reads the catchment descriptors from the descriptors file.
        :return: nested dictionary {key: link, value: {key: descriptor_name, value: descriptor_value}}
        """
        logger = getLogger('TORRENTpy.nw')
        try:
            with open(self.descriptors_file) as my_file:
                my_reader = csv.DictReader(my_file)
                fields = my_reader.fieldnames[:]
                fields.remove('WaterBody')
                found = list()
                for row in my_reader:
                    my_dict = dict()
                    for field in fields:
                        my_dict[field] = float(row[field])
                    if row['WaterBody'] in self.links_mapping:
                        self.links_mapping[row['WaterBody']].descriptors = my_dict
                    else:
                        logger.exception("{} is in the .descriptors file but it is not "
                                         "in the .connectivity file.".format(row['WaterBody']))
                    found.append(row['WaterBody'])

            missing = [wb for wb in self.links_mapping if wb not in found]
            if missing:
                logger.error("The following waterbodies are not in the descriptors file: {}.".format(missing))
                raise Exception("The following waterbodies are not in the descriptors file: {}.".format(missing))

        except IOError:
            logger.error("No descriptors file found for {}.".format(self.catchment))
            raise Exception("No descriptors file found for {}.".format(self.catchment))

    def set_links_models(self, kb,
                         catchment_h=None, river_h=None, lake_h=None,
                         catchment_q=None, river_q=None, lake_q=None):
        logger = getLogger('TORRENTpy.nw')

        # check that the models needed are provided
        if 1 in self.links_categories:
            if self.water_quality:
                if not catchment_h:
                    logger.error("The Network contains river basins, but no catchment hydrology model provided.")
                    raise Exception("The Network contains river basins, but no catchment hydrology model provided.")
                if not catchment_q:
                    logger.error("The Network contains river basins, but no catchment water quality model provided.")
                    raise Exception("The Network contains river basins, but no catchment water quality model provided.")
                if not river_h:
                    logger.error("The Network contains river basins, but no river hydrology model provided.")
                    raise Exception("The Network contains river basins, but no river hydrology model provided.")
                if not river_q:
                    logger.error("The Network contains river basins, but no river water quality model provided.")
                    raise Exception("The Network contains river basins, but no river water quality model provided.")
            else:
                if not catchment_h:
                    logger.error("The Network contains river basins, but no catchment hydrology model provided.")
                    raise Exception("The Network contains river basins, but no catchment hydrology model provided.")
                if not catchment_h:
                    logger.error("The Network contains river basins, but no river hydrology model provided.")
                    raise Exception("The Network contains river basins, but no river hydrology model provided.")
        if 2 in self.links_categories:
            if self.water_quality:
                if not lake_h:
                    logger.error("The Network contains lakes, but no lake hydrology model provided.")
                    raise Exception("The Network contains lakes, but no lake hydrology model provided.")
                if not lake_q:
                    logger.error("The Network contains lakes, but no lake water quality model provided.")
                    raise Exception("The Network contains lakes, but no lake water quality model provided.")
            else:
                if not lake_h:
                    logger.error("The Network contains lakes, but no lake hydrology model provided.")
                    raise Exception("The Network contains lakes, but no lake hydrology model provided.")

        if not self.links_have_models:  # check that assignment was not already done
            # assign Models to the Links
            if self.water_quality:  # assign hydrology + water quality Models
                for link in self.links:
                    if link.category == 1:  # river basin
                        link.c_models.append(kb.get_catchment_model(catchment_h)('c', catchment_h))
                        link.c_models.append(kb.get_catchment_model(catchment_q)('c', catchment_q))
                        link.r_models.append(kb.get_river_model(river_h)('r', river_h))
                        link.r_models.append(kb.get_river_model(river_q)('r', river_q))
                    elif link.category == 2:  # lake
                        link.l_models.append(kb.get_lake_model(lake_h)('l', lake_h))
                        link.l_models.append(kb.get_lake_model(lake_q)('l', lake_q))
                    else:  # unknown waterbody type
                        logger.error("Link {}: {} is not a registered type of waterbody.".format(
                            link, link.category))
                        raise Exception("Link {}: {} is not a registered type of waterbody.".format(
                            link, link.category))
            else:  # assign hydrology models only
                for link in self.links:
                    if link.category == 1:  # river basin
                        link.c_models.append(kb.get_catchment_model(catchment_h)('c', catchment_h))
                        link.r_models.append(kb.get_river_model(river_h)('r', river_h))
                    elif link.category == 2:  # lake
                        link.l_models.append(kb.get_lake_model(lake_h)('l', lake_h))
                    else:  # unknown waterbody type
                        logger.error("Link {}: {} is not a registered type of waterbody.".format(
                            link, link.category))
                        raise Exception("Link {}: {} is not a registered type of waterbody.".format(
                            link, link.category))

            for link in self.links:
                # gather all models in one list
                link.all_models = link.c_models + link.r_models + link.l_models
                # set the parameters for all Models of the Links
                for model in link.all_models:
                    model.set_parameters(link, self.catchment, self.outlet, self.in_fld, self.out_fld)
                    model.set_constants(self.in_fld)

            # change Network attributes to state that assignment of Models for all Links is now complete
            self.links_have_models = True
        else:  # assignment already done, ignore reassignment
            logger.warning("Assignment of Models to Links was already done, reassignment was ignored.")

    def set_links_models_from_dict(self, kb,
                                   the_dict):
        logger = getLogger('TORRENTpy.nw')
        if not self.links_have_models:  # check that assignment was not already done
            # assign Models to the Links
            done = list()
            if self.water_quality:  # assign hydrology + water quality Models (i.e. requires a list of 6 models)
                default = False
                default_models = None
                for link_names in the_dict:
                    my_list = the_dict[link_names]
                    for link_name in link_names.split('$'):
                        if link_name in self.links_mapping:
                            try:
                                if my_list[0]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(my_list[0])('c', my_list[0]))
                                if my_list[3]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(my_list[3])('c', my_list[3]))
                                if my_list[1]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(my_list[1])('r', my_list[1]))
                                if my_list[4]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(my_list[4])('r', my_list[4]))
                                if my_list[2]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(my_list[2])('l', my_list[2]))
                                if my_list[5]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(my_list[5])('l', my_list[5]))
                                done.append(link_name)
                            except IndexError:
                                logger.error("Link {} in dictionary of models does not feature "
                                             "a list of 6 models.".format(link_name))
                                raise Exception("Link {} in dictionary of models does not feature "
                                                "a list of 6 models.".format(link_name))
                        elif link_name == 'DEFAULT':
                            default = True
                            default_models = my_list[:]
                        else:
                            logger.error("Link {} is not part of the Network.".format(link_name))
                            raise Exception("Link {} is not part of the Network.".format(link_name))
                if default:
                    for link_name in self.links_mapping:
                        if link_name not in done:
                            try:
                                if default_models[0]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(default_models[0])('c', default_models[0]))
                                if default_models[3]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(default_models[3])('c', default_models[3]))
                                if default_models[1]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(default_models[1])('r', default_models[1]))
                                if default_models[4]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(default_models[4])('r', default_models[4]))
                                if default_models[2]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(default_models[2])('l', default_models[2]))
                                if default_models[5]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(default_models[5])('l', default_models[5]))
                            except IndexError:
                                logger.error("DEFAULT in dictionary of models does not feature "
                                             "a list of 6 models.".format(link_name))
                                raise Exception("DEFAULT in dictionary of models does not feature "
                                                "a list of 6 models.".format(link_name))
                else:  # all links should be done
                    missing = [link for link in self.links_mapping if link not in done]
                    if missing:
                        logger.error("The following links have not been given any model: {}.".format(missing))
                        raise Exception("The following links have not been given any model: {}.".format(missing))

            else:  # i.e. assign Hydrology Models only
                # requires a list of 3 models (if more than 3 is provided, the remainder is ignored)
                default = False
                default_models = None
                for link_names in the_dict:
                    my_list = the_dict[link_names]
                    for link_name in link_names.split('$'):
                        if link_name in self.links_mapping:
                            try:
                                if my_list[0]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(my_list[0])('c', my_list[0]))
                                if my_list[1]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(my_list[1])('r', my_list[1]))
                                if my_list[2]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(my_list[2])('l', my_list[2]))
                                done.append(link_name)
                            except IndexError:
                                logger.error("Link {} in dictionary of models does not feature "
                                             "a list of 3 models.".format(link_name))
                                raise Exception("Link {} in dictionary of models does not feature "
                                                "a list of 3 models.".format(link_name))
                        elif link_name == 'DEFAULT':
                            default = True
                            default_models = my_list[:]
                        else:
                            logger.error("Link {} is not part of the Network.".format(link_name))
                            raise Exception("Link {} is not part of the Network.".format(link_name))
                if default:
                    for link_name in self.links_mapping:
                        if link_name not in done:
                            try:
                                if default_models[0]:
                                    self.links_mapping[link_name].c_models.append(
                                        kb.get_catchment_model(default_models[0])('c', default_models[0]))
                                if default_models[1]:
                                    self.links_mapping[link_name].r_models.append(
                                        kb.get_river_model(default_models[1])('r', default_models[1]))
                                if default_models[2]:
                                    self.links_mapping[link_name].l_models.append(
                                        kb.get_lake_model(default_models[2])('l', default_models[2]))
                            except IndexError:
                                logger.error("DEFAULT in dictionary of models does not feature "
                                             "a list of 3 models.".format(link_name))
                                raise Exception("DEFAULT in dictionary of models does not feature "
                                                "a list of 3 models.".format(link_name))
                else:  # all links should be done
                    missing = [link for link in self.links_mapping if link not in done]
                    if missing:
                        logger.error("The following links have not been given any model: {}.".format(missing))
                        raise Exception("The following links have not been given any model: {}.".format(missing))

            for link in self.links:
                # gather all models in one list
                link.all_models = link.c_models + link.r_models + link.l_models
                # set the parameters and constants for all Models of the Links
                for model in link.all_models:
                    model.set_parameters(link, self.catchment, self.outlet, self.in_fld, self.out_fld)
                    model.set_constants(self.in_fld)

            # change Network attributes to state that assignment of Models for all Links is now complete
            self.links_have_models = True
        else:  # assignment already done, ignore reassignment
            logger.warning("Assignment of Models to Links was already done, reassignment was ignored.")

    def simulate(self, db, tf, out_format):

        logger = getLogger('TORRENTpy.nw')

        # create empty output files
        io.create_simulation_files(self, out_format)

        # Set the initial conditions ('blank' warm up run slice by slice) if required
        my_last_lines = dict()
        if tf.warm_up:  # Warm-up run required
            logger.info("Determining initial conditions.")
            # Initialise dicts needed to link time slices together (use last time step of one as first for the other)
            for link in self.links:
                # For links, get a dict of the models states initial conditions from "educated guesses"
                my_last_lines[link.name] = dict()
                for model in link.all_models:
                    my_last_lines[link.name].update(model.initialise(link))
            for node in self.nodes:
                # For nodes, no states so no initial conditions, but instantiation of dict required
                my_last_lines[node.name] = dict()

            for my_simu_slice, my_save_slice in izip(tf.warm_up.simu_slices, tf.warm_up.save_slices):
                logger.info("Running Warm-Up Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                                     my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
                # Initialise data models
                db.set_db_for_links_and_nodes(my_simu_slice)

                # Get history of previous time slice last time step for initial conditions of current time slice
                for link in self.links:
                    db.simulation[link.name][my_simu_slice[0]].update(my_last_lines[link.name])
                for node in self.nodes:
                    db.simulation[node.name][my_simu_slice[0]].update(my_last_lines[node.name])

                # Simulate
                self.run(db, tf, my_simu_slice)

                # Save history (last time step) for next slice
                for link in self.links:
                    my_last_lines[link.name].update(db.simulation[link.name][my_simu_slice[-1]])
                for node in self.nodes:
                    my_last_lines[node.name].update(db.simulation[node.name][my_simu_slice[-1]])

            # "Garbage collection"
            db.simulation = None

        else:  # Warm-up run not required
            # Initialise dicts needed to link time slices together (use last time step of one as first for the other)
            for link in self.links:
                # For links, get a dict of the models states initial conditions from "educated guesses"
                my_last_lines[link.name] = dict()
                for model in link.all_models:
                    my_last_lines[link.name].update(model.initialise(link))
            for node in self.nodes:
                # For nodes, no states so no initial conditions, but instantiation of dict required
                my_last_lines[node.name] = dict()

        # Simulate (run slice by slice)
        logger.info("Starting the simulation.")
        # Get meteo input data
        for my_simu_slice, my_save_slice in izip(tf.simu_slices, tf.save_slices):

            logger.info("Running Period {} - {}.".format(my_simu_slice[1].strftime('%d/%m/%Y %H:%M:%S'),
                                                         my_simu_slice[-1].strftime('%d/%m/%Y %H:%M:%S')))
            # Initialise data models
            db.set_db_for_links_and_nodes(my_simu_slice)

            # Get history of previous time step for initial conditions of current time step
            for link in self.links:
                db.simulation[link.name][my_simu_slice[0]].update(my_last_lines[link.name])
            for node in self.nodes:
                db.simulation[node.name][my_simu_slice[0]].update(my_last_lines[node.name])

            # Simulate
            self.run(db, tf, my_simu_slice)

            # Write results in files
            io.update_simulation_files(self, tf, my_save_slice, db, out_format, method='summary')

            # Save history (last time step) for next slice
            for link in self.links:
                my_last_lines[link.name].update(db.simulation[link.name][my_simu_slice[-1]])
            for node in self.nodes:
                my_last_lines[node.name].update(db.simulation[node.name][my_simu_slice[-1]])

            # "Garbage collection"
            db.simulation = None

        logger.warning("Ending TORRENTpy session for {} at {}.".format(self.catchment, self.outlet))

    def run(self, db, tf, timeslice):
        """
        This function runs the simulations for a given catchment (defined by a Network object) and given time period
        (defined by the time slice). For each time step, it first runs the models associated with the links (defined
        as Model objects), then it sums up all of what is arriving at each node.

        N.B. The first time step in the time slice is ignored because it is for the initial or previous conditions that
        are needed for the models to get the previous states of the links.

        :param db: DataBase object containing:
            simulation: the nested dictionaries for the nodes and the links for variables
                { key = link/node: value = nested_dictionary(index=datetime,column=variable) }
            meteo: the nested dictionaries for the links for meteorological inputs
                { key = link: value = nested_dictionary(index=datetime,column=meteo_input) }
            contamination: the nested dictionaries for the links for contaminant inputs
                { key = link: value = nested_dictionary(index=datetime,column=contaminant_input) }
        :param tf: TimeFrame object for the simulation period
        :type tf: TimeFrame
        :param timeslice: list of DateTime to be simulated
        :type timeslice: list()
        """
        logger = getLogger('TORRENTpy.nw')
        logger.info("> Simulating.")
        my_dict_variables = dict()
        logger_simu = getLogger('TORRENTpy.sm')
        for variable in self.variables:
            my_dict_variables[variable] = 0.0
        for step in timeslice[1:]:  # ignore the index 0 because it is the initial conditions
            # Calculate water (and contaminant) runoff from catchment for each link
            for link in self.links:
                if link.c_models:
                    for model in link.c_models:
                        model.simulate(db, tf, step, link, logger_simu)
            # Sum up everything coming towards each node
            delta = timedelta(minutes=tf.simu_gap)
            for node in self.nodes:
                # Sum up outputs for hydrology
                variable_h = self.variable_h
                for link in node.routing:  # for the streams of the links upstream of the node
                    if link.category == 1:  # river basin
                        my_dict_variables[variable_h] += \
                            db.simulation[link.name][step - delta][''.join(['r_out_', variable_h])]
                    elif link.category == 2:  # lake
                        my_dict_variables[variable_h] += \
                            db.simulation[link.name][step - delta][''.join(['l_out_', variable_h])]
                for link in node.adding:  # for the catchment of the link downstream of this node
                    if link.category == 1:  # river basin
                        my_dict_variables[variable_h] += db.simulation[link.name][step][''.join(['c_out_', variable_h])]
                db.simulation[node.name][step - delta][variable_h] = my_dict_variables[variable_h]
                # Sum up outputs for water quality
                if self.water_quality:
                    for variable in self.variables_q:
                        for link in node.routing:  # for the streams of the links upstream of the node
                            if link.category == 1:  # river basin
                                my_dict_variables[variable] += \
                                    db.simulation[link.name][step - delta][''.join(['r_out_', variable])] * \
                                    db.simulation[link.name][step - delta][''.join(['r_out_', variable_h])]
                            elif link.category == 2:  # lake
                                my_dict_variables[variable] += \
                                    db.simulation[link.name][step - delta][''.join(['l_out_', variable])] * \
                                    db.simulation[link.name][step - delta][''.join(['l_out_', variable_h])]
                        for link in node.adding:  # for the catchment of the link downstream of this node
                            if link.category == 1:  # river basin
                                my_dict_variables[variable] += \
                                    db.simulation[link.name][step][''.join(['c_out_', variable])] * \
                                    db.simulation[link.name][step][''.join(['c_out_', variable_h])]
                        if my_dict_variables[variable_h] > 0.0:
                            db.simulation[node.name][step - delta][variable] = \
                                my_dict_variables[variable] / my_dict_variables[variable_h]
                # Reset values to zero for next node
                for variable in self.variables:
                    my_dict_variables[variable] = 0.0
            # Calculate water (and contaminant) routing in river reach for each link
            for link in self.links:
                if link.r_models:
                    for model in link.r_models:
                        model.simulate(db, tf, step, link, logger_simu)
            # Calculate water (and contaminant) routing in lake for each link
            for link in self.links:
                if link.l_models:
                    for model in link.l_models:
                        model.simulate(db, tf, step, link, logger_simu)

        # Sum up everything that was routed towards each node at penultimate time step
        step = timeslice[-1]
        for node in self.nodes:
            # Sum up outputs for hydrology
            variable_h = self.variable_h
            for link in node.routing:  # for the streams of the links upstream of the node
                if link.category == 1:  # river
                    my_dict_variables[variable_h] += db.simulation[link.name][step][''.join(['r_out_', variable_h])]
                elif link.category == 2:  # lake
                    my_dict_variables[variable_h] += db.simulation[link.name][step][''.join(['l_out_', variable_h])]
            db.simulation[node.name][step][variable_h] = my_dict_variables[variable_h]
            # Sum up output for water quality
            if self.water_quality:
                for variable in self.variables_q:
                    for link in node.routing:  # for the streams of the links upstream of the node
                        if link.category == 1:  # river basin
                            my_dict_variables[variable] += db.simulation[link.name][step][
                                                               ''.join(['r_out_', variable])] * \
                                                           db.simulation[link.name][step][
                                                               ''.join(['r_out_', variable_h])]
                        elif link.category == 2:  # lake
                            my_dict_variables[variable] += db.simulation[link.name][step][
                                                               ''.join(['l_out_', variable])] * \
                                                           db.simulation[link.name][step][
                                                               ''.join(['l_out_', variable_h])]
                    if my_dict_variables[variable_h] > 0.0:
                        db.simulation[node.name][step][variable] = my_dict_variables[variable] / my_dict_variables[
                            variable_h]
                    my_dict_variables[variable] = 0.0
            my_dict_variables[variable_h] = 0.0


class Link(object):
    def __init__(self, name, connections):
        self.name = name
        self.connections = connections
        self.category = None
        self.descriptors = None
        self.c_models = []
        self.r_models = []
        self.l_models = []
        self.all_models = None
        self.models_parameters = dict()
        self.extra = dict()


class Node(object):
    def __init__(self, name, routing, adding):
        self.name = name
        self.routing = routing
        self.adding = adding
        self.extra = dict()
