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
    r_in_q_h2o = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "q_h2o"]
    r_s_v_h2o = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_v_h2o"]
    r_p_k_h2o = dict_param[waterbody]["r_p_k_h2o"] * 3600.0  # convert hours in seconds

    # # 1.2. Hydrological calculations

    # calculate outflow, at current time step
    r_out_q_h2o = r_s_v_h2o / r_p_k_h2o
    # calculate storage in temporary variable, for next time step
    r_s_v_h2o_old = r_s_v_h2o
    r_s_v_h2o_temp = r_s_v_h2o_old + (r_in_q_h2o - r_out_q_h2o) * time_step_sec
    # check if storage has gone negative
    if r_s_v_h2o_temp < 0.0:  # temporary cannot be used
        logger.debug("{}: {} - Volume in River Store has gone negative, outflow constrained "
                     "to what is in store.". format(waterbody, datetime_time_step))
        # constrain outflow: allow maximum outflow at 95% of what was in store
        r_out_q_h2o = 0.95 * (r_in_q_h2o + r_s_v_h2o_old / time_step_sec)
        # calculate final storage with constrained outflow
        r_s_v_h2o += (r_in_q_h2o - r_out_q_h2o) * time_step_sec
    else:
        r_s_v_h2o = r_s_v_h2o_temp  # temporary storage becomes final storage

    # # 1.3 Save inputs, states, and outputs
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_q_h2o", r_in_q_h2o)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_v_h2o", r_s_v_h2o)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_q_h2o", r_out_q_h2o)
