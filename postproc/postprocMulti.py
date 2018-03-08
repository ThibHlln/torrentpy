import logging
from multiprocessing import Pool, log_to_stderr
from os import path
from csv import DictReader


import postprocPerf as ppPf
import postprocPlot as ppPl


def get_arguments_from_batch_file(batch_file, root, log_file):
    try:
        with open(batch_file, 'rb') as my_file:
            my_reader = DictReader(my_file)
            my_list_of_tuples = list()
            for line in my_reader:
                my_list_of_tuples.append((line['Catchment'], line['Outlet'], line['Gauge'],
                                          root, log_file))

        return my_list_of_tuples
    except IOError:
        raise Exception('{} does not exist.'.format(batch_file))


def single_run(catchment, outlet, gauge, root, log_file):
    """
    :param catchment: name of the catchment
    :param outlet: european code of the outlet of the catchment
    :param gauge: identification number of the hydrometric station
    :param root: location of the root of the CSF folder
    :param log_file: location of the log file to use for the FileHandler
    :return: NOTHING
    """
    mp_logger = log_to_stderr()
    mp_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                           datefmt="%d/%m/%Y - %H:%M:%S"))
    logger = logging.getLogger("MultiPostProc")
    logger.addHandler(handler)
    try:
        ppPl.main(catchment, outlet, gauge, root)
        ppPf.main(catchment, outlet, gauge, root)
    except Exception as e:
        mp_logger.error('Exception for arguments ({}, {}, {})'.format(catchment, outlet, gauge))
        logger.error('Exception for arguments ({}, {}, {})'.format(catchment, outlet, gauge))
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
    csf_root = path.realpath('../..')  # move to grand-parent directory of this current python file
    input_dir = ''.join([csf_root, "/in/"])
    output_dir = ''.join([csf_root, "/out/"])

    my_log_file = '{}/postprocessing.batch.log'.format(output_dir)
    my_batch_file = '{}/postprocessing.batch'.format(input_dir)

    pool = Pool(processes=1, maxtasksperchild=1)

    arguments = get_arguments_from_batch_file(my_batch_file, csf_root, my_log_file)

    results = pool.imap_unordered(single_run_star, iterable=arguments)

    pool.close()
    pool.join()
