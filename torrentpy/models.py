from structures import smart, linres, inca
try:
    import SMARTc
    smart_in_c = True
except ImportError:
    SMARTc = None
    smart_in_c = False


def run_catchment_model(identifier, waterbody, dict_data_frame,
                        dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                        datetime_time_step, time_gap,
                        logger):
    """
    This function uses the identifier string of the Model object to run the appropriate (combination of) model(s)
    """
    if identifier == "SMART_INCAL":
        # SMART
        smart_in = smart.get_in(waterbody, datetime_time_step, time_gap,
                                dict_data_frame, dict_desc, dict_param, dict_meteo)

        if smart_in_c:
            smart_out = SMARTc.onestep_c(*smart_in)
        else:
            smart_out = smart.run(waterbody, datetime_time_step, logger, *smart_in)

        smart.get_out(waterbody, datetime_time_step, dict_data_frame, *smart_out)

        # INCA Land
        incal_in = inca.get_in_land(waterbody, datetime_time_step, time_gap,
                                    dict_data_frame, dict_desc, dict_param, dict_meteo, dict_loads, dict_const)

        incal_out = inca.run_on_land(waterbody, datetime_time_step, logger, *incal_in)

        inca.get_out_land(waterbody, datetime_time_step, dict_data_frame, *incal_out)

    elif identifier == "SMART":
        # SMART
        smart_in = smart.get_in(waterbody, datetime_time_step, time_gap,
                                dict_data_frame, dict_desc, dict_param, dict_meteo)

        if smart_in_c:
            smart_out = SMARTc.onestep_c(*smart_in)
        else:
            smart_out = smart.run(waterbody, datetime_time_step, logger, *smart_in)

        smart.get_out(waterbody, datetime_time_step, dict_data_frame, *smart_out)
    else:
        raise Exception('The model {} is not associated to any run script.'.format(identifier))


def run_river_model(identifier, obj_network, waterbody, dict_data_frame,
                    dict_param, dict_const, dict_meteo,
                    datetime_time_step, time_gap,
                    logger):
    """
    This function uses the identifier string of the Model object to run the appropriate (combination of) model(s)
    """
    if identifier == "LINRES_INCAS":
        # LINRES
        linres_in = linres.get_in(obj_network, waterbody, datetime_time_step, time_gap,
                                  dict_data_frame, dict_param)

        if smart_in_c:
            linres_out = SMARTc.onestep_r(*linres_in)
        else:
            linres_out = linres.run(waterbody, datetime_time_step, logger, *linres_in)

        linres.get_out(waterbody, datetime_time_step, dict_data_frame, *linres_out)

        # INCA Stream
        incas_in = inca.get_in_stream(obj_network, waterbody, datetime_time_step, time_gap,
                                      dict_data_frame, dict_param, dict_meteo, dict_const)

        incas_out = inca.run_in_stream(waterbody, datetime_time_step, logger, *incas_in)

        inca.get_out_stream(waterbody, datetime_time_step, dict_data_frame, *incas_out)

    elif identifier == "LINRES":
        # LINRES
        linres_in = linres.get_in(obj_network, waterbody, datetime_time_step, time_gap,
                                  dict_data_frame, dict_param)

        if smart_in_c:
            linres_out = SMARTc.onestep_r(*linres_in)
        else:
            linres_out = linres.run(waterbody, datetime_time_step, logger, *linres_in)

        linres.get_out(waterbody, datetime_time_step, dict_data_frame, *linres_out)
    else:
        raise Exception('The model {} is not associated to any run script.'.format(identifier))


def run_lake_model(identifier, waterbody):
    """
    This function uses the identifier string of the Model object to run the appropriate (combination of) model(s)
    """
    # TO BE DEVELOPED
    raise Exception(
        'The model {} is not associated to any run script, {} cannot modelled.'.format(identifier, waterbody))


def initialise_catchment_model(identifier, dict_desc, dict_param):
    """
    This function uses the identifier string of the Model object to initialise the appropriate (combination of) model(s)
    """
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
    """
    This function uses the identifier string of the Model object to initialise the appropriate (combination of) model(s)
    """
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
    """
    This function uses the identifier string of the Model object to initialise the appropriate (combination of) model(s)
    """
    # TO BE DEVELOPED
    raise Exception(
        'The model {} is not associated to any run script, cannot be initialised.'.format(identifier))


def infer_parameters_from_descriptors(dict_desc, model_component):
    """
    This function uses the model components contained in the identifier string of the Model object to
    infer the parameter values for the model components if required
    """
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
