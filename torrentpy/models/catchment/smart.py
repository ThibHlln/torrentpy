# -*- coding: utf-8 -*-

# This file is part of TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork
# Copyright (C) 2018  Thibault Hallouin (1), Eva Mockler (1,2), Michael Bruen (1)
#
# (1) Dooge Centre for Water Resources Research, University College Dublin, Ireland
# (2) Environmental Protection Agency, Ireland
#
# TORRENTpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TORRENTpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TORRENTpy. If not, see <http://www.gnu.org/licenses/>.

from datetime import timedelta
from math import exp, log
import csv
import os

try:
    import smartcpp
    smart_in_cpp = True
except ImportError:
    smartcpp = None
    smart_in_cpp = False

from ..model import Model


class SMARTc(Model):
    def __init__(self, category, identifier):
        Model.__init__(self, category, identifier)
        # set model variables names
        self.inputs_names = ['c_in_rain', 'c_in_peva']
        self.parameters_names = ['c_p_t', 'c_p_c', 'c_p_h', 'c_p_d', 'c_p_s', 'c_p_z', 'c_p_sk', 'c_p_fk', 'c_p_gk']
        self.states_names = ['c_s_v_h2o_ove', 'c_s_v_h2o_dra', 'c_s_v_h2o_int', 'c_s_v_h2o_sgw', 'c_s_v_h2o_dgw',
                             'c_s_v_h2o_ly1', 'c_s_v_h2o_ly2', 'c_s_v_h2o_ly3',
                             'c_s_v_h2o_ly4', 'c_s_v_h2o_ly5', 'c_s_v_h2o_ly6']
        self.processes_names = ['c_pr_eff_rain_to_ove', 'c_pr_eff_rain_to_dra', 'c_pr_eff_rain_to_int',
                                'c_pr_eff_rain_to_sgw', 'c_pr_eff_rain_to_dgw']
        self.outputs_names = ['c_out_aeva', 'c_out_q_h2o_ove', 'c_out_q_h2o_dra', 'c_out_q_h2o_int',
                              'c_out_q_h2o_sgw', 'c_out_q_h2o_dgw', 'c_out_q_h2o']

    def set_constants(self, input_folder):
        self._set_constants_with_file(input_folder)

    def set_parameters(self, link, catchment, outlet, input_folder, output_folder):
        if os.path.isfile('{}{}_{}.{}.parameters'.format(input_folder, catchment, outlet, self.identifier)):
            self._set_parameters_with_file(link, catchment, outlet, input_folder)
        else:
            self._infer_parameters(link, catchment, outlet, output_folder)

    def _infer_parameters(self, link, catchment, outlet, output_folder):

        dict_for_file = infer_parameters(link.descriptors)

        my_dict = dict(dict_for_file)
        dict_for_file['WaterBody'] = link.name

        if os.path.isfile('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                           self.identifier, self.category)):
            with open('{}{}_{}.{}.parameters'.format(output_folder, catchment, outlet,
                                                     self.identifier, self.category),
                      'ab') as my_file:
                header = ['WaterBody'] + self.parameters_names
                my_writer = csv.DictWriter(my_file, fieldnames=header)
                my_writer.writerow(dict_for_file)
        else:
            with open('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                       self.identifier, self.category),
                      'wb') as my_file:
                header = ['WaterBody'] + self.parameters_names
                my_writer = csv.DictWriter(my_file, fieldnames=header)
                my_writer.writeheader()
                my_writer.writerow(dict_for_file)

        self.parameters = my_dict
        link.models_parameters.update(my_dict)

    def initialise(self, link):

        return initialise_states(link.descriptors, self.parameters, link.extra)

    def simulate(self, db, tf, step, link, logger):

        simulate(link.name, step, tf.simu_gap,
                 self.parameters,
                 db.simulation, link.descriptors, db.meteo,
                 logger)


def simulate(waterbody, datetime_time_step, time_gap,
             dict_param,
             dict_data_frame, dict_desc, dict_meteo,
             logger):

    smart_in = get_in(waterbody, datetime_time_step, time_gap,
                      dict_data_frame, dict_desc, dict_param, dict_meteo)

    if smart_in_cpp:
        smart_out = smartcpp.onestep_c(*smart_in)
    else:
        smart_out = run(waterbody, datetime_time_step, logger, *smart_in)

    get_out(waterbody, datetime_time_step, dict_data_frame, *smart_out)


def run(waterbody, datetime_time_step, logger,
        area_m2, time_gap_sec,
        c_in_rain, c_in_peva,
        c_p_t, c_p_c, c_p_h, c_p_d, c_p_s, c_p_z, c_p_sk, c_p_fk, c_p_gk,
        c_s_v_h2o_ove, c_s_v_h2o_dra, c_s_v_h2o_int, c_s_v_h2o_sgw, c_s_v_h2o_dgw,
        c_s_v_h2o_ly1, c_s_v_h2o_ly2, c_s_v_h2o_ly3, c_s_v_h2o_ly4, c_s_v_h2o_ly5, c_s_v_h2o_ly6):
    """
    Catchment Constants
    _ area_m2                   catchment area [m2]
    _ time_gap_sec              time gap between two simulation time steps [seconds]

    Catchment Model * c_ *
    _ Hydrology
    ___ Inputs * in_ *
    _____ c_in_rain             precipitation as rain [mm/time step]
    _____ c_in_peva             potential evapotranspiration [mm/time step]
    ___ Parameters * p_ *
    _____ c_p_t                 T: rainfall aerial correction coefficient
    _____ c_p_c                 C: evaporation decay parameter
    _____ c_p_h                 H: quick runoff coefficient
    _____ c_p_d                 D: drain flow parameter - fraction of saturation excess diverted to drain flow
    _____ c_p_s                 S: soil outflow coefficient
    _____ c_p_z                 Z: effective soil depth [mm]
    _____ c_p_sk                SK: surface routing parameter [hours]
    _____ c_p_fk                FK: inter flow routing parameter [hours]
    _____ c_p_gk                GK: groundwater routing parameter [hours]
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

    ___ Processes * pr_ *
    _____ c_pr_eff_rain_to_ove  effective rainfall converted into overland flow runoff [mm]
    _____ c_pr_eff_rain_to_dra  effective rainfall converted into to drain flow runoff [mm]
    _____ c_pr_eff_rain_to_int  effective rainfall converted into to interflow runoff [mm]
    _____ c_pr_eff_rain_to_sgw  effective rainfall converted into to shallow groundwater flow runoff [mm]
    _____ c_pr_eff_rain_to_dgw  effective rainfall converted into to deep groundwater flow runoff [mm]
    ___ Outputs * out_ *
    _____ c_out_aeva            actual evapotranspiration [m3/s]
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

    # # 1.1. Unit conversions
    c_p_sk *= 3600.0  # convert hours in seconds
    c_p_fk *= 3600.0  # convert hours in seconds
    c_p_gk *= 3600.0  # convert hours in seconds

    # # 1.2. Hydrological calculations

    # /!\ all calculations in mm equivalent until further notice

    # calculate capacity Z and level LVL of each layer (assumed equal) from effective soil depth
    dict_z_lyr = dict()
    for i in [1, 2, 3, 4, 5, 6]:
        dict_z_lyr[i] = c_p_z / nb_soil_layers
    dict_lvl_lyr = dict()
    # use indices to identify the six soil layers (from 1 for top layer to 6 for bottom layer)
    dict_lvl_lyr[1] = c_s_v_h2o_ly1 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[2] = c_s_v_h2o_ly2 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[3] = c_s_v_h2o_ly3 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[4] = c_s_v_h2o_ly4 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[5] = c_s_v_h2o_ly5 / area_m2 * 1e3  # factor 1000 to convert m in mm
    dict_lvl_lyr[6] = c_s_v_h2o_ly6 / area_m2 * 1e3  # factor 1000 to convert m in mm

    # calculate cumulative level of water in all soil layers at beginning of time step (i.e. soil moisture)
    lvl_total_start = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_start += dict_lvl_lyr[i]

    # apply parameter T to rainfall data (aerial rainfall correction)
    rain = c_in_rain * c_p_t
    # calculate excess rainfall
    excess_rain = rain - c_in_peva
    # initialise actual evapotranspiration variable
    aeva = 0.0

    if excess_rain >= 0.0:  # excess rainfall available for runoff and infiltration
        # actual evapotranspiration = potential evapotranspiration
        aeva += c_in_peva
        # calculate surface runoff using quick runoff parameter H and relative soil moisture content
        h_prime = c_p_h * (lvl_total_start / c_p_z)
        c_pr_eff_rain_to_ove = h_prime * excess_rain  # excess rainfall contribution to quick surface runoff store
        excess_rain -= c_pr_eff_rain_to_ove  # remainder that infiltrates
        # calculate percolation through soil layers (from top layer [1] to bottom layer [6])
        for i in [1, 2, 3, 4, 5, 6]:
            space_in_lyr = dict_z_lyr[i] - dict_lvl_lyr[i]
            if excess_rain <= space_in_lyr:
                dict_lvl_lyr[i] += excess_rain
                excess_rain = 0.0
            else:
                dict_lvl_lyr[i] = dict_z_lyr[i]
                excess_rain -= space_in_lyr
        # calculate saturation excess from remaining excess rainfall after filling layers (if not 0)
        c_pr_eff_rain_to_dra = c_p_d * excess_rain  # sat. excess contr. (if not 0) to quick interflow runoff store
        c_pr_eff_rain_to_int = (1.0 - c_p_d) * excess_rain  # sat. ex. contr. (if not 0) to slow interflow runoff store
        # calculate leak from soil layers (i.e. piston flow becoming active during rainfall events)
        s_prime = c_p_s * (lvl_total_start / c_p_z)
        # leak to interflow
        for i in [1, 2, 3, 4, 5, 6]:  # soil moisture outflow reducing exponentially downwards
            leak_interflow = dict_lvl_lyr[i] * (s_prime ** i)
            if leak_interflow < dict_lvl_lyr[i]:
                c_pr_eff_rain_to_int += leak_interflow  # soil moisture outflow contrib. to slow interflow runoff store
                dict_lvl_lyr[i] -= leak_interflow
        # leak to shallow groundwater flow
        c_pr_eff_rain_to_sgw = 0.0
        for i in [1, 2, 3, 4, 5, 6]:  # soil moisture outflow reducing linearly downwards
            leak_shallow_flow = dict_lvl_lyr[i] * (s_prime / i)
            if leak_shallow_flow < dict_lvl_lyr[i]:
                c_pr_eff_rain_to_sgw += leak_shallow_flow  # soil moisture outflow cont. to slow shallow GW runoff store
                dict_lvl_lyr[i] -= leak_shallow_flow
        # leak to deep groundwater flow
        c_pr_eff_rain_to_dgw = 0.0
        for i in [6, 5, 4, 3, 2, 1]:  # soil moisture outflow reducing exponentially upwards
            leak_deep_flow = dict_lvl_lyr[i] * (s_prime ** (7 - i))
            if leak_deep_flow < dict_lvl_lyr[i]:
                c_pr_eff_rain_to_dgw += leak_deep_flow  # soil moisture outflow contrib. to slow deep GW runoff store
                dict_lvl_lyr[i] -= leak_deep_flow
    else:  # no excess rainfall (i.e. potential evapotranspiration not satisfied by available rainfall)
        c_pr_eff_rain_to_ove = 0.0  # no effective rainfall contribution to quick overland flow runoff store
        c_pr_eff_rain_to_dra = 0.0  # no effective rainfall contribution to quick drain flow runoff store
        c_pr_eff_rain_to_int = 0.0  # no effective rainfall contribution to quick + leak interflow runoff store
        c_pr_eff_rain_to_sgw = 0.0  # no effective rainfall contribution to shallow groundwater flow runoff store
        c_pr_eff_rain_to_dgw = 0.0  # no effective rainfall contribution to deep groundwater flow runoff store

        deficit_rain = excess_rain * (-1.0)  # excess is negative => excess is actually a deficit
        aeva += rain
        for i in [1, 2, 3, 4, 5, 6]:  # attempt to satisfy PE from soil layers (from top layer [1] to bottom layer [6]
            if dict_lvl_lyr[i] >= deficit_rain:  # i.e. all moisture required available in this soil layer
                dict_lvl_lyr[i] -= deficit_rain  # soil layer is reduced by the moisture required
                aeva += deficit_rain  # this moisture contributes to the actual evapotranspiration
                deficit_rain = 0.0  # the full moisture still required has been met
            else:  # i.e. not all moisture required available in this soil layer
                aeva += dict_lvl_lyr[i]  # takes what is available in this layer for evapotranspiration
                # effectively reduce the evapotranspiration demand for the next layer using parameter C
                # i.e. the more you move down through the soil layers, the less AET can meet PET (exponentially)
                deficit_rain = c_p_c * (deficit_rain - dict_lvl_lyr[i])
                dict_lvl_lyr[i] = 0.0  # soil layer is now empty

    # calculate cumulative level of water in all soil layers at end of time step (i.e. soil moisture)
    lvl_total_end = 0.0
    for i in [1, 2, 3, 4, 5, 6]:
        lvl_total_end += dict_lvl_lyr[i]

    # /!\ all calculations in S.I. units now (i.e. mm converted into cubic metres)

    # calculate actual evapotranspiration as a flux
    c_out_aeva = aeva / 1e3 * area_m2 / time_gap_sec  # [m3/s]

    # route overland flow (quick surface runoff)
    c_out_q_h2o_ove = c_s_v_h2o_ove / c_p_sk  # [m3/s]
    c_s_v_h2o_ove += (c_pr_eff_rain_to_ove / 1e3 * area_m2) - (c_out_q_h2o_ove * time_gap_sec)  # [m3] - [m3]
    if c_s_v_h2o_ove < 0.0:
        logger.debug(''.join([
            'SMART # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
            ' - Volume in OVE Store has gone negative, volume reset to zero.']))
        c_s_v_h2o_ove = 0.0
    # route drain flow (quick interflow runoff)
    c_out_q_h2o_dra = c_s_v_h2o_dra / c_p_sk  # [m3/s]
    c_s_v_h2o_dra += (c_pr_eff_rain_to_dra / 1e3 * area_m2) - (c_out_q_h2o_dra * time_gap_sec)  # [m3] - [m3]
    if c_s_v_h2o_dra < 0.0:
        logger.debug(''.join([
            'SMART # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
            ' - Volume in DRA Store has gone negative, volume reset to zero.']))
        c_s_v_h2o_dra = 0.0
    # route interflow (slow interflow runoff)
    c_out_q_h2o_int = c_s_v_h2o_int / c_p_fk  # [m3/s]
    c_s_v_h2o_int += (c_pr_eff_rain_to_int / 1e3 * area_m2) - (c_out_q_h2o_int * time_gap_sec)  # [m3] - [m3]
    if c_s_v_h2o_int < 0.0:
        logger.debug(''.join([
            'SMART # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
            ' - Volume in INT Store has gone negative, volume reset to zero.']))
        c_s_v_h2o_int = 0.0
    # route shallow groundwater flow (slow shallow GW runoff)
    c_out_q_h2o_sgw = c_s_v_h2o_sgw / c_p_gk  # [m3/s]
    c_s_v_h2o_sgw += (c_pr_eff_rain_to_sgw / 1e3 * area_m2) - (c_out_q_h2o_sgw * time_gap_sec)  # [m3] - [m3]
    if c_s_v_h2o_sgw < 0.0:
        logger.debug(''.join([
            'SMART # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
            ' - Volume in SGW Store has gone negative, volume reset to zero.']))
        c_s_v_h2o_sgw = 0.0
    # route deep groundwater flow (slow deep GW runoff)
    c_out_q_h2o_dgw = c_s_v_h2o_dgw / c_p_gk  # [m3/s]
    c_s_v_h2o_dgw += (c_pr_eff_rain_to_dgw / 1e3 * area_m2) - (c_out_q_h2o_dgw * time_gap_sec)  # [m3] - [m3]
    if c_s_v_h2o_dgw < 0.0:
        logger.debug(''.join([
            'SMART # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
            ' - Volume in DGW Store has gone negative, volume reset to zero.']))
        c_s_v_h2o_dgw = 0.0

    # # 1.3. Returns outputs, updated states, and internal process variables
    return \
        c_out_aeva, c_out_q_h2o_ove, c_out_q_h2o_dra, c_out_q_h2o_int, c_out_q_h2o_sgw, c_out_q_h2o_dgw, \
        c_s_v_h2o_ove, c_s_v_h2o_dra, c_s_v_h2o_int, c_s_v_h2o_sgw, c_s_v_h2o_dgw, \
        dict_lvl_lyr[1] / 1e3 * area_m2, dict_lvl_lyr[2] / 1e3 * area_m2, dict_lvl_lyr[3] / 1e3 * area_m2, \
        dict_lvl_lyr[4] / 1e3 * area_m2, dict_lvl_lyr[5] / 1e3 * area_m2, dict_lvl_lyr[6] / 1e3 * area_m2, \
        c_pr_eff_rain_to_ove, c_pr_eff_rain_to_dra, c_pr_eff_rain_to_int, c_pr_eff_rain_to_sgw, c_pr_eff_rain_to_dgw


def get_in(waterbody, datetime_time_step, time_gap_min,
           dict_data_frame, dict_desc, dict_param, dict_meteo):
    """
    This function is the interface between the data models of the simulator and the model.
    It provides the inputs, parameters, processes, and states to the model.
    It also saves the inputs into the data frame.
    It can only return a tuple of scalar variables.
    """
    # bring in model constants
    area_m2 = dict_desc['area']
    time_gap_sec = time_gap_min * 60.0

    # bring in model inputs
    c_in_rain = dict_meteo[waterbody]['rain'][datetime_time_step]
    c_in_peva = dict_meteo[waterbody]['peva'][datetime_time_step]
    # store input in data frame
    dict_data_frame[waterbody][datetime_time_step]['c_in_rain'] = c_in_rain
    dict_data_frame[waterbody][datetime_time_step]['c_in_peva'] = c_in_peva

    # bring in model parameter values
    c_p_t = dict_param['c_p_t']
    c_p_c = dict_param['c_p_c']
    c_p_h = dict_param['c_p_h']
    c_p_d = dict_param['c_p_d']
    c_p_s = dict_param['c_p_s']
    c_p_z = dict_param['c_p_z']
    c_p_sk = dict_param['c_p_sk']
    c_p_fk = dict_param['c_p_fk']
    c_p_gk = dict_param['c_p_gk']

    # bring in model states
    c_s_v_h2o_ove = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ove']
    c_s_v_h2o_dra = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_dra']
    c_s_v_h2o_int = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_int']
    c_s_v_h2o_sgw = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_sgw']
    c_s_v_h2o_dgw = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_dgw']
    c_s_v_h2o_ly1 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly1']
    c_s_v_h2o_ly2 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly2']
    c_s_v_h2o_ly3 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly3']
    c_s_v_h2o_ly4 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly4']
    c_s_v_h2o_ly5 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly5']
    c_s_v_h2o_ly6 = \
        dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_s_v_h2o_ly6']

    # return constants, model inputs, model parameter values, and model states
    return \
        area_m2, time_gap_sec, \
        c_in_rain, c_in_peva, \
        c_p_t, c_p_c, c_p_h, c_p_d, c_p_s, c_p_z, c_p_sk, c_p_fk, c_p_gk, \
        c_s_v_h2o_ove, c_s_v_h2o_dra, c_s_v_h2o_int, c_s_v_h2o_sgw, c_s_v_h2o_dgw, \
        c_s_v_h2o_ly1, c_s_v_h2o_ly2, c_s_v_h2o_ly3, c_s_v_h2o_ly4, c_s_v_h2o_ly5, c_s_v_h2o_ly6


def get_out(waterbody, datetime_time_step, dict_data_frame,
            c_out_aeva, c_out_q_h2o_ove, c_out_q_h2o_dra, c_out_q_h2o_int, c_out_q_h2o_sgw, c_out_q_h2o_dgw,
            c_s_v_h2o_ove, c_s_v_h2o_dra, c_s_v_h2o_int, c_s_v_h2o_sgw, c_s_v_h2o_dgw,
            c_s_v_h2o_ly1, c_s_v_h2o_ly2, c_s_v_h2o_ly3, c_s_v_h2o_ly4, c_s_v_h2o_ly5, c_s_v_h2o_ly6,
            c_pr_eff_rain_to_ove, c_pr_eff_rain_to_dra, c_pr_eff_rain_to_int,
            c_pr_eff_rain_to_sgw, c_pr_eff_rain_to_dgw):
    """
    This function is the interface between the model and the data models of the simulator.
    It stores the outputs, updated states, and processed in the data frame.
    """
    # calculate total outflow (total runoff)
    c_out_q_h2o = c_out_q_h2o_ove + c_out_q_h2o_dra + c_out_q_h2o_int + c_out_q_h2o_sgw + c_out_q_h2o_dgw  # [m3/s]
    # store outputs in data frame
    dict_data_frame[waterbody][datetime_time_step]['c_out_aeva'] = c_out_aeva
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o_ove'] = c_out_q_h2o_ove
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o_dra'] = c_out_q_h2o_dra
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o_int'] = c_out_q_h2o_int
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o_sgw'] = c_out_q_h2o_sgw
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o_dgw'] = c_out_q_h2o_dgw
    dict_data_frame[waterbody][datetime_time_step]['c_out_q_h2o'] = c_out_q_h2o

    # store states in data frame
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ove'] = c_s_v_h2o_ove
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_dra'] = c_s_v_h2o_dra
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_int'] = c_s_v_h2o_int
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_sgw'] = c_s_v_h2o_sgw
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_dgw'] = c_s_v_h2o_dgw
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly1'] = c_s_v_h2o_ly1
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly2'] = c_s_v_h2o_ly2
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly3'] = c_s_v_h2o_ly3
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly4'] = c_s_v_h2o_ly4
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly5'] = c_s_v_h2o_ly5
    dict_data_frame[waterbody][datetime_time_step]['c_s_v_h2o_ly6'] = c_s_v_h2o_ly6

    # store process variables in data frame
    dict_data_frame[waterbody][datetime_time_step]['c_pr_eff_rain_to_ove'] = c_pr_eff_rain_to_ove
    dict_data_frame[waterbody][datetime_time_step]['c_pr_eff_rain_to_dra'] = c_pr_eff_rain_to_dra
    dict_data_frame[waterbody][datetime_time_step]['c_pr_eff_rain_to_int'] = c_pr_eff_rain_to_int
    dict_data_frame[waterbody][datetime_time_step]['c_pr_eff_rain_to_sgw'] = c_pr_eff_rain_to_sgw
    dict_data_frame[waterbody][datetime_time_step]['c_pr_eff_rain_to_dgw'] = c_pr_eff_rain_to_dgw


def infer_parameters(dict_desc):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for EPA Pathways Project by Dr. Eva Mockler
    (using equations available in CMT Fortran code by Prof. Michael Bruen and Dr. Eva Mockler).
    """
    my_dict_param = dict()

    # Parameter T: Rainfall aerial correction coefficient
    my_dict_param['c_p_t'] = 1.0  # set to 1 because rainfall value assumed to be best estimate if no calibration

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

    if my_dict_param['c_p_h'] < 0.0:
        my_dict_param['c_p_h'] = 0.0
    elif my_dict_param['c_p_h'] > 1.0:
        my_dict_param['c_p_h'] = 1.0

    # Parameter D: Drain flow parameter - fraction of saturation excess diverted to drain flow
    drain_eff_factor = 0.6
    my_dict_param['c_p_d'] = dict_desc['land_drain_ratio'] * drain_eff_factor

    if my_dict_param['c_p_d'] < 0.0:
        my_dict_param['c_p_d'] = 0.0
    elif my_dict_param['c_p_d'] > 1.0:
        my_dict_param['c_p_d'] = 1.0

    # Parameter S: Soil outflow coefficient
    my_dict_param['c_p_s'] = 8.61144e-14 * dict_desc['SAAR'] ** 3.207 * \
        dict_desc['AVG.SLOPE'] ** (-1.089) * \
        (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** (-3.765) * \
        (dict_desc['URBEXT'] ** 0.5 + 1.0) ** 17.515 * \
        (dict_desc['FOREST'] + 1.0) ** 9.544 * \
        (dict_desc['WellDrain'] + 1.0) ** 5.654 * \
        (dict_desc['HighP'] ** 0.5 + 1.0) ** (-6.206) * \
        ((dict_desc['Rkd'] + dict_desc['Lk']) + 1.0) ** 1.553 * \
        ((dict_desc['Lm'] + dict_desc['Rf']) + 1.0) ** 4.251 * \
        exp(dict_desc['Ll']) ** (-1.186)

    if my_dict_param['c_p_s'] < 0.0:
        my_dict_param['c_p_s'] = 0.0
    elif my_dict_param['c_p_s'] > 1.0:
        my_dict_param['c_p_s'] = 1.0

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

    return my_dict_param


def infer_parameters_thesis(dict_desc):
    """
    This function infers the value of the model parameters from catchment descriptors
    using regression relationships developed for EPA Pathways Project by Dr. Eva Mockler
    (using equations available in Eva Mockler's Ph.D. thesis).
    """
    my_dict_param = dict()

    # Parameter T: Rainfall aerial correction coefficient
    my_dict_param['c_p_t'] = 65.622 * dict_desc['SAAPE'] ** (-0.652) * \
        dict_desc['TAYSLO'] ** 0.003 * \
        (dict_desc['SlopeLow'] + 1.0) ** (-0.075) * \
        (dict_desc['Peat'] ** 0.5 + 1.0) ** (-0.221) * \
        (dict_desc['Made'] ** 0.5 + 1.0) ** (-0.481)

    # Parameter C: Evaporation decay parameter
    my_dict_param['c_p_c'] = 9.04064 * dict_desc['SAAR'] ** (-0.71009) * \
        dict_desc['Q.mm'] ** 0.57326 * \
        dict_desc['FLATWET'] ** (-0.75321) * \
        (dict_desc['AlluvMIN'] + 1.0) ** (-3.3778) * \
        (dict_desc['FOREST'] + 1.0) ** (-0.71328) * \
        ((dict_desc['Pu'] + dict_desc['Pl']) ** 0.5 + 1.0) ** 0.22084

    if my_dict_param['c_p_c'] < 0.1:
        my_dict_param['c_p_c'] = 0.1
    elif my_dict_param['c_p_c'] > 1.0:
        my_dict_param['c_p_c'] = 1.0

    # Parameter H: Quick runoff coefficient
    my_dict_param['c_p_h'] = 2.7886 * dict_desc['DRAIND'] ** 0.15655 * \
        dict_desc['WtdReCoMod'] ** 0.03626 * \
        (dict_desc['PoorDrain'] + 1.0) ** (-0.08069) * \
        (dict_desc['Water'] ** 0.25 + 1.0) ** 0.10238 * \
        (dict_desc['ModP'] + 1.0) ** (-0.14992) * \
        ((dict_desc['Rkc'] + dict_desc['Rk']) + 1.0) ** (-0.14598) * \
        ((dict_desc['Pu'] + dict_desc['Pl']) ** 0.5 + 1.0) ** (-0.17896) * \
        ((dict_desc['Lg'] + dict_desc['Rg']) ** 0.5 + 1.0) ** 0.22405

    if my_dict_param['c_p_h'] < 0.0:
        my_dict_param['c_p_h'] = 0.0
    elif my_dict_param['c_p_h'] > 1.0:
        my_dict_param['c_p_h'] = 1.0

    # Parameter D: Drain flow parameter - fraction of saturation excess diverted to drain flow
    drain_eff_factor = 0.8
    my_dict_param['c_p_d'] = dict_desc['land_drain_ratio'] * drain_eff_factor

    if my_dict_param['c_p_d'] < 0.0:
        my_dict_param['c_p_d'] = 0.0
    elif my_dict_param['c_p_d'] > 1.0:
        my_dict_param['c_p_d'] = 1.0

    # Parameter S: Soil outflow coefficient
    my_dict_param['c_p_s'] = 8.61144e-14 * dict_desc['SAAR'] ** 3.207 * \
        dict_desc['AVG.SLOPE'] ** (-1.089) * \
        (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** (-3.765) * \
        (dict_desc['URBEXT'] ** 0.5 + 1.0) ** 17.515 * \
        (dict_desc['FOREST'] + 1.0) ** 9.544 * \
        (dict_desc['WellDrain'] + 1.0) ** 5.654 * \
        (dict_desc['HighP'] ** 0.5 + 1.0) ** (-6.206) * \
        ((dict_desc['Rkd'] + dict_desc['Lk']) + 1.0) ** 1.553 * \
        ((dict_desc['Lm'] + dict_desc['Rf']) + 1.0) ** 4.251 * \
        exp(dict_desc['Ll']) ** (-1.186)

    if my_dict_param['c_p_s'] < 0.0:
        my_dict_param['c_p_s'] = 0.0
    elif my_dict_param['c_p_s'] > 1.0:
        my_dict_param['c_p_s'] = 1.0

    # Parameter Z: Effective soil depth (mm)
    my_dict_param['c_p_z'] = 9183325.942 * dict_desc['SAAR'] ** (-1.8501) * \
        dict_desc['DRAIND'] ** 0.6332 * \
        (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** 1.7288 * \
        dict_desc['FARL'] ** (-2.9124) * \
        (dict_desc['URBEXT'] ** 0.5 + 1.0) ** (-5.6337) * \
        (dict_desc['HighP'] ** 0.5 + 1.0) ** 3.0505 * \
        ((dict_desc['Lm'] + dict_desc['Rf']) + 1.0) ** (-2.1927) * \
        exp(dict_desc['Ll']) ** 0.5544

    # Parameter SK: Surface routing parameter (hours)
    my_dict_param['c_p_sk'] = 2.8e5 * (dict_desc['BFIsoil'] ** 2.0 + 1.0) ** 1.32 * \
        dict_desc['FARL'] ** (-8.366) * \
        dict_desc['SAAR'] ** (-1.24) * \
        (dict_desc['ARTDRAIN2'] + 1.0) ** (-0.529) * \
        (dict_desc['PoorDrain'] + 1.0) ** (-1.605)

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
        ((dict_desc['Rkc'] + dict_desc['Rk']) + 1.0) ** (-1.6107)

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

    return my_dict_param


def initialise_states(dict_desc, dict_param, kwa):
    """
    This function initialises the model states before starting the simulations.
    If a warm-up run is used, this initialisation happens before the start of the warm-up run.
    If no warm-up is used, this initialisation happens before the start of the actual simulation run.
    """
    area_m2 = dict_desc['area']

    my_dict = dict()

    try:  # try to make an educated guess
        my_dict.update({
            'c_s_v_h2o_ove':
                (kwa['aar'] * kwa['r-o_ratio']) * kwa['r-o_split'][0] / 1000 * area_m2 / 8766 * dict_param['c_p_sk'],
            'c_s_v_h2o_int':
                (kwa['aar'] * kwa['r-o_ratio']) * kwa['r-o_split'][1] / 1000 * area_m2 / 8766 * dict_param['c_p_fk'],
            'c_s_v_h2o_dra':
                (kwa['aar'] * kwa['r-o_ratio']) * kwa['r-o_split'][2] / 1000 * area_m2 / 8766 * dict_param['c_p_fk'],
            'c_s_v_h2o_sgw':
                (kwa['aar'] * kwa['r-o_ratio']) * kwa['r-o_split'][3] / 1000 * area_m2 / 8766 * dict_param['c_p_gk'],
            'c_s_v_h2o_dgw':
                (kwa['aar'] * kwa['r-o_ratio']) * kwa['r-o_split'][4] / 1000 * area_m2 / 8766 * dict_param['c_p_gk']
        })
    except KeyError:
        my_dict.update({
            'c_s_v_h2o_ove': 0.0,
            'c_s_v_h2o_int': 0.0,
            'c_s_v_h2o_dra': 0.0,
            'c_s_v_h2o_sgw': 0.0,
            'c_s_v_h2o_dgw': 0.0
        })

    my_dict.update({
        'c_s_v_h2o_ly1': (dict_param['c_p_z'] / 12) / 1000 * area_m2,
        'c_s_v_h2o_ly2': (dict_param['c_p_z'] / 12) / 1000 * area_m2,
        'c_s_v_h2o_ly3': (dict_param['c_p_z'] / 12) / 1000 * area_m2,
        'c_s_v_h2o_ly4': (dict_param['c_p_z'] / 12) / 1000 * area_m2,
        'c_s_v_h2o_ly5': (dict_param['c_p_z'] / 12) / 1000 * area_m2,
        'c_s_v_h2o_ly6': (dict_param['c_p_z'] / 12) / 1000 * area_m2
    })

    return my_dict
