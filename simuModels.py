

from models import smart, linres


def catchment_model(identifier, waterbody, dict_data_frame,
                    dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                    datetime_time_step, time_gap,
                    logger):

    if identifier == "SMART":
        smart.run(waterbody, dict_data_frame,
                  dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                  datetime_time_step, time_gap,
                  logger)


def river_model(identifier, obj_network, waterbody, dict_data_frame,
                dict_desc, dict_param, dict_meteo,
                datetime_time_step, time_gap,
                logger):

    if identifier == "LINRES":
        linres.run(obj_network, waterbody, dict_data_frame,
                   dict_desc, dict_param, dict_meteo,
                   datetime_time_step, time_gap,
                   logger)


def lake_model(identifier, waterbody, dict_data_frame,
               dict_desc, dict_param, dict_meteo,
               datetime_time_step, time_gap,
               logger):
    logger.warning("No lake model available, {} not modelled.".format(waterbody))
    # TO BE DEVELOPED
