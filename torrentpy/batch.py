from multiprocessing import Pool, cpu_count, log_to_stderr
from csv import DictReader
from datetime import datetime
from os import path, remove, sep
import logging

from torrentpy import *


class Batch(object):
    def __init__(self, kb, batch_file, in_dir, out_dir, **kwargs):
        self.size = 0
        self.kb = kb
        self.jobs = None
        self.in_dir = in_dir
        self.out_dir = out_dir
        # Logger to output in console and in log file
        self.log_file = None
        self._set_logger()
        # Write the first logging message to inform of the start of the batch session
        logger = logging.getLogger('TORRENTpy.bh')
        logger.warning("Starting TORRENTpy Batch Session.")
        # generate a dictionary with all required arguments for each job
        self._set_jobs(batch_file, kwargs)

    def _set_logger(self):
        # Create Logger [ levels: debug < info < warning < error < critical ]
        logger = logging.getLogger('TORRENTpy')
        logger.setLevel(logging.WARNING)
        # Create FileHandler
        log_file = self.out_dir + 'simu.batch.log'
        if path.isfile(log_file):  # del file if already exists
            remove(log_file)
        f_handler = logging.FileHandler(log_file)
        f_handler.setLevel(logging.WARNING)
        # Create StreamHandler
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.WARNING)
        # Create Formatter
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt="%d/%m/%Y - %H:%M:%S")
        # Apply Formatter and Handler
        f_handler.setFormatter(formatter)
        s_handler.setFormatter(formatter)
        logger.addHandler(f_handler)
        logger.addHandler(s_handler)

        self.log_file = log_file

    def _set_jobs(self, batch_file, kwargs):

        my_jobs = list()
        with open(batch_file) as my_file:
            my_reader = DictReader(my_file)
            fields = my_reader.fieldnames[:]
            for row in my_reader:
                my_dict_job = dict()
                for field in fields:
                    if ';' in row[field]:  # it is a list, assume it is a list of strings
                        my_dict_job[field] = row[field].split(';')
                    elif 'dt' in field:  # it is a datetime DD/MM/YY HH:MM:SS
                        my_dict_job[field] = datetime.strptime(row[field], '%d/%m/%Y %H:%M:%S')
                    elif row[field] == 'True':  # it is a boolean
                        my_dict_job[field] = True
                    elif row[field] == 'False':  # it is a boolean
                        my_dict_job[field] = False
                    else:
                        try:  # it is a numerical value (assume it is an integer, because not argument requires float)
                            my_dict_job[field] = int(row[field])
                        except ValueError:  # it is not a numerical value, keep it as a string
                            my_dict_job[field] = str(row[field])
                my_dict_job.update(kwargs)
                self._check_all_args(my_dict_job)
                my_jobs.append(my_dict_job)
                self.size += 1
        self.jobs = my_jobs

    def _check_all_args(self, dict_args):
        logger = logging.getLogger('TORRENTpy.bh')

        mandatory_args = [
            'catchment', 'outlet', 'dt_data_start', 'dt_data_end', 'dt_save_start', 'dt_save_end',
            'variable_h', 'data_increment_in_minutes', 'save_increment_in_minutes',
            'simu_increment_in_minutes'
        ]

        optional_args = {
            'in_format': 'csv', 'out_format': 'csv', 'expected_simu_slice_length': 0, 'verbose': False,
            'catchment_h': None, 'river_h': None, 'lake_h': None, 'variables_q': None,
            'catchment_q': None, 'river_q': None, 'lake_q': None,
            'meteo_cumulative': [], 'meteo_average': [], 'contamination_cumulative': [],
            'contamination_average': [], 'warm_up_in_days': 0, 'water_quality': False
        }

        # check if mandatory arguments are all defined, if not, raise Exception
        for mandatory_arg in mandatory_args:
            if mandatory_arg not in dict_args:
                logger.error("The batch session cannot proceed, "
                             "it is missing the mandatory argument: {}.".format(mandatory_arg))
                raise Exception("The batch session cannot proceed, "
                                "it is missing the mandatory argument: {}.".format(mandatory_arg))
        # check if optional arguments are defined, if not, give them their default value
        for optional_arg in optional_args:
            if optional_arg not in dict_args:
                dict_args[optional_arg] = optional_args[optional_arg]

        # special case for inferring folders from directories
        if 'in_fld' not in dict_args:
            dict_args['in_fld'] = \
                ''.join([self.in_dir, '{}_{}'.format(dict_args['catchment'], dict_args['outlet']), sep])
        if 'out_fld' not in dict_args:
            dict_args['out_fld'] = \
                ''.join([self.out_dir, '{}_{}'.format(dict_args['catchment'], dict_args['outlet']), sep])

    def launch(self):
        logger = logging.getLogger('TORRENTpy.bh')

        cores = cpu_count()
        pool = Pool(processes=cores, maxtasksperchild=1)
        # 'processes' is the number of simultaneous runs (children) allowed (maximum = number of processors available)
        # 'maxtasksperchild' is set to 1 to kill each child after task completion to make sure to clean memory properly

        arguments = [(self.kb, kwargs, self.log_file) for kwargs in self.jobs]

        pool.imap_unordered(run_job_unpacked, iterable=arguments)

        pool.close()
        pool.join()

        logger.warning("Ending TORRENTpy Batch Session.")


def set_up_and_run_job(kb, dict_args):

    nw = Network(
        catchment=dict_args['catchment'],
        outlet=dict_args['outlet'],
        in_fld=dict_args['in_fld'],
        out_fld=dict_args['out_fld'],
        variable_h=dict_args['variable_h'],
        variables_q=dict_args['variables_q'],
        water_quality=dict_args['water_quality'],
        verbose=dict_args['verbose']
    )

    # special case if Links and/or Nodes are given something for the 'extra' attribute
    if 'links_extra' in dict_args:
        for link in nw.links:
            link.extra.update(dict_args['links_extra'])
    if 'nodes_extra' in dict_args:
        for node in nw.nodes:
            node.extra.update(dict_args['nodes_extra'])

    tf = TimeFrame(
        dt_data_start=dict_args['dt_data_start'],
        dt_data_end=dict_args['dt_data_end'],
        dt_save_start=dict_args['dt_save_start'],
        dt_save_end=dict_args['dt_save_end'],
        data_increment_in_minutes=dict_args['data_increment_in_minutes'],
        save_increment_in_minutes=dict_args['save_increment_in_minutes'],
        simu_increment_in_minutes=dict_args['simu_increment_in_minutes'],
        expected_simu_slice_length=dict_args['expected_simu_slice_length'],
        warm_up_in_days=dict_args['warm_up_in_days']
    )

    db = DataBase(
        nw, tf, kb,
        in_format=dict_args['in_format'],
        meteo_cumulative=dict_args['meteo_cumulative'],
        meteo_average=dict_args['meteo_average'],
        contamination_cumulative=dict_args['contamination_cumulative'],
        contamination_average=dict_args['contamination_average']
    )

    nw.set_links_models(
        kb,
        catchment_h=dict_args['catchment_h'],
        river_h=dict_args['river_h'],
        lake_h=dict_args['lake_h'],
        catchment_q=dict_args['catchment_q'],
        river_q=dict_args['river_q'],
        lake_q=dict_args['lake_q']
    )

    nw.simulate(
        db, tf,
        out_format=dict_args['out_format']
    )


def run_job(kb, args, log_file):
    # set up all the loggers required (two required because it is difficult to catch the exception from multiple jobs)
    mp_logger = log_to_stderr()
    mp_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                           datefmt="%d/%m/%Y - %H:%M:%S"))
    logger = logging.getLogger('TORRENTpy.bh')
    logger.addHandler(handler)
    # set up and run for the job passes, and catch and raise exceptions when they show up
    try:
        set_up_and_run_job(kb, args)
    except Exception as e:
        mp_logger.error("Exception for arguments ({}, {})".format(args['catchment'], args['outlet']))
        logger.error("Exception for arguments ({}, {})".format(args['catchment'], args['outlet']))
        logger.exception(e)
        raise e


def run_job_unpacked(args):
    # simple function that unpacks the arguments given as a tuple
    return run_job(*args)
