from multiprocessing import Pool, cpu_count
from os import path, chdir
from csv import DictReader
from sys import exit

import simuRunSingle as sRS


def get_arguments_from_batch_file():
    root = path.realpath('..')  # move to parent directory of this current python file
    chdir(root)  # define parent directory as root in order to use only relative paths after this
    input_directory = "in/"

    try:
        with open('{}simulation.batch'.format(input_directory), 'rb') as my_file:
            my_reader = DictReader(my_file)
            my_list_of_tuples = list()
            for line in my_reader:
                my_list_of_tuples.append((line['Catchment'], line['OUTLET'],
                                          int(line['#SliceUp']), int(line['#WarmUp'])))

        return my_list_of_tuples
    except IOError:
        exit('{}simulation.batch does not exist.'.format(input_directory))


def single_run(catchment, outlet, slice_up, warm_up):
    """
    This function allows to call the function responsible for the simulation of one catchment for one time period.
    It avoids calling the single run simulator with arguments in command lines by providing the arguments as parameters
    of its main function.
    :param catchment: name of the catchment
    :param outlet: european code of the outlet of the catchment
    :param slice_up: length of the time slices over the time period
    :param warm_up: durations of the warm-up
    :return: NOTHING
    """
    sRS.main(catchment, outlet, slice_up, warm_up)


def single_run_star(args):
    """
    This function unpacks a tuple of arguments to be given to a function call.
    i.e. it converts a function call f_star( (a, b, c, ...) ) into f(a, b, c, ...).
    :param args: tuple of arguments (catchment, outlet, slice_up, warm_up)
    :return: a call to the single_run function with unpacked arguments
    """
    return single_run(*args)


if __name__ == '__main__':
    cores = cpu_count()
    pool = Pool(processes=cores, maxtasksperchild=1)

    arguments = get_arguments_from_batch_file()

    pool.map_async(single_run_star, iterable=arguments)
    pool.close()
    pool.join()
