from multiprocessing import Pool, cpu_count, log_to_stderr
from os import path, remove, getcwd
from csv import DictReader
from sys import exit
import logging

import CSFrun as csfR


def setup_logger(name, log_file, level=logging.DEBUG):
    # Create Formatter
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt="%d/%m/%Y - %H:%M:%S")
    # Create FileHandler
    if path.isfile(log_file):
        remove(log_file)
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    # Create Logger [ levels: debug < info < warning < error < critical ]
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)


def get_arguments_from_batch_file(batch_file, root, log_file):
    try:
        with open(batch_file, 'rb') as my_file:
            my_reader = DictReader(my_file)
            my_list_of_tuples = list()
            for line in my_reader:
                my_list_of_tuples.append((line['Catchment'], line['OUTLET'],
                                          int(line['#SliceUp']), int(line['#WarmUp']),
                                          root, log_file))

        return my_list_of_tuples
    except IOError:
        exit('{} does not exist.'.format(batch_file))


def single_run(catchment, outlet, slice_up, warm_up, root, log_file):
    """
    This function allows to call the function responsible for the simulation of one catchment for one time period.
    It avoids calling the single run simulator with arguments in command lines by providing the arguments as parameters
    of its main function.
    :param catchment: name of the catchment
    :param outlet: european code of the outlet of the catchment
    :param slice_up: length of the time slices over the time period
    :param warm_up: durations of the warm-up
    :param root: location of the root of the CSF folder
    :param log_file: location of the log file to use for the FileHandler
    :return: NOTHING
    """
    mp_logger = log_to_stderr()
    mp_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                           datefmt="%d/%m/%Y - %H:%M:%S"))
    logger = logging.getLogger("MultiRun.single_run")
    logger.addHandler(handler)
    try:
        csfR.main(catchment, outlet, slice_up, warm_up, root)
    except Exception as e:
        mp_logger.error('Exception for arguments ({}, {}, {}, {})'.format(catchment, outlet, slice_up, warm_up))
        logger.error('Exception for arguments ({}, {}, {}, {})'.format(catchment, outlet, slice_up, warm_up))
        logger.exception(e)
        raise e


def single_run_star(args):
    """
    This function unpacks a tuple of arguments to be given to a function call.
    i.e. it converts a function call f_star( (a, b, c, ...) ) into f(a, b, c, ...).
    :param args: tuple of arguments (catchment, outlet, slice_up, warm_up)
    :return: a call to the single_run function with unpacked arguments
    """
    return single_run(*args)


if __name__ == '__main__':
    # Define the root of the CSF package
    if getcwd() == path.dirname(path.realpath(__file__)):  # execution from the directory where the script is
        csf_root = path.realpath('..')  # move to parent of parent directory of this current python file
    else:  # execution not from the directory where the script is
        csf_root = getcwd()  # keep the current working directory

    input_dir = ''.join([csf_root, "/in/"])
    output_dir = ''.join([csf_root, "/out/"])

    my_log_file = '{}/simulation.batch.log'.format(output_dir)
    my_batch_file = '{}/simulation.batch'.format(input_dir)

    setup_logger('MultiRun', my_log_file, level=logging.DEBUG)

    cores = cpu_count()
    pool = Pool(processes=cores, maxtasksperchild=1)
    # 'processes' is the number of simultaneous runs (children) allowed (maximum = number of processors available)
    # 'maxtasksperchild' is set to 1 to kill each child after task completion to make sure to clean memory properly

    arguments = get_arguments_from_batch_file(my_batch_file, csf_root, my_log_file)

    results = pool.imap_unordered(single_run_star, iterable=arguments)

    pool.close()
    pool.join()
