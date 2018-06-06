from datetime import timedelta
from collections import OrderedDict


def increase_time_resolution_of_irregular_mean_data(dict_info, time_delta_lo, time_delta_hi):
    """
    Create high resolution mean data from lower resolution mean data
    using backwards duplication.
    """
    new_dict_info = dict()
    # get the series of DateTime in the data
    my_dts = dict_info.keys()
    for i, my_dt in enumerate(my_dts[1:]):
        # determine the duration of the cumulative data between the two time steps
        my_delta = my_dt - my_dts[i]
        if my_delta >= timedelta(seconds=1.5 * time_delta_lo.total_seconds()):
            my_delta = time_delta_lo
        # determine the number of hours the cumulative data has to be spread over
        (divisor, remainder) = divmod(int(my_delta.total_seconds()), int(time_delta_hi.total_seconds()))
        if remainder != 0:
            raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
        elif divisor < 1:
            raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                            "{} < {}.".format(my_delta, time_delta_hi))
        # determine the high resolution value
        try:
            my_value = float(dict_info[my_dt])
        except ValueError:  # no data for this time step
            my_value = ''
        # spread the hourly value backwards
        for my_sub_step in xrange(0, -divisor, -1):
            if new_dict_info.get(my_dt + my_sub_step * time_delta_hi):  # should not happen
                raise Exception("Increase Resolution: Overwriting already existing data for datetime.")
            else:
                new_dict_info[my_dt + my_sub_step * time_delta_hi] = my_value

    return new_dict_info


def decrease_time_resolution_of_irregular_mean_data(dict_info, dt_start, dt_end, time_delta_hi, time_delta_lo):
    """ Creates low resolution cumulative data from high resolution cumulative data
    using arithmetic mean. """
    my_dt = dt_start
    new_dict_info = OrderedDict()

    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    while (dt_start <= my_dt) and (my_dt <= dt_end):
        try:
            my_values = 0.0
            for my_sub_step in xrange(0, -divisor, -1):
                my_values += dict_info[my_dt + my_sub_step * time_delta_hi]
            new_dict_info[my_dt] = my_values / divisor
            my_dt += time_delta_lo
        except KeyError:  # at least one of the values is not available (i.e. missing value)
            my_dt += time_delta_lo
        except TypeError:  # at least one of the values was not a float [string] (i.e. missing value)
            my_dt += time_delta_lo

    return new_dict_info


def rescale_time_resolution_of_irregular_mean_data(dict_data, start_data, end_data, time_delta_lo, time_delta_hi):
    my_tmp_dict = increase_time_resolution_of_irregular_mean_data(dict_data, time_delta_lo, time_delta_hi)
    my_new_dict = decrease_time_resolution_of_irregular_mean_data(my_tmp_dict, start_data, end_data,
                                                                  time_delta_hi, time_delta_lo)

    return my_new_dict
