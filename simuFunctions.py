import sys
from pandas import DataFrame

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
        sys.exit('The model {} is not associated to any inferring script.'.format(model))

    return my_dict_param


def distribute_loadings_across_year(dict_annual_loads, dict_applications, df_distributions, link, time_steps):

    my__data_frame = DataFrame(index=time_steps, columns=dict_applications[link]).fillna(0.0)

    for contaminant in dict_applications[link]:
        for datetime_time_step in time_steps:
            day_of_year = float(datetime_time_step.timetuple().tm_yday)
            my__data_frame.set_value(datetime_time_step, contaminant,
                                     dict_annual_loads[link][contaminant] *
                                     df_distributions.loc[day_of_year, dict_applications[link][contaminant]])

    return my__data_frame
