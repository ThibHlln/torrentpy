from datetime import timedelta


def run(waterbody, datetime_time_step, logger,
        time_gap_min,
        r_in_q_h2o, r_s_v_h2o, r_p_k_h2o):
    """
    River Constants
    _ time_gap_min        time gap between two simulation time steps [minutes]

    River Model * r_ *
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

    # # 1.1. Unit conversions
    time_gap_sec = time_gap_min * 60.0  # [seconds]
    r_p_k_h2o *= 3600.0  # convert hours into seconds

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

    # # 1.3. Return states and outputs
    return \
        r_out_q_h2o, r_s_v_h2o


def get_in(network, waterbody, datetime_time_step, time_gap_min,
           dict_data_frame, dict_param):
    """
    This function is the interface between the data structures of the simulator and the model.
    It provides the inputs, parameters, processes, and states to the model.
    It also saves the inputs into the data frame.
    It can only return a tuple of scalar variables.
    """
    # find the node that is the input for the waterbody
    node_up = network.connections[waterbody][1]

    # bring in model inputs
    r_in_q_h2o = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]["q_h2o"]
    # store input in data frame
    dict_data_frame[waterbody][datetime_time_step]["r_in_q_h2o"] = r_in_q_h2o

    # bring in model states
    r_s_v_h2o = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]["r_s_v_h2o"]

    # bring in model parameter values
    r_p_k_h2o = dict_param["r_p_k_h2o"]

    # return model constants, model inputs, model parameter values, and model states
    return \
        time_gap_min, \
        r_in_q_h2o, r_s_v_h2o, r_p_k_h2o


def get_out(waterbody, datetime_time_step, dict_data_frame,
            r_out_q_h2o, r_s_v_h2o):
    """
    This function is the interface between the model and the data structures of the simulator.
    It stores the processes, states, and outputs in the data frame.
    """
    # store states in data frame
    dict_data_frame[waterbody][datetime_time_step]["r_s_v_h2o"] = r_s_v_h2o
    # store outputs in data frame
    dict_data_frame[waterbody][datetime_time_step]["r_out_q_h2o"] = r_out_q_h2o


def infer_parameters(dict_desc, my_dict_param):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for EPA Pathways Project by Dr. Eva Mockler
    (using equations available in CMT Fortran code by Prof. Michael Bruen and Dr. Eva Mockler).
    """
    # Parameter RK: River routing parameter (hours)
    lgth = dict_desc['stream_length']
    rk = lgth / 1.0  # i.e. assuming a water velocity of 1 m/s
    rk /= 3600.0  # convert seconds into hours
    my_dict_param['r_p_k_h2o'] = rk


def infer_parameters_thesis(dict_desc, my_dict_param):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for EPA Pathways Project by Dr. Eva Mockler
    (using equations available in Eva Mockler's Ph.D. thesis).
    """
    # Parameter RK: River routing parameter (hours)
    lgth = dict_desc['stream_length']
    q_mm = 0.7 * dict_desc['SAAR'] * (dict_desc['area'] / 1e6) * 3.171e-5
    slp = dict_desc['TAYSLO'] / 1000.0
    n = 0.04
    rk = lgth / (
        (q_mm ** 0.4 * slp ** 0.3) / ((3.67 * q_mm ** 0.45) ** 0.4 * (n ** 0.6))
    )
    rk /= 3600.0  # convert seconds into hours
    my_dict_param['r_p_k_h2o'] = rk


def initialise_states(dict_desc, dict_param):
    """
    This function initialises the model states before starting the simulations.
    If a warm-up run is used, this initialisation happens before the start of the warm-up run.
    If no warm-up is used, this initialisation happens before the start of the actual simulation run.
    """
    area_m2 = dict_desc['area']

    return {
        'r_s_v_h2o': (1200 * 0.45) / 1000 * area_m2 / 8766 * dict_param['r_p_k_h2o']
    }
