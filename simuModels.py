import sys


from models import smart, linres, inca


def catchment_model(identifier, waterbody, dict_data_frame,
                    dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                    datetime_time_step, time_gap,
                    logger):

    if identifier == "SMART_INCAL":
        my_dict_hydro = smart.run(waterbody, dict_data_frame,
                                  dict_desc, dict_param, dict_meteo,
                                  datetime_time_step, time_gap,
                                  logger)
        inca.run_on_land(waterbody, dict_data_frame,
                         dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                         datetime_time_step, time_gap,
                         logger,
                         my_dict_hydro)
    elif identifier == "SMART":
        smart.run(waterbody, dict_data_frame,
                  dict_desc, dict_param, dict_meteo,
                  datetime_time_step, time_gap,
                  logger)
    else:
        sys.exit('The model {} is not associated to any script.'.format(identifier))


def river_model(identifier, obj_network, waterbody, dict_data_frame,
                dict_param, dict_meteo,
                datetime_time_step, time_gap,
                logger):

    if identifier == "LINRES_INCAS":
        linres.run(obj_network, waterbody, dict_data_frame,
                   dict_param,
                   datetime_time_step, time_gap,
                   logger)
        inca.run_in_stream(obj_network, waterbody, dict_data_frame,
                           dict_param, dict_meteo,
                           datetime_time_step, time_gap,
                           logger)
    elif identifier == "LINRES":
        linres.run(obj_network, waterbody, dict_data_frame,
                   dict_param,
                   datetime_time_step, time_gap,
                   logger)
    else:
        sys.exit('The model {} is not associated to any script.'.format(identifier))


def lake_model(identifier, waterbody, dict_data_frame,
               dict_desc, dict_param, dict_meteo,
               datetime_time_step, time_gap,
               logger):
    logger.warning("No lake model available, {} not modelled.".format(waterbody))
    # TO BE DEVELOPED
