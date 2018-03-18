from models import smart, linres, inca


def run_catchment_model(identifier, waterbody, dict_data_frame,
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
        raise Exception('The model {} is not associated to any run script.'.format(identifier))


def run_river_model(identifier, obj_network, waterbody, dict_data_frame,
                    dict_param, dict_const, dict_meteo,
                    datetime_time_step, time_gap,
                    logger):

    if identifier == "LINRES_INCAS":
        linres.run(obj_network, waterbody, dict_data_frame,
                   dict_param,
                   datetime_time_step, time_gap,
                   logger)
        inca.run_in_stream(obj_network, waterbody, dict_data_frame,
                           dict_param, dict_const, dict_meteo,
                           datetime_time_step, time_gap,
                           logger)
    elif identifier == "LINRES":
        linres.run(obj_network, waterbody, dict_data_frame,
                   dict_param,
                   datetime_time_step, time_gap,
                   logger)
    else:
        raise Exception('The model {} is not associated to any run script.'.format(identifier))


def run_lake_model(identifier, waterbody):
    # TO BE DEVELOPED
    raise Exception(
        'The model {} is not associated to any run script, {} cannot modelled.'.format(identifier, waterbody))


def initialise_catchment_model(identifier, dict_desc, dict_param):

    dict_init = dict()

    if identifier == "SMART_INCAL":
        dict_init.update(
            smart.initialise_states(dict_desc, dict_param)
        )
        dict_init.update(
            inca.initialise_land_states()
        )
    elif identifier == "SMART":
        dict_init.update(
            smart.initialise_states(dict_desc, dict_param)
        )
    else:
        raise Exception('The model {} is not associated to any initialisation script.'.format(identifier))

    return dict_init


def initialise_river_model(identifier, dict_desc, dict_param):

    dict_init = dict()

    if identifier == "LINRES_INCAS":
        dict_init.update(
            linres.initialise_states(dict_desc, dict_param)
        )
        dict_init.update(
            inca.initialise_stream_states()
        )
    elif identifier == "LINRES":
        dict_init.update(
            linres.initialise_states(dict_desc, dict_param)
        )
    else:
        raise Exception('The model {} is not associated to any initialisation script.'.format(identifier))

    return dict_init


def initialise_lake_model(identifier):
    # TO BE DEVELOPED
    raise Exception(
        'The model {} is not associated to any run script, cannot be initialised.'.format(identifier))


def infer_parameters_from_descriptors(dict_desc, model_component):

    dict_param = dict()

    if model_component == "SMART":
        smart.infer_parameters(dict_desc, dict_param)
    elif model_component == "LINRES":
        linres.infer_parameters(dict_desc, dict_param)
    elif model_component == "INCAL":
        inca.infer_land_parameters(dict_desc, dict_param)
    elif model_component == "INCAS":
        inca.infer_stream_parameters(dict_param)
    else:
        raise Exception('The model {} has no parameter inferring script.'.format(model_component))

    return dict_param
