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

try:
    import smartcpp
    smart_in_cpp = True
except ImportError:
    smartcpp = None
    smart_in_cpp = False

from ..model import Model
from ...inout import open_csv_wb, open_csv_ab


class SMARTr(Model):
    def __init__(self, category, identifier):
        Model.__init__(self, category, identifier)
        # set model variables names
        self.inputs_names = ['r_in_q_h2o']
        self.parameters_names = ['r_p_rk']
        self.states_names = ['r_s_v_h2o']
        self.outputs_names = ['r_out_q_h2o']

    def set_constants(self, input_folder):
        self._set_constants_with_file(input_folder)

    def set_parameters(self, link, catchment, outlet, input_folder, output_folder):
        if os.path.isfile('{}{}_{}.{}{}.parameters'.format(
                input_folder, catchment, outlet, self.identifier, self.category)):
            self._set_parameters_with_file(link, catchment, outlet, input_folder)
        else:
            self._infer_parameters(link, catchment, outlet, output_folder)

    def _infer_parameters(self, link, catchment, outlet, output_folder):

        dict_for_file = self._infer_parameters_from_descriptors(link.descriptors)

        my_dict = dict(dict_for_file)
        dict_for_file['WaterBody'] = link.name

        if os.path.isfile('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                           self.identifier, self.category)):
            with open_csv_ab('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                              self.identifier, self.category)) as my_file:
                header = ['WaterBody'] + self.parameters_names
                my_writer = csv.DictWriter(my_file, fieldnames=header)
                my_writer.writerow(dict_for_file)
        else:
            with open_csv_wb('{}{}_{}.{}{}.parameters'.format(output_folder, catchment, outlet,
                                                              self.identifier, self.category)) as my_file:
                header = ['WaterBody'] + self.parameters_names
                my_writer = csv.DictWriter(my_file, fieldnames=header)
                my_writer.writeheader()
                my_writer.writerow(dict_for_file)

        self.parameters = my_dict
        link.models_parameters.update(my_dict)

    def initialise(self, link):

        return self._initialise_states(link.descriptors, self.parameters, link.extra)

    def simulate(self, db, tf, step, link, logger):

        self._simulate(link.name, link.connections,
                       step, tf.simu_gap,
                       self.parameters,
                       db.simulation,
                       logger)

    def _simulate(self, waterbody, connections,
                  datetime_time_step, time_gap,
                  dict_param,
                  dict_data_frame,
                  logger):

        smart_in = self._get_in(connections, waterbody, datetime_time_step, time_gap,
                                dict_data_frame, dict_param)

        if smart_in_cpp:
            smart_out = smartcpp.onestep_r(*smart_in)
        else:
            smart_out = self._run(waterbody, datetime_time_step, logger, *smart_in)

        self._get_out(waterbody, datetime_time_step, dict_data_frame, *smart_out)

    @staticmethod
    def _run(waterbody, datetime_time_step, logger,
             time_gap_sec,
             r_in_q_h2o, r_p_rk, r_s_v_h2o):
        """
        This function was written by Thibault Hallouin but is largely inspired by the work of Eva Mockler, namely for
        the work published in: Mockler, E., O’Loughlin, F., and Bruen, M.: Understanding hydrological flow paths in
        conceptual catchment models using uncertainty and sensitivity analysis, Computers & Geosciences, 90, 66–77,
        doi:10.1016/j.cageo.2015.08.015, 2016.

        River Constants
        _ time_gap_sec        time gap between two simulation time steps [seconds]

        River Model * r_ *
        _ Hydrology
        ___ Inputs * in_ *
        _____ r_in_q_h2o      flow at inlet [m3/s]
        ___ Parameters * p_ *
        _____ r_p_rk          linear factor k for water where Storage = k.Flow [hours]
        ___ States * s_ *
        _____ r_s_v_h2o       volume of water in store [m3]
        ___ Outputs * out_ *
        _____ r_out_q_h2o     flow at outlet [m3/s]
        """
        # # 1. Hydrology

        # # 1.1. Unit conversions
        r_p_rk *= 3600.0  # convert hours into seconds

        # # 1.2. Hydrological calculations

        # calculate outflow, at current time step
        r_out_q_h2o = r_s_v_h2o / r_p_rk
        # calculate storage in temporary variable, for next time step
        r_s_v_h2o_old = r_s_v_h2o
        r_s_v_h2o_temp = r_s_v_h2o_old + (r_in_q_h2o - r_out_q_h2o) * time_gap_sec
        # check if storage has gone negative
        if r_s_v_h2o_temp < 0.0:  # temporary cannot be used
            logger.debug(''.join(['LINRES # ', waterbody, ': ', datetime_time_step.strftime('%d/%m/%Y %H:%M:%S'),
                                  ' - Volume in River Store has gone negative, '
                                  'outflow constrained to 95% of what is in store.']))
            # constrain outflow: allow maximum outflow at 95% of what was in store
            r_out_q_h2o = 0.95 * (r_in_q_h2o + r_s_v_h2o_old / time_gap_sec)
            # calculate final storage with constrained outflow
            r_s_v_h2o += (r_in_q_h2o - r_out_q_h2o) * time_gap_sec
        else:
            r_s_v_h2o = r_s_v_h2o_temp  # temporary storage becomes final storage

        # # 1.3. Return outputs and updated states
        return \
            r_out_q_h2o, r_s_v_h2o

    @staticmethod
    def _get_in(connections, waterbody, datetime_time_step, time_gap_min,
                dict_data_frame, dict_param):
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

        # bring in model inputs
        r_in_q_h2o = dict_data_frame[node_up][datetime_time_step + timedelta(minutes=-time_gap_min)]['q_h2o']
        # store input in data frame
        dict_data_frame[waterbody][datetime_time_step]['r_in_q_h2o'] = r_in_q_h2o

        # bring in model parameter values
        r_p_rk = dict_param['r_p_rk']

        # bring in model states
        r_s_v_h2o = dict_data_frame[waterbody][datetime_time_step + timedelta(minutes=-time_gap_min)]['r_s_v_h2o']

        # return constants, model inputs, model parameter values, and model states
        return \
            time_gap_sec, \
            r_in_q_h2o, r_p_rk, r_s_v_h2o

    @staticmethod
    def _get_out(waterbody, datetime_time_step, dict_data_frame,
                 r_out_q_h2o, r_s_v_h2o):
        """
        This function is the interface between the model and the data models of the simulator.
        It stores the outputs, and updated states in the data frame.
        """
        # store outputs in data frame
        dict_data_frame[waterbody][datetime_time_step]['r_out_q_h2o'] = r_out_q_h2o
        # store states in data frame
        dict_data_frame[waterbody][datetime_time_step]['r_s_v_h2o'] = r_s_v_h2o

    @staticmethod
    def _infer_parameters_from_descriptors(dict_desc):
        """
        This function infers the value of the model parameters from catchment descriptors
        using regression relationships developed for EPA Pathways Project by Dr. Eva Mockler
        (using equations available in CMT Fortran code by Prof. Michael Bruen and Dr. Eva Mockler).
        """
        my_dict_param = dict()
        # Parameter RK: River routing parameter (hours)
        lgth = dict_desc['stream_length']
        rk = lgth / 1.0  # i.e. assuming a water velocity of 1 m/s
        rk /= 3600.0  # convert seconds into hours
        my_dict_param['r_p_rk'] = rk

        return my_dict_param

    @staticmethod
    def _initialise_states(dict_desc, dict_param, kwa):
        """
        This function initialises the model states before starting the simulations.
        If a warm-up run is used, this initialisation happens before the start of the warm-up run.
        If no warm-up is used, this initialisation happens before the start of the actual simulation run.
        """
        area_m2 = dict_desc['area']

        my_dict = dict()
        try:
            my_dict.update({
                'r_s_v_h2o': (kwa['aar'] * kwa['r-o_ratio']) / 1000 * area_m2 / 8766 * dict_param['r_p_rk']
            })
        except KeyError:
            my_dict.update({
                'r_s_v_h2o': 0.0
            })

        return my_dict
