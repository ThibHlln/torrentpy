import datetime


def smart(waterbody, dict_data_frame, dict_param, dict_meteo, datetime_time_step, time_gap):

    list_inputs = ["rain", "peva"]
    list_parameters = ["a", "b"]
    list_states = ["h"]
    list_outputs = ["q", "aeva"]

    # Store the inputs & parameters
    for variable in list_inputs:
        dict_data_frame[waterbody].set_value(datetime_time_step, variable,
                                             dict_meteo[waterbody].loc[datetime_time_step, variable])
    for parameter in list_parameters:
        dict_data_frame[waterbody].set_value(datetime_time_step, parameter,
                                             dict_param[waterbody][parameter])

    # Inputs

    rain = dict_meteo[waterbody].loc[datetime_time_step, "rain"]
    peva = dict_meteo[waterbody].loc[datetime_time_step, "peva"]

    # States & Outputs

    aeva = peva - (0.1 * dict_data_frame[waterbody].loc[datetime_time_step, "a"] +
                   0.2 * dict_data_frame[waterbody].loc[datetime_time_step, "b"])
    if rain >= 0.5:
        q = rain - 0.5
        h = dict_data_frame[waterbody].loc[datetime_time_step, "a"] + 1
    else:
        q = 0
        h = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "a"]

    dict_data_frame[waterbody].set_value(datetime_time_step, "aeva", aeva)
    dict_data_frame[waterbody].set_value(datetime_time_step, "q", q)
    dict_data_frame[waterbody].set_value(datetime_time_step, "h", h)

    # q_ove = ""
    # q_dra = ""
    # q_int = ""
    # q_sgw = ""
    # q_dgw = ""
    # q = q_ove + q_dra + q_int + q_sgw + q_dgw
    #
    # c_nh4 = ""
    # c_no3 = ""
    # c_dph = ""
    # c_pph = ""
    # c_sed = ""


def linres(obj_network, waterbody, dict_data_frame, dict_param, dict_meteo, datetime_time_step, time_gap):

    r_q_in = dict_data_frame[obj_network.connections[waterbody][1]].loc[datetime_time_step +
                                                                        datetime.timedelta(minutes=-time_gap), "q"]

    r_q = r_q_in - 0.10 * r_q_in

    dict_data_frame[waterbody].set_value(datetime_time_step, "r_q_in", r_q_in)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_q", r_q)

    # Inputs
    q = ""
    c_nh4 = ""
    c_no3 = ""
    c_dph = ""
    c_pph = ""
    c_sed = ""

    # Outputs
    r_q = ""
    r_c_nh4 = ""
    r_c_no3 = ""
    r_c_dph = ""
    r_c_pph = ""
    r_c_sed = ""

    return 2


def bathtub(waterbody, dict_data_frame, dict_param, dict_meteo, datetime_time_step, time_gap):
    return 3
