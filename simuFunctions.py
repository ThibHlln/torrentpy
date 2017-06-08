import math
from pandas import DataFrame

import simuFiles as sF


def infer_parameters_from_descriptors(obj_network, dict_desc, logger):

    dict_parameters = dict()

    for waterbody in obj_network.links:
        my_dict = dict()

        # HYDROLOGICAL MODEL
        # Parameter T: Rainfall aerial correction coefficient
        my_dict['c_p_t'] = 65.622 * dict_desc[waterbody]['SAAPE'] ** (-0.652) * \
            dict_desc[waterbody]['TAYSLO'] ** 0.003 * \
            (dict_desc[waterbody]['SlopeLow'] + 1.0) ** (-0.075) * \
            (dict_desc[waterbody]['PEAT'] ** 0.5 + 1.0) ** (-0.221) * \
            (dict_desc[waterbody]['Made'] ** 0.5 + 1.0) ** (-0.481)

        # Parameter C: Evaporation decay parameter
        my_dict['c_p_c'] = 9.041 * dict_desc[waterbody]['SAAR'] ** (-0.71) * \
            dict_desc[waterbody]['Q.mm'] ** 0.573 * \
            dict_desc[waterbody]['FLATWET'] ** (-0.753) * \
            (dict_desc[waterbody]['AlluvMIN'] + 1.0) * (-3.378) * \
            (dict_desc[waterbody]['FOREST'] + 1.0) * (-0.713) * \
            ((dict_desc[waterbody]['Pu'] + dict_desc[waterbody]['Pl']) ** 0.5 + 1.0) ** 0.221

        # Parameter H: Quick runoff coefficient
        my_dict['c_p_h'] = 2.789 * dict_desc[waterbody]['DRAIND'] ** 0.157 * \
            dict_desc[waterbody]['WtdReCoMod'] ** 0.036 * \
            (dict_desc[waterbody]['PoorDrain'] + 1.0) ** (-0.081) * \
            (dict_desc[waterbody]['Water'] ** 0.25 + 1.0) ** 0.102 * \
            (dict_desc[waterbody]['ModP'] + 1.0) ** (-0.15) * \
            ((dict_desc[waterbody]['Rkc'] + dict_desc[waterbody]['Rk']) + 1.0) ** (-0.146) * \
            ((dict_desc[waterbody]['Pu'] + dict_desc[waterbody]['Pl']) ** 0.5 + 1.0) ** (-0.179) * \
            ((dict_desc[waterbody]['Lg'] + dict_desc[waterbody]['Rg']) ** 0.5 + 1.0) ** 0.224

        # Parameter S: Drain flow parameter - fraction of saturation excess diverted to drain flow
        drain_eff_factor = 0.75
        my_dict['c_p_s'] = dict_desc[waterbody]['land_drain_ratio'] * drain_eff_factor

        # Parameter D: Soil outflow coefficient
        my_dict['c_p_d'] = 8.611e-14 * dict_desc[waterbody]['SAAR'] ** 3.207 * \
            dict_desc[waterbody]['AVG.SLOPE'] ** (-1.089) * \
            (dict_desc[waterbody]['BFIsoil'] ** 2.0 + 1.0) ** (-3.765) * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1.0) ** 17.515 * \
            (dict_desc[waterbody]['FOREST'] + 1.0) ** 9.544 * \
            (dict_desc[waterbody]['WellDrain'] + 1.0) ** 5.654 * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1.0) ** (-6.206) * \
            ((dict_desc[waterbody]['Rkd'] + dict_desc[waterbody]['Lk']) + 1.0) ** 1.553 * \
            ((dict_desc[waterbody]['Lm'] + dict_desc[waterbody]['Rf']) + 1.0) ** 4.251 * \
            math.exp(dict_desc[waterbody]['Ll']) ** (-1.186)

        # Parameter Z: Effective soil depth (mm)
        my_dict['c_p_z'] = 9.2e6 * dict_desc[waterbody]['SAAR'] ** (-1.85) * \
            dict_desc[waterbody]['DRAIND'] ** 0.633 * \
            (dict_desc[waterbody]['BFIsoil'] ** 2.0 + 1.0) ** 1.729 * \
            dict_desc[waterbody]['FARL'] ** (-2.912) * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1.0) ** (-5.634) * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1.0) ** 3.051 * \
            ((dict_desc[waterbody]['Lm'] + dict_desc[waterbody]['Rf']) + 1.0) ** (-2.193) * \
            math.exp(dict_desc[waterbody]['Ll']) ** 0.554

        # Parameter SK: Surface routing parameter (hours)
        my_dict['c_p_sk'] = 2.8e5 * (dict_desc[waterbody]['BFIsoil'] ** 2.0 + 1.0) ** 1.32 * \
            dict_desc[waterbody]['FARL'] ** (-8.366) * \
            dict_desc[waterbody]['SAAR'] ** (-1.24) * \
            (dict_desc[waterbody]['ARTDRAIN2'] + 1.0) ** (-0.529) * \
            (dict_desc[waterbody]['PoorDrain'] + 1.0) ** (-1.605)

        # Parameter FK: Interflow routing parameter (hours)
        my_dict['c_p_fk'] = 5.67e-7 * dict_desc[waterbody]['SAAR'] ** 5.619 * \
            dict_desc[waterbody]['Q.mm'] ** (-3.037) * \
            (dict_desc[waterbody]['ARTDRAIN2'] + 1.0) ** (-1.279) * \
            (dict_desc[waterbody]['BFIsoil'] ** 2.0 + 1.0) ** 3.017 * \
            ((dict_desc[waterbody]['VulX'] + dict_desc[waterbody]['VulE']) ** 0.5 + 1.0) ** (-2.823) * \
            ((dict_desc[waterbody]['VulM'] + dict_desc[waterbody]['VulL']) + 1.0) ** 2.727 * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1.0) ** (-10.386) * \
            (dict_desc[waterbody]['FOREST'] + 1.0) ** (-2.43) * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1.0) ** 6.089 * \
            (dict_desc[waterbody]['PNA'] + 1.0) ** 2.781 * \
            ((dict_desc[waterbody]['Rkc'] + dict_desc[waterbody]['Rk']) + 1.0) ** (-1.6107)

        # Parameter GK: Groundwater routing parameter (hours)
        my_dict['c_p_gk'] = 46950.0 + dict_desc[waterbody]['SlopeLow'] * 8676.0 + \
            dict_desc[waterbody]['SAAPE'] * (-82.27) + \
            (dict_desc[waterbody]['Rkc'] + dict_desc[waterbody]['Rk']) * (-7204.0) + \
            (dict_desc[waterbody]['Pu'] + dict_desc[waterbody]['Pl']) * (-1911.0) + \
            dict_desc[waterbody]['Made'] * (-127800.0) + \
            dict_desc[waterbody]['WtdReCoMod'] * (-49470.0) + \
            dict_desc[waterbody]['FOREST'] * 9257.0 + \
            dict_desc[waterbody]['SAAR'] * (-5.379) + \
            dict_desc[waterbody]['WtdReCoMod'] * dict_desc[waterbody]['SAAR'] * 41.68
        if my_dict['c_p_gk'] < 0.3 * my_dict['c_p_fk']:
            my_dict['c_p_gk'] = 3.0 * my_dict['c_p_fk']

        # Parameter RK: River routing parameter (hours)
        l = dict_desc[waterbody]['stream_length']
        q = 0.7 * dict_desc[waterbody]['SAAR'] * dict_desc[waterbody]['area'] * 3.171e-5
        slp = dict_desc[waterbody]['TAYSLO'] / 1000.0
        n = 0.04
        r_in_sec = l / (
            (q ** (2.0 / 5.0) * slp ** (3.0 / 10.0)) / ((3.67 * q ** 0.45) ** (2.0 / 5.0) * n ** (3.0 / 5.0)))
        my_dict['c_p_rk'] = r_in_sec / 3600.0  # convert sec in hours
        my_dict['r_p_k_h2o'] = r_in_sec / 3600.0  # convert sec in hours

        # WATER QUALITY MODEL

        # overland flow attenuation
        my_dict['c_p_att_no3_ove'] = 1.0
        my_dict['c_p_att_nh4_ove'] = 1.0
        my_dict['c_p_att_dph_ove'] = 1.0
        my_dict['c_p_att_pph_ove'] = 0.5
        my_dict['c_p_att_sed_ove'] = 0.5
        my_dict['c_p_att_no3_dra'] = 1.0
        my_dict['c_p_att_nh4_dra'] = 1.0
        my_dict['c_p_att_dph_dra'] = 0.8
        my_dict['c_p_att_pph_dra'] = 0.8
        my_dict['c_p_att_sed_dra'] = 0.8

        # inter flow attenuation
        # factor = 1.0 * (dict_desc[waterbody]['N_subsoil_transport'] / 100.0) * \
        #     (dict_desc[waterbody]['N_near_surface_delivery'] / 100.0)
        # if factor < 0.0001:
        #     factor = 0.0001
        # elif factor > 1.0:
        #     factor = 1.0
        # factor = factor ** 0.04
        my_dict['c_p_att_no3_int'] = 1.0  # factor
        my_dict['c_p_att_nh4_int'] = 1.0  # factor
        # factor = 1.0 * (dict_desc[waterbody]['P_subsoil_transport'] / 100.0) * \
        #     (dict_desc[waterbody]['P_near_surface_delivery'] / 100.0)
        # if factor < 0.0001:
        #     factor = 0.0001
        # elif factor > 1.0:
        #     factor = 1.0
        # factor = factor ** 0.04
        my_dict['c_p_att_dph_int'] = 1.0  # factor
        my_dict['c_p_att_pph_int'] = 1.0
        my_dict['c_p_att_sed_int'] = 1.0

        # shallow ground water attenuation
        # factor = 1.0 * (dict_desc[waterbody]['N_bedrock_transport'] / 100.0)
        # if factor < 0.01:
        #     factor = 0.01
        # elif factor > 1.0:
        #     factor = 1.0
        # factor = factor ** 0.02
        my_dict['c_p_att_no3_sgw'] = 1.0  # factor
        my_dict['c_p_att_nh4_sgw'] = 1.0  # factor
        my_dict['c_p_att_dph_sgw'] = 0.6
        my_dict['c_p_att_pph_sgw'] = 0.0
        my_dict['c_p_att_sed_sgw'] = 0.0

        # deep ground water attenuation
        my_dict['c_p_att_no3_dgw'] = 1.0  # factor
        my_dict['c_p_att_nh4_dgw'] = 1.0  # factor
        my_dict['c_p_att_dph_dgw'] = 0.5
        my_dict['c_p_att_pph_dgw'] = 0.0
        my_dict['c_p_att_sed_dgw'] = 0.0

        # soil attenuation
        my_dict['c_p_att_no3_soil'] = 1.0
        my_dict['c_p_att_nh4_soil'] = 1.0
        my_dict['c_p_att_p_org_ra_soil'] = 0.15
        my_dict['c_p_att_p_ino_ra_soil'] = 0.15
        my_dict['c_p_att_p_org_fb_soil'] = 1.0
        my_dict['c_p_att_p_ino_fb_soil'] = 1.0
        my_dict['c_p_att_sed_soil'] = 1.0

        # linear reservoir attenuation
        my_dict['r_p_att_no3'] = 0.9
        my_dict['r_p_att_nh4'] = 0.9
        my_dict['r_p_att_dph'] = 0.9
        my_dict['r_p_att_pph'] = 1.0
        my_dict['r_p_att_sed'] = 1.0

        # ATTRIBUTE ALL PARAMETERS TO RELEVANT WATERBODY
        logger.info('Parameters for {} are:\n'
                    'T = {}\n'
                    'C = {}\n'
                    'H = {}\n'
                    'S = {}\n'
                    'D = {}\n'
                    'Z = {}\n'
                    'SK = {}\n'
                    'FK = {}\n'
                    'GK = {}\n'
                    'RK = {}'.format(waterbody, my_dict['c_p_t'],  my_dict['c_p_c'], my_dict['c_p_h'], my_dict['c_p_s'],
                                     my_dict['c_p_d'], my_dict['c_p_z'], my_dict['c_p_sk'], my_dict['c_p_fk'],
                                     my_dict['c_p_gk'], my_dict['c_p_rk']))

        dict_parameters[waterbody] = my_dict

    return dict_parameters


def distribute_loadings_across_year(obj_network, dict_annual_loads, dict_applications, time_steps, specs_folder):

    my_distributions = sF.get_df_distributions_from_file(specs_folder)

    dict_loadings = dict()
    for link in obj_network.links:
        my_df = DataFrame(index=time_steps, columns=dict_applications[link]).fillna(0.0)
        for contaminant in dict_applications[link]:
            for datetime_time_step in time_steps:
                day_of_year = float(datetime_time_step.timetuple().tm_yday)
                my_df.set_value(datetime_time_step, contaminant,
                                dict_annual_loads[link][contaminant] *
                                my_distributions.loc[day_of_year, dict_applications[link][contaminant]])
        dict_loadings[link] = my_df

    return dict_loadings
