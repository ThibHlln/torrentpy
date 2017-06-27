import datetime


def run(obj_network, waterbody, dict_data_frame,
        dict_param,
        datetime_time_step, time_gap,
        logger):
    """
    River model * r_ *
    _ Hydrology
    ___ Inputs * in_ *
    _____ r_in_q_h2o      flow at inlet [m3/s]
    ___ States * s_ *
    _____ r_s_v_h2o       volume of water in store [m3]
    ___ Parameters * p_ *
    _____ r_p_k_h2o       linear factor k for water where Storage = k.Flow [s]
    ___ Outputs * out_ *
    _____ r_out_q_h2o     flow at outlet [m3/s]
    """

    # # 1. Hydrology
    # # 1.0. Define internal constants
    node_up = obj_network.connections[waterbody][1]
    time_step_sec = time_gap * 60.0  # [seconds]

    # # 1.1. Collect inputs, states, and parameters
    r_in_q_h2o = dict_data_frame[node_up].get_value(datetime_time_step + datetime.timedelta(minutes=-time_gap), "q_h2o")
    r_s_v_h2o = dict_data_frame[waterbody].get_value(datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                     "r_s_v_h2o")
    r_p_k_h2o = dict_param[waterbody]['LINRES']["r_p_k_h2o"]  # in seconds

    # # 1.2. Hydrological calculations

    # calculate outflow, at current time step
    r_out_q_h2o = r_s_v_h2o / r_p_k_h2o
    # calculate storage in temporary variable, for next time step
    r_s_v_h2o_old = r_s_v_h2o
    r_s_v_h2o_temp = r_s_v_h2o_old + (r_in_q_h2o - r_out_q_h2o) * time_step_sec
    # check if storage has gone negative
    if r_s_v_h2o_temp < 0.0:  # temporary cannot be used
        logger.debug(''.join([waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - Volume in River Store has gone negative, '
                              'outflow constrained to 95% of what is in store.']))
        # constrain outflow: allow maximum outflow at 95% of what was in store
        r_out_q_h2o = 0.95 * (r_in_q_h2o + r_s_v_h2o_old / time_step_sec)
        # calculate final storage with constrained outflow
        r_s_v_h2o += (r_in_q_h2o - r_out_q_h2o) * time_step_sec
    else:
        r_s_v_h2o = r_s_v_h2o_temp  # temporary storage becomes final storage

    # # 1.3. Save inputs, states, and outputs
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_q_h2o", r_in_q_h2o)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_v_h2o", r_s_v_h2o)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_q_h2o", r_out_q_h2o)


def infer_parameters(dict_desc, my_dict_param):
    # LINEAR RESERVOIR
    # Parameter RK: River routing parameter (hours)
    l = dict_desc['stream_length']
    q = 0.7 * dict_desc['SAAR'] * (dict_desc['area'] / 1e6) * 3.171e-5
    slp = dict_desc['TAYSLO'] / 1000.0
    n = 0.04
    # rk = l / (
    #     (q ** 0.4 * slp ** 0.3) / ((3.67 * q ** 0.45) ** 0.4 * (n ** 0.6))
    # )
    rk = l / 1.0
    my_dict_param['r_p_k_h2o'] = rk
