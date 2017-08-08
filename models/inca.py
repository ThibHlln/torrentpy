from math import exp, log, sin, pi
from datetime import timedelta
from calendar import isleap


def run_on_land(waterbody, dict_data_frame,
                dict_desc, dict_param, dict_const, dict_meteo, dict_loads,
                datetime_time_step, time_gap,
                logger,
                my_dict_hydro):
    """
    Catchment model * c_ *
    _ Water Quality
    ___ Inputs * in_ *
    _____ c_in_temp             soil temperature [degree celsius]
    _____ c_in_m_no3            nitrate loading on land [kg/time step]
    _____ c_in_m_nh4            ammonia loading on land [kg/time step]
    _____ c_in_m_p_ino          inorganic phosphorus loading on land [kg/time step]
    _____ c_in_m_p_org          organic phosphorus loading on land [kg/time step]
    ___ States * s_ *
    _____ c_s_c_no3_ove         concentration of nitrate in overland store [kg/m3]
    _____ c_s_c_no3_dra         concentration of nitrate in drain store [kg/m3]
    _____ c_s_c_no3_int         concentration of nitrate in inter store [kg/m3]
    _____ c_s_c_no3_sgw         concentration of nitrate in shallow groundwater store [kg/m3]
    _____ c_s_c_no3_dgw         concentration of nitrate in deep groundwater store [kg/m3]
    _____ c_s_c_nh4_ove         concentration of ammonia in overland store [kg/m3]
    _____ c_s_c_nh4_dra         concentration of ammonia in drain store [kg/m3]
    _____ c_s_c_nh4_int         concentration of ammonia in inter store [kg/m3]
    _____ c_s_c_nh4_sgw         concentration of ammonia in shallow groundwater store [kg/m3]
    _____ c_s_c_nh4_dgw         concentration of ammonia in deep groundwater store [kg/m3]
    _____ c_s_c_dph_ove         concentration of dissolved phosphorus in overland store [kg/m3]
    _____ c_s_c_dph_dra         concentration of dissolved phosphorus in drain store [kg/m3]
    _____ c_s_c_dph_int         concentration of dissolved phosphorus in inter store [kg/m3]
    _____ c_s_c_dph_sgw         concentration of dissolved phosphorus in shallow groundwater store [kg/m3]
    _____ c_s_c_dph_dgw         concentration of dissolved phosphorus in deep groundwater store [kg/m3]
    _____ c_s_c_pph_ove         concentration of particulate phosphorus in overland store [kg/m3]
    _____ c_s_c_pph_dra         concentration of particulate phosphorus in drain store [kg/m3]
    _____ c_s_c_pph_int         concentration of particulate phosphorus in inter store [kg/m3]
    _____ c_s_c_pph_sgw         concentration of particulate phosphorus in shallow groundwater store [kg/m3]
    _____ c_s_c_pph_dgw         concentration of particulate phosphorus in deep groundwater store [kg/m3]
    _____ c_s_c_sed_ove         concentration of sediment in overland store [kg/m3]
    _____ c_s_c_sed_dra         concentration of sediment in drain store [kg/m3]
    _____ c_s_c_sed_int         concentration of sediment in inter store [kg/m3]
    _____ c_s_c_sed_sgw         concentration of sediment in shallow groundwater store [kg/m3]
    _____ c_s_c_sed_dgw         concentration of sediment in deep groundwater store [kg/m3]
    _____ c_s_c_no3_soil        concentration of nitrate in soil column [kg/m3]
    _____ c_s_c_nh4_soil        concentration of ammonia in soil column [kg/m3]
    _____ c_s_c_p_org_ra_soil   concentration of readily available organic phosphorus in soil column [kg/m3]
    _____ c_s_c_p_ino_ra_soil   concentration of readily available inorganic phosphorus in soil column [kg/m3]
    _____ c_s_m_p_org_fb_soil   mass of firmly bound organic phosphorus in soil column [kg]
    _____ c_s_m_p_ino_fb_soil   mass of firmly bound inorganic phosphorus in soil column [kg]
    _____ c_s_m_sed_soil        mass of sediment in soil column [kg]
    ___ Parameters * p_ *
    _____ c_p_att_no3_ove       daily attenuation factor for nitrate in overland flow [-]
    _____ c_p_att_nh4_ove       daily attenuation factor for ammonia in overland flow [-]
    _____ c_p_att_dph_ove       daily attenuation factor for dissolved phosphorus in overland flow [-]
    _____ c_p_att_pph_ove       daily attenuation factor for particulate phosphorus in overland flow [-]
    _____ c_p_att_sed_ove       daily attenuation factor for sediment in overland flow [-]
    _____ c_p_att_no3_dra       daily attenuation factor for nitrate in drain flow [-]
    _____ c_p_att_nh4_dra       daily attenuation factor for ammonia in drain flow [-]
    _____ c_p_att_dph_dra       daily attenuation factor for dissolved phosphorus in drain flow [-]
    _____ c_p_att_pph_dra       daily attenuation factor for particulate phosphorus in drain flow [-]
    _____ c_p_att_sed_dra       daily attenuation factor for sediment in drain flow [-]
    _____ c_p_att_no3_int       daily attenuation factor for nitrate in inter flow [-]
    _____ c_p_att_nh4_int       daily attenuation factor for ammonia in inter flow [-]
    _____ c_p_att_dph_int       daily attenuation factor for dissolved phosphorus in inter flow [-]
    _____ c_p_att_pph_int       daily attenuation factor for particulate phosphorus in inter flow [-]
    _____ c_p_att_sed_int       daily attenuation factor for sediment in inter flow [-]
    _____ c_p_att_no3_sgw       daily attenuation factor for nitrate in shallow groundwater flow [-]
    _____ c_p_att_nh4_sgw       daily attenuation factor for ammonia in shallow groundwater flow [-]
    _____ c_p_att_dph_sgw       daily attenuation factor for dissolved phosphorus in shallow groundwater flow [-]
    _____ c_p_att_pph_sgw       daily attenuation factor for particulate phosphorus in shallow groundwater flow [-]
    _____ c_p_att_sed_sgw       daily attenuation factor for sediment in shallow groundwater flow [-]
    _____ c_p_att_no3_dgw       daily attenuation factor for nitrate in deep groundwater flow [-]
    _____ c_p_att_nh4_dgw       daily attenuation factor for ammonia in deep groundwater flow [-]
    _____ c_p_att_dph_dgw       daily attenuation factor for dissolved phosphorus in deep groundwater flow [-]
    _____ c_p_att_pph_dgw       daily attenuation factor for particulate phosphorus in deep groundwater flow [-]
    _____ c_p_att_sed_dgw       daily attenuation factor for sediment in deep groundwater flow [-]
    _____ c_p_att_no3_soil      daily attenuation factor for nitrate in soil column [-]
    _____ c_p_att_nh4_soil      daily attenuation factor for ammonia in soil column [-]
    _____ c_p_att_p_org_ra_soil daily attenuation factor for readily available organic phosphorus in soil column [-]
    _____ c_p_att_p_ino_ra_soil daily attenuation factor for readily available inorganic phosphorus in soil column [-]
    _____ c_p_att_p_org_fb_soil daily attenuation factor for firmly bound organic phosphorus in soil column [-]
    _____ c_p_att_p_ino_fb_soil daily attenuation factor for firmly bound inorganic phosphorus in soil column [-]
    _____ c_p_att_sed_soil      daily attenuation factor for sediment in soil column [-]
    ___ Constants * cst_ *
    _____ c_cst_mob_no3_ove     mobilisation factor for nitrate to overland flow [-]
    _____ c_cst_mob_no3_dra     mobilisation factor for nitrate to drain flow [-]
    _____ c_cst_mob_no3_int     mobilisation factor for nitrate to inter flow [-]
    _____ c_cst_mob_no3_sgw     mobilisation factor for nitrate to shallow groundwater flow [-]
    _____ c_cst_mob_no3_dgw     mobilisation factor for nitrate to deep groundwater flow [-]
    _____ c_cst_mob_nh4_ove     mobilisation factor for ammonia to overland flow [-]
    _____ c_cst_mob_nh4_dra     mobilisation factor for ammonia to drain flow [-]
    _____ c_cst_mob_nh4_int     mobilisation factor for ammonia to inter flow [-]
    _____ c_cst_mob_nh4_sgw     mobilisation factor for ammonia to shallow groundwater flow [-]
    _____ c_cst_mob_nh4_dgw     mobilisation factor for ammonia to deep groundwater flow [-]
    _____ c_cst_mob_dph_ove     mobilisation factor for dissolved phosphorus to overland flow [-]
    _____ c_cst_mob_dph_dra     mobilisation factor for dissolved phosphorus to drain flow [-]
    _____ c_cst_mob_dph_int     mobilisation factor for dissolved phosphorus to inter flow [-]
    _____ c_cst_mob_dph_sgw     mobilisation factor for dissolved phosphorus to shallow groundwater flow [-]
    _____ c_cst_mob_dph_dgw     mobilisation factor for dissolved phosphorus to deep groundwater flow [-]
    _____ c_cst_mob_pph_ove     mobilisation factor for particulate phosphorus to overland flow [-]
    _____ c_cst_mob_pph_dra     mobilisation factor for particulate phosphorus to drain flow [-]
    _____ c_cst_mob_pph_int     mobilisation factor for particulate phosphorus to inter flow [-]
    _____ c_cst_mob_pph_sgw     mobilisation factor for particulate phosphorus to shallow groundwater flow [-]
    _____ c_cst_mob_pph_dgw     mobilisation factor for particulate phosphorus to deep groundwater flow [-]
    _____ c_cst_mob_sed_ove     mobilisation factor for sediment to overland flow [-]
    _____ c_cst_mob_sed_dra     mobilisation factor for sediment to drain flow [-]
    _____ c_cst_mob_sed_int     mobilisation factor for sediment to inter flow [-]
    _____ c_cst_mob_sed_sgw     mobilisation factor for sediment to shallow groundwater flow [-]
    _____ c_cst_mob_sed_dgw     mobilisation factor for sediment to deep groundwater flow [-]
    _____ c_cst_sed_daily_thr   daily flow threshold for sediment mobilisation [mm/day]
    _____ c_cst_sed_k           factor combining the effects of erodibility, topography, cover and support practice [?]
    _____ c_cst_sed_p           required power of flow for sediment MUSLE equation [-]
    _____ c_cst_soil_test_p     soil test P [kg/kg]
    _____ c_cst_soil_c1n        rate coefficient for denitrification [m/day]
    _____ c_cst_soil_c3n        rate coefficient for NO3 plant uptake [m/day]
    _____ c_cst_soil_c4n        rate coefficient for nitrification [m/day]
    _____ c_cst_soil_c5n        rate coefficient for N mineralisation [m/day]
    _____ c_cst_soil_c6n        rate coefficient for N immobilisation [m/day]
    _____ c_cst_soil_c7n        rate coefficient for NH4 plant uptake [m/day]
    _____ c_cst_soil_c1p        rate coefficient for organic P plant uptake [m/day]
    _____ c_cst_soil_c2p        rate coefficient for P immobilisation [m/day]
    _____ c_cst_soil_c3p        rate coefficient for P mineralisation [m/day]
    _____ c_cst_soil_c4p        conversion rate of readily available organic P into firmly bound organic P [-]
    _____ c_cst_soil_c5p        conversion rate of firmly bound organic P into readily available organic P [-]
    _____ c_cst_soil_c6p        rate coefficient for inorganic P plant uptake [m/day]
    _____ c_cst_soil_c7p        conversion rate of readily available inorganic P into firmly bound inorganic P [-]
    _____ c_cst_soil_c8p        conversion rate of firmly bound inorganic P into readily available inorganic P [-]
    _____ c_cst_day_grow        index of the starting day for the growing season in the year [-]
    ___ Outputs * out_ *
    _____ c_out_c_no3_ove       nitrate concentration in overland flow [kg/m3]
    _____ c_out_c_nh4_ove       ammonia concentration in overland flow [kg/m3]
    _____ c_out_c_dph_ove       dissolved phosphorus in overland flow [kg/m3]
    _____ c_out_c_pph_ove       particulate phosphorus in overland flow [kg/m3]
    _____ c_out_c_sed_ove       sediment concentration in overland flow [kg/m3]
    _____ c_out_c_no3_dra       nitrate concentration in drain flow [kg/m3]
    _____ c_out_c_nh4_dra       ammonia concentration in drain flow [kg/m3]
    _____ c_out_c_dph_dra       dissolved phosphorus in drain flow [kg/m3]
    _____ c_out_c_pph_dra       particulate phosphorus in drain flow [kg/m3]
    _____ c_out_c_sed_dra       sediment concentration in drain flow [kg/m3]
    _____ c_out_c_no3_int       nitrate concentration in inter flow [kg/m3]
    _____ c_out_c_nh4_int       ammonia concentration in inter flow [kg/m3]
    _____ c_out_c_dph_int       dissolved phosphorus in inter flow [kg/m3]
    _____ c_out_c_pph_int       particulate phosphorus in inter flow [kg/m3]
    _____ c_out_c_sed_int       sediment concentration in inter flow [kg/m3]
    _____ c_out_c_no3_sgw       nitrate concentration in shallow groundwater flow [kg/m3]
    _____ c_out_c_nh4_sgw       ammonia concentration in shallow groundwater flow [kg/m3]
    _____ c_out_c_dph_sgw       dissolved phosphorus in shallow groundwater flow [kg/m3]
    _____ c_out_c_pph_sgw       particulate phosphorus in shallow groundwater flow [kg/m3]
    _____ c_out_c_sed_sgw       sediment concentration in shallow groundwater flow [kg/m3]
    _____ c_out_c_no3_dgw       nitrate concentration in deep groundwater flow [kg/m3]
    _____ c_out_c_nh4_dgw       ammonia concentration in deep groundwater flow [kg/m3]
    _____ c_out_c_dph_dgw       dissolved phosphorus in deep groundwater flow [kg/m3]
    _____ c_out_c_pph_dgw       particulate phosphorus in deep groundwater flow [kg/m3]
    _____ c_out_c_sed_dgw       sediment concentration in deep groundwater flow [kg/m3]
    _____ c_out_c_no3           nitrate concentration in total outflow [kg/m3]
    _____ c_out_c_nh4           ammonia concentration in total outflow [kg/m3]
    _____ c_out_c_dph           dissolved phosphorus in total outflow [kg/m3]
    _____ c_out_c_pph           particulate phosphorus in total outflow [kg/m3]
    _____ c_out_c_sed           sediment concentration in total outflow [kg/m3]
    """

    # # 2. Water quality calculations
    # # 2.0. Define internal constants
    area_m2 = dict_desc[waterbody]['area']  # catchment area [m2]
    time_step_sec = time_gap * 60.0  # [seconds]
    time_factor = time_step_sec / 86400.0
    if time_factor < 0.005:
        time_factor = 0.005
    flow_tolerance = dict_const['c_cst_flow_tolerance']  # [m3/s]
    volume_tolerance = dict_const['c_cst_vol_tolerance']  # [m3]
    flow_threshold_for_erosion = {
        'ove': dict_const['c_cst_flow_thr_mm_for_ero_ove'],  # [mm]
        'dra': dict_const['c_cst_flow_thr_mm_for_ero_dra']  # [mm]
    }
    stores = ['ove', 'dra', 'int', 'sgw', 'dgw']
    stores_contaminants = ['no3', 'nh4', 'dph', 'pph', 'sed']
    soil_contaminants = {'no3': 'c', 'nh4': 'c',
                         'p_ino_ra': 'c', 'p_ino_fb': 'm', 'p_org_ra': 'c', 'p_org_fb': 'm',
                         'sed': 'm'}

    # # 2.1. Define variables originating from hydrological model
    lvl_total_start = my_dict_hydro['dict_lvl_soil']['start']
    lvl_total_end = my_dict_hydro['dict_lvl_soil']['end']

    dict_states_old_hd = my_dict_hydro['dict_states_old_hd']
    dict_flows_mm_hd = my_dict_hydro['dict_flows_mm_hd']
    dict_states_hd = my_dict_hydro['dict_states_hd']
    dict_outputs_hd = my_dict_hydro['dict_outputs_hd']

    # # 2.2. Collect inputs, states, parameters, and constants
    c_in_temp = dict_meteo[waterbody][datetime_time_step]["airt"]
    mass_n = \
        dict_loads[waterbody][datetime_time_step]["org_n_grassland"] * \
        dict_desc[waterbody]["grassland_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["ino_n_grassland"] * \
        dict_desc[waterbody]["grassland_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["org_n_arable"] * \
        dict_desc[waterbody]["arable_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["ino_n_arable"] * \
        dict_desc[waterbody]["arable_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["n_urban"] * \
        dict_desc[waterbody]["urban_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["n_atm_deposition"] * \
        dict_desc[waterbody]["woodland_ratio"] * area_m2 * 1e-4 + \
        dict_loads[waterbody][datetime_time_step]["n_septic_tanks"]
    c_in_m_no3 = mass_n * 0.70  # assumed 70% as nitrate
    c_in_m_nh4 = mass_n * 0.30  # assumed 30% as ammonia
    c_in_m_p_ino = (dict_loads[waterbody][datetime_time_step]["ino_p_grassland"] *
                    dict_desc[waterbody]["grassland_ratio"] * area_m2 * 1e-4 +
                    dict_loads[waterbody][datetime_time_step]["ino_p_arable"] *
                    dict_desc[waterbody]["arable_ratio"] * area_m2 * 1e-4 +
                    dict_loads[waterbody][datetime_time_step]["p_urban"] *
                    dict_desc[waterbody]["urban_ratio"] * area_m2 * 1e-4 +
                    dict_loads[waterbody][datetime_time_step]["p_atm_deposition"] *
                    dict_desc[waterbody]["woodland_ratio"] * area_m2 * 1e-4)
    c_in_m_p_org = (dict_loads[waterbody][datetime_time_step]["org_p_grassland"] *
                    dict_desc[waterbody]["grassland_ratio"] * area_m2 * 1e-4 +
                    dict_loads[waterbody][datetime_time_step]["org_p_arable"] *
                    dict_desc[waterbody]["arable_ratio"] * area_m2 * 1e-4 +
                    dict_loads[waterbody][datetime_time_step]["p_septic_tanks"])
    dict_mass_applied = dict()
    dict_mass_applied['no3'] = c_in_m_no3
    dict_mass_applied['nh4'] = c_in_m_nh4
    dict_mass_applied['p_ino'] = c_in_m_p_ino
    dict_mass_applied['p_org'] = c_in_m_p_org

    c_p_z = dict_param["c_p_z"]

    dict_states_wq = dict()  # for states of the stores + soil
    dict_c_outflow = dict()  # for outflow concentrations from stores
    dict_att_factors = dict()  # for attenuation factors in stores
    dict_mob_factors = dict()  # for mobilisation factors in stores
    for store in stores:
        my_dict_1 = dict()
        my_dict_2 = dict()
        my_dict_3 = dict()
        my_dict_4 = dict()
        for contaminant in stores_contaminants:
            my_dict_1[contaminant] = \
                dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)][
                    ''.join(['c_s_c_', contaminant, '_', store])]
            my_dict_2[contaminant] = 0.0  # initialisation only
            my_dict_3[contaminant] = \
                dict_param[''.join(['c_p_att_', contaminant, '_', store])] ** time_factor
            my_dict_4[contaminant] = dict_const[''.join(['c_cst_mob_', contaminant, '_', store])]
        dict_states_wq[store] = my_dict_1
        dict_c_outflow[store] = my_dict_2
        dict_att_factors[store] = my_dict_3
        dict_mob_factors[store] = my_dict_4
    my_dict_5 = dict()
    my_dict_6 = dict()
    for contaminant in soil_contaminants:
        my_dict_5[contaminant] = \
            dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)][
                ''.join(['c_s_', soil_contaminants[contaminant], '_', contaminant, '_soil'])]
        my_dict_6[contaminant] = \
            dict_param[''.join(['c_p_att_', contaminant, '_soil'])] ** time_factor
    dict_states_wq['soil'] = my_dict_5
    # create 'artificial' states (in dictionary only) to sum organic and inorganic DPH and PPH
    dict_states_wq['soil']['dph'] = dict_states_wq['soil']['p_org_ra'] + dict_states_wq['soil']['p_ino_ra']  # [kg/m3]
    dict_states_wq['soil']['pph'] = dict_states_wq['soil']['p_org_fb'] + dict_states_wq['soil']['p_ino_fb']  # [kg]
    dict_att_factors['soil'] = my_dict_6

    daily_sediment_threshold = dict_const['c_cst_sed_daily_thr']  # [mm/day]
    sediment_threshold = daily_sediment_threshold * time_factor
    sediment_k = dict_const['c_cst_sed_k']
    sediment_p = dict_const['c_cst_sed_p']
    soil_test_p = dict_const['c_cst_soil_test_p']  # [kg/kg]
    day_growing_season = dict_const['c_cst_day_grow']
    day_of_year = float(datetime_time_step.timetuple().tm_yday)
    if isleap(datetime_time_step.timetuple().tm_year):
        days_in_year = 366.0
    else:
        days_in_year = 365.0

    cst_c1n = dict_const["c_cst_soil_c1n"]  # rate coefficient (m/day) for denitrification
    cst_c3n = dict_const["c_cst_soil_c3n"]  # rate coefficient (m/day) for NO3 plant uptake
    cst_c4n = dict_const["c_cst_soil_c4n"]  # rate coefficient (m/day) for nitrification
    cst_c5n = dict_const["c_cst_soil_c5n"]  # rate coefficient (m/day) for N mineralisation
    cst_c6n = dict_const["c_cst_soil_c6n"]  # rate coefficient (m/day) for N immobilisation
    cst_c7n = dict_const["c_cst_soil_c7n"]  # rate coefficient (m/day) for NH4 plant uptake
    cst_c1p = dict_const["c_cst_soil_c1p"]  # rate coefficient (m/day) for organic P plant uptake
    cst_c2p = dict_const["c_cst_soil_c2p"]  # rate coefficient (m/day) for P immobilisation
    cst_c3p = dict_const["c_cst_soil_c3p"]  # rate coefficient (m/day) for P mineralisation
    cst_c4p = dict_const["c_cst_soil_c4p"]  # conversion rate of r. avail. organic P into f. bound organic P
    cst_c5p = dict_const["c_cst_soil_c5p"]  # conversion rate of f. bound organic P into r. avail. organic P
    cst_c6p = dict_const["c_cst_soil_c6p"]  # rate coefficient (m/day) for inorganic P plant uptake
    cst_c7p = dict_const["c_cst_soil_c7p"]  # conversion rate of r. avail. ino. P into f. bound ino. P
    cst_c8p = dict_const["c_cst_soil_c8p"]  # conversion rate of f. bound ino. P into r. available ino. P

    # # 2.3. Water quality calculations
    # # 2.3.1. Overland flow contamination & drain flow contamination
    dict_m_mobilised = {'no3': 0.0, 'nh4': 0.0, 'dph': 0.0, 'pph': 0.0, 'sed': 0.0}
    for store in ['ove', 'dra']:
        # dissolved contaminants: nitrate, ammonia, dissolved (= readily available) phosphorus
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
            m_mobilised = (dict_flows_mm_hd[store] / 1e3 * area_m2) * dict_states_wq['soil'][contaminant] * mobilisation
            m_store = m_store_att + m_mobilised - dict_outputs_hd[store] * time_step_sec * c_store
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                      ' - ', contaminant.upper(), ' Quantity in ', store.upper(),
                                      ' Store has gone negative, quantity reset to zero']))
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
        if (dict_flows_mm_hd[store] < sediment_threshold) or \
                (dict_flows_mm_hd[store] < flow_threshold_for_erosion[store]):
            m_sediment_per_area = 0.0
            m_sediment = 0.0
            dict_c_outflow[store][contaminant] = 0.0
        else:
            m_sediment_per_area = (sediment_k * dict_flows_mm_hd[store] ** sediment_p) * time_factor
            m_sediment = m_sediment_per_area * area_m2
            dict_c_outflow[store][contaminant] = m_sediment / (dict_flows_mm_hd[store] / 1e3 * area_m2)
        if store == 'ove':  # no mass balance, all sediment assumed gone
            dict_states_wq[store][contaminant] = 0.0
        elif store == 'dra':  # mass balance
            m_store = \
                m_store_att + m_sediment - dict_outputs_hd[store] * time_step_sec * dict_c_outflow[store][contaminant]
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                      ' - ', contaminant.upper(), ' Quantity in ', store.upper(),
                                      ' Store has gone negative, quantity reset to zero']))
                dict_states_wq[store][contaminant] = 0.0
            else:
                dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
        dict_m_mobilised[contaminant] += m_sediment
        dict_states_wq[store][contaminant] = 0.0

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
        if (dict_flows_mm_hd[store] < sediment_threshold) or \
                (dict_flows_mm_hd[store] < flow_threshold_for_erosion[store]):
            m_particulate_p = 0.0
            dict_c_outflow[store][contaminant] = 0.0
        else:
            soil_loss = m_sediment_per_area * 1e4 * 3.1536e7 / time_step_sec  # [kg/ha/yr]
            p_enrichment_ratio = exp(2.48 - 0.27 * log(soil_loss))  # [-]  # soil loss cannot be equal to 0
            if p_enrichment_ratio < 0.1:
                p_enrichment_ratio = 0.1
            elif p_enrichment_ratio > 6.0:
                p_enrichment_ratio = 6.0
            m_particulate_p = soil_test_p * m_sediment * p_enrichment_ratio  # [kg]
            # try to find the PPH 'demand' from the soil firmly bound P
            if m_particulate_p <= dict_states_wq['soil']['p_ino_fb']:  # P removed from inorganic P firmly in soil
                dict_states_wq['soil']['p_ino_fb'] -= m_particulate_p
                m_particulate_p_missing = 0.0  # [kg]
            else:  # P is also removed from organic firmly bound after inorganic firmly bound
                m_particulate_p_missing = m_particulate_p - dict_states_wq['soil']['p_ino_fb']
                dict_states_wq['soil']['p_ino_fb'] = 0.0
                if m_particulate_p_missing <= dict_states_wq['soil']['p_org_fb']:
                    dict_states_wq['soil']['p_org_fb'] -= m_particulate_p_missing
                    m_particulate_p_missing = 0.0  # [kg]
                else:
                    m_particulate_p_missing -= dict_states_wq['soil']['p_org_fb']
                    dict_states_wq['soil']['p_org_fb'] = 0.0
            dict_states_wq['soil'][contaminant] = dict_states_wq['soil']['p_org_fb'] + \
                dict_states_wq['soil']['p_ino_fb']
            m_particulate_p -= m_particulate_p_missing  # remove part of the demand that could not be satisfied by soil
            dict_c_outflow[store][contaminant] = m_particulate_p / (dict_flows_mm_hd[store] / 1e3 * area_m2)
        m_store = \
            m_store_att + m_particulate_p - dict_outputs_hd[store] * time_step_sec * dict_c_outflow[store][contaminant]
        if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
            logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"), ' - ',
                                  contaminant.upper(), ' Quantity in ', store.upper(),
                                  ' Store has gone negative, quantity reset to zero']))
            dict_states_wq[store][contaminant] = 0.0
        else:
            dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
        dict_m_mobilised[contaminant] += m_particulate_p

    # # 2.3.2. Interflow contamination, Shallow groundwater flow contamination, & Deep groundwater flow contamination
    for store in ['int', 'sgw', 'dgw']:
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
            m_mobilised = (dict_flows_mm_hd[store] / 1e3 * area_m2) * dict_states_wq['soil'][contaminant] * mobilisation
            m_store = m_store_att + m_mobilised - dict_outputs_hd[store] * time_step_sec * c_store
            if (m_store < 0.0) or (dict_states_hd[store] < volume_tolerance):
                logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                      ' - ', contaminant.upper(), ' Quantity in ', store.upper(),
                                      ' Store has gone negative, quantity reset to zero']))
                dict_states_wq[store][contaminant] = 0.0
            else:
                dict_states_wq[store][contaminant] = m_store / dict_states_hd[store]
            dict_m_mobilised[contaminant] += m_mobilised

    # # 2.3.3. Soil store contamination
    # nitrate
    s1 = lvl_total_end / (c_p_z * 0.275)  # soil moisture factor
    # assuming field capacity = 110 mm/m depth & soil porosity = 0.4 => 0.11 * 0.4 = 0.275
    # (SMD max assumed by Met Eireann)
    if s1 > 1.0:
        s1 = 1.0
    elif s1 < 0.0:
        s1 = 0.0
    s2 = 0.66 + 0.34 * sin(2.0 * pi * (day_of_year - day_growing_season) / days_in_year)  # seasonal plant growth
    c3_no3 = cst_c3n * (1.047 ** (c_in_temp - 20.0))
    pu_no3 = c3_no3 * s1 * s2  # plant uptake [-/day]
    c1 = cst_c1n * (1.047 ** (c_in_temp - 20.0))
    c4 = cst_c4n * (1.047 ** (c_in_temp - 20.0))
    if c_in_temp < 0.0:
        dn = 0.0  # no denitrification
        ni = 0.0  # no nitrification
        fx = 0.0  # no fixation
    else:
        dn = c1 * s1  # denitrification [-/day]
        ni = c4 * s1 * dict_states_wq['soil']['nh4'] * (lvl_total_start / 1e3 * area_m2)  # nitrification [kg]
        fx = 0.0  # fixation
    processes_attenuation = 1.0 - pu_no3 - dn + fx  # attenuation due to processes in soil system
    external_attenuation = dict_att_factors['soil']['no3']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['no3'] * (lvl_total_start / 1e3 * area_m2)  # mass in soil at beginning of time step
    m_soil_new = m_soil * attenuation + ni * time_factor + dict_mass_applied['no3'] - dict_m_mobilised['no3']
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - NO3 Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['no3'] = 0.0
    else:
        dict_states_wq['soil']['no3'] = m_soil_new / (lvl_total_end / 1e3 * area_m2)

    # ammonia
    c3_nh4 = cst_c7n * (1.047 ** (c_in_temp - 20.0))
    pu_nh4 = c3_nh4 * s1 * s2  # plant uptake [-/day]
    if c_in_temp < 0.0:
        im = 0.0  # no immobilisation
        mi = 0.0  # no mineralisation
    else:
        im = cst_c6n * (1.047 ** (c_in_temp - 20.0)) * s1  # immobilisation [-/day]
        mi = cst_c5n * (1.047 ** (c_in_temp - 20.0)) * s1 * area_m2 / 1e4  # mineralisation [kg]
    processes_attenuation = 1.0 - pu_nh4 - im
    external_attenuation = dict_att_factors['soil']['nh4']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['nh4'] * (lvl_total_start / 1e3 * area_m2)
    m_soil_new = m_soil * attenuation + dict_mass_applied['nh4'] - (mi + ni) * time_factor - dict_m_mobilised['nh4']
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - NH4 Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['nh4'] = 0.0
    else:
        dict_states_wq['soil']['nh4'] = m_soil_new / (lvl_total_end / 1e3 * area_m2)

    # readily available inorganic phosphorus
    c3_p_ino_ra = cst_c6p * (1.047 ** (c_in_temp - 20.0))
    pu_p_ino_ra = c3_p_ino_ra * s1 * s2  # plant uptake [-/day]
    pmi = cst_c3p * (1.047 ** (c_in_temp - 20.0)) * s1 * dict_states_wq['soil']['p_org_ra'] * \
        (lvl_total_start / 1e3 * area_m2)  # mineralisation [kg]
    pim = cst_c2p * (1.047 ** (c_in_temp - 20.0)) * s1 * dict_states_wq['soil']['p_ino_ra'] * \
        (lvl_total_start / 1e3 * area_m2)  # immobilisation [kg]
    processes_attenuation = 1.0 - pu_p_ino_ra
    external_attenuation = dict_att_factors['soil']['p_ino_ra']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    conversion_p_ino_fb_into_ra = (cst_c8p * dict_states_wq['soil']['p_ino_fb'])  # state for FB was already in kg
    conversion_p_ino_ra_into_fb = (cst_c7p * dict_states_wq['soil']['p_ino_ra'] * (lvl_total_start / 1e3 * area_m2))
    # state for RA was in kg/m3, needed conversion in kg
    m_soil = dict_states_wq['soil']['p_ino_ra'] * (lvl_total_start / 1e3 * area_m2)
    m_soil_new = m_soil * attenuation + dict_mass_applied['p_ino'] - 0.5 * dict_m_mobilised['dph'] + \
        (pmi - pim + conversion_p_ino_fb_into_ra - conversion_p_ino_ra_into_fb) * time_factor
    # assumed that all p_ino applied is in the readily available form
    # assumed that half of the dph mobilised from soil is inorganic
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - P_INO_RA Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['p_ino_ra'] = 0.0
    else:
        dict_states_wq['soil']['p_ino_ra'] = m_soil_new / (lvl_total_end / 1e3 * area_m2)

    # firmly bound inorganic phosphorus
    processes_attenuation = 1.0  # no processes consume firmly bound P
    external_attenuation = dict_att_factors['soil']['p_ino_fb']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['p_ino_fb']  # state for FB is already in kg
    m_soil_new = m_soil * attenuation - 0.5 * dict_m_mobilised['pph'] + \
        (conversion_p_ino_ra_into_fb - conversion_p_ino_fb_into_ra) * time_factor
    # assumed that half of the pph mobilised from soil is inorganic
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - P_INO_FB Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['p_ino_fb'] = 0.0
    else:
        dict_states_wq['soil']['p_ino_fb'] = m_soil_new  # store state in kg

    # readily available organic phosphorus
    c3_p_org_ra = cst_c1p * (1.047 ** (c_in_temp - 20.0))
    pu_p_org_ra = c3_p_org_ra * s1 * s2  # plant uptake
    processes_attenuation = 1.0 - pu_p_org_ra
    external_attenuation = dict_att_factors['soil']['p_org_ra']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    conversion_p_org_fb_into_ra = (cst_c5p * dict_states_wq['soil']['p_org_fb'])  # state for FB was already in kg
    conversion_p_org_ra_into_fb = (cst_c4p * dict_states_wq['soil']['p_org_ra'] * (lvl_total_start / 1e3 * area_m2))
    # state for RA was in kg/m3, needed conversion in kg
    m_soil = dict_states_wq['soil']['p_org_ra'] * (lvl_total_start / 1e3 * area_m2)
    m_soil_new = m_soil * attenuation + dict_mass_applied['p_org'] - 0.5 * dict_m_mobilised['dph'] + \
        (pim - pmi + conversion_p_org_fb_into_ra - conversion_p_org_ra_into_fb) * time_factor
    # assumed that all p_org applied is in the readily available form
    # assumed that half of the dph mobilised from soil is organic
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - P_ORG_RA Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['p_org_ra'] = 0.0
    else:
        dict_states_wq['soil']['p_org_ra'] = m_soil_new / (lvl_total_end / 1e3 * area_m2)

    # firmly bound organic phosphorus
    processes_attenuation = 1.0  # no processes consume firmly bound P
    external_attenuation = dict_att_factors['soil']['p_org_fb']
    attenuation = (processes_attenuation * external_attenuation) ** time_factor
    if attenuation > 1.0:
        attenuation = 1.0
    elif attenuation < 0.0:
        attenuation = 0.0
    m_soil = dict_states_wq['soil']['p_org_fb']  # state for FB is already in kg
    m_soil_new = m_soil * attenuation - 0.5 * dict_m_mobilised['pph'] + \
        (conversion_p_org_ra_into_fb - conversion_p_org_fb_into_ra) * time_factor
    # assumed that half of the pph mobilised from soil is organic
    if (m_soil_new < 0.0) or ((lvl_total_end / 1e3 * area_m2) < volume_tolerance):
        logger.debug(''.join(['INCAL # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - P_ORG_FB Quantity in SOIL Store has gone negative, quantity reset to zero.']))
        dict_states_wq['soil']['p_org_fb'] = 0.0
    else:
        dict_states_wq['soil']['p_org_fb'] = m_soil_new  # store state in kg

    # sediment: no calculation, unlimited availability assumed

    # # 2.4. Save inputs, states, and outputs
    dict_data_frame[waterbody][datetime_time_step]["c_in_temp"] = c_in_temp
    dict_data_frame[waterbody][datetime_time_step]["c_in_m_no3"] = c_in_m_no3
    dict_data_frame[waterbody][datetime_time_step]["c_in_m_nh4"] = c_in_m_nh4
    dict_data_frame[waterbody][datetime_time_step]["c_in_m_p_ino"] = c_in_m_p_ino
    dict_data_frame[waterbody][datetime_time_step]["c_in_m_p_org"] = c_in_m_p_org

    for contaminant in stores_contaminants:
        m_outflow = 0.0
        for store in stores:
            dict_data_frame[waterbody][datetime_time_step][''.join(['c_s_c_', contaminant, '_', store])] = \
                dict_states_wq[store][contaminant]
            dict_data_frame[waterbody][datetime_time_step][''.join(['c_out_c_', contaminant, '_', store])] = \
                dict_c_outflow[store][contaminant]
            if dict_data_frame[waterbody][datetime_time_step][''.join(['c_out_q_h2o_', store])] >= flow_tolerance:
                m_outflow += dict_c_outflow[store][contaminant] * \
                    dict_data_frame[waterbody][datetime_time_step][''.join(['c_out_q_h2o_', store])]
        if dict_data_frame[waterbody][datetime_time_step]["c_out_q_h2o"] > 0.0:
            c_outflow = m_outflow / dict_data_frame[waterbody][datetime_time_step]["c_out_q_h2o"]
        else:
            c_outflow = 0.0
        dict_data_frame[waterbody][datetime_time_step][''.join(['c_out_c_', contaminant])] = c_outflow
    for contaminant in soil_contaminants:
        dict_data_frame[waterbody][datetime_time_step][''.join(['c_s_', soil_contaminants[contaminant], '_',
                                                                contaminant, '_soil'])] = \
            dict_states_wq['soil'][contaminant]


def run_in_stream(obj_network, waterbody, dict_data_frame,
                  dict_param, dict_const, dict_meteo,
                  datetime_time_step, time_gap,
                  logger):
    """
    River model * r_ *
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
    _____ r_p_att_no3     daily attenuation factor for nitrate [-]
    _____ r_p_att_nh4     daily attenuation factor for ammonia [-]
    _____ r_p_att_dph     daily attenuation factor for dissolved phosphorus [-]
    _____ r_p_att_pph     daily attenuation factor for particulate phosphorus [-]
    _____ r_p_att_sed     daily attenuation factor for sediment [-]
    ___ Constants * cst_ *
    _____ r_cst_c_dn      denitrification rate constant [-]
    _____ r_cst_c_ni      nitrification rate constant [-]
    ___ Outputs * out_ *
    _____ r_out_c_no3     nitrate concentration at outlet [kg/m3]
    _____ r_out_c_nh4     ammonia concentration at outlet [kg/m3]
    _____ r_out_c_dph     dissolved phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_pph     particulate phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_sed     sediment concentration at outlet [kg/m3]
    """

    # # 2. Water quality
    # # 2.0. Define internal constants
    node_up = obj_network.connections[waterbody][1]
    time_step_sec = time_gap * 60.0  # [seconds]
    flow_tolerance = dict_const['r_cst_flow_tolerance']
    volume_tolerance = dict_const['r_cst_vol_tolerance']

    # # 2.1. Define variables originating from hydraulic model
    r_in_q_h2o = dict_data_frame[waterbody][datetime_time_step]["r_in_q_h2o"]
    r_out_q_h2o = dict_data_frame[waterbody][datetime_time_step]["r_out_q_h2o"]
    r_s_v_h2o_old = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_v_h2o"]
    r_s_v_h2o = dict_data_frame[waterbody][datetime_time_step]["r_s_v_h2o"]

    # # 2.2. Collect inputs, states, parameters and constants
    r_in_temp = dict_meteo[waterbody][datetime_time_step]["airt"]
    r_in_c_no3 = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["c_no3"]
    r_in_c_nh4 = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["c_nh4"]
    r_in_c_dph = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["c_dph"]
    r_in_c_pph = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["c_pph"]
    r_in_c_sed = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap)]["c_sed"]

    r_s_m_no3 = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_m_no3"]
    r_s_m_nh4 = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_m_nh4"]
    r_s_m_dph = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_m_dph"]
    r_s_m_pph = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_m_pph"]
    r_s_m_sed = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap)]["r_s_m_sed"]

    r_p_att_no3 = dict_param["r_p_att_no3"]
    r_p_att_nh4 = dict_param["r_p_att_nh4"]
    r_p_att_dph = dict_param["r_p_att_dph"]
    r_p_att_pph = dict_param["r_p_att_pph"]
    r_p_att_sed = dict_param["r_p_att_sed"]

    r_cst_c_dn = dict_const['r_cst_c_dn']
    r_cst_c_ni = dict_const['r_cst_c_ni']

    # # 2.3. Water quality calculations

    # check if inflow negligible, if so set all concentrations to zero
    if r_in_q_h2o < flow_tolerance:
        logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - Inflow to River Store too low, inflow concentrations set to zero.']))
        r_in_c_no3 = 0.0
        r_in_c_nh4 = 0.0
        r_in_c_dph = 0.0
        r_in_c_pph = 0.0
        r_in_c_sed = 0.0
    # check if storage negligible, if so set all quantities to zero, all out concentrations to zero
    if r_s_v_h2o_old < volume_tolerance:
        logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                              ' - Volume in River Store too low, in-store contaminant quantities '
                              'and outflow concentrations set to zero.']))
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
            c10 = r_cst_c_ni * (1.047 ** (r_in_temp - 20.0))
            c11 = r_cst_c_dn * (1.047 ** (r_in_temp - 20.0))
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
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  ' - NO3 Quantity has gone negative in River Store, quantity reset to zero.']))
            r_s_m_no3 = 0.0
        # calculate outflow concentration
        if (r_s_v_h2o > volume_tolerance) and (r_out_q_h2o > flow_tolerance):
            r_out_c_no3 = r_s_m_no3 / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  " - Volume/Flow in River Store too low, outflow NO3 concentration set to zero."]))
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
        if (r_s_v_h2o > volume_tolerance) and (r_out_q_h2o > flow_tolerance):
            r_out_c_nh4 = r_s_m_nh4 / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  " - Volume/Flow in River Store too low, outflow NH4 concentration set to zero."]))
            r_out_c_nh4 = 0.0

        # # 2.2.3. Dissolved phosphorus DPH
        r_s_m_dph_old = r_s_m_dph
        # calculate concentration in store at beginning of time step
        concentration_dph = r_s_m_dph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_dph = r_s_m_dph_old + ((r_in_c_dph * r_in_q_h2o) - (concentration_dph * r_out_q_h2o)) * time_step_sec
        if r_s_m_dph < 0.0:
            r_s_m_dph = 0.0
        # apply attenuation factor to store
        r_s_m_dph = r_s_m_dph * r_p_att_dph
        # calculate outflow concentration
        if (r_s_v_h2o > volume_tolerance) and (r_out_q_h2o > flow_tolerance):
            r_out_c_dph = r_s_m_dph / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  " - Volume/Flow in River Store too low, outflow DPH concentration set to zero."]))
            r_out_c_dph = 0.0

        # # 2.2.4. Particulate phosphorus PPH
        r_s_m_pph_old = r_s_m_pph
        # calculate concentration in store at beginning of time step
        concentration_pph = r_s_m_pph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_pph = r_s_m_pph_old + ((r_in_c_pph * r_in_q_h2o) - (concentration_pph * r_out_q_h2o)) * time_step_sec
        if r_s_m_pph < 0.0:
            r_s_m_pph = 0.0
        # apply attenuation factor to store
        r_s_m_pph = r_s_m_pph * r_p_att_pph
        # calculate outflow concentration
        if (r_s_v_h2o > volume_tolerance) and (r_out_q_h2o > flow_tolerance):
            r_out_c_pph = r_s_m_pph / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  " - Volume/Flow in River Store too low, outflow PPH concentration set to zero."]))
            r_out_c_pph = 0.0

        # # 2.2.5. Sediments SED
        r_s_m_sed_old = r_s_m_sed
        # calculate concentration in store at beginning of time step
        concentration_sed = r_s_m_sed_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_sed = r_s_m_sed_old + ((r_in_c_sed * r_in_q_h2o) - (concentration_sed * r_out_q_h2o)) * time_step_sec
        if r_s_m_sed < 0.0:
            r_s_m_sed = 0.0
        # apply attenuation factor to store
        r_s_m_sed = r_s_m_sed * r_p_att_sed
        # calculate outflow concentration
        if (r_s_v_h2o > volume_tolerance) and (r_out_q_h2o > flow_tolerance):
            r_out_c_sed = r_s_m_sed / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime("%d/%m/%Y %H:%M:%S"),
                                  " - Volume/Flow in River Store too low, outflow SED concentration set to zero."]))
            r_out_c_sed = 0.0

    # # 2.4. Save inputs, states, and outputs

    dict_data_frame[waterbody][datetime_time_step]["r_in_temp"] = r_in_temp
    dict_data_frame[waterbody][datetime_time_step]["r_in_c_no3"] = r_in_c_no3
    dict_data_frame[waterbody][datetime_time_step]["r_in_c_nh4"] = r_in_c_nh4
    dict_data_frame[waterbody][datetime_time_step]["r_in_c_dph"] = r_in_c_dph
    dict_data_frame[waterbody][datetime_time_step]["r_in_c_pph"] = r_in_c_pph
    dict_data_frame[waterbody][datetime_time_step]["r_in_c_sed"] = r_in_c_sed

    dict_data_frame[waterbody][datetime_time_step]["r_s_m_no3"] = r_s_m_no3
    dict_data_frame[waterbody][datetime_time_step]["r_s_m_nh4"] = r_s_m_nh4
    dict_data_frame[waterbody][datetime_time_step]["r_s_m_dph"] = r_s_m_dph
    dict_data_frame[waterbody][datetime_time_step]["r_s_m_pph"] = r_s_m_pph
    dict_data_frame[waterbody][datetime_time_step]["r_s_m_sed"] = r_s_m_sed

    dict_data_frame[waterbody][datetime_time_step]["r_out_c_no3"] = r_out_c_no3
    dict_data_frame[waterbody][datetime_time_step]["r_out_c_nh4"] = r_out_c_nh4
    dict_data_frame[waterbody][datetime_time_step]["r_out_c_dph"] = r_out_c_dph
    dict_data_frame[waterbody][datetime_time_step]["r_out_c_pph"] = r_out_c_pph
    dict_data_frame[waterbody][datetime_time_step]["r_out_c_sed"] = r_out_c_sed


def infer_land_parameters(dict_desc, my_dict_param):
    # INCA LAND MODEL
    # overland flow attenuation
    my_dict_param['c_p_att_no3_ove'] = 1.0
    my_dict_param['c_p_att_nh4_ove'] = 1.0
    my_dict_param['c_p_att_dph_ove'] = 0.1
    my_dict_param['c_p_att_pph_ove'] = 0.5
    my_dict_param['c_p_att_sed_ove'] = 0.5
    my_dict_param['c_p_att_no3_dra'] = 1.0
    my_dict_param['c_p_att_nh4_dra'] = 1.0
    my_dict_param['c_p_att_dph_dra'] = 0.8
    my_dict_param['c_p_att_pph_dra'] = 0.8
    my_dict_param['c_p_att_sed_dra'] = 0.8
    # inter flow attenuation
    factor = 1.0 * dict_desc['N_subsoil_transport'] * dict_desc['N_near_surface_delivery']
    if factor < 0.0001:
        factor = 0.0001
    elif factor > 1.0:
        factor = 1.0
    factor = factor ** 0.04
    my_dict_param['c_p_att_no3_int'] = factor
    my_dict_param['c_p_att_nh4_int'] = factor
    factor = 1.0 * dict_desc['P_subsoil_transport'] * dict_desc['P_near_surface_delivery']
    if factor < 0.0001:
        factor = 0.0001
    elif factor > 1.0:
        factor = 1.0
    factor = factor ** 0.04
    my_dict_param['c_p_att_dph_int'] = factor
    my_dict_param['c_p_att_pph_int'] = 0.0
    my_dict_param['c_p_att_sed_int'] = 0.0
    # shallow ground water attenuation
    factor = 1.0 * dict_desc['N_bedrock_transport']
    if factor < 0.01:
        factor = 0.01
    elif factor > 1.0:
        factor = 1.0
    factor = factor ** 0.02
    my_dict_param['c_p_att_no3_sgw'] = factor
    my_dict_param['c_p_att_nh4_sgw'] = factor
    my_dict_param['c_p_att_dph_sgw'] = 0.6
    my_dict_param['c_p_att_pph_sgw'] = 0.0
    my_dict_param['c_p_att_sed_sgw'] = 0.0
    # deep ground water attenuation
    my_dict_param['c_p_att_no3_dgw'] = factor
    my_dict_param['c_p_att_nh4_dgw'] = factor
    my_dict_param['c_p_att_dph_dgw'] = 0.5
    my_dict_param['c_p_att_pph_dgw'] = 0.0
    my_dict_param['c_p_att_sed_dgw'] = 0.0
    # soil attenuation
    my_dict_param['c_p_att_no3_soil'] = 0.5
    my_dict_param['c_p_att_nh4_soil'] = 0.5
    my_dict_param['c_p_att_p_org_ra_soil'] = 0.15
    my_dict_param['c_p_att_p_ino_ra_soil'] = 0.15
    my_dict_param['c_p_att_p_org_fb_soil'] = 1.0
    my_dict_param['c_p_att_p_ino_fb_soil'] = 1.0
    my_dict_param['c_p_att_sed_soil'] = 1.0


def infer_stream_parameters(my_dict_param):
    # INCA STREAM MODEL
    # linear reservoir attenuation
    my_dict_param['r_p_att_no3'] = 0.9
    my_dict_param['r_p_att_nh4'] = 0.9
    my_dict_param['r_p_att_dph'] = 0.9
    my_dict_param['r_p_att_pph'] = 1.0
    my_dict_param['r_p_att_sed'] = 1.0
