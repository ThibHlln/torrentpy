import logging
from multiprocessing import Pool
from os import chdir
from csv import DictReader


import postprocPerf as ppPf
import postprocPlot as ppPl


def get_arguments_from_batch_file(batch_file):
    try:
        with open(batch_file, 'rb') as my_file:
            my_reader = DictReader(my_file)
            my_list_of_tuples = list()
            for line in my_reader:
                my_list_of_tuples.append((line['Catchment'], line['Outlet'], line['Gauge']))

        return my_list_of_tuples
    except IOError:
        raise Exception('{} does not exist.'.format(batch_file))


def single_run(catchment, outlet, gauge):
    """
    :param catchment: name of the catchment
    :param outlet: european code of the outlet of the catchment
    :param gauge: identification number of the hydrometric station
    :return: NOTHING
    """
    logger = logging.getLogger("MultiPostProc")
    logger.setLevel(logging.ERROR)
    try:
        ppPl.main(catchment, outlet, gauge)
        ppPf.main(catchment, outlet, gauge)
    except Exception as e:
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
    chdir("C:/PycharmProjects/Python/CatchmentSimulationFramework/")  # define root
    input_dir = "in/"
    output_dir = "out/"

    my_batch_file = '{}/postprocessing.batch'.format(input_dir)

    pool = Pool(processes=1, maxtasksperchild=1)

    arguments = get_arguments_from_batch_file(my_batch_file)

    results = pool.imap_unordered(single_run_star, iterable=arguments)

    pool.close()
    pool.join()
