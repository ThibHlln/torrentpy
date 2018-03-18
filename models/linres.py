from datetime import timedelta


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
    _____ r_p_k_h2o       linear factor k for water where Storage = k.Flow [hours]
    ___ Outputs * out_ *
    _____ r_out_q_h2o     flow at outlet [m3/s]
    """
    # # 1. Hydrology
    # # 1.0. Define internal constants
    node_up = obj_network.connections[waterbody][1]
    time_gap_sec = time_gap * 60.0  # [seconds]

    # # 1.1. Collect inputs, states, and parameters
    r_in_q_h2o = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["q_h2o"]
    r_s_v_h2o = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_v_h2o"]
    r_p_k_h2o = dict_param["r_p_k_h2o"] * 3600.0  # convert hours into seconds

    # # 1.2. Hydrological calculations

    # calculate outflow, at current time step
    r_out_q_h2o = r_s_v_h2o / r_p_k_h2o
    # calculate storage in temporary variable, for next time step
    r_s_v_h2o_old = r_s_v_h2o
    r_s_v_h2o_temp = r_s_v_h2o_old + (r_in_q_h2o - r_out_q_h2o) * time_gap_sec
    # check if storage has gone negative
    if r_s_v_h2o_temp < 0.0:  # temporary cannot be used
        logger.debug(''.join(['LINRES # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - Volume in River Store has gone negative, '
                              'outflow constrained to 95% of what is in store.']))
        # constrain outflow: allow maximum outflow at 95% of what was in store
        r_out_q_h2o = 0.95 * (r_in_q_h2o + r_s_v_h2o_old / time_gap_sec)
        # calculate final storage with constrained outflow
        r_s_v_h2o += (r_in_q_h2o - r_out_q_h2o) * time_gap_sec
    else:
        r_s_v_h2o = r_s_v_h2o_temp  # temporary storage becomes final storage

    # # 1.3. Save inputs, states, and outputs
    dict_data_frame[waterbody][datetime_time_step]["r_in_q_h2o"] = r_in_q_h2o
    dict_data_frame[waterbody][datetime_time_step]["r_s_v_h2o"] = r_s_v_h2o
    dict_data_frame[waterbody][datetime_time_step]["r_out_q_h2o"] = r_out_q_h2o


def infer_parameters(dict_desc, my_dict_param):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for Pathways Project by Dr. Eva Mockler
    (using equations available in CMT Fortran code by Prof. Michael Bruen and Dr. Eva Mockler).
    """
    # Parameter RK: River routing parameter (hours)
    l = dict_desc['stream_length']
    q = 0.7 * dict_desc['SAAR'] * (dict_desc['area'] / 1e6) * 3.171e-5
    slp = dict_desc['TAYSLO'] / 1000.0
    n = 0.04
    # rk = l / (
    #     (q ** 0.4 * slp ** 0.3) / ((3.67 * q ** 0.45) ** 0.4 * (n ** 0.6))
    # )
    rk = l / 1.0
    rk /= 3600.0  # convert seconds into hours
    my_dict_param['r_p_k_h2o'] = rk


def infer_parameters_thesis(dict_desc, my_dict_param):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for Pathways Project by Dr. Eva Mockler
    (using equations available in Eva Mockler's Ph.D. thesis).
    """
    # Parameter RK: River routing parameter (hours)
    l = dict_desc['stream_length']
    q = 0.7 * dict_desc['SAAR'] * (dict_desc['area'] / 1e6) * 3.171e-5
    slp = dict_desc['TAYSLO'] / 1000.0
    n = 0.04
    rk = l / (
        (q ** 0.4 * slp ** 0.3) / ((3.67 * q ** 0.45) ** 0.4 * (n ** 0.6))
    )
    rk /= 3600.0  # convert seconds into hours
    my_dict_param['r_p_k_h2o'] = rk


def initialise_states(dict_desc, dict_param):

    area_m2 = dict_desc['area']

    return {
        'r_s_v_h2o': (1200 * 0.45) / 1000 * area_m2 / 8766 * dict_param['r_p_k_h2o']
    }
