import datetime

import models.smart as smart
import models.linres as linres
import models.inca as inca


def infer_parameters_from_descriptors(dict_desc, model):

    my_dict_param = dict()

    if model == "SMART":
        smart.infer_parameters(dict_desc, my_dict_param)
    elif model == "LINRES":
        linres.infer_parameters(dict_desc, my_dict_param)
    elif model == "INCAL":
        inca.infer_land_parameters(dict_desc, my_dict_param)
    elif model == "INCAS":
        inca.infer_stream_parameters(my_dict_param)
    else:
        raise Exception('The model {} is not associated to any inferring script.'.format(model))

    return my_dict_param


def distribute_loadings_across_year(dict_annual_loads, dict_applications, nd_distributions, link,
                                    my_tf, data_slice, simu_slice):

    my_nd_data = {i: {c: 0.0 for c in dict_applications[link]} for i in simu_slice}

    divisor = my_tf.step_data / my_tf.step_simu

    for contaminant in dict_applications[link]:
        for my_dt_data in data_slice[1:]:
            day_of_year = my_dt_data.timetuple().tm_yday
            my_value = dict_annual_loads[link][contaminant] * \
                nd_distributions[day_of_year][dict_applications[link][contaminant]]
            my_portion = float(my_value) / divisor
            for my_sub_step in xrange(0, -divisor, -1):
                my_dt_simu = my_dt_data + datetime.timedelta(minutes=my_sub_step * my_tf.step_simu)
                my_nd_data[my_dt_simu][contaminant] = my_portion

    return my_nd_data
