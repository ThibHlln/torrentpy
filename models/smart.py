# __________________
#
# Catchment model * c_ *
# _ Hydrology
# ___ Inputs
# _____ c_in_rain             precipitation as rain [mm/time step]
# _____ c_in_peva             potential evapotranspiration [mm/time step]
# _____ c_in_temp             water temperature [degree celsius]
# ___ States
# _____ c_s_v_h2o_ove         volume of water in overland store [m3]
# _____ c_s_v_h2o_dra         volume of water in drain store [m3]
# _____ c_s_v_h2o_int         volume of water in inter store [m3]
# _____ c_s_v_h2o_sgw         volume of water in shallow groundwater store [m3]
# _____ c_s_v_h2o_dgw         volume of water in deep groundwater store [m3]
# _____ c_s_v_h2o_ly1         volume of water in first soil layer store [m3]
# _____ c_s_v_h2o_ly2         volume of water in second soil layer store [m3]
# _____ c_s_v_h2o_ly3         volume of water in third soil layer store [m3]
# _____ c_s_v_h2o_ly4         volume of water in fourth soil layer store [m3]
# _____ c_s_v_h2o_ly5         volume of water in fifth soil layer store [m3]
# _____ c_s_v_h2o_ly6         volume of water in sixth soil layer store [m3]
# ___ Parameters
# _____ c_p_t                 T: rainfall aerial correction coefficient
# _____ c_p_c                 C: evaporation decay parameter
# _____ c_p_h                 H: quick runoff coefficient
# _____ c_p_s                 S: drain flow parameter - fraction of saturation excess diverted to drain flow
# _____ c_p_d                 D: soil outflow coefficient
# _____ c_p_z                 Z: effective soil depth [mm]
# _____ c_p_sk                SK: surface routing parameter [s]
# _____ c_p_fk                FK: inter flow routing parameter [s]
# _____ c_p_gk                GK: groundwater routing parameter [s]
# _____ c_p_rk                RK: river routing parameter [s]
# ___ Outputs
# _____ c_out_aeva            actual evapotranspiration [mm]
# _____ c_out_q_h2o_ove       overland flow [m3/s]
# _____ c_out_q_h2o_dra       drain flow [m3/s]
# _____ c_out_q_h2o_int       inter flow [m3/s]
# _____ c_out_q_h2o_sgw       shallow groundwater flow [m3/s]
# _____ c_out_q_h2o_dgw       deep groundwater flow [m3/s]
# _____ c_out_q_h2o           total outflow [m3/s]
# _ Water Quality
# ___ Inputs
# _____ c_in_l_no3            nitrate loading on land [kg/ha/time step]
# _____ c_in_l_nh4            ammonia loading on land [kg/ha/time step]
# _____ c_in_l_dph            dissolved phosphorus loading on land [kg/ha/time step]
# _____ c_in_l_pph            particulate phosphorus loading on land [kg/ha/time step]
# _____ c_in_l_sed            sediment movable from land [kg/ha/time step]
# ___ States
# _____ c_s_c_no3_ove         concentration of nitrate in overland store [kg/m3]
# _____ c_s_c_no3_dra         concentration of nitrate in drain store [kg/m3]
# _____ c_s_c_no3_int         concentration of nitrate in inter store [kg/m3]
# _____ c_s_c_no3_sgw         concentration of nitrate in shallow groundwater store [kg/m3]
# _____ c_s_c_no3_dgw         concentration of nitrate in deep groundwater store [kg/m3]
# _____ c_s_c_nh4_ove         concentration of ammonia in overland store [kg/m3]
# _____ c_s_c_nh4_dra         concentration of ammonia in drain store [kg/m3]
# _____ c_s_c_nh4_int         concentration of ammonia in inter store [kg/m3]
# _____ c_s_c_nh4_sgw         concentration of ammonia in shallow groundwater store [kg/m3]
# _____ c_s_c_nh4_dgw         concentration of ammonia in deep groundwater store [kg/m3]
# _____ c_s_c_dph_ove         concentration of dissolved phosphorus in overland store [kg/m3]
# _____ c_s_c_dph_dra         concentration of dissolved phosphorus in drain store [kg/m3]
# _____ c_s_c_dph_int         concentration of dissolved phosphorus in inter store [kg/m3]
# _____ c_s_c_dph_sgw         concentration of dissolved phosphorus in shallow groundwater store [kg/m3]
# _____ c_s_c_dph_dgw         concentration of dissolved phosphorus in deep groundwater store [kg/m3]
# _____ c_s_c_pph_ove         concentration of particulate phosphorus in overland store [kg/m3]
# _____ c_s_c_pph_dra         concentration of particulate phosphorus in drain store [kg/m3]
# _____ c_s_c_pph_int         concentration of particulate phosphorus in inter store [kg/m3]
# _____ c_s_c_pph_sgw         concentration of particulate phosphorus in shallow groundwater store [kg/m3]
# _____ c_s_c_pph_dgw         concentration of particulate phosphorus in deep groundwater store [kg/m3]
# _____ c_s_c_sed_ove         concentration of sediment in overland store [kg/m3]
# _____ c_s_c_sed_dra         concentration of sediment in drain store [kg/m3]
# _____ c_s_c_sed_int         concentration of sediment in inter store [kg/m3]
# _____ c_s_c_sed_sgw         concentration of sediment in shallow groundwater store [kg/m3]
# _____ c_s_c_sed_dgw         concentration of sediment in deep groundwater store [kg/m3]
# _____ c_s_c_no3_soil        concentration of nitrate in soil column [kg/m3]
# _____ c_s_c_nh4_soil        concentration of ammonia in soil column [kg/m3]
# _____ c_s_c_p_org_ra_soil   concentration of readily available organic phosphorus in soil column [kg/m3]
# _____ c_s_c_p_ino_ra_soil   concentration of readily available inorganic phosphorus phosphorus in soil column [kg/m3]
# _____ c_s_m_p_org_fb_soil   mass of firmly bound organic phosphorus in soil column [kg]
# _____ c_s_m_p_ino_fb_soil   mass of firmly bound inorganic phosphorus in soil column [kg]
# ___ Parameters
# _____ c_p_att_no3_ove       daily attenuation factor for nitrate in overland flow [-]
# _____ c_p_att_nh4_ove       daily attenuation factor for ammonia in overland flow [-]
# _____ c_p_att_dph_ove       daily attenuation factor for dissolved phosphorus in overland flow [-]
# _____ c_p_att_pph_ove       daily attenuation factor for particulate phosphorus in overland flow [-]
# _____ c_p_att_sed_ove       daily attenuation factor for sediment in overland flow [-]
# _____ c_p_att_no3_dra       daily attenuation factor for nitrate in drain flow [-]
# _____ c_p_att_nh4_dra       daily attenuation factor for ammonia in drain flow [-]
# _____ c_p_att_dph_dra       daily attenuation factor for dissolved phosphorus in drain flow [-]
# _____ c_p_att_pph_dra       daily attenuation factor for particulate phosphorus in drain flow [-]
# _____ c_p_att_sed_dra       daily attenuation factor for sediment in drain flow [-]
# _____ c_p_att_no3_int       daily attenuation factor for nitrate in inter flow [-]
# _____ c_p_att_nh4_int       daily attenuation factor for ammonia in inter flow [-]
# _____ c_p_att_dph_int       daily attenuation factor for dissolved phosphorus in inter flow [-]
# _____ c_p_att_pph_int       daily attenuation factor for particulate phosphorus in inter flow [-]
# _____ c_p_att_sed_int       daily attenuation factor for sediment in inter flow [-]
# _____ c_p_att_no3_sgw       daily attenuation factor for nitrate in shallow groundwater flow [-]
# _____ c_p_att_nh4_sgw       daily attenuation factor for ammonia in shallow groundwater flow [-]
# _____ c_p_att_dph_sgw       daily attenuation factor for dissolved phosphorus in shallow groundwater flow [-]
# _____ c_p_att_pph_sgw       daily attenuation factor for particulate phosphorus in shallow groundwater flow [-]
# _____ c_p_att_sed_sgw       daily attenuation factor for sediment in shallow groundwater flow [-]
# _____ c_p_att_no3_dgw       daily attenuation factor for nitrate in deep groundwater flow [-]
# _____ c_p_att_nh4_dgw       daily attenuation factor for ammonia in deep groundwater flow [-]
# _____ c_p_att_dph_dgw       daily attenuation factor for dissolved phosphorus in deep groundwater flow [-]
# _____ c_p_att_pph_dgw       daily attenuation factor for particulate phosphorus in deep groundwater flow [-]
# _____ c_p_att_sed_dgw       daily attenuation factor for sediment in deep groundwater flow [-]
# _____ c_p_att_no3_soil      daily attenuation factor for nitrate in soil column [-]
# _____ c_p_att_nh4_soil      daily attenuation factor for ammonia in soil column [-]
# _____ c_p_att_p_org_ra_soil daily attenuation factor for readily available organic phosphorus in soil column [-]
# _____ c_p_att_p_ino_ra_soil daily attenuation factor for readily available inorganic phosphorus in soil column [-]
# _____ c_p_att_p_org_fb_soil daily attenuation factor for firmly bound organic phosphorus in soil column [-]
# _____ c_p_att_p_ino_fb_soil daily attenuation factor for firmly bound inorganic phosphorus in soil column [-]
# ___ Outputs
# _____ c_out_c_no3_ove       nitrate concentration in overland flow [kg/m3]
# _____ c_out_c_nh4_ove       ammonia concentration in overland flow [kg/m3]
# _____ c_out_c_dph_ove       dissolved phosphorus in overland flow [kg/m3]
# _____ c_out_c_pph_ove       particulate phosphorus in overland flow [kg/m3]
# _____ c_out_c_sed_ove       sediment concentration in overland flow [kg/m3]
# _____ c_out_c_no3_dra       nitrate concentration in drain flow [kg/m3]
# _____ c_out_c_nh4_dra       ammonia concentration in drain flow [kg/m3]
# _____ c_out_c_dph_dra       dissolved phosphorus in drain flow [kg/m3]
# _____ c_out_c_pph_dra       particulate phosphorus in drain flow [kg/m3]
# _____ c_out_c_sed_dra       sediment concentration in drain flow [kg/m3]
# _____ c_out_c_no3_int       nitrate concentration in inter flow [kg/m3]
# _____ c_out_c_nh4_int       ammonia concentration in inter flow [kg/m3]
# _____ c_out_c_dph_int       dissolved phosphorus in inter flow [kg/m3]
# _____ c_out_c_pph_int       particulate phosphorus in inter flow [kg/m3]
# _____ c_out_c_sed_int       sediment concentration in inter flow [kg/m3]
# _____ c_out_c_no3_sgw       nitrate concentration in shallow groundwater flow [kg/m3]
# _____ c_out_c_nh4_sgw       ammonia concentration in shallow groundwater flow [kg/m3]
# _____ c_out_c_dph_sgw       dissolved phosphorus in shallow groundwater flow [kg/m3]
# _____ c_out_c_pph_sgw       particulate phosphorus in shallow groundwater flow [kg/m3]
# _____ c_out_c_sed_sgw       sediment concentration in shallow groundwater flow [kg/m3]
# _____ c_out_c_no3_dgw       nitrate concentration in deep groundwater flow [kg/m3]
# _____ c_out_c_nh4_dgw       ammonia concentration in deep groundwater flow [kg/m3]
# _____ c_out_c_dph_dgw       dissolved phosphorus in deep groundwater flow [kg/m3]
# _____ c_out_c_pph_dgw       particulate phosphorus in deep groundwater flow [kg/m3]
# _____ c_out_c_sed_dgw       sediment concentration in deep groundwater flow [kg/m3]
# _____ c_out_c_no3           nitrate concentration in total outflow [kg/m3]
# _____ c_out_c_nh4           ammonia concentration in total outflow [kg/m3]
# _____ c_out_c_dph           dissolved phosphorus in total outflow [kg/m3]
# _____ c_out_c_pph           particulate phosphorus in total outflow [kg/m3]
# _____ c_out_c_sed           sediment concentration in total outflow [kg/m3]
# __________________
#

import math
import datetime


def run(waterbody, dict_data_frame, dict_param, dict_meteo, dict_loads, datetime_time_step, time_gap):

    nb_soil_layers = 6.0  # number of layers in soil column
    area = 100.0  # catchment area in m2
    time_step_min = 1440  # in minutes
    time_step_sec = time_step_min * 60  # in seconds
    time_factor = time_step_sec / 86400.0
    if time_factor < 0.005:
        time_factor = 0.005

    volume_tolerance = 1.0E-8
    flow_threshold_for_erosion = {
        'ove': 0.005,
        'dra': 0.05
    }

    stores = ['ove', 'dra', 'int', 'sgw', 'dgw']
    stores_contaminants = ['no3', 'nh4', 'dph', 'pph', 'sed']
    soil_contaminants = ['no3', 'nh4', 'p_ino_ra', 'p_ino_fb', 'p_org_ra', 'p_org_fb']

    daily_sediment_threshold = 1.0
    sediment_threshold = daily_sediment_threshold * time_factor
    sediment_k = 1.0
    sediment_p = 1.0
    soil_test_p = 1.0  # [mg/kg]

    day_growing_season = 152.0
    day_of_year = 1.0

    # dictionaries to be used for 6 soil layers
    dict_z_lyr = dict()
    dict_lvl_lyr = dict()

    # other dictionaries
    dict_mob_factors = {
        'ove': {'no3': 1.0, 'nh4': 1.0, 'dph': 1.0, 'pph': 1.0, 'sed': 1.0},
        'dra': {'no3': 1.0, 'nh4': 1.0, 'dph': 1.0, 'pph': 1.0, 'sed': 1.0},
        'int': {'no3': 1.0, 'nh4': 1.0, 'dph': 1.0, 'pph': 1.0, 'sed': 1.0},
        'sgw': {'no3': 1.0, 'nh4': 1.0, 'dph': 1.0, 'pph': 1.0, 'sed': 1.0},
        'dgw': {'no3': 1.0, 'nh4': 1.0, 'dph': 1.0, 'pph': 1.0, 'sed': 1.0}
    }

    # # 1. Hydrology
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

    c_p_t = dict_param[waterbody]["c_p_t"]
    c_p_c = dict_param[waterbody]["c_p_c"]
    c_p_h = dict_param[waterbody]["c_p_h"]
    c_p_s = dict_param[waterbody]["c_p_s"]
    c_p_d = dict_param[waterbody]["c_p_d"]
    c_p_z = dict_param[waterbody]["c_p_z"]
    c_p_sk = dict_param[waterbody]["c_p_sk"]
    c_p_fk = dict_param[waterbody]["c_p_fk"]
    c_p_gk = dict_param[waterbody]["c_p_gk"]
    c_p_rk = dict_param[waterbody]["c_p_rk"]

    # # 1.2. Hydrological calculations

    # all calculations in mm equivalent until further notice

    # calculate capacity Z and level LVL of each layer (assumed equal) from effective soil depth
    for i in [1, 2, 3, 4, 5, 6]:
        dict_z_lyr[i] = c_p_z / nb_soil_layers

    dict_lvl_lyr[1] = c_s_v_h2o_ly1 / area * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[2] = c_s_v_h2o_ly2 / area * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[3] = c_s_v_h2o_ly3 / area * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[4] = c_s_v_h2o_ly4 / area * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[5] = c_s_v_h2o_ly5 / area * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[6] = c_s_v_h2o_ly6 / area * 1e3  # factor 1000 to convert m in mm

    # calculate cumulative level of water in all soil layers at beginning of time step
    lvl_total_start = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_start += dict_lvl_lyr[i]

    # apply parameter T to rainfall data
    c_in_rain = c_in_rain * c_p_t
    # calculate rainfall excess
    excess_rain = c_in_rain - c_in_peva
    # initialise actual evapotranspiration variable
    c_out_aeva = 0.0

    if excess_rain >= 0.0:  # excess rainfall available for runoff and infiltration
        # actual evapotranspiration = potential evapotranspiration
        c_out_aeva += c_in_peva
        # calculate surface runoff using H and Y parameters
        h_prime = c_p_h * (lvl_total_start / c_p_z)
        overland_flow = h_prime * excess_rain  # surface runoff
        excess_rain = excess_rain - overland_flow  # remainder that infiltrates
        # calculate percolation through soil layers
        for i in [1, 2, 3, 4, 5, 6]:
            space_in_lyr = dict_z_lyr[i] - dict_lvl_lyr[i]
            if space_in_lyr <= excess_rain:
                dict_lvl_lyr[i] += excess_rain
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
        overland_flow = 0.0  # no quick overland flow
        drain_flow = 0.0  # no quick drain flow
        inter_flow = 0.0  # no quick + leak interflow
        shallow_flow = 0.0  # no shallow groundwater flow
        deep_flow = 0.0

        deficit_rain = excess_rain * (-1.0)  # excess is actually a deficit
        c_out_aeva += c_in_rain
        for i in [1, 2, 3, 4, 5, 6]:
            if dict_lvl_lyr[i] >= deficit_rain:
                dict_lvl_lyr[i] -= deficit_rain
                c_out_aeva += deficit_rain
                deficit_rain = 0.0
            else:
                c_out_aeva += dict_lvl_lyr[i]
                deficit_rain = c_p_c * (deficit_rain - dict_lvl_lyr[i])
                dict_lvl_lyr[i] = 0.0

    # calculate cumulative level of water in all soil layers at end of time step
    lvl_total_end = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_end += dict_lvl_lyr[i]

    # all calculations in S.I. units now

    # route overland flow (direct runoff)
    c_out_q_h2o_ove = c_s_v_h2o_ove / c_p_sk  # [m3/s]
    c_s_v_h2o_ove_old = c_s_v_h2o_ove
    c_s_v_h2o_ove += (overland_flow / 1e3 * area) - (c_out_q_h2o_ove * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_ove < 0.0:
        c_s_v_h2o_ove = 0.0
    # route drain flow
    c_out_q_h2o_dra = c_s_v_h2o_dra / c_p_sk  # [m3/s]
    c_s_v_h2o_dra_old = c_s_v_h2o_dra
    c_s_v_h2o_dra += (drain_flow / 1e3 * area) - (c_out_q_h2o_dra * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_dra < 0.0:
        c_s_v_h2o_dra = 0.0
    # route interflow
    c_out_q_h2o_int = c_s_v_h2o_int / c_p_fk  # [m3/s]
    c_s_v_h2o_int_old = c_s_v_h2o_int
    c_s_v_h2o_int += (inter_flow / 1e3 * area) - (c_out_q_h2o_int * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_int < 0.0:
        c_s_v_h2o_int = 0.0
    # route shallow groundwater flow
    c_out_q_h2o_sgw = c_s_v_h2o_sgw / c_p_gk  # [m3/s]
    c_s_v_h2o_sgw_old = c_s_v_h2o_sgw
    c_s_v_h2o_sgw += (inter_flow / 1e3 * area) - (c_out_q_h2o_sgw * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_sgw < 0.0:
        c_s_v_h2o_sgw = 0.0
    # route deep groundwater flow
    c_out_q_h2o_dgw = c_s_v_h2o_dgw / c_p_gk  # [m3/s]
    c_s_v_h2o_dgw_old = c_s_v_h2o_dgw
    c_s_v_h2o_dgw += (inter_flow / 1e3 * area) - (c_out_q_h2o_dgw * time_step_sec)  # [m3] - [m3]
    if c_s_v_h2o_dgw < 0.0:
        c_s_v_h2o_dgw = 0.0
    # calculate total outflow
    c_out_q_h2o = c_out_q_h2o_ove + c_out_q_h2o_dra + c_out_q_h2o_int + c_out_q_h2o_sgw + c_out_q_h2o_dgw  # [m3/s]

    # store states and outputs in dictionaries for use in water quality calculations
    dict_states_old_hd = {
        'ove': c_s_v_h2o_ove_old,
        'dra': c_s_v_h2o_dra_old,
        'int': c_s_v_h2o_int_old,
        'sgw': c_s_v_h2o_sgw_old,
        'dgw': c_s_v_h2o_dgw_old
    }

    dict_states_hd = {
        'ove': c_s_v_h2o_ove,
        'dra': c_s_v_h2o_dra,
        'int': c_s_v_h2o_int,
        'sgw': c_s_v_h2o_sgw,
        'dgw': c_s_v_h2o_dgw
    }

    dict_flows_mm_hd = {
        'ove': overland_flow,
        'dra': drain_flow,
        'int': inter_flow,
        'sgw': shallow_flow,
        'dgw': deep_flow
    }

    dict_outputs_hd = {
        'ove': c_out_q_h2o_ove,
        'dra': c_out_q_h2o_dra,
        'int': c_out_q_h2o_int,
        'sgw': c_out_q_h2o_sgw,
        'dgw': c_out_q_h2o_dgw
    }

    # 1.3. Save inputs, states, and outputs
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_rain", c_in_rain)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_peva", c_in_rain)

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ove", c_s_v_h2o_ove)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_dra", c_s_v_h2o_dra)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_int", c_s_v_h2o_int)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_sgw", c_s_v_h2o_sgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_dgw", c_s_v_h2o_dgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly1", c_s_v_h2o_ly1)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly2", c_s_v_h2o_ly2)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly3", c_s_v_h2o_ly3)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly4", c_s_v_h2o_ly4)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly5", c_s_v_h2o_ly5)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_v_h2o_ly6", c_s_v_h2o_ly6)

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_aeva", c_out_aeva)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_ove", c_out_q_h2o_ove)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_dra", c_out_q_h2o_dra)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_int", c_out_q_h2o_int)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_sgw", c_out_q_h2o_sgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o_dgw", c_out_q_h2o_dgw)
    dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_q_h2o", c_out_q_h2o)

    # # 2. Water quality calculations
    # # 2.1. Collect inputs, states, and parameters

    c_in_temp = dict_meteo[waterbody].loc[datetime_time_step, "temp"]
    c_in_l_no3 = dict_loads[waterbody].loc[datetime_time_step, "no3"]
    c_in_l_nh4 = dict_loads[waterbody].loc[datetime_time_step, "no3"]
    c_in_l_p_ino = dict_loads[waterbody].loc[datetime_time_step, "no3"]
    c_in_l_p_org = dict_loads[waterbody].loc[datetime_time_step, "no3"]
    dict_mass_applied = dict()
    dict_mass_applied['no3'] = c_in_l_no3 * area * 1e-4  # area in m2 converted into ha
    dict_mass_applied['nh4'] = c_in_l_nh4 * area * 1e-4  # area in m2 converted into ha
    dict_mass_applied['p_ino'] = c_in_l_p_ino * area * 1e-4  # area in m2 converted into ha
    dict_mass_applied['p_org'] = c_in_l_p_org * area * 1e-4  # area in m2 converted into ha

    dict_states_wq = dict()  # for states of the stores
    dict_c_outflow = dict()  # for outflow concentrations from stores
    dict_att_factors = dict()  # for attenuation factors in stores
    for store in stores:
        my_dict_1 = dict()
        my_dict_2 = dict()
        my_dict_3 = dict()
        for contaminant in stores_contaminants:
            my_dict_1[contaminant] = dict_data_frame[waterbody].loc[datetime_time_step +
                                                                    datetime.timedelta(minutes=-time_gap),
                                                                    "c_s_v_{}_{}".format(contaminant, store)]
            my_dict_2[contaminant] = 0.0
            my_dict_3[contaminant] = dict_param[waterbody]["c_p_att_{}_{}".format(contaminant, store)] * time_factor
        dict_states_wq[store] = my_dict_1[:]
        dict_c_outflow[store] = my_dict_2[:]
        dict_att_factors[store] = my_dict_3[:]
    my_dict_4 = dict()
    for contaminant in soil_contaminants:
        my_dict_4[contaminant] = dict_data_frame[waterbody].loc[datetime_time_step +
                                                                datetime.timedelta(minutes=-time_gap),
                                                                "c_s_v_{}_soil".format(contaminant)]
    dict_states_wq['soil'] = my_dict_4[:]
    # create 'artificial' states (in dictionary only) to sum organic and inorganic DPH and PPH
    dict_states_wq['soil']['dph'] = dict_states_wq['soil']['p_org_ra'] + dict_states_wq['soil']['p_ino_ra']  # [kg/m3]
    dict_states_wq['soil']['pph'] = dict_states_wq['soil']['p_org_fb'] + dict_states_wq['soil']['p_ino_fb']  # [kg]

    # # 2.2. Water quality calculations
    # # 2.2.1. Overland flow contamination & drain flow contamination
    dict_m_mobilised = {'no3': 0.0, 'nh4': 0.0, 'dph': 0.0, 'pph': 0.0, 'sed': 0.0}
    for store in ['ove', 'dra']:
        # dissolved contaminants: nitrate, ammonia, dissolved phosphorus (readily available)
        for contaminant in ['no3', 'nh4', 'dph']:
            c_store = dict_states_wq[store][contaminant]
            m_store = c_store * dict_states_old_hd[store]
            dict_c_outflow[store][contaminant] = c_store
            attenuation = dict_att_factors[store][contaminant]
            if attenuation > 1.0:
                attenuation = 1.0
            elif attenuation < 0.0:
                attenuation = 0.0
            m_store_att = m_store * attenuation
            mobilisation = dict_mob_factors[store][contaminant]
            if (mobilisation < 0.0) or (mobilisation > 1.0):
                mobilisation = 1.0
            m_mobilised = (dict_flows_mm_hd[store] / 1e3 * area) * dict_states_wq['soil'][contaminant] * mobilisation
            m_store = m_store_att + m_mobilised - dict_outputs_hd[store] * c_store
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                dict_states_wq[store][contaminant] = 0.0
            else:
                dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
            dict_m_mobilised[contaminant] += m_mobilised

        # sediment
        contaminant = 'sed'
        c_store = dict_states_wq[store][contaminant]
        m_store = c_store * dict_states_old_hd[store]
        attenuation = dict_att_factors[store][contaminant]
        if attenuation > 1.0:
            attenuation = 1.0
        elif attenuation < 0.0:
            attenuation = 0.0
        m_store_att = m_store * attenuation
        m_sediment_per_area = 0.0
        if (dict_flows_mm_hd[store] < sediment_threshold) or \
                (dict_flows_mm_hd[store] < flow_threshold_for_erosion[store]):
            m_sediment = 0.0
            dict_c_outflow[store][contaminant] = 0.0
        else:
            m_sediment_per_area = (sediment_k * dict_flows_mm_hd[store] ** sediment_p) * time_factor
            m_sediment = m_sediment_per_area * area
            dict_c_outflow[store][contaminant] = m_sediment / (dict_flows_mm_hd[store] / 1e3 * area)
        if store == 'ove':  # no mass balance, all sediment assumed gone
            dict_states_wq[store][contaminant] = 0.0
        elif store == 'dra':  # mass balance
            m_store = m_store_att + m_sediment - dict_outputs_hd[store] * dict_c_outflow[store][contaminant]
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                dict_states_wq[store][contaminant] = 0.0
            else:
                dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
        dict_m_mobilised[contaminant] += m_sediment

        # particulate phosphorus (firmly bound phosphorus)
        contaminant = 'pph'
        c_store = dict_states_wq[store][contaminant]
        m_store = c_store * dict_states_old_hd[store]
        attenuation = dict_att_factors[store][contaminant]
        if attenuation > 1.0:
            attenuation = 1.0
        elif attenuation < 0.0:
            attenuation = 0.0
        m_store_att = m_store * attenuation
        if (overland_flow < sediment_threshold) or (dict_flows_mm_hd[store] < flow_threshold_for_erosion[store]):
            m_particulate_p = 0.0
            dict_c_outflow[store][contaminant] = 0.0
        else:
            soil_loss = m_sediment_per_area * 1e4 * 3.1536e7 / time_step_sec  # [kg/ha/yr]
            p_enrichment_ratio = math.exp(2.48 - 0.27 * math.log1p(soil_loss))  # [-]
            if p_enrichment_ratio < 0.1:
                p_enrichment_ratio = 0.1
            elif p_enrichment_ratio > 6.0:
                p_enrichment_ratio = 6.0
            m_particulate_p = soil_test_p * m_sediment * p_enrichment_ratio  # [kg]
            if m_particulate_p < dict_states_wq['soil']['p_ino_fb']:  # P removed from inorganic P firmly in soil
                dict_states_wq['soil']['p_ino_fb'] -= m_particulate_p
                m_particulate_p_missing = 0.0  # [kg]
            else:  # P is also removed from organic firmly bound after inorganic firmly bound
                m_particulate_p_missing = m_particulate_p - dict_states_wq['soil']['p_ino_fb']
                dict_states_wq['soil']['p_ino_fb'] = 0.0
                if m_particulate_p_missing < dict_states_wq['soil']['p_org_fb']:
                    dict_states_wq['soil']['p_org_fb'] -= m_particulate_p_missing
                    m_particulate_p_missing = 0.0  # [kg]
                else:
                    m_particulate_p_missing -= dict_states_wq['soil']['p_org_fb']
                    dict_states_wq['soil']['p_org_fb'] = 0.0
            dict_states_wq['soil'][contaminant] = dict_states_wq['soil']['p_org_fb'] + \
                dict_states_wq['soil']['p_ino_fb']
            m_particulate_p -= m_particulate_p_missing
            dict_c_outflow[store][contaminant] = m_particulate_p / (dict_flows_mm_hd[store] / 1e3 * area)
        m_store = m_store_att + m_particulate_p - dict_outputs_hd[store] * c_store
        if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
            dict_states_wq[store][contaminant] = 0.0
        else:
            dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
        dict_m_mobilised[contaminant] += m_particulate_p

    # # 2.2.2. Interflow contamination, Shallow groundwater flow contamination, & Deep groundwater flow contamination
    for store in ['int', 'sgw', 'dgw']:
        for contaminant in stores_contaminants:
            c_store = dict_states_wq[store][contaminant]
            m_store = c_store * dict_states_old_hd[store]
            dict_c_outflow[store][contaminant] = c_store
            attenuation = dict_att_factors[store][contaminant]
            if attenuation > 1.0:
                attenuation = 1.0
            elif attenuation < 0.0:
                attenuation = 0.0
            m_store_att = m_store * attenuation
            mobilisation = dict_mob_factors[store][contaminant]
            if (mobilisation < 0.0) or (mobilisation > 1.0):
                mobilisation = 1.0
            m_mobilised = (dict_flows_mm_hd[store] / 1e3 * area) * dict_states_wq['soil'][contaminant] * mobilisation
            m_store = m_store_att + m_mobilised - dict_outputs_hd[store] * c_store
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                dict_states_wq[store][contaminant] = 0.0
            else:
                dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]

    # # 2.2.3. Soil store contamination
    # soil constants
    cst_c1n = 1.0  # rate coefficient (m/day) for denitrification
    cst_c3n = 1.0  # rate coefficient (m/day) for NO3 plant uptake
    cst_c4n = 1.0  # rate coefficient (m/day) for nitrification
    cst_c5n = 1.0  # rate coefficient (m/day) for N mineralisation
    cst_c6n = 1.0  # rate coefficient (m/day) for N immobilisation
    cst_c7n = 1.0  # rate coefficient (m/day) for NH4 plant uptake
    cst_c1p = 1.0  # rate coefficient (m/day) for organic P plant uptake
    cst_c2p = 1.0  # rate coefficient (m/day) for P immobilisation
    cst_c3p = 1.0  # rate coefficient (m/day) for P mineralisation
    cst_c4p = 1.0  # conversion rate of readily available organic P into firmly bound organic P
    cst_c5p = 1.0  # conversion rate of firmly bound organic P into readily available organic P
    cst_c6p = 1.0  # rate coefficient (m/day) for inorganic P plant uptake
    cst_c7p = 1.0  # conversion rate of readily available inorganic P into firmly bound inorganic P
    cst_c8p = 1.0  # conversion rate of firmly bound inorganic P into readily available inorganic P

    # nitrate
    s1 = lvl_total_end / (c_p_z * 0.275)  # soil moisture factor
    # assuming field capacity = 110 mm/m depth & soil porosity = 0.4 => 0.11 * 0.4 = 0.275
    # (SMD max assumed by Met Eireann)
    if s1 > 1.0:
        s1 = 1.0
    elif s1 < 0.0:
        s1 = 0.0
    s2 = 0.66 + 0.34 * math.sin(2.0 * math.pi * (day_of_year - day_growing_season) / 365.0)  # seasonal plant growth
    c3_no3 = cst_c3n * (1.047 ** (c_in_temp - 20.0))
    pu_no3 = c3_no3 * s1 * s2  # plant uptake
    c1 = cst_c1n * (1.047 ** (c_in_temp - 20.0))
    c4 = cst_c4n * (1.047 ** (c_in_temp - 20.0))
    if c_in_temp < 0.0:
        dn = 0.0  # no denitrification
        ni = 0.0  # no nitrification
        fx = 0.0  # no fixation
    else:
        dn = c1 * s1  # denitrification
        ni = c4 * s1 * dict_states_wq['soil']['nh4'] * (lvl_total_start / 1e3 * area)  # nitrification
        fx = 0.0  # fixation
    processes_attenuation = 1.0 - pu_no3 - dn + fx  # attenuation due to processes in soil system
    external_attenuation = dict_att_factors['soil']['no3']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['no3'] * (lvl_total_start / 1e3 * area)  # mass in soil at beginning of time step
    m_soil_new = m_soil * attenuation + ni * time_factor + dict_mass_applied['no3'] - dict_m_mobilised['no3']
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['no3'] = 0.0
    else:
        dict_states_wq['soil']['no3'] = m_soil_new / (lvl_total_end / 1e3 * area)

    # ammonia
    c3_nh4 = cst_c7n * (1.047 ** (c_in_temp - 20.0))
    pu_nh4 = c3_nh4 * s1 * s2  # plant uptake
    if c_in_temp < 0.0:
        im = 0.0  # no immobilisation
        mi = 0.0  # no mineralisation
    else:
        im = cst_c6n * (1.047 ** (c_in_temp - 20.0)) * s1  # immobilisation
        mi = cst_c5n * (1.047 ** (c_in_temp - 20.0)) * s1 * area / 1e4  # mineralisation
    processes_attenuation = 1.0 - pu_nh4 - im
    external_attenuation = dict_att_factors['soil']['nh4']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['nh4'] * (lvl_total_start / 1e3 * area)
    m_soil_new = m_soil * attenuation + dict_mass_applied['nh4'] - (mi + ni) * time_factor - dict_m_mobilised['nh4']
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['nh4'] = 0.0
    else:
        dict_states_wq['soil']['nh4'] = m_soil_new / (lvl_total_end / 1e3 * area)

    # readily available inorganic phosphorus
    c3_p_ino_ra = cst_c6p * (1.047 ** (c_in_temp - 20.0))
    pu_p_ino_ra = c3_p_ino_ra * s1 * s2  # plant uptake
    pmi = cst_c3p * (1.047 ** (c_in_temp - 20.0)) * s1 * dict_states_wq['soil']['p_org_ra'] * \
        (lvl_total_start / 1e3 * area)  # mineralisation
    pim = cst_c2p * (1.047 ** (c_in_temp - 20.0)) * s1 * dict_states_wq['soil']['p_ino_ra'] * \
        (lvl_total_start / 1e3 * area)  # immobilisation
    processes_attenuation = 1.0 - pu_p_ino_ra
    external_attenuation = dict_att_factors['soil']['dph']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    conversion_p_ino_fb_into_ra = (cst_c8p * dict_states_wq['soil']['p_ino_fb'])
    conversion_p_ino_ra_into_fb = (cst_c7p * dict_states_wq['soil']['p_ino_ra'] * (lvl_total_start / 1e3 * area))
    m_soil = dict_states_wq['soil']['p_ino_ra'] * (lvl_total_start / 1e3 * area)
    m_soil_new = m_soil * attenuation + dict_mass_applied['p_ino'] - 0.5 * dict_m_mobilised['dph'] + \
        (pmi - pim + conversion_p_ino_fb_into_ra - conversion_p_ino_ra_into_fb) * time_factor
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['p_ino_ra'] = 0.0
    else:
        dict_states_wq['soil']['p_ino_ra'] = m_soil_new / (lvl_total_end / 1e3 * area)

    # firmly bound inorganic phosphorus
    processes_attenuation = 1.0  # no processes consume firmly bound P
    external_attenuation = dict_att_factors['soil']['pph']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['p_ino_fb']
    m_soil_new = m_soil * attenuation - 0.5 * dict_m_mobilised['pph'] + \
        (conversion_p_ino_ra_into_fb - conversion_p_ino_fb_into_ra) * time_factor
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['p_ino_fb'] = 0.0
    else:
        dict_states_wq['soil']['p_ino_fb'] = m_soil_new

    # readily available organic phosphorus
    c3_p_org_ra = cst_c1p * (1.047 ** (c_in_temp - 20.0))
    pu_p_org_ra = c3_p_org_ra * s1 * s2  # plant uptake
    processes_attenuation = 1.0 - pu_p_org_ra
    external_attenuation = dict_att_factors['soil']['dph']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    conversion_p_org_fb_into_ra = (cst_c5p * dict_states_wq['soil']['p_org_fb'])
    conversion_p_org_ra_into_fb = (cst_c4p * dict_states_wq['soil']['p_org_ra'] * (lvl_total_start / 1e3 * area))
    m_soil = dict_states_wq['soil']['p_org_ra'] * (lvl_total_start / 1e3 * area)
    m_soil_new = m_soil * attenuation + dict_mass_applied['p_org'] - 0.5 * dict_m_mobilised['dph'] + \
        (pim - pmi + conversion_p_org_fb_into_ra - conversion_p_org_ra_into_fb) * time_factor
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['p_org_ra'] = 0.0
    else:
        dict_states_wq['soil']['p_org_ra'] = m_soil_new / (lvl_total_end / 1e3 * area)

    # firmly bound organic phosphorus
    processes_attenuation = 1.0  # no processes consume firmly bound P
    external_attenuation = dict_att_factors['soil']['pph']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['p_org_fb']
    m_soil_new = m_soil * attenuation - 0.5 * dict_m_mobilised['pph'] + \
        (conversion_p_ino_ra_into_fb - conversion_p_ino_fb_into_ra) * time_factor
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area) < volume_tolerance):
        dict_states_wq['soil']['p_org_fb'] = 0.0
    else:
        dict_states_wq['soil']['p_org_fb'] = m_soil_new

    # sediment: no calculation, unlimited availability assumed

    # 2.3. Save inputs, states, and outputs

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_temp", c_in_temp)

    dict_data_frame[waterbody].set_value(datetime_time_step, "c_in_rain", c_in_rain)

    for contaminant in stores_contaminants:
        m_outflow = 0.0
        for store in stores:
            dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_c_{}_{}".format(contaminant, store),
                                                 dict_states_wq[store][contaminant])
            dict_data_frame[waterbody].set_value(datetime_time_step, "c_out_c_{}_{}".format(contaminant, store),
                                                 dict_c_outflow[store][contaminant])
            m_outflow += dict_c_outflow[store][contaminant] * \
                dict_data_frame[waterbody].loc[datetime_time_step, "c_out_q_h2o_{}".format(store)]
        c_outflow = m_outflow / dict_data_frame[waterbody].loc[datetime_time_step, "c_out_q_h2o"]
        dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_c_{}".format(contaminant), c_outflow)

    for contaminant in soil_contaminants:
        dict_data_frame[waterbody].set_value(datetime_time_step, "c_s_c_{}_soil".format(contaminant),
                                             dict_states_wq['soil'][contaminant])
