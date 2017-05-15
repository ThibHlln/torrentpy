import datetime


def run(obj_network, waterbody, dict_data_frame,
        dict_param, dict_meteo,
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
    _ Water Quality
    ___ Inputs * in_ *
    _____ r_in_temp       water temperature [degree celsius]
    _____ r_in_c_no3      nitrate concentration at inlet [kg/m3]
    _____ r_in_c_nh4      ammonia concentration at inlet [kg/m3]
    _____ r_in_c_dph      dissolved phosphorus concentration at inlet [kg/m3]
    _____ r_in_c_pph      particulate phosphorus concentration at inlet [kg/m3]
    _____ r_in_c_sed      sediment concentration at inlet [kg/m3]
    ___ States * s_ *
    _____ r_s_m_no3       quantity of nitrate in store [kg]
    _____ r_s_m_nh4       quantity of ammonia in store [kg]
    _____ r_s_m_dph       quantity of dissolved phosphorus in store [kg]
    _____ r_s_m_pph       quantity of particulate phosphorus in store [kg]
    _____ r_s_m_sed       quantity of sediment in store [kg]
    ___ Parameters * p_ *
    _____ r_p_k_no3       linear factor k for nitrate [s]
    _____ r_p_k_nh4       linear factor k for ammonia [s]
    _____ r_p_k_dph       linear factor k for dissolved phosphorus [s]
    _____ r_p_k_pph       linear factor k for particulate phosphorus [s]
    _____ r_p_k_sed       linear factor k for sediment [s]
    ___ Outputs * out_ *
    _____ r_out_c_no3     nitrate concentration at outlet [kg/m3]
    _____ r_out_c_nh4     ammonia concentration at outlet [kg/m3]
    _____ r_out_c_dph     dissolved phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_pph     particulate phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_sed     sediment concentration at outlet [kg/m3]
    """

    time_step_sec = time_gap * 60.0  # [seconds]
    flow_tolerance = 1.0E-8
    volume_tolerance = 1.0E-8

    # # 1. Hydrology
    # # 1.1. Collect inputs, states, and parameters
    node_up = obj_network.connections[waterbody][1]
    r_in_q_h2o = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "q_h2o"]
    r_s_v_h2o = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_v_h2o"]
    r_p_k_h2o = dict_param[waterbody]["r_p_k_h2o"]

    # # 1.2. Hydrological calculations

    # calculate outflow, at current time step
    r_out_q_h2o = r_s_v_h2o / r_p_k_h2o
    # calculate storage in temporary variable, for next time step
    r_s_v_h2o_old = r_s_v_h2o
    r_s_v_h2o_temp = r_s_v_h2o_old + (r_in_q_h2o - r_out_q_h2o) * time_step_sec
    # check if storage has gone negative
    if r_s_v_h2o_temp < 0.0:  # temporary cannot be used
        logger.info("{}: {} - Volume in River Store has gone negative, outflow constrained "
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

    # # 2. Water quality
    # # 2.1. Collect inputs, states, and parameters
    r_in_temp = dict_meteo[waterbody].loc[datetime_time_step, "temp"]
    r_in_c_no3 = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "c_no3"]
    r_in_c_nh4 = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "c_no3"]
    r_in_c_dph = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "c_no3"]
    r_in_c_pph = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "c_no3"]
    r_in_c_sed = dict_data_frame[node_up].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "c_no3"]

    r_s_m_no3 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_m_no3"]
    r_s_m_nh4 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_m_nh4"]
    r_s_m_dph = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_m_dph"]
    r_s_m_pph = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_m_pph"]
    r_s_m_sed = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap), "r_s_m_sed"]

    r_p_att_no3 = dict_param[waterbody]["r_p_att_h2o"]
    r_p_att_nh4 = dict_param[waterbody]["r_p_att_h2o"]
    r_p_att_dph = dict_param[waterbody]["r_p_att_h2o"]
    r_p_att_pph = dict_param[waterbody]["r_p_att_h2o"]
    r_p_att_sed = dict_param[waterbody]["r_p_att_h2o"]

    # # 2.2. Water quality calculations

    # check if inflow negligible, if so set all concentrations to zero
    if r_in_q_h2o < flow_tolerance:
        logger.info("{}: {} - Inflow to River Store too low, inflow concentrations set "
                    "to zero.".format(waterbody, datetime_time_step))
        r_in_c_no3 = 0.0
        r_in_c_nh4 = 0.0
        r_in_c_dph = 0.0
        r_in_c_pph = 0.0
        r_in_c_sed = 0.0
    # check if storage negligible, if so set all quantities to zero, all out concentrations to zero
    if r_s_v_h2o_old < volume_tolerance:
        logger.info("{}: {} - Volume in River Store too low, in-store contaminant quantities and outflow "
                    "concentrations set to zero.".format(waterbody, datetime_time_step))
        r_s_m_no3 = 0.0
        r_s_m_nh4 = 0.0
        r_s_m_dph = 0.0
        r_s_m_pph = 0.0
        r_s_m_sed = 0.0

        r_out_c_no3 = 0.0
        r_out_c_nh4 = 0.0
        r_out_c_dph = 0.0
        r_out_c_pph = 0.0
        r_out_c_sed = 0.0
    else:
        # # 2.2.1. Nitrate NO3
        r_s_m_no3_old = r_s_m_no3
        # calculate concentration in store at beginning of time step
        concentration_no3 = r_s_m_no3_old / r_s_v_h2o_old
        if r_in_temp < 0.0:  # frozen, no denitrification/no nitrification
            c10 = 0.0
            c11 = 0.0
        else:  # not frozen
            c10 = 0.1 * (1.047 ** (r_in_temp - 20.0))
            c11 = 0.06 * (1.047 ** (r_in_temp - 20.0))
            if c10 < 0.0:  # check if rate constant between 0 and 1
                c10 = 0.0
            elif c10 > 1.0:
                c10 = 1.0
            if c11 < 0.0:  # check if rate constant between 0 and 1
                c11 = 0.0
            elif c11 > 1.0:
                c11 = 1.0
        rni = c10 * r_s_m_nh4  # nitrification rate [kg]
        rdn = c11 * r_s_m_no3  # denitrification rate [kg]
        # update of amount in store
        r_s_m_no3 = r_s_m_no3_old + rni - rdn + \
            ((r_in_c_no3 * r_in_q_h2o) - (concentration_no3 * r_out_q_h2o)) * time_step_sec
        if r_s_m_no3 < 0.0:
            logger.info("{}: {} - NO3 Quantity has gone negative in River Store, quantity "
                        "reset to zero.".format(waterbody, datetime_time_step))
            r_s_m_no3 = 0.0
        # calculate outflow concentration
        if r_s_v_h2o > volume_tolerance:
            r_out_c_no3 = r_s_m_no3 / r_s_v_h2o
        else:
            logger.info("{}: {} - Volume in River Store too low, outflow NO3 concentration set "
                        "to zero.".format(waterbody, datetime_time_step))
            r_out_c_no3 = 0.0

        # # 2.2.2. Ammonia NH4
        r_s_m_nh4_old = r_s_m_nh4
        # calculate concentration in store at beginning of time step
        concentration_nh4 = r_s_m_nh4_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_nh4 = r_s_m_nh4_old - rni + \
            ((r_in_c_nh4 * r_in_q_h2o) - (concentration_nh4 * r_out_q_h2o)) * time_step_sec
        if r_s_m_nh4 < 0.0:
            r_s_m_nh4 = 0.0
        # calculate outflow concentration
        if r_s_v_h2o > volume_tolerance:
            r_out_c_nh4 = r_s_m_nh4 / r_s_v_h2o
        else:
            logger.info("{}: {} - Volume in River Store too low, outflow NH4 concentration set "
                        "to zero.".format(waterbody, datetime_time_step))
            r_out_c_nh4 = 0.0

        # # 2.2.3. Dissolved phosphorus DPH
        r_s_m_dph_old = r_s_m_dph
        # calculate concentration in store at beginning of time step
        concentration_dph = r_s_m_dph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_dph = r_s_m_dph_old + ((r_in_c_dph * r_in_q_h2o) - (concentration_dph * r_out_q_h2o)) * time_step_sec
        if r_s_m_dph < 0.0:
            r_s_m_dph = 0.0
        # calculate outflow concentration
        if r_s_v_h2o > volume_tolerance:
            r_out_c_dph = r_s_m_dph / r_s_v_h2o
        else:
            logger.info("{}: {} - Volume in River Store too low, outflow DPH concentration set "
                        "to zero.".format(waterbody, datetime_time_step))
            r_out_c_dph = 0.0

        # # 2.2.4. Particulate phosphorus PPH
        r_s_m_pph_old = r_s_m_pph
        # calculate concentration in store at beginning of time step
        concentration_pph = r_s_m_pph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_pph = r_s_m_pph_old + ((r_in_c_pph * r_in_q_h2o) - (concentration_pph * r_out_q_h2o)) * time_step_sec
        if r_s_m_pph < 0.0:
            r_s_m_pph = 0.0
        # calculate outflow concentration
        if r_s_v_h2o > volume_tolerance:
            r_out_c_pph = r_s_m_pph / r_s_v_h2o
        else:
            logger.info("{}: {} - Volume in River Store too low, outflow PPH concentration set "
                        "to zero.".format(waterbody, datetime_time_step))
            r_out_c_pph = 0.0

        # # 2.2.5. Sediments SED
        r_s_m_sed_old = r_s_m_sed
        # calculate concentration in store at beginning of time step
        concentration_sed = r_s_m_sed_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_sed = r_s_m_sed_old + ((r_in_c_sed * r_in_q_h2o) - (concentration_sed * r_out_q_h2o)) * time_step_sec
        if r_s_m_sed < 0.0:
            r_s_m_sed = 0.0
        # calculate outflow concentration
        if r_s_v_h2o > volume_tolerance:
            r_out_c_sed = r_s_m_sed / r_s_v_h2o
        else:
            logger.info("{}: {} - Volume in River Store too low, outflow SED concentration set "
                        "to zero.".format(waterbody, datetime_time_step))
            r_out_c_sed = 0.0

    # # 2.3. Save inputs, states, and outputs

    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_rain", r_in_temp)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_c_no3", r_in_c_no3)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_c_nh4", r_in_c_nh4)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_c_dph", r_in_c_dph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_c_pph", r_in_c_pph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_in_c_sed", r_in_c_sed)

    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_m_no3", r_s_m_no3)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_m_nh4", r_s_m_nh4)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_m_dph", r_s_m_dph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_m_pph", r_s_m_pph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_s_m_sed", r_s_m_sed)

    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_c_no3", r_out_c_no3)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_c_nh4", r_out_c_nh4)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_c_dph", r_out_c_dph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_c_pph", r_out_c_pph)
    dict_data_frame[waterbody].set_value(datetime_time_step, "r_out_c_sed", r_out_c_sed)
