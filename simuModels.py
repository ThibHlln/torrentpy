import datetime

from models import smart, linres


def catchment_model(waterbody, dict_data_frame, dict_param, dict_meteo, dict_loads, datetime_time_step, time_gap):

    smart.run(waterbody, dict_data_frame, dict_param, dict_meteo, dict_loads, datetime_time_step, time_gap)


def river_model(obj_network, waterbody, dict_data_frame, dict_param, dict_meteo, datetime_time_step, time_gap):

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


def lake_model(waterbody, dict_data_frame, dict_param, dict_meteo, datetime_time_step, time_gap):
    return 3
