import datetime


def distribute_loadings_across_year(dict_annual_loads, dict_applications, nd_distributions, link,
                                    my_tf, data_slice, simu_slice):

    my_nd_data = {i: {c: 0.0 for c in dict_applications[link]} for i in simu_slice}

    divisor = my_tf.gap_data / my_tf.gap_simu

    for contaminant in dict_applications[link]:
        for my_dt_data in data_slice[1:]:
            day_of_year = my_dt_data.timetuple().tm_yday
            my_value = dict_annual_loads[link][contaminant] * \
                nd_distributions[day_of_year][dict_applications[link][contaminant]]
            my_portion = float(my_value) / divisor
            for my_sub_step in xrange(0, -divisor, -1):
                my_dt_simu = my_dt_data + datetime.timedelta(minutes=my_sub_step * my_tf.gap_simu)
                my_nd_data[my_dt_simu][contaminant] = my_portion

    return my_nd_data
