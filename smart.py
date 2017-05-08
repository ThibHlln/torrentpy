# __________________
#
# Catchment model * c_ *
# _ Hydrology
# ___ Inputs
# _____ c_in_rain              precipitation as rain [mm/time step]
# _____ c_in_peva              potential evapotranspiration [mm/time step]
# ___ States
# _____ c_s_v_h2o_ove       volume of water in overland store [m3]
# _____ c_s_v_h2o_dra       volume of water in drain store [m3]
# _____ c_s_v_h2o_int       volume of water in inter store [m3]
# _____ c_s_v_h2o_sgw       volume of water in shallow groundwater store [m3]
# _____ c_s_v_h2o_dgw       volume of water in deep groundwater store [m3]
# _____ c_s_v_h2o_ly1       volume of water in first soil layer store [m3]
# _____ c_s_v_h2o_ly2       volume of water in second soil layer store [m3]
# _____ c_s_v_h2o_ly3       volume of water in third soil layer store [m3]
# _____ c_s_v_h2o_ly4       volume of water in fourth soil layer store [m3]
# _____ c_s_v_h2o_ly5       volume of water in fifth soil layer store [m3]
# _____ c_s_v_h2o_ly6       volume of water in sixth soil layer store [m3]
# ___ Parameters
# _____ c_p_t               T: rainfall aerial correction coefficient
# _____ c_p_c               C: evaporation decay parameter
# _____ c_p_h               H: quick runoff coefficient
# _____ c_p_s               S: drain flow parameter - fraction of saturation excess diverted to drain flow
# _____ c_p_d               D: soil outflow coefficient
# _____ c_p_z               Z: effective soil depth [mm]
# _____ c_p_sk              SK: surface routing parameter [hours]
# _____ c_p_fk              FK: inter flow routing parameter [hours]
# _____ c_p_gk              GK: groundwater routing parameter [hours]
# _____ c_p_rk              RK: river routing parameter [hours]
# ___ Outputs
# _____ c_out_aeva          actual evapotranspiration [mm]
# _____ c_out_q_h2o_ove     overland flow [m3/s]
# _____ c_out_q_h2o_dra     drain flow [m3/s]
# _____ c_out_q_h2o_int     inter flow [m3/s]
# _____ c_out_q_h2o_sgw     shallow groundwater flow [m3/s]
# _____ c_out_q_h2o_dgw     deep groundwater flow [m3/s]
# _____ c_out_q_h2o         total outflow [m3/s]
# _ Water Quality
# ___ Inputs
# _____ c_in_l_no3          nitrate loading on land [kg/ha/time step]
# _____ c_in_l_nh4          ammonia loading on land [kg/ha/time step]
# _____ c_in_l_dph          dissolved phosphorus loading on land [kg/ha/time step]
# _____ c_in_l_pph          particulate phosphorus loading on land [kg/ha/time step]
# _____ c_in_l_sed          sediment movable from land [kg/ha/time step]
# ___ States
# _____ c_s_c_no3_ove       concentration of nitrate in overland store [kg/m3]
# _____ c_s_c_no3_dra       concentration of nitrate in drain store [kg/m3]
# _____ c_s_c_no3_int       concentration of nitrate in inter store [kg/m3]
# _____ c_s_c_no3_sgw       concentration of nitrate in shallow groundwater store [kg/m3]
# _____ c_s_c_no3_dgw       concentration of nitrate in deep groundwater store [kg/m3]
# _____ c_s_c_no3_ly1       concentration of nitrate in first soil layer store [kg/m3]
# _____ c_s_c_no3_ly2       concentration of nitrate in second soil layer store [kg/m3]
# _____ c_s_c_no3_ly3       concentration of nitrate in third soil layer store [kg/m3]
# _____ c_s_c_no3_ly4       concentration of nitrate in fourth soil layer store [kg/m3]
# _____ c_s_c_no3_ly5       concentration of nitrate in fifth soil layer store [kg/m3]
# _____ c_s_c_no3_ly6       concentration of nitrate in sixth soil layer store [kg/m3]
# _____ c_s_c_nh4_ove       concentration of ammonia in overland store [kg/m3]
# _____ c_s_c_nh4_dra       concentration of ammonia in drain store [kg/m3]
# _____ c_s_c_nh4_int       concentration of ammonia in inter store [kg/m3]
# _____ c_s_c_nh4_sgw       concentration of ammonia in shallow groundwater store [kg/m3]
# _____ c_s_c_nh4_dgw       concentration of ammonia in deep groundwater store [kg/m3]
# _____ c_s_c_nh4_ly1       concentration of ammonia in first soil layer store [kg/m3]
# _____ c_s_c_nh4_ly2       concentration of ammonia in second soil layer store [kg/m3]
# _____ c_s_c_nh4_ly3       concentration of ammonia in third soil layer store [kg/m3]
# _____ c_s_c_nh4_ly4       concentration of ammonia in fourth soil layer store [kg/m3]
# _____ c_s_c_nh4_ly5       concentration of ammonia in fifth soil layer store [kg/m3]
# _____ c_s_c_nh4_ly6       concentration of ammonia in sixth soil layer store [kg/m3]
# _____ c_s_c_dph_ove       concentration of dissolved phosphorus in overland store [kg/m3]
# _____ c_s_c_dph_dra       concentration of dissolved phosphorus in drain store [kg/m3]
# _____ c_s_c_dph_int       concentration of dissolved phosphorus in inter store [kg/m3]
# _____ c_s_c_dph_sgw       concentration of dissolved phosphorus in shallow groundwater store [kg/m3]
# _____ c_s_c_dph_dgw       concentration of dissolved phosphorus in deep groundwater store [kg/m3]
# _____ c_s_c_dph_ly1       concentration of dissolved phosphorus in first soil layer store [kg/m3]
# _____ c_s_c_dph_ly2       concentration of dissolved phosphorus in second soil layer store [kg/m3]
# _____ c_s_c_dph_ly3       concentration of dissolved phosphorus in third soil layer store [kg/m3]
# _____ c_s_c_dph_ly4       concentration of dissolved phosphorus in fourth soil layer store [kg/m3]
# _____ c_s_c_dph_ly5       concentration of dissolved phosphorus in fifth soil layer store [kg/m3]
# _____ c_s_c_dph_ly6       concentration of dissolved phosphorus in sixth soil layer store [kg/m3]
# _____ c_s_c_sed_ove       concentration of particulate phosphorus in overland store [kg/m3]
# _____ c_s_c_sed_dra       concentration of particulate phosphorus in drain store [kg/m3]
# _____ c_s_c_sed_int       concentration of particulate phosphorus in inter store [kg/m3]
# _____ c_s_c_sed_sgw       concentration of particulate phosphorus in shallow groundwater store [kg/m3]
# _____ c_s_c_sed_dgw       concentration of particulate phosphorus in deep groundwater store [kg/m3]
# _____ c_s_c_sed_ly1       concentration of particulate phosphorus in first soil layer store [kg/m3]
# _____ c_s_c_sed_ly2       concentration of particulate phosphorus in second soil layer store [kg/m3]
# _____ c_s_c_sed_ly3       concentration of particulate phosphorus in third soil layer store [kg/m3]
# _____ c_s_c_sed_ly4       concentration of particulate phosphorus in fourth soil layer store [kg/m3]
# _____ c_s_c_sed_ly5       concentration of particulate phosphorus in fifth soil layer store [kg/m3]
# _____ c_s_c_sed_ly6       concentration of particulate phosphorus in sixth soil layer store [kg/m3]
# _____ c_s_c_no3_ove       concentration of sediment in overland store [kg/m3]
# _____ c_s_c_no3_dra       concentration of sediment in drain store [kg/m3]
# _____ c_s_c_no3_int       concentration of sediment in inter store [kg/m3]
# _____ c_s_c_no3_sgw       concentration of sediment in shallow groundwater store [kg/m3]
# _____ c_s_c_no3_dgw       concentration of sediment in deep groundwater store [kg/m3]
# _____ c_s_c_no3_ly1       concentration of sediment in first soil layer store [kg/m3]
# _____ c_s_c_no3_ly2       concentration of sediment in second soil layer store [kg/m3]
# _____ c_s_c_no3_ly3       concentration of sediment in third soil layer store [kg/m3]
# _____ c_s_c_no3_ly4       concentration of sediment in fourth soil layer store [kg/m3]
# _____ c_s_c_no3_ly5       concentration of sediment in fifth soil layer store [kg/m3]
# _____ c_s_c_no3_ly6       concentration of sediment in sixth soil layer store [kg/m3]
# ___ Parameters
# _____ c_p_att_no3         daily attenuation factor for nitrate
# _____ c_p_att_nh4         daily attenuation factor for ammonia
# _____ c_p_att_dph         daily attenuation factor for dissolved phosphorus
# _____ c_p_att_pph         daily attenuation factor for particulate phosphorus
# _____ c_p_att_sed         daily attenuation factor for sediment
# ___ Outputs
# _____ c_out_c_no3         nitrate concentration in outflow [kg/m3]
# _____ c_out_c_nh4         ammonia concentration in outflow [kg/m3]
# _____ c_out_c_dph         dissolved phosphorus in outflow [kg/m3]
# _____ c_out_c_pph         particulate phosphorus in outflow [kg/m3]
# _____ c_out_c_sed         sediment concentration in outflow [kg/m3]
# __________________
#

nb_soil_layers = 6.0  # number of layers in soil column
max_capacity_layer = 25.0  # maximum capacity of each layer (except the lowest)
area = 100.0  # catchment area in m2
time_step_min = 1440  # in minutes
time_step_sec = time_step_min * 60  # in seconds

stores = ['ove', 'dra', 'int', 'sgw', 'dgw']
species = ['no3', 'nh4', 'dph', 'pph', 'sed']
state_species = ['no3', 'nh4', 'p_ino', 'p_ino_fb', 'p_org', 'p_org_fb', 'sed']

# dictionaries to be used for 6 soil layers
dict_z_lyr = dict()
dict_lvl_lyr = dict()

# # 1. Hydrology
# # 1.1. Collect inputs, states, and parameters
c_in_rain = 1.0
c_in_peva = 1.0

c_s_v_h2o_ove = 1.0
c_s_v_h2o_dra = 1.0
c_s_v_h2o_int = 1.0
c_s_v_h2o_sgw = 1.0
c_s_v_h2o_dgw = 1.0

c_s_v_h2o_ly1 = 1.0
c_s_v_h2o_ly2 = 1.0
c_s_v_h2o_ly3 = 1.0
c_s_v_h2o_ly4 = 1.0
c_s_v_h2o_ly5 = 1.0
c_s_v_h2o_ly6 = 1.0

c_p_t = 1.0
c_p_c = 1.0
c_p_h = 1.0
c_p_s = 1.0
c_p_d = 1.0
c_p_z = 1.0
c_p_sk = 1.0
c_p_fk = 1.0
c_p_gk = 1.0
c_p_rk = 1.0

# # 1.2. Hydrological calculations

# all calculations in mm equivalent until further notice

# calculate capacity Z and level LVL of each layer (assumed equal) from effective soil depth
for i in [1, 2, 3, 4, 5, 6]:
    dict_z_lyr[i] = c_p_z / nb_soil_layers

dict_lvl_lyr[1] = c_s_v_h2o_ly1 / area * 1000  # factor 1000 to convert m in mm
dict_lvl_lyr[2] = c_s_v_h2o_ly2 / area * 1000  # factor 1000 to convert m in mm
dict_lvl_lyr[3] = c_s_v_h2o_ly3 / area * 1000  # factor 1000 to convert m in mm
dict_lvl_lyr[4] = c_s_v_h2o_ly4 / area * 1000  # factor 1000 to convert m in mm
dict_lvl_lyr[5] = c_s_v_h2o_ly5 / area * 1000  # factor 1000 to convert m in mm
dict_lvl_lyr[6] = c_s_v_h2o_ly6 / area * 1000  # factor 1000 to convert m in mm

# calculate cumulative level of rain in all soil layers
lvl_total = 0.0
for i in [1, 2, 3, 4, 5, 6]:
    lvl_total += dict_lvl_lyr[i]

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
    h_prime = c_p_h * (lvl_total / c_p_z)
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
    d_prime = c_p_d * (lvl_total / c_p_z)
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

    deficit_rain = - excess_rain
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

# all calculations in S.I. units now

# route overland flow (direct runoff)
c_out_q_h2o_ove = c_s_v_h2o_ove / c_p_sk  # [m3/s]
c_s_v_h2o_ove_old = c_s_v_h2o_ove
c_s_v_h2o_ove += (overland_flow / 1000 * area) - (c_out_q_h2o_ove * time_step_sec)  # [m3] - [m3]
if c_s_v_h2o_ove < 0.0:
    c_s_v_h2o_ove = 0.0
# route drain flow
c_out_q_h2o_dra = c_s_v_h2o_dra / c_p_sk  # [m3/s]
c_s_v_h2o_dra_old = c_s_v_h2o_dra
c_s_v_h2o_dra += (drain_flow / 1000 * area) - (c_out_q_h2o_dra * time_step_sec)  # [m3] - [m3]
if c_s_v_h2o_dra < 0.0:
    c_s_v_h2o_dra = 0.0
# route interflow
c_out_q_h2o_int = c_s_v_h2o_int / c_p_fk  # [m3/s]
c_s_v_h2o_int_old = c_s_v_h2o_int
c_s_v_h2o_int += (inter_flow / 1000 * area) - (c_out_q_h2o_int * time_step_sec)  # [m3] - [m3]
if c_s_v_h2o_int < 0.0:
    c_s_v_h2o_int = 0.0
# route shallow groundwater flow
c_out_q_h2o_sgw = c_s_v_h2o_sgw / c_p_gk  # [m3/s]
c_s_v_h2o_sgw_old = c_s_v_h2o_sgw
c_s_v_h2o_sgw += (inter_flow / 1000 * area) - (c_out_q_h2o_sgw * time_step_sec)  # [m3] - [m3]
if c_s_v_h2o_sgw < 0.0:
    c_s_v_h2o_sgw = 0.0
# route deep groundwater flow
c_out_q_h2o_dgw = c_s_v_h2o_dgw / c_p_gk  # [m3/s]
c_s_v_h2o_dgw_old = c_s_v_h2o_dgw
c_s_v_h2o_dgw += (inter_flow / 1000 * area) - (c_out_q_h2o_dgw * time_step_sec)  # [m3] - [m3]
if c_s_v_h2o_dgw < 0.0:
    c_s_v_h2o_dgw = 0.0
# calculate total outflow
c_out_q_h2o = c_out_q_h2o_ove + c_out_q_h2o_dra + c_out_q_h2o_int + c_out_q_h2o_sgw + c_out_q_h2o_dgw  # [m3/s]

# convert moisture of soil layers from mm into m3
c_s_v_h2o_ly1 = dict_lvl_lyr[1] / 1000 * area
c_s_v_h2o_ly2 = dict_lvl_lyr[2] / 1000 * area
c_s_v_h2o_ly3 = dict_lvl_lyr[3] / 1000 * area
c_s_v_h2o_ly4 = dict_lvl_lyr[4] / 1000 * area
c_s_v_h2o_ly5 = dict_lvl_lyr[5] / 1000 * area

# # 2. Hydrology
# # 2.1. Collect inputs, states, and parameters

c_in_l_no3 = 1.0
c_in_l_nh4 = 1.0
c_in_l_dph = 1.0
c_in_l_pph = 1.0
c_in_l_sed = 1.0
mass_no3 = c_in_l_no3 * area * 1.0e-4  # area in m2 converted into ha
mass_nh4 = c_in_l_nh4 * area * 1.0e-4  # area in m2 converted into ha
mass_dph = c_in_l_dph * area * 1.0e-4  # area in m2 converted into ha
mass_pph = c_in_l_pph * area * 1.0e-4  # area in m2 converted into ha
mass_sed = c_in_l_sed * area * 1.0e-4  # area in m2 converted into ha

dict_states = dict()
for store in stores:
    my_dict = dict()
    for specie in state_species:
        my_dict[specie] = 1.0
    dict_states[store] = my_dict[:]

c_p_att_no3 = 1.0
c_p_att_nh4 = 1.0
c_p_att_dph = 1.0
c_p_att_pph = 1.0
c_p_att_sed = 1.0
# adapt daily attenuation factors to actual time step
time_factor = time_step_sec / 86400.0
if time_factor < 0.005:
    time_factor = 0.005
attenuation_no3 = c_p_att_no3 * time_factor
attenuation_nh4 = c_p_att_nh4 * time_factor
attenuation_dph = c_p_att_dph * time_factor
attenuation_pph = c_p_att_pph * time_factor
attenuation_sed = c_p_att_sed * time_factor

# # 2.2. Water quality calculations



