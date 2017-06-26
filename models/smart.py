import datetime
from math import exp, log


def run(waterbody, dict_data_frame,
        dict_desc, dict_param, dict_meteo,
        datetime_time_step, time_gap,
        logger):
    """
    Catchment model * c_ *
    _ Hydrology
    ___ Inputs * in_ *
    _____ c_in_rain             precipitation as rain [mm/time step]
    _____ c_in_peva             potential evapotranspiration [mm/time step]
    ___ States * s_ *
    _____ c_s_v_h2o_ove         volume of water in overland store [m3]
    _____ c_s_v_h2o_dra         volume of water in drain store [m3]
    _____ c_s_v_h2o_int         volume of water in inter store [m3]
    _____ c_s_v_h2o_sgw         volume of water in shallow groundwater store [m3]
    _____ c_s_v_h2o_dgw         volume of water in deep groundwater store [m3]
    _____ c_s_v_h2o_ly1         volume of water in first soil layer store [m3]
    _____ c_s_v_h2o_ly2         volume of water in second soil layer store [m3]
    _____ c_s_v_h2o_ly3         volume of water in third soil layer store [m3]
    _____ c_s_v_h2o_ly4         volume of water in fourth soil layer store [m3]
    _____ c_s_v_h2o_ly5         volume of water in fifth soil layer store [m3]
    _____ c_s_v_h2o_ly6         volume of water in sixth soil layer store [m3]
    ___ Parameters * p_ *
    _____ c_p_t                 T: rainfall aerial correction coefficient
    _____ c_p_c                 C: evaporation decay parameter
    _____ c_p_h                 H: quick runoff coefficient
    _____ c_p_s                 S: drain flow parameter - fraction of saturation excess diverted to drain flow
    _____ c_p_d                 D: soil outflow coefficient
    _____ c_p_z                 Z: effective soil depth [mm]
    _____ c_p_sk                SK: surface routing parameter [hours]
    _____ c_p_fk                FK: inter flow routing parameter [hours]
    _____ c_p_gk                GK: groundwater routing parameter [hours]
    ___ Outputs * out_ *
    _____ c_out_aeva            actual evapotranspiration [mm]
    _____ c_out_q_h2o_ove       overland flow [m3/s]
    _____ c_out_q_h2o_dra       drain flow [m3/s]
    _____ c_out_q_h2o_int       inter flow [m3/s]
    _____ c_out_q_h2o_sgw       shallow groundwater flow [m3/s]
    _____ c_out_q_h2o_dgw       deep groundwater flow [m3/s]
    _____ c_out_q_h2o           total outflow [m3/s]
    """

    # # 1. Hydrology
    # # 1.0. Define internal constants
    nb_soil_layers = 6.0  # number of layers in soil column [-]
    area_m2 = dict_desc[waterbody]['area']  # catchment area [m2]
    time_step_sec = time_gap * 60.0  # [seconds]

    # # 1.1. Collect inputs, states, and parameters
    c_in_rain = dict_meteo[waterbody].loc[datetime_time_step, "rain"]
    c_in_peva = dict_meteo[waterbody].loc[datetime_time_step, "peva"]

    c_s_v_h2o_ove = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ove"]
    c_s_v_h2o_dra = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_dra"]
    c_s_v_h2o_int = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_int"]
    c_s_v_h2o_sgw = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_sgw"]
    c_s_v_h2o_dgw = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_dgw"]
    c_s_v_h2o_ly1 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly1"]
    c_s_v_h2o_ly2 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly2"]
    c_s_v_h2o_ly3 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly3"]
    c_s_v_h2o_ly4 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly4"]
    c_s_v_h2o_ly5 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly5"]
    c_s_v_h2o_ly6 = dict_data_frame[waterbody].loc[datetime_time_step + datetime.timedelta(minutes=-time_gap),
                                                   "c_s_v_h2o_ly6"]

    c_p_t = dict_param[waterbody]['SMART']["c_p_t"]
    c_p_c = dict_param[waterbody]['SMART']["c_p_c"]
    c_p_h = dict_param[waterbody]['SMART']["c_p_h"]
    c_p_s = dict_param[waterbody]['SMART']["c_p_s"]
    c_p_d = dict_param[waterbody]['SMART']["c_p_d"]
    c_p_z = dict_param[waterbody]['SMART']["c_p_z"]
    c_p_sk = dict_param[waterbody]['SMART']["c_p_sk"] * 3600.0  # convert hours in seconds
    c_p_fk = dict_param[waterbody]['SMART']["c_p_fk"] * 3600.0  # convert hours in seconds
    c_p_gk = dict_param[waterbody]['SMART']["c_p_gk"] * 3600.0  # convert hours in seconds

    # # 1.2. Hydrological calculations

    # all calculations in mm equivalent until further notice

    # calculate capacity Z and level LVL of each layer (assumed equal) from effective soil depth
    dict_z_lyr = dict()
    for i in [1, 2, 3, 4, 5, 6]:
        dict_z_lyr[i] = c_p_z / nb_soil_layers
    dict_lvl_lyr = dict()
    dict_lvl_lyr[1] = c_s_v_h2o_ly1 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[2] = c_s_v_h2o_ly2 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[3] = c_s_v_h2o_ly3 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[4] = c_s_v_h2o_ly4 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[5] = c_s_v_h2o_ly5 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[6] = c_s_v_h2o_ly6 / area_m2 * 1e3  # factor 1000 to convert m in mm

    # calculate cumulative level of water in all soil layers at beginning of time step
    lvl_total_start = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_start += dict_lvl_lyr[i]

    # apply parameter T to rainfall data
    rain = c_in_rain * c_p_t
    # calculate rainfall excess
    excess_rain = rain - c_in_peva
    # initialise actual evapotranspiration variable
    c_out_aeva = 0.0

    if excess_rain >= 0.0:  # excess rainfall available for runoff and infiltration
        # actual evapotranspiration = potential evapotranspiration
        c_out_aeva += c_in_peva
        # calculate surface runoff using H parameter
        h_prime = c_p_h * (lvl_total_start / c_p_z)
        overland_flow = h_prime * excess_rain  # surface runoff
        excess_rain -= overland_flow  # remainder that infiltrates
        # calculate percolation through soil layers
        for i in [1, 2, 3, 4, 5, 6]:
            space_in_lyr = dict_z_lyr[i] - dict_lvl_lyr[i]
            if excess_rain <= space_in_lyr:
                dict_lvl_lyr[i] += excess_rain
                excess_rain = 0.0
            else:
                dict_lvl_lyr[i] = dict_z_lyr[i]
                excess_rain -= space_in_lyr
        # calculate saturation excess from remaining excess rainfall after filling layers
        drain_flow = c_p_s * excess_rain
        inter_flow = (1.0 - c_p_s) * excess_rain
        # calculate leak from soil layers
        d_prime = c_p_d * (lvl_total_start / c_p_z)
        # leak to interflow
        for i in [1, 2, 3, 4, 5, 6]:
            leak_interflow = dict_lvl_lyr[i] * (d_prime ** i)
            if leak_interflow < dict_lvl_lyr[i]:
                inter_flow += leak_interflow
                dict_lvl_lyr[i] -= leak_interflow
        # leak to shallow groundwater flow
        shallow_flow = 0.0
        for i in [1, 2, 3, 4, 5, 6]:
            leak_shallow_flow = dict_lvl_lyr[i] * (d_prime / i)
            if leak_shallow_flow < dict_lvl_lyr[i]:
                shallow_flow += leak_shallow_flow
                dict_lvl_lyr[i] -= leak_shallow_flow
        # leak to deep groundwater flow
        power = 0.0
        deep_flow = 0.0
        for i in [6, 5, 4, 3, 2, 1]:
            power += 1.0
            leak_deep_flow = dict_lvl_lyr[i] * (d_prime ** power)
            if leak_deep_flow < dict_lvl_lyr[i]:
                deep_flow += leak_deep_flow
                dict_lvl_lyr[i] -= leak_deep_flow
    else:  # no excess rainfall
        overland_flow = 0.0  # no soil contribution to quick overland flow store
        drain_flow = 0.0  # no soil contribution to quick drain flow store
        inter_flow = 0.0  # no soil contribution to quick + leak interflow store
        shallow_flow = 0.0  # no soil contribution to shallow groundwater flow store
        deep_flow = 0.0  # no soil contribution to deep groundwater flow store

        deficit_rain = excess_rain * (-1.0)  # excess is negative = excess is actually a deficit
        c_out_aeva += rain
        for i in [1, 2, 3, 4, 5, 6]:
            if dict_lvl_lyr[i] >= deficit_rain:  # i.e. all moisture required available in this soil layer
                dict_lvl_lyr[i] -= deficit_rain  # soil layer is reduced by the moisture required
                c_out_aeva += deficit_rain  # this moisture contributes to the actual evapotranspiration
                deficit_rain = 0.0  # the full moisture still required has been met
            else:
                c_out_aeva += dict_lvl_lyr[i]  # takes what is available in this layer
                # effectively reduce the evaporation demand for the next layer using parameter C
                # i.e. the more you move down through the soil layers, the less AEva can meet PEva (exponentially)
                deficit_rain = c_p_c * (deficit_rain - dict_lvl_lyr[i])
                dict_lvl_lyr[i] = 0.0  # soil layer is now empty

    # calculate cumulative level of water in all soil layers at end of time step
    lvl_total_end = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_end += dict_lvl_lyr[i]

    # all calculations in S.I. units now

    # route overland flow (direct runoff)
    c_out_q_h2o_ove = c_s_v_h2o_ove / c_p_sk  # [m3/s]
    c_s_v_h2o_ove_old = c_s_v_h2o_ove
    c_s_v_h2o_ove += (overland_flow / 1e3 * area_m2) - (c_out_q_h2o_ove * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_ove < 0.0:
        logger.debug("{}: {} - Volume in OVE Store has gone negative, volume reset "
                     "to zero.".format(waterbody, datetime_time_step))
        c_s_v_h2o_ove = 0.0
    # route drain flow
    c_out_q_h2o_dra = c_s_v_h2o_dra / c_p_sk  # [m3/s]
    c_s_v_h2o_dra_old = c_s_v_h2o_dra
    c_s_v_h2o_dra += (drain_flow / 1e3 * area_m2) - (c_out_q_h2o_dra * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_dra < 0.0:
        logger.debug("{}: {} - Volume in DRA Store has gone negative, volume reset "
                     "to zero.".format(waterbody, datetime_time_step))
        c_s_v_h2o_dra = 0.0
    # route interflow
    c_out_q_h2o_int = c_s_v_h2o_int / c_p_fk  # [m3/s]
    c_s_v_h2o_int_old = c_s_v_h2o_int
    c_s_v_h2o_int += (inter_flow / 1e3 * area_m2) - (c_out_q_h2o_int * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_int < 0.0:
        logger.debug("{}: {} - Volume in INT Store has gone negative, volume reset "
                     "to zero.".format(waterbody, datetime_time_step))
        c_s_v_h2o_int = 0.0
    # route shallow groundwater flow
    c_out_q_h2o_sgw = c_s_v_h2o_sgw / c_p_gk  # [m3/s]
    c_s_v_h2o_sgw_old = c_s_v_h2o_sgw
    c_s_v_h2o_sgw += (shallow_flow / 1e3 * area_m2) - (c_out_q_h2o_sgw * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_sgw < 0.0:
        logger.debug("{}: {} - Volume in SGW Store has gone negative, volume reset "
                     "to zero.".format(waterbody, datetime_time_step))
        c_s_v_h2o_sgw = 0.0
    # route deep groundwater flow
    c_out_q_h2o_dgw = c_s_v_h2o_dgw / c_p_gk  # [m3/s]
    c_s_v_h2o_dgw_old = c_s_v_h2o_dgw
    c_s_v_h2o_dgw += (deep_flow / 1e3 * area_m2) - (c_out_q_h2o_dgw * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_dgw < 0.0:
        logger.debug("{}: {} - Volume in DGW Store has gone negative, volume reset "
                     "to zero.".format(waterbody, datetime_time_step))
        c_s_v_h2o_dgw = 0.0
    # calculate total outflow
    c_out_q_h2o = c_out_q_h2o_ove + c_out_q_h2o_dra + c_out_q_h2o_int + c_out_q_h2o_sgw + c_out_q_h2o_dgw  # [m3/s]

    # store states and outputs in dictionaries for use in water quality calculations
    dict_lvl_soil = {
        'start': lvl_total_start,
        'end': lvl_total_end
    }  # volumes in soil at beginning and end of time step

    dict_states_old_hd = {
        'ove': c_s_v_h2o_ove_old,
        'dra': c_s_v_h2o_dra_old,
        'int': c_s_v_h2o_int_old,
        'sgw': c_s_v_h2o_sgw_old,
        'dgw': c_s_v_h2o_dgw_old
    }  # volumes in stores at beginning of time step

    dict_flows_mm_hd = {
        'ove': overland_flow,
        'dra': drain_flow,
        'int': inter_flow,
        'sgw': shallow_flow,
        'dgw': deep_flow
    }  # flows leaking from soil layers to the different stores during time step

    dict_states_hd = {
        'ove': c_s_v_h2o_ove,
        'dra': c_s_v_h2o_dra,
        'int': c_s_v_h2o_int,
        'sgw': c_s_v_h2o_sgw,
        'dgw': c_s_v_h2o_dgw
    }  # volumes in stores at end of time step

    dict_outputs_hd = {
        'ove': c_out_q_h2o_ove,
        'dra': c_out_q_h2o_dra,
        'int': c_out_q_h2o_int,
        'sgw': c_out_q_h2o_sgw,
        'dgw': c_out_q_h2o_dgw
    }  # flows leaving the different stores during time step

    # # 1.3. Save inputs, states, and outputs
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_rain", c_in_rain)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_peva", c_in_peva)

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ove", c_s_v_h2o_ove)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_dra", c_s_v_h2o_dra)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_int", c_s_v_h2o_int)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_sgw", c_s_v_h2o_sgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_dgw", c_s_v_h2o_dgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly1", dict_lvl_lyr[1] / 1e3 * area_m2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly2", dict_lvl_lyr[2] / 1e3 * area_m2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly3", dict_lvl_lyr[3] / 1e3 * area_m2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly4", dict_lvl_lyr[4] / 1e3 * area_m2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly5", dict_lvl_lyr[5] / 1e3 * area_m2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly6", dict_lvl_lyr[6] / 1e3 * area_m2)

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_aeva", c_out_aeva)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_ove", c_out_q_h2o_ove)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_dra", c_out_q_h2o_dra)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_int", c_out_q_h2o_int)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_sgw", c_out_q_h2o_sgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_dgw", c_out_q_h2o_dgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o", c_out_q_h2o)

    return {
        'dict_lvl_soil': dict_lvl_soil,
        'dict_states_old_hd': dict_states_old_hd,
        'dict_flows_mm_hd': dict_flows_mm_hd,
        'dict_states_hd': dict_states_hd,
        'dict_outputs_hd': dict_outputs_hd
    }


def infer_parameters(dict_desc, my_dict_param):
    # HYDROLOGICAL MODEL
    # Parameter T: Rainfall aerial correction coefficient
    # my_dict['c_p_t'] = 65.622 * dict_desc['SAAPE'] ** (-0.652) * \
    #     dict_desc['TAYSLO'] ** 0.003 * \
    #     (dict_desc['SlopeLow'] + 1.0) ** (-0.075) * \
    #     (dict_desc['PEAT'] ** 0.5 + 1.0) ** (-0.221) * \
    #     (dict_desc['Made'] ** 0.5 + 1.0) ** (-0.481)
    my_dict_param['c_p_t'] = 1.0
    # Parameter C: Evaporation decay parameter
    my_dict_param['c_p_c'] = log((9.04064 * dict_desc['SAAR'] ** (-0.71009) *
                                  dict_desc['Q.mm'] ** 0.57326 *
                                  dict_desc['FLATWET'] ** (-0.75321) *
                                  (dict_desc['AlluvMIN'] + 1.0) ** (-3.3778) *
                                  (dict_desc['FOREST'] + 1.0) ** (-0.71328) *
                                  ((dict_desc['Pu'] + dict_desc['Pl']) ** 0.5 + 1.0) ** 0.22084) -
                                 1.0)
    if my_dict_param['c_p_c'] < 0.1:
        my_dict_param['c_p_c'] = 0.1
    elif my_dict_param['c_p_c'] > 1.0:
        my_dict_param['c_p_c'] = 1.0

    # Parameter H: Quick runoff coefficient
    my_dict_param['c_p_h'] = log((2.7886 * dict_desc['DRAIND'] ** 0.15655 *
                                  dict_desc['WtdReCoMod'] ** 0.03626 *
                                  (dict_desc['PoorDrain'] + 1.0) ** (-0.08069) *
                                  (dict_desc['Water'] ** 0.25 + 1.0) ** 0.10238 *
                                  (dict_desc['ModP'] + 1.0) ** (-0.14992) *
                                  ((dict_desc['Rkc'] + dict_desc['Rk']) + 1.0) ** (-0.14598) *
                                  ((dict_desc['Pu'] + dict_desc['Pl']) ** 0.5 + 1.0) ** (-0.17896) *
                                  ((dict_desc['Lg'] + dict_desc['Rg']) ** 0.5 + 1.0) ** 0.22405) -
                                 1.0)
    # Parameter S: Drain flow parameter - fraction of saturation excess diverted to drain flow
    drain_eff_factor = 0.6
    my_dict_param['c_p_s'] = dict_desc['land_drain_ratio'] * drain_eff_factor
    # Parameter D: Soil outflow coefficient
    my_dict_param['c_p_d'] = 8.61144e-14 * dict_desc['SAAR'] ** 3.207 * \
                             dict_desc['AVG.SLOPE'] ** (-1.089) * \
                             (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** (-3.765) * \
                             (dict_desc['URBEXT'] ** 0.5 + 1.0) ** 17.515 * \
                             (dict_desc['FOREST'] + 1.0) ** 9.544 * \
                             (dict_desc['WellDrain'] + 1.0) ** 5.654 * \
                             (dict_desc['HighP'] ** 0.5 + 1.0) ** (-6.206) * \
                             ((dict_desc['Rkd'] + dict_desc['Lk']) + 1.0) ** 1.553 * \
                             ((dict_desc['Lm'] + dict_desc['Rf']) + 1.0) ** 4.251 * \
                             exp(dict_desc['Ll']) ** (-1.186)
    # Parameter Z: Effective soil depth (mm)
    my_dict_param['c_p_z'] = 9183325.942 * dict_desc['SAAR'] ** (-1.8501) * \
                             dict_desc['DRAIND'] ** 0.6332 * \
                             (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** 1.7288 * \
                             dict_desc['FARL'] ** (-2.9124) * \
                             (dict_desc['URBEXT'] ** 0.5 + 1.0) ** (-5.6337) * \
                             (dict_desc['HighP'] ** 0.5 + 1.0) ** 3.0505 * \
                             ((dict_desc['Lm'] + dict_desc['Rf']) + 1.0) ** (-2.1927) * \
                             exp(dict_desc['Ll']) ** 0.5544 + \
                             1.0
    # Parameter SK: Surface routing parameter (hours)
    my_dict_param['c_p_sk'] = 14612.0 * (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** 2.015 * \
                              dict_desc['FARL'] ** (-6.859) * \
                              dict_desc['SAAR'] ** (-0.825) * \
                              (dict_desc['ARTDRAIN2'] + 1.0) ** (-1.052) * \
                              (dict_desc['PoorDrain'] + 1.0) ** (-1.467) + \
                              1.0
    # Parameter FK: Interflow routing parameter (hours)
    my_dict_param['c_p_fk'] = 5.67e-7 * dict_desc['SAAR'] ** 5.6188 * \
                              dict_desc['Q.mm'] ** (-3.0367) * \
                              (dict_desc['ARTDRAIN2'] + 1.0) ** (-1.2787) * \
                              (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** 3.0169 * \
                              ((dict_desc['VulX'] + dict_desc['VulE']) ** 0.5 + 1.0) ** (-2.8231) * \
                              ((dict_desc['VulM'] + dict_desc['VulL']) + 1.0) ** 2.7265 * \
                              (dict_desc['URBEXT'] ** 0.5 + 1.0) ** (-10.386) * \
                              (dict_desc['FOREST'] + 1.0) ** (-2.4304) * \
                              (dict_desc['HighP'] ** 0.5 + 1.0) ** 6.0892 * \
                              (dict_desc['PNA'] + 1.0) ** 2.7813 * \
                              ((dict_desc['Rkc'] + dict_desc['Rk']) + 1.0) ** (-1.6107) + \
                              1.0
    # Parameter GK: Groundwater routing parameter (hours)
    my_dict_param['c_p_gk'] = 46950.0 + dict_desc['SlopeLow'] * 8676.0 + \
                              dict_desc['SAAPE'] * (-82.27) + \
                              (dict_desc['Rkc'] + dict_desc['Rk']) * (-7204.0) + \
                              (dict_desc['Pu'] + dict_desc['Pl']) * (-1911.0) + \
                              dict_desc['Made'] * (-127800.0) + \
                              dict_desc['WtdReCoMod'] * (-49470.0) + \
                              dict_desc['FOREST'] * 9257.0 + \
                              dict_desc['SAAR'] * (-5.379) + \
                              dict_desc['WtdReCoMod'] * dict_desc['SAAR'] * 41.68
    if my_dict_param['c_p_gk'] < 0.3 * my_dict_param['c_p_fk']:
        my_dict_param['c_p_gk'] = 3.0 * my_dict_param['c_p_fk']
