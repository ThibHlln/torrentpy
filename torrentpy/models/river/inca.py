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
import os
import csv

from ..model import Model


class INCAr(Model):
    def __init__(self, category, identifier):
        Model.__init__(self, category, identifier)
        # set model variables names
        self.inputs_names = ['r_in_temp', 'r_in_c_no3', 'r_in_c_nh4', 'r_in_c_dph', 'r_in_c_pph', 'r_in_c_sed']
        self.parameters_names = ['r_p_att_no3', 'r_p_att_nh4', 'r_p_att_dph', 'r_p_att_pph', 'r_p_att_sed']
        self.states_names = ['r_s_m_no3', 'r_s_m_nh4', 'r_s_m_dph', 'r_s_m_pph', 'r_s_m_sed']
        self.constants_names = ['r_cst_c_dn', 'r_cst_c_ni', 'r_cst_flow_tolerance', 'r_cst_vol_tolerance']
        self.outputs_names = ['r_out_c_no3', 'r_out_c_nh4', 'r_out_c_dph', 'r_out_c_pph', 'r_out_c_sed']

    def set_constants(self, input_folder):
        self._set_constants_with_file(input_folder)

    def set_parameters(self, link, catchment, outlet, input_folder, output_folder):
        if os.path.isfile("{}{}_{}.{}.parameters".format(input_folder, catchment, outlet, self.identifier)):
            self._set_parameters_with_file(link, catchment, outlet, input_folder)
        else:
            self._infer_parameters(link, catchment, outlet, output_folder)

    def _infer_parameters(self, link, catchment, outlet, output_folder):

        dict_for_file = infer_parameters(link.descriptors)

        my_dict = dict(dict_for_file)
        dict_for_file['WaterBody'] = link.name

        if os.path.isfile('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                           self.identifier, self.category)):
            with open('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
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

        return initialise_states()

    def simulate(self, db, tf, step, link, logger):

        simulate(link.name, link.connections,
                 step, tf.simu_gap,
                 self.parameters, self.constants,
                 db.simulation, db.meteo,
                 logger)


def simulate(waterbody, connections,
             datetime_time_step, time_gap,
             dict_param, dict_const,
             dict_data_frame, dict_meteo,
             logger):

    inca_in = get_in(connections, waterbody, datetime_time_step, time_gap,
                     dict_data_frame, dict_param, dict_meteo, dict_const)

    inca_out = run(waterbody, datetime_time_step, logger, *inca_in)

    get_out(waterbody, datetime_time_step, dict_data_frame, *inca_out)


def run(waterbody, datetime_time_step, logger,
        time_gap_sec,
        r_in_temp,
        r_in_c_no3, r_in_c_nh4, r_in_c_dph, r_in_c_pph, r_in_c_sed,
        r_p_att_no3, r_p_att_nh4, r_p_att_dph, r_p_att_pph, r_p_att_sed,
        r_s_m_no3, r_s_m_nh4, r_s_m_dph, r_s_m_pph, r_s_m_sed,
        r_cst_c_dn, r_cst_c_ni, r_cst_flow_tolerance, r_cst_vol_tolerance,
        # inheritance from the hydrological model
        r_in_q_h2o, r_s_v_h2o_old, r_s_v_h2o, r_out_q_h2o):
    """
    River Constants
    _ time_gap_sec        time gap between two simulation time steps [seconds]

    River Model * r_ *
    _ Water Quality
    ___ Inputs * in_ *
    _____ r_in_temp       water temperature [degree celsius]
    _____ r_in_c_no3      nitrate concentration at inlet [kg/m3]
    _____ r_in_c_nh4      ammonia concentration at inlet [kg/m3]
    _____ r_in_c_dph      dissolved phosphorus concentration at inlet [kg/m3]
    _____ r_in_c_pph      particulate phosphorus concentration at inlet [kg/m3]
    _____ r_in_c_sed      sediment concentration at inlet [kg/m3]
    ___ Parameters * p_ *
    _____ r_p_att_no3     daily attenuation factor for nitrate [-]
    _____ r_p_att_nh4     daily attenuation factor for ammonia [-]
    _____ r_p_att_dph     daily attenuation factor for dissolved phosphorus [-]
    _____ r_p_att_pph     daily attenuation factor for particulate phosphorus [-]
    _____ r_p_att_sed     daily attenuation factor for sediment [-]
    ___ States * s_ *
    _____ r_s_m_no3       quantity of nitrate in store [kg]
    _____ r_s_m_nh4       quantity of ammonia in store [kg]
    _____ r_s_m_dph       quantity of dissolved phosphorus in store [kg]
    _____ r_s_m_pph       quantity of particulate phosphorus in store [kg]
    _____ r_s_m_sed       quantity of sediment in store [kg]
    ___ Constants * cst_ *
    _____ r_cst_c_dn      denitrification rate constant [-]
    _____ r_cst_c_ni      nitrification rate constant [-]
    _____ r_cst_flow_tolerance      minimum flow to consider equal to no flow [m3/s]
    _____ r_cst_vol_tolerance       minimum volume to consider equal to empty [m3]
    ___ Outputs * out_ *
    _____ r_out_c_no3     nitrate concentration at outlet [kg/m3]
    _____ r_out_c_nh4     ammonia concentration at outlet [kg/m3]
    _____ r_out_c_dph     dissolved phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_pph     particulate phosphorus concentration at outlet [kg/m3]
    _____ r_out_c_sed     sediment concentration at outlet [kg/m3]
    """

    # # 2. Water quality

    # # 2.1. Water quality calculations

    # check if inflow negligible, if so set all concentrations to zero
    if r_in_q_h2o < r_cst_flow_tolerance:
        logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                              ' - Inflow to River Store too low, inflow concentrations set to zero.']))
        r_in_c_no3 = 0.0
        r_in_c_nh4 = 0.0
        r_in_c_dph = 0.0
        r_in_c_pph = 0.0
        r_in_c_sed = 0.0
    # check if storage negligible, if so set all quantities to zero, all out concentrations to zero
    if r_s_v_h2o_old < r_cst_vol_tolerance:
        logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
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
        # # 2.1.1. Nitrate NO3
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
            ((r_in_c_no3 * r_in_q_h2o) - (concentration_no3 * r_out_q_h2o)) * time_gap_sec
        if r_s_m_no3 < 0.0:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - NO3 Quantity has gone negative in River Store, quantity reset to zero.']))
            r_s_m_no3 = 0.0
        # calculate outflow concentration
        if (r_s_v_h2o > r_cst_vol_tolerance) and (r_out_q_h2o > r_cst_flow_tolerance):
            r_out_c_no3 = r_s_m_no3 / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume/Flow in River Store too low, outflow NO3 concentration set to zero.']))
            r_out_c_no3 = 0.0

        # # 2.1.2. Ammonia NH4
        r_s_m_nh4_old = r_s_m_nh4
        # calculate concentration in store at beginning of time step
        concentration_nh4 = r_s_m_nh4_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_nh4 = r_s_m_nh4_old - rni + \
            ((r_in_c_nh4 * r_in_q_h2o) - (concentration_nh4 * r_out_q_h2o)) * time_gap_sec
        if r_s_m_nh4 < 0.0:
            r_s_m_nh4 = 0.0
        # calculate outflow concentration
        if (r_s_v_h2o > r_cst_vol_tolerance) and (r_out_q_h2o > r_cst_flow_tolerance):
            r_out_c_nh4 = r_s_m_nh4 / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume/Flow in River Store too low, outflow NH4 concentration set to zero.']))
            r_out_c_nh4 = 0.0

        # # 2.1.3. Dissolved phosphorus DPH
        r_s_m_dph_old = r_s_m_dph
        # calculate concentration in store at beginning of time step
        concentration_dph = r_s_m_dph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_dph = r_s_m_dph_old + ((r_in_c_dph * r_in_q_h2o) - (concentration_dph * r_out_q_h2o)) * time_gap_sec
        if r_s_m_dph < 0.0:
            r_s_m_dph = 0.0
        # apply attenuation factor to store
        r_s_m_dph = r_s_m_dph * r_p_att_dph
        # calculate outflow concentration
        if (r_s_v_h2o > r_cst_vol_tolerance) and (r_out_q_h2o > r_cst_flow_tolerance):
            r_out_c_dph = r_s_m_dph / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume/Flow in River Store too low, outflow DPH concentration set to zero.']))
            r_out_c_dph = 0.0

        # # 2.1.4. Particulate phosphorus PPH
        r_s_m_pph_old = r_s_m_pph
        # calculate concentration in store at beginning of time step
        concentration_pph = r_s_m_pph_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_pph = r_s_m_pph_old + ((r_in_c_pph * r_in_q_h2o) - (concentration_pph * r_out_q_h2o)) * time_gap_sec
        if r_s_m_pph < 0.0:
            r_s_m_pph = 0.0
        # apply attenuation factor to store
        r_s_m_pph = r_s_m_pph * r_p_att_pph
        # calculate outflow concentration
        if (r_s_v_h2o > r_cst_vol_tolerance) and (r_out_q_h2o > r_cst_flow_tolerance):
            r_out_c_pph = r_s_m_pph / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume/Flow in River Store too low, outflow PPH concentration set to zero.']))
            r_out_c_pph = 0.0

        # # 2.1.5. Sediments SED
        r_s_m_sed_old = r_s_m_sed
        # calculate concentration in store at beginning of time step
        concentration_sed = r_s_m_sed_old / r_s_v_h2o_old
        # update of amount in store
        r_s_m_sed = r_s_m_sed_old + ((r_in_c_sed * r_in_q_h2o) - (concentration_sed * r_out_q_h2o)) * time_gap_sec
        if r_s_m_sed < 0.0:
            r_s_m_sed = 0.0
        # apply attenuation factor to store
        r_s_m_sed = r_s_m_sed * r_p_att_sed
        # calculate outflow concentration
        if (r_s_v_h2o > r_cst_vol_tolerance) and (r_out_q_h2o > r_cst_flow_tolerance):
            r_out_c_sed = r_s_m_sed / r_s_v_h2o
        else:
            logger.debug(''.join(['INCAS # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume/Flow in River Store too low, outflow SED concentration set to zero.']))
            r_out_c_sed = 0.0

    # # 2.2. Return outputs and updated states
    return \
        r_out_c_no3, r_out_c_nh4, r_out_c_dph, r_out_c_pph, r_out_c_sed, \
        r_s_m_no3, r_s_m_nh4, r_s_m_dph, r_s_m_pph, r_s_m_sed


def get_in(connections, waterbody, datetime_time_step, time_gap_min,
           dict_data_frame, dict_param, dict_meteo, dict_const):
    """
    This function is the interface between the data models of the simulator and the model.
    It provides the inputs, parameters, processes, and states to the model.
    It also saves the inputs into the data frame.
    It can only return a tuple of scalar variables.
    """
    # find the node that is the input for the waterbody
    node_up = connections[1]

    # convert constants
    time_gap_sec = time_gap_min * 60.0

    # bring in water quality river model inputs
    r_in_temp = dict_meteo[waterbody]['airt'][datetime_time_step]
    r_in_c_no3 = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_no3']
    r_in_c_nh4 = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_nh4']
    r_in_c_dph = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_dph']
    r_in_c_pph = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_pph']
    r_in_c_sed = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['c_sed']
    # store water quality inputs in data frame
    dict_data_frame[waterbody][datetime_time_step]['r_in_temp'] = r_in_temp
    dict_data_frame[waterbody][datetime_time_step]['r_in_c_no3'] = r_in_c_no3
    dict_data_frame[waterbody][datetime_time_step]['r_in_c_nh4'] = r_in_c_nh4
    dict_data_frame[waterbody][datetime_time_step]['r_in_c_dph'] = r_in_c_dph
    dict_data_frame[waterbody][datetime_time_step]['r_in_c_pph'] = r_in_c_pph
    dict_data_frame[waterbody][datetime_time_step]['r_in_c_sed'] = r_in_c_sed

    # bring in water quality river model parameters
    r_p_att_no3 = dict_param['r_p_att_no3']
    r_p_att_nh4 = dict_param['r_p_att_nh4']
    r_p_att_dph = dict_param['r_p_att_dph']
    r_p_att_pph = dict_param['r_p_att_pph']
    r_p_att_sed = dict_param['r_p_att_sed']

    # bring in water quality river model states
    r_s_m_no3 = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_m_no3']
    r_s_m_nh4 = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_m_nh4']
    r_s_m_dph = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_m_dph']
    r_s_m_pph = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_m_pph']
    r_s_m_sed = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_m_sed']

    # bring in water quality river model constants
    r_cst_c_dn = dict_const['r_cst_c_dn']
    r_cst_c_ni = dict_const['r_cst_c_ni']
    r_cst_flow_tolerance = dict_const['r_cst_flow_tolerance']
    r_cst_vol_tolerance = dict_const['r_cst_vol_tolerance']

    # bring in variables originating from the hydrological model
    r_in_q_h2o = dict_data_frame[waterbody][datetime_time_step]['r_in_q_h2o']
    r_s_v_h2o_old = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_v_h2o']
    r_s_v_h2o = dict_data_frame[waterbody][datetime_time_step]['r_s_v_h2o']
    r_out_q_h2o = dict_data_frame[waterbody][datetime_time_step]['r_out_q_h2o']

    # return constants, model inputs, model parameter values, model states, and model constants + hydrology inheritance
    return \
        time_gap_sec, \
        r_in_temp, \
        r_in_c_no3, r_in_c_nh4, r_in_c_dph, r_in_c_pph, r_in_c_sed, \
        r_p_att_no3, r_p_att_nh4, r_p_att_dph, r_p_att_pph, r_p_att_sed, \
        r_s_m_no3, r_s_m_nh4, r_s_m_dph, r_s_m_pph, r_s_m_sed, \
        r_cst_c_dn, r_cst_c_ni, r_cst_flow_tolerance, r_cst_vol_tolerance, \
        r_in_q_h2o, r_s_v_h2o_old, r_s_v_h2o, r_out_q_h2o


def get_out(waterbody, datetime_time_step, dict_data_frame,
            r_out_c_no3, r_out_c_nh4, r_out_c_dph, r_out_c_pph, r_out_c_sed,
            r_s_m_no3, r_s_m_nh4, r_s_m_dph, r_s_m_pph, r_s_m_sed
            ):
    """
    This function is the interface between the model and the data models of the simulator.
    It stores the outputs, and updated states in the data frame.
    """
    # store water quality river model outputs in data frame
    dict_data_frame[waterbody][datetime_time_step]['r_out_c_no3'] = r_out_c_no3
    dict_data_frame[waterbody][datetime_time_step]['r_out_c_nh4'] = r_out_c_nh4
    dict_data_frame[waterbody][datetime_time_step]['r_out_c_dph'] = r_out_c_dph
    dict_data_frame[waterbody][datetime_time_step]['r_out_c_pph'] = r_out_c_pph
    dict_data_frame[waterbody][datetime_time_step]['r_out_c_sed'] = r_out_c_sed

    # store water quality river model states in data frame
    dict_data_frame[waterbody][datetime_time_step]['r_s_m_no3'] = r_s_m_no3
    dict_data_frame[waterbody][datetime_time_step]['r_s_m_nh4'] = r_s_m_nh4
    dict_data_frame[waterbody][datetime_time_step]['r_s_m_dph'] = r_s_m_dph
    dict_data_frame[waterbody][datetime_time_step]['r_s_m_pph'] = r_s_m_pph
    dict_data_frame[waterbody][datetime_time_step]['r_s_m_sed'] = r_s_m_sed


def infer_parameters(dict_desc):
    """
    This function uses the parameter values customised for Irish conditions in the EPA Pathways Project
    by Dr. Mesfin Desta and Dr. Eva Mockler, adapated from the values originally used in the INCA model for the UK
    (using values available in CMT Fortran code by Prof. Michael Bruen and Dr. Eva Mockler).
    """
    my_dict_param = dict()
    # INCA STREAM MODEL
    # linear reservoir attenuation
    my_dict_param['r_p_att_no3'] = 0.9
    my_dict_param['r_p_att_nh4'] = 0.9
    my_dict_param['r_p_att_dph'] = 0.9
    my_dict_param['r_p_att_pph'] = 1.0
    my_dict_param['r_p_att_sed'] = 1.0

    return my_dict_param


def initialise_states():
    """
    This function initialises the model states before starting the simulations.
    If a warm-up run is used, this initialisation happens before the start of the warm-up run.
    If no warm-up is used, this initialisation happens before the start of the actual simulation run.
    """
    # currently states are not initialised, but a warm-up run can be used to start with states not null
    return {}
