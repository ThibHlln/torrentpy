from fractions import gcd
from datetime import timedelta


def get_required_resolution(start_data, start_simu, delta_data, delta_simu):
    # GCD(delta_data, delta_simu) gives the maximum time resolution possible to match data and simu
    # shift = start_data - start_simu gives the data shift (e.g. data starting at 8am, simu starting at 9am)
    # GCD(shift, GCD(delta_data, delta_simu)) gives the maximum time resolution to match both the difference in
    # start dates and the difference in data/simu time deltas.
    return timedelta(seconds=gcd((start_data - start_simu).total_seconds(),
                                 gcd(delta_data.total_seconds(), delta_simu.total_seconds())))


def check_interval_in_list(list_of_dt, data_file):
    list_intervals = list()
    for i in range(len(list_of_dt) - 1):
        list_intervals.append(list_of_dt[i+1] - list_of_dt[i])
    interval = list(set(list_intervals))
    if len(interval) == 1:
        if list_of_dt[0] + interval[0] * (len(list_of_dt) - 1) == list_of_dt[-1]:
            return list_of_dt[0], list_of_dt[-1], interval[0]
        else:
            raise Exception('Missing Data: {} is missing at least one datetime in period.'.format(data_file))
    else:
        raise Exception('Inconsistent Interval: {} does not feature a single time interval.'.format(data_file))


def rescale_time_resolution_of_regular_cumulative_data(dict_data,
                                                       start_data, end_data, time_delta_data,
                                                       time_delta_res,
                                                       start_simu, end_simu, time_delta_simu):

    if time_delta_data > time_delta_res:  # i.e. information resolution too low to generate simu timeseries
        my_tmp_dict = increase_time_resolution_of_regular_cumulative_data(dict_data, start_data, end_data,
                                                                          time_delta_data, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_data == time_delta_res (time_delta_data < time_delta_res cannot be true because use of GCD)
        my_tmp_dict = dict_data

    if time_delta_simu > time_delta_res:  # i.e. information resolution too high to generate simu timeseries
        my_new_dict = decrease_time_resolution_of_regular_cumulative_data(my_tmp_dict, start_simu, end_simu,
                                                                          time_delta_simu, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_simu == time_delta_res (time_delta_simu < time_delta_res cannot be true because use of GCD)
        my_new_dict = decrease_time_resolution_of_regular_cumulative_data(my_tmp_dict, start_simu, end_simu,
                                                                          time_delta_simu, time_delta_res)
        # use decrease_data_time_resolution anyway for the only purpose to reduce the size of the dict
        # to the only required DateTimes in the simulation period

    return my_new_dict


def increase_time_resolution_of_regular_cumulative_data(dict_info, start_lo, end_lo,
                                                        time_delta_lo, time_delta_hi):
    """ Use the low resolution to create the high resolution """
    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_value = dict_info[my_dt_lo]
        my_portion = my_value / divisor
        for my_sub_step in xrange(0, -divisor, -1):
            new_dict_info[my_dt_lo + my_sub_step * time_delta_hi] = my_portion
        my_dt_lo += time_delta_lo

    return new_dict_info


def decrease_time_resolution_of_regular_cumulative_data(dict_info, start_lo, end_lo,
                                                        time_delta_lo, time_delta_hi):
    """ Use the high resolution to create the low resolution """
    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_portion = 0.0
        for my_sub_step in xrange(0, -divisor, -1):
            my_portion += dict_info[my_dt_lo + my_sub_step * time_delta_hi]
        new_dict_info[my_dt_lo] = my_portion
        my_dt_lo += time_delta_lo

    return new_dict_info


def rescale_time_resolution_of_regular_mean_data(dict_data,
                                                 start_data, end_data, time_delta_data,
                                                 time_delta_res,
                                                 start_simu, end_simu, time_delta_simu):

    if time_delta_data > time_delta_res:  # i.e. information resolution too low to generate simu timeseries
        my_tmp_dict = increase_time_resolution_of_regular_mean_data(dict_data, start_data, end_data,
                                                                    time_delta_data, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_data == time_delta_res (time_delta_data < time_delta_res cannot be true because use of GCD)
        my_tmp_dict = dict_data

    if time_delta_simu > time_delta_res:  # i.e. information resolution too high to generate simu timeseries
        my_new_dict = decrease_time_resolution_of_regular_mean_data(my_tmp_dict, start_simu, end_simu,
                                                                    time_delta_simu, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_simu == time_delta_res (time_delta_simu < time_delta_res cannot be true because use of GCD)
        my_new_dict = decrease_time_resolution_of_regular_mean_data(my_tmp_dict, start_simu, end_simu,
                                                                    time_delta_simu, time_delta_res)
        # use decrease_data_time_resolution anyway for the only purpose to reduce the size of the dict
        # to the only required DateTimes in the simulation period

    return my_new_dict


def increase_time_resolution_of_regular_mean_data(dict_info, start_lo, end_lo,
                                                  time_delta_lo, time_delta_hi):
    """ Use the low resolution to create the high resolution """
    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_value = dict_info[my_dt_lo]
        for my_sub_step in xrange(0, -divisor, -1):
            new_dict_info[my_dt_lo + my_sub_step * time_delta_hi] = my_value
        my_dt_lo += time_delta_lo

    return new_dict_info


def decrease_time_resolution_of_regular_mean_data(dict_info, start_lo, end_lo,
                                                  time_delta_lo, time_delta_hi):
    """ Use the high resolution to create the low resolution """
    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_values = 0.0
        for my_sub_step in xrange(0, -divisor, -1):
            my_values += dict_info[my_dt_lo + my_sub_step * time_delta_hi]
        new_dict_info[my_dt_lo] = my_values / divisor
        my_dt_lo += time_delta_lo

    return new_dict_info


def distribute_loadings_across_year(dict_annual_loads, dict_applications, nd_distributions, link,
                                    my_tf, save_slice, simu_slice):
    """
    This function distributes the annual nutrient loadings across the year, using an application distribution.
    The annual amount is spread on every time step in the simulation time series.
    """

    my_nd_data = {c: {i: 0.0 for i in simu_slice} for c in dict_applications[link]}

    divisor = 1440 / my_tf.simu_gap  # 1440 minutes (= 1 day) because using daily distribution of annual loads

    for contaminant in dict_applications[link]:
        for my_dt_save in save_slice[1:]:
            day_of_year = my_dt_save.timetuple().tm_yday
            my_daily_value = dict_annual_loads[link][contaminant] * \
                nd_distributions[day_of_year][dict_applications[link][contaminant]]
            my_portion = float(my_daily_value) / divisor
            for my_sub_step in xrange(0, -divisor, -1):
                my_dt_simu = my_dt_save + timedelta(minutes=my_sub_step * my_tf.simu_gap)
                my_nd_data[contaminant][my_dt_simu] = my_portion

    return my_nd_data
