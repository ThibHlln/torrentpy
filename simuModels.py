import datetime

from models import smart, linres


def catchment_model(waterbody, dict_data_frame, dict_param, dict_meteo, dict_loads, datetime_time_step, time_gap):

    list_hd_inputs = ["c_in_rain", "c_in_peva", "c_in_temp"]
    list_hd_states = ["c_s_v_h2o_ove", "c_s_v_h2o_dra", "c_s_v_h2o_int", "c_s_v_h2o_sgw", "c_s_v_h2o_dgw",
                      "c_s_v_h2o_ly1", "c_s_v_h2o_ly2", "c_s_v_h2o_ly3", "c_s_v_h2o_ly4", "c_s_v_h2o_ly5",
                      "c_s_v_h2o_ly6"]
    list_hd_parameters = ["c_p_t", "c_p_c", "c_p_h", "c_p_s", "c_p_d", "c_p_z", "c_p_sk", "c_p_fk", "c_p_gk", "c_p_rk"]
    list_hd_outputs = ["c_out_aeva", "c_out_q_h2o_ove", "c_out_q_h2o_dra", "c_out_q_h2o_int", "c_out_q_h2o_sgw",
                       "c_out_q_h2o_dgw", "c_out_q_h2o"]

    list_wq_inputs = ["c_in_l_no3", "c_in_l_nh4", "c_in_l_dph", "c_in_l_pph", "c_in_l_sed"]
    list_wq_states = ["c_s_c_no3_ove", "c_s_c_no3_dra", "c_s_c_no3_int", "c_s_c_no3_sgw", "c_s_c_no3_dgw",
                      "c_s_c_nh4_ove", "c_s_c_nh4_dra", "c_s_c_nh4_int", "c_s_c_nh4_sgw", "c_s_c_nh4_dgw",
                      "c_s_c_dph_ove", "c_s_c_dph_dra", "c_s_c_dph_int", "c_s_c_dph_sgw", "c_s_c_dph_dgw",
                      "c_s_c_pph_ove", "c_s_c_pph_dra", "c_s_c_pph_int", "c_s_c_pph_sgw", "c_s_c_pph_dgw",
                      "c_s_c_sed_ove", "c_s_c_sed_dra", "c_s_c_sed_int", "c_s_c_sed_sgw", "c_s_c_sed_dgw",
                      "c_s_c_no3_soil", "c_s_c_nh4_soil", "c_s_c_p_org_ra_soil", "c_s_c_p_ino_ra_soil",
                      "c_s_m_p_org_fb_soil", "c_s_m_p_ino_fb_soil"]
    list_wq_parameters = ["c_p_att_no3_ove", "c_p_att_nh4_ove", "c_p_att_dph_ove", "c_p_att_pph_ove", "c_p_att_sed_ove",
                          "c_p_att_no3_dra", "c_p_att_nh4_dra", "c_p_att_dph_dra", "c_p_att_pph_dra", "c_p_att_sed_dra",
                          "c_p_att_no3_int", "c_p_att_nh4_int", "c_p_att_dph_int", "c_p_att_pph_int", "c_p_att_sed_int",
                          "c_p_att_no3_sgw", "c_p_att_nh4_sgw", "c_p_att_dph_sgw", "c_p_att_pph_sgw", "c_p_att_sed_sgw",
                          "c_p_att_no3_dgw", "c_p_att_nh4_dgw", "c_p_att_dph_dgw", "c_p_att_pph_dgw", "c_p_att_sed_dgw",
                          "c_p_att_no3_soil", "c_p_att_nh4_soil", "c_p_att_p_org_ra_soil", "c_p_att_p_ino_ra_soil",
                          "c_p_att_p_org_fb_soil", "c_p_att_p_ino_fb_soil"]
    list_wq_outputs = ["c_out_c_no3_ove", "c_out_c_nh4_ove", "c_out_c_dph_ove", "c_out_c_pph_ove", "c_out_c_sed_ove",
                       "c_out_c_no3_dra", "c_out_c_nh4_dra", "c_out_c_dph_dra", "c_out_c_pph_dra", "c_out_c_sed_dra",
                       "c_out_c_no3_int", "c_out_c_nh4_int", "c_out_c_dph_int", "c_out_c_pph_int", "c_out_c_sed_int",
                       "c_out_c_no3_sgw", "c_out_c_nh4_sgw", "c_out_c_dph_sgw", "c_out_c_pph_sgw", "c_out_c_sed_sgw",
                       "c_out_c_no3_dgw", "c_out_c_nh4_dgw", "c_out_c_dph_dgw", "c_out_c_pph_dgw", "c_out_c_sed_dgw"]

    # Store the inputs & parameters
    for variable in list_hd_inputs:
        dict_data_frame[waterbody].set_value(datetime_time_step, variable,
                                             dict_meteo[waterbody].loc[datetime_time_step, variable])
    for variable in list_wq_inputs:
        dict_data_frame[waterbody].set_value(datetime_time_step, variable,
                                             dict_loads[waterbody].loc[datetime_time_step, variable])
    for parameter in list_hd_parameters + list_wq_parameters:
        dict_data_frame[waterbody].set_value(datetime_time_step, parameter,
                                             dict_param[waterbody][parameter])

    # States & Outputs

    smart.run()

    dict_data_frame[waterbody].set_value(datetime_time_step, "aeva", aeva)
    dict_data_frame[waterbody].set_value(datetime_time_step, "q", q)
    dict_data_frame[waterbody].set_value(datetime_time_step, "h", h)


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
