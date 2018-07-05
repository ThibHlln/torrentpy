from logging import getLogger
from datetime import timedelta
from glob import glob

import inout as io
from .timeframe import get_required_resolution, \
    rescale_time_resolution_of_regular_cumulative_data, \
    rescale_time_resolution_of_regular_mean_data


class DataBase(object):
    def __init__(self, network, timeframe, knowledgebase, in_format,
                 meteo_cumulative=list(), meteo_average=list(),
                 contamination_cumulative=list(), contamination_average=list()):
        self._nw = network
        self._tf = timeframe
        self._kb = knowledgebase
        # for meteorology
        self.meteo = None
        self.meteo_cumulative = meteo_cumulative
        self.meteo_average = meteo_average
        # for contamination
        self.contamination = None
        self.contamination_cumulative = contamination_cumulative
        self.contamination_average = contamination_average
        # for simulation
        self.simulation = None

        # set the input database as required
        self._set_db_for_meteo_links(in_format)
        if network.water_quality:
            self._set_db_for_contamination_links(in_format)

    def _set_db_for_meteo_links(self, in_format):
        """
        This function generates a nested dictionary for each link and stores them in a single dictionary that is
        returned. Each nested dictionary has the dimension of the simulation time slice times the number of
        meteorological variables.
        """
        logger = getLogger('TORRENTpy.db')
        # Read the meteorological input files
        logger.info("Collection meteorological information.")
        db_meteo = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)

        for link in self._nw.links:
            db_meteo[link.name] = get_nd_input_data_from_file(self.meteo_cumulative, self.meteo_average,
                                                              self._tf, self._nw.catchment, link.name,
                                                              in_format, self._nw.in_fld, 'meteorology')
        self.meteo = db_meteo

    def _set_db_for_contamination_links(self, in_format):
        """
        This function generates a nested dictionary for each link and stores them in a single dictionary that is
        returned. Each nested dictionary has the dimension of the simulation time slice times the number of
        contaminant inputs.
        """
        logger = getLogger('TORRENTpy.db')
        # Read the annual loadings file and the application files to distribute the loadings for each time step
        logger.info("Collection contamination information.")
        db_contamination = dict()  # key: waterbody, value: data frame (x: time step, y: meteo data type)

        for link in self._nw.links:
            db_contamination[link.name] = get_nd_input_data_from_file(self.contamination_cumulative,
                                                                      self.contamination_average,
                                                                      self._tf, self._nw.catchment, link.name,
                                                                      in_format, self._nw.in_fld, 'contamination')

        self.contamination = db_contamination

    def set_db_for_links_and_nodes(self, my_simu_slice):
        """
        This function generates a nested dictionary for each node and for each link and stores them in a single
        dictionary that is returned. Each nested dictionary has the dimension of the simulation time slice times
        the number of variables (inputs, states, processes, and outputs) for all the models of the link.

        :param my_simu_slice: list of DateTime to be simulated
        :type my_simu_slice: list
        """
        logger = getLogger('TORRENTpy.db')
        logger.info("> Generating data structures.")
        dict__nd_data = dict()  # key: waterbody, value: data frame (x: time step, y: data type)
        # Create NestedDicts for the nodes
        for node in self._nw.nodes:
            my_dict_with_variables = {c: 0.0 for c in self._nw.variables}
            dict__nd_data[node.name] = \
                {i: dict(my_dict_with_variables) for i in my_simu_slice}
        # Create NestedDicts for the links
        for link in self._nw.links:
            # Create NestedDicts for the links
            my_headers = list()
            for model in link.all_models:
                my_headers += model.inputs_names + model.states_names + model.processes_names + model.outputs_names
            my_dict_with_headers = {c: 0.0 for c in my_headers}
            dict__nd_data[link.name] = \
                {i: dict(my_dict_with_headers) for i in my_simu_slice}

        self.simulation = dict__nd_data


def get_nd_input_data_from_file(cml, avg, tf, catchment, link, in_file_format, in_folder, data_category):
    logger = getLogger('TORRENTpy.db')
    if in_file_format == 'netcdf':
        return get_nd_input_data_from_netcdf_file(cml, avg, tf, catchment, link, in_folder, data_category)
    elif in_file_format == 'csv':
        return get_nd_input_data_from_csv_file(cml, avg, tf, catchment, link, in_folder, data_category)
    else:
        logger.error("The input format type \'{}\' cannot be read by TORRENTpy, "
                     "choose from: \'csv\', \'netcdf\'.".format(in_file_format))
        raise Exception("The input format type \'{}\' cannot be read by TORRENTpy, "
                        "choose from: \'csv\', \'netcdf\'.".format(in_file_format))


def get_nd_input_data_from_csv_file(cml, avg, tf, catchment, link, in_folder, data_category):
    logger = getLogger('TORRENTpy.db')

    nd_data_simu = {c: dict() for c in cml + avg}

    for data_type in cml:  # i.e. cumulative data
        my_data_file = None
        if glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type)):
            if len(glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type))) == 1:
                my_data_file = glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type))[0]
            else:
                logger.error("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_type))
                raise Exception("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_type))
        elif glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category)):
            if len(glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category))) == 1:
                my_data_file = glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category))[0]
            else:
                logger.error("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_category))
                raise Exception("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_category))

        if not my_data_file:
            logger.error(
                "{}{}_{}*.{} or .{} do not exist.".format(in_folder, catchment, link, data_type, data_category))
            raise Exception(
                "{}{}_{}*.{} or .{} do not exist.".format(in_folder, catchment, link, data_type, data_category))

        my_nd_data_data = io.read_csv_timeseries_with_data_checks(my_data_file, tf)

        time_delta_res = get_required_resolution(
            tf.data_needed_start, tf.simu_start,
            timedelta(minutes=tf.data_gap), timedelta(minutes=tf.simu_gap))

        nd_data_simu[data_type] = rescale_time_resolution_of_regular_cumulative_data(
            my_nd_data_data[data_type],
            tf.data_needed_start, tf.data_needed_end, timedelta(minutes=tf.data_gap),
            time_delta_res,
            tf.simu_start, tf.simu_end, timedelta(minutes=tf.simu_gap))

        del my_nd_data_data

    for data_type in avg:  # i.e. average data
        my_data_file = None
        if glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type)):
            if len(glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type))) == 1:
                my_data_file = glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_type))[0]
            else:
                logger.error("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_type))
                raise Exception("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_type))
        elif glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category)):
            if len(glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category))) == 1:
                my_data_file = glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category))[0]
            else:
                logger.error("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_category))
                raise Exception("{}{}_{}*.{} exists more than once.".format(in_folder, catchment, link, data_category))

        if not my_data_file:
            logger.error(
                "{}{}_{}*.{} or .{} do not exist.".format(in_folder, catchment, link, data_type, data_category))
            raise Exception(
                "{}{}_{}*.{} or .{} do not exist.".format(in_folder, catchment, link, data_type, data_category))

        my_nd_data_data = io.read_csv_timeseries_with_data_checks(my_data_file, tf)

        time_delta_res = get_required_resolution(
            tf.data_needed_start, tf.simu_start,
            timedelta(minutes=tf.data_gap), timedelta(minutes=tf.simu_gap))

        nd_data_simu[data_type] = rescale_time_resolution_of_regular_mean_data(
            my_nd_data_data[data_type],
            tf.data_needed_start, tf.data_needed_end, timedelta(minutes=tf.data_gap),
            time_delta_res,
            tf.simu_start, tf.simu_end, timedelta(minutes=tf.simu_gap))

        del my_nd_data_data

    return nd_data_simu


def get_nd_input_data_from_netcdf_file(cml, avg, tf, catchment, link, in_folder, data_category):
    logger = getLogger('TORRENTpy.db')

    nd_data_simu = {c: dict() for c in cml + avg}

    for data_type in cml:  # i.e. cumulative data
        my_data_file = None
        if glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, data_type)):
            if len(glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, data_type))) == 1:
                my_data_file = glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, data_type))[0]
            else:
                logger.error("{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, data_type))
                raise Exception("{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, data_type))
        elif glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category)):
            if len(glob('{}{}_{}*.{}'.format(in_folder, catchment, link, data_category))) == 1:
                my_data_file = glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, data_category))[0]
            else:
                logger.error(
                    "{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, data_category))
                raise Exception(
                    "{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, data_category))

        if not my_data_file:
            logger.error(
                "{}{}_{}*.{}.nc or .{}.nc do not exist.".format(in_folder, catchment, link, data_type, data_category))
            raise Exception(
                "{}{}_{}*.{}.nc or .{}.nc do not exist.".format(in_folder, catchment, link, data_type, data_category))

        my_nd_data_data = io.read_netcdf_timeseries_with_data_checks(my_data_file, tf)

        time_delta_res = get_required_resolution(
            tf.data_needed_start, tf.simu_start,
            timedelta(minutes=tf.data_gap), timedelta(minutes=tf.simu_gap))

        nd_data_simu[data_type] = rescale_time_resolution_of_regular_cumulative_data(
            my_nd_data_data[data_type],
            tf.data_needed_start, tf.data_needed_end, timedelta(minutes=tf.data_gap),
            time_delta_res,
            tf.simu_start, tf.simu_end, timedelta(minutes=tf.simu_gap))

        del my_nd_data_data

    for data_type in avg:  # i.e. average data
        my_data_file = None
        for ext in [data_type, data_category]:
            if glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, ext)):
                if len(glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, ext))) == 1:
                    my_data_file = glob('{}{}_{}*.{}.nc'.format(in_folder, catchment, link, ext))[0]
                else:
                    logger.error("{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, ext))
                    raise Exception("{}{}_{}*.{}.nc exists more than once.".format(in_folder, catchment, link, ext))
        if not my_data_file:
            logger.error(
                "{}{}_{}*.{}.nc or .{}.nc do not exist.".format(in_folder, catchment, link, data_type, data_category))
            raise Exception(
                "{}{}_{}*.{}.nc or .{}.nc do not exist.".format(in_folder, catchment, link, data_type, data_category))

        my_nd_data_data = io.read_netcdf_timeseries_with_data_checks(my_data_file, tf)

        time_delta_res = get_required_resolution(
            tf.data_needed_start, tf.simu_start,
            timedelta(minutes=tf.data_gap), timedelta(minutes=tf.simu_gap))

        nd_data_simu[data_type] = rescale_time_resolution_of_regular_mean_data(
            my_nd_data_data[data_type],
            tf.data_needed_start, tf.data_needed_end, timedelta(minutes=tf.data_gap),
            time_delta_res,
            tf.simu_start, tf.simu_end, timedelta(minutes=tf.simu_gap))

        del my_nd_data_data

    return nd_data_simu
