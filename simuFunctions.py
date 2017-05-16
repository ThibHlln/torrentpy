import math


def infer_parameters_from_descriptors(obj_network, dict_desc):

    dict_parameters = dict()

    for waterbody in obj_network.links:
        my_dict = dict()
        # Parameter T
        my_dict['c_p_t'] = 65.622 * dict_desc[waterbody]['SAAPE'] ** (-0.652) * \
            dict_desc[waterbody]['TAYSLO'] ** 0.003 * \
            (dict_desc[waterbody]['SlopeLow'] + 1) ** (-0.075) * \
            (dict_desc[waterbody]['PEAT'] ** 0.5 + 1) ** (-0.221) * \
            (dict_desc[waterbody]['Made'] ** 0.5 + 1) ** (-0.481)

        # Parameter C
        my_dict['c_p_c'] = 9.041 * dict_desc[waterbody]['SAAR'] ** (-0.71) * \
            dict_desc[waterbody]['Q.mm'] ** 0.573 * \
            dict_desc[waterbody]['FLATWET'] ** (-0.753) * \
            (dict_desc[waterbody]['AlluvMIN'] + 1) * (-3.378) * \
            (dict_desc[waterbody]['FOREST'] + 1) * (-0.713) * \
            (dict_desc[waterbody]['Pu_Pl'] ** 0.5 + 1) ** 0.221

        # Parameter H
        my_dict['c_p_h'] = 2.789 * dict_desc[waterbody]['DRAIND'] ** 0.157 * \
            dict_desc[waterbody]['WtdReCoMod'] ** 0.036 * \
            (dict_desc[waterbody]['PoorDrain'] + 1) ** (-0.081) * \
            (dict_desc[waterbody]['Water'] ** 0.25 + 1) ** 0.102 * \
            (dict_desc[waterbody]['ModP'] + 1) ** (-0.15) * \
            (dict_desc[waterbody]['Rkc_Rk'] + 1) ** (-0.146) * \
            (dict_desc[waterbody]['Pu_Pl'] ** 0.5 + 1) ** (-0.179) * \
            (dict_desc[waterbody]['Lg_Rg'] ** 0.5 + 1) ** 0.224

        # Parameter S
        drain_eff_factor = 0.75
        my_dict['c_p_s'] = dict_desc[waterbody]['land_drain_ratio'] * drain_eff_factor

        # Parameter D
        my_dict['c_p_d'] = 8.611e-14 * dict_desc[waterbody]['SAAR'] ** 3.207 * \
            dict_desc[waterbody]['AVG.SLOPE'] ** (-1.089) * \
            (dict_desc[waterbody]['BFIsoil'] ** 2 + 1) ** (-3.765) * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1) ** 17.515 * \
            (dict_desc[waterbody]['FOREST'] + 1) ** 9.544 * \
            (dict_desc[waterbody]['WellDrain'] + 1) ** 5.654 * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1) ** (-6.206) * \
            (dict_desc[waterbody]['Rkd_Lk'] + 1) ** 1.553 * \
            (dict_desc[waterbody]['Lm_Rf'] + 1) ** 4.251 * \
            math.exp(dict_desc[waterbody]['Ll']) ** (-1.186)

        # Parameter Z
        my_dict['c_p_z'] = 9.2e6 * dict_desc[waterbody]['SAAR'] ** (-1.85) * \
            dict_desc[waterbody]['DRAIND'] ** 0.633 * \
            (dict_desc[waterbody]['BFIsoil'] ** 2 + 1) ** 1.729 * \
            dict_desc[waterbody]['FARL'] ** (-2.912) * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1) ** (-5.634) * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1) ** 3.051 * \
            (dict_desc[waterbody]['Lm_Rf'] + 1) ** (-2.193) * \
            math.exp(dict_desc[waterbody]['Ll']) ** 0.554

        # Parameter SK
        my_dict['c_p_sk'] = 2.8e5 * (dict_desc[waterbody]['BFIsoil'] ** 2 + 1) ** 1.32 * \
            dict_desc[waterbody]['FARL'] ** (-8.366) * \
            dict_desc[waterbody]['SAAR'] ** (-1.24) * \
            (dict_desc[waterbody]['ARTDRAIN'] ** 2 + 1) ** (-0.529) * \
            (dict_desc[waterbody]['PoorDrain'] + 1) ** (-1.605)

        # Parameter FK
        my_dict['c_p_fk'] = 5.67e-7 * dict_desc[waterbody]['SAAR'] ** 5.619 * \
            dict_desc[waterbody]['Q.mm'] ** (-3.037) * \
            (dict_desc[waterbody]['ARTDRAIN'] ** 2 + 1) ** (-1.279) * \
            (dict_desc[waterbody]['BFIsoil'] ** 2 + 1) ** 3.017 * \
            (dict_desc[waterbody]['VulXE'] ** 0.5 + 1) ** (-2.823) * \
            (dict_desc[waterbody]['VulML'] + 1) ** 2.727 * \
            (dict_desc[waterbody]['URBEXT'] ** 0.5 + 1) ** (-10.386) * \
            (dict_desc[waterbody]['FOREST'] + 1) ** -2.43 * \
            (dict_desc[waterbody]['HighP'] ** 0.5 + 1) ** 6.089 * \
            (dict_desc[waterbody]['PNA'] + 1) ** 2.781 * \
            (dict_desc[waterbody]['Rkc_Rk'] + 1) ** (-1.6107)

        # Parameter GK
        my_dict['c_p_gk'] = 46950 + dict_desc[waterbody]['SlopeLow'] * 8676 + \
            dict_desc[waterbody]['SAAPE'] * (-82.27) + \
            dict_desc[waterbody]['Rkc_Rk'] * (-7204) + \
            dict_desc[waterbody]['Pu_Pl'] * (-1911) + \
            dict_desc[waterbody]['Made'] * (-127800) + \
            dict_desc[waterbody]['WtdReCoMod'] * (-49470) + \
            dict_desc[waterbody]['FOREST'] * 9257 + \
            dict_desc[waterbody]['SAAR'] * (-5.379) + \
            dict_desc[waterbody]['WtdReCoMod'] * dict_desc['SAAR'] * 41.68

        # Parameter RK
        l = dict_desc[waterbody]['stream_length']
        q = 0.7 * dict_desc[waterbody]['SAAR'] * dict_desc[waterbody]['AREA'] * 3.171e-5
        slp = dict_desc[waterbody]['TAYSLO'] / 1000.0
        n = 0.04
        my_dict['c_p_s'] = l / ((q**(2/5) * slp**(3/10)) / ((3.67 * q**0.45) ** (2/5) * n**(3/5)))

        dict_parameters[waterbody] = my_dict[:]

    return dict_parameters

