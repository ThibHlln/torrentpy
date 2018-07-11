# -*- coding: utf-8 -*-

# This file is part of TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork
# Copyright (C) 2018  Thibault Hallouin (1)
#
# (1) Dooge Centre for Water Resources Research, University College Dublin, Ireland
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

from builtins import range
from datetime import timedelta
from fractions import gcd
from math import ceil
from logging import getLogger


class TimeFrame(object):
    """
    This class gathers the temporal information provided by the user. Then, it defines the temporal attributes
    of the simulator.

    Three type of temporal attributes are considered: 'data' refers to the input to the simulator
    (e.g. meteorological variables in input files), 'simu' refers to the internal time used by the models (i.e.
    model temporal discretisation), and 'save' refers to the output from the simulator (i.e. what will be written in the
    output files).

    For each type, three attributes (start, end, gap) are required to build timeseries. Then each timeseries will
    broken down into slices (to avoid flash memory limitations).

    In terms of starts/ends, the user is only required to provide them for 'data' and for 'save', start/end for 'simu'
    are inferred using 'save' start/end/gap and the 'simu' gap.

    In terms of timeseries, 'simu' and 'save' timeseries are built using their respective start/end/gap, however,
    the 'simu' timeseries will only be built if the data period specified provides enough information. For 'data',
    only a timeseries of needed_data is provided (i.e. a the minimum timeseries of data required to cover the 'simu'
    period). This is to avoid storing in flash memory an unnecessary long timeseries if 'simu' period is significantly
    shorter than 'data' period.
    To allow for initial conditions to be set up, one or more time steps are added prior the respective starts of
    'simu' and 'save'. The 'save' time is added one datetime before save_start, while the 'simu' is added one or more
    datetime if it requires several simu_gap to cover one data_gap.

    N.B. The 'save' gap is required to be a multiple of 'simu' gap because this simulator is not intended to
    interpolate on the simulation results, the simulator can only extract or summarise from simulation steps.
    Instead, the user is expected to adapt their simulation gap to match the required reporting gap.
    """
    def __init__(self, dt_data_start, dt_data_end, dt_save_start, dt_save_end,
                 data_increment_in_minutes, save_increment_in_minutes, simu_increment_in_minutes,
                 expected_simu_slice_length, warm_up_in_days=0):

        # Time Attributes for Input Data (Read in Files)
        self.data_start = dt_data_start  # DateTime
        self.data_end = dt_data_end  # DateTime
        self.data_gap = data_increment_in_minutes  # Int [minutes]

        # Time Attributed for Output Data (Save/Write in Files)
        self.save_start = dt_save_start  # DateTime
        self.save_end = dt_save_end  # DateTime
        self.save_gap = save_increment_in_minutes  # Int [minutes]

        # Time Attributes for Simulation (Internal to the Simulator)
        self.simu_gap = simu_increment_in_minutes  # Int [minutes]
        self.simu_start_earliest, self.simu_end_latest = \
            TimeFrame._get_most_possible_extreme_simu_start_end(self)  # DateTime, DateTime
        self.simu_start, self.simu_end = \
            TimeFrame._get_simu_start_end_given_save_start_end(self)  # DateTime, DateTime

        # Time Attributes Only for Input Data Needed given Simulation Period
        self.data_needed_start, self.data_needed_end = \
            TimeFrame._get_data_start_end_given_simu_start_end(self)

        # DateTime Series for Data, Save, and Simulation
        self.needed_data_series = TimeFrame._get_list_data_needed_dt_without_initial_conditions(self)
        self.save_series = TimeFrame._get_list_save_dt_with_initial_conditions(self)
        self.simu_series = TimeFrame._get_list_simu_dt_with_initial_conditions(self)

        # Slices of DateTime Series for Save and Simulation
        self.save_slices, self.simu_slices = \
            TimeFrame._slice_datetime_series(self, expected_simu_slice_length)

        # Another instance of a TimeFrame if warm-up is required
        self.warm_up = None
        if not warm_up_in_days == 0:
            self.warm_up = TimeFrame(dt_data_start, dt_data_end, dt_save_start, dt_save_start +
                                     timedelta(days=warm_up_in_days) - timedelta(minutes=save_increment_in_minutes),
                                     data_increment_in_minutes, save_increment_in_minutes, simu_increment_in_minutes,
                                     expected_simu_slice_length)

    def _get_most_possible_extreme_simu_start_end(self):
        logger = getLogger('TORRENTpy.tf')

        # check whether data period makes sense on its own
        if not self.data_start <= self.data_end:
            logger.error("Data Start is greater than Data End.")
            raise Exception("Data Start is greater than Data End.")

        # determine the maximum possible simulation period given the period of data availability
        simu_start_earliest = self.data_start - timedelta(minutes=self.data_gap) + timedelta(minutes=self.simu_gap)
        simu_end_latest = self.data_end

        return simu_start_earliest, simu_end_latest

    def _get_simu_start_end_given_save_start_end(self):
        logger = getLogger('TORRENTpy.tf')

        # check whether saving/reporting period makes sense on its own
        if not self.save_start <= self.save_end:
            logger.error("Save Start is greater than Save End.")
            raise Exception("Save Start is greater than Save End.")

        # check whether the simulation time gap will allow to report on the saving/reporting time gap
        if not self.save_gap % self.simu_gap == 0:
            logger.error("Save Gap is not greater and a multiple of Simulation Gap.")
            raise Exception("Save Gap is not greater and a multiple of Simulation Gap.")

        # determine the simulation period required to cover the whole saving/reporting period
        simu_start = self.save_start - timedelta(minutes=self.save_gap) + timedelta(minutes=self.simu_gap)
        simu_end = self.save_end

        # check if simu_start/simu_end period is contained in simu_start_earlier/simu_end_latest (i.e. available data)
        if not ((self.simu_start_earliest <= simu_start) and (simu_end <= self.simu_end_latest)):
            logger.error("Input Data Period is insufficient to cover Save Period.")
            raise Exception("Input Data Period is insufficient to cover Save Period.")

        return simu_start, simu_end

    def _get_data_start_end_given_simu_start_end(self):
        logger = getLogger('TORRENTpy.tf')

        # check if Data Period is a multiple of Data Time Gap
        if not (self.data_end - self.data_start).total_seconds() % \
                timedelta(minutes=self.data_gap).total_seconds() == 0:
            logger.error("Data Period does not contain a whole number of Data Time Gaps.")
            raise Exception("Data Period does not contain a whole number of Data Time Gaps.")

        # increment from data_start until simu_start is just covered
        data_start_for_simu = self.data_start
        while data_start_for_simu < self.simu_start:
            data_start_for_simu += timedelta(minutes=self.data_gap)

        # decrement from data_end until end_start is just covered
        data_end_for_simu = self.data_end
        while data_end_for_simu >= self.simu_end:
            data_end_for_simu -= timedelta(minutes=self.data_gap)
        data_end_for_simu += timedelta(minutes=self.data_gap)

        return data_start_for_simu, data_end_for_simu

    def _get_list_data_needed_dt_without_initial_conditions(self):

        # generate a list of DateTime for Data Period without initial conditions (not required)
        my_list_datetime = list()
        my_dt = self.data_needed_start
        while my_dt <= self.data_needed_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.data_gap)

        return my_list_datetime

    def _get_list_save_dt_with_initial_conditions(self):

        # generate a list of DateTime for Saving/Reporting Period with one extra prior step for initial conditions
        my_list_datetime = list()
        my_dt = self.save_start - timedelta(minutes=self.save_gap)
        while my_dt <= self.save_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.save_gap)

        return my_list_datetime

    def _get_list_simu_dt_with_initial_conditions(self):

        # generate a list of DateTime for Simulation Period with one extra prior step for initial conditions
        my_list_datetime = list()
        my_dt = self.simu_start - timedelta(minutes=self.simu_gap)
        while my_dt <= self.simu_end:
            my_list_datetime.append(my_dt)
            my_dt += timedelta(minutes=self.simu_gap)

        return my_list_datetime

    def _slice_datetime_series(self, expected_length):
        logger = getLogger('TORRENTpy.tf')

        my_save_slices = list()
        my_simu_slices = list()

        if expected_length > 0:  # i.e. a slice length has been specified and is greater than 0
            if not (expected_length * self.simu_gap) >= self.save_gap:
                logger.error("Expected Length for Slicing Up is smaller than the Saving Time Gap.")
                raise Exception("Expected Length for Slicing Up is smaller than the Saving Time Gap.")

            # Adjust the length to make sure that it slices exactly between two saving/reporting steps
            simu_slice_length = (expected_length * self.simu_gap) // self.save_gap * self.save_gap // self.simu_gap
            save_slice_length = simu_slice_length * self.simu_gap // self.save_gap

            if simu_slice_length > 0:  # the expected length is longer than one saving/reporting time gap
                stop_index = int(ceil(float(len(self.save_series)) / float(save_slice_length)))
                for i in range(0, stop_index, 1):
                    start_index = i * save_slice_length
                    end_index = ((i + 1) * save_slice_length) + 1
                    if len(self.save_series[start_index:end_index]) > 1:  # it would only be the initial conditions
                        my_save_slices.append(self.save_series[start_index:end_index])
                stop_index = int(ceil(float(len(self.simu_series)) / float(simu_slice_length)))
                for i in range(0, stop_index, 1):
                    start_index = i * simu_slice_length
                    end_index = ((i + 1) * simu_slice_length) + 1
                    if len(self.simu_series[start_index:end_index]) > 1:  # it would only be the initial conditions
                        my_simu_slices.append(self.simu_series[start_index:end_index])
            else:  # no need to slice, return the complete original lists (i.e. one slice for each)
                my_save_slices.append(self.save_series[:])
                my_simu_slices.append(self.simu_series[:])
        else:  # i.e. a slice length has not been specified or is equal to 0
            my_save_slices.append(self.save_series[:])
            my_simu_slices.append(self.simu_series[:])

        return my_save_slices, my_simu_slices


def get_required_resolution(start_data, start_simu, delta_data, delta_simu):
    # GCD(delta_data, delta_simu) gives the maximum time resolution possible to match data and simu
    # shift = start_data - start_simu gives the data shift (e.g. data starting at 8am, simu starting at 9am)
    # GCD(shift, GCD(delta_data, delta_simu)) gives the maximum time resolution to match both the difference in
    # start dates and the difference in data/simu time deltas.
    return timedelta(seconds=gcd((start_data - start_simu).total_seconds(),
                                 gcd(delta_data.total_seconds(), delta_simu.total_seconds())))


def check_interval_in_list(list_of_dt, data_file):
    logger = getLogger('TORRENTpy.tf')

    list_intervals = list()
    for i in range(len(list_of_dt) - 1):
        list_intervals.append(list_of_dt[i+1] - list_of_dt[i])
    interval = list(set(list_intervals))
    if len(interval) == 1:
        if list_of_dt[0] + interval[0] * (len(list_of_dt) - 1) == list_of_dt[-1]:
            return list_of_dt[0], list_of_dt[-1], interval[0]
        else:
            logger.error("Missing Data: {} is missing at least one datetime in period.".format(data_file))
            raise Exception("Missing Data: {} is missing at least one datetime in period.".format(data_file))
    else:
        logger.error("Inconsistent Interval: {} does not feature a single time interval.".format(data_file))
        raise Exception("Inconsistent Interval: {} does not feature a single time interval.".format(data_file))


def rescale_time_resolution_of_regular_cumulative_data(dict_data,
                                                       start_data, end_data, time_delta_data,
                                                       time_delta_res,
                                                       start_simu, end_simu, time_delta_simu):

    if time_delta_data > time_delta_res:  # i.e. information resolution too low to generate simu timeseries
        my_tmp_dict = increase_time_resolution_of_regular_cumulative_data(dict_data, start_data, end_data,
                                                                          time_delta_data, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_data == time_delta_res (time_delta_data < time_delta_res cannot be true because use of GCD)
        my_tmp_dict = dict_data

    if time_delta_simu > time_delta_res:  # i.e. information resolution too high to generate simu timeseries
        my_new_dict = decrease_time_resolution_of_regular_cumulative_data(my_tmp_dict, start_simu, end_simu,
                                                                          time_delta_simu, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_simu == time_delta_res (time_delta_simu < time_delta_res cannot be true because use of GCD)
        my_new_dict = decrease_time_resolution_of_regular_cumulative_data(my_tmp_dict, start_simu, end_simu,
                                                                          time_delta_simu, time_delta_res)
        # use decrease_data_time_resolution anyway for the only purpose to reduce the size of the dict
        # to the only required DateTimes in the simulation period

    return my_new_dict


def increase_time_resolution_of_regular_cumulative_data(dict_info, start_lo, end_lo,
                                                        time_delta_lo, time_delta_hi):
    """ Use the low resolution to create the high resolution """
    logger = getLogger('TORRENTpy.tf')

    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        logger.error("Increase Resolution: Time Deltas are not multiples of each other.")
        raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        logger.error("Increase Resolution: Low resolution lower than higher resolution "
                     "{} < {}.".format(time_delta_lo, time_delta_hi))
        raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_value = dict_info[my_dt_lo]
        my_portion = my_value / divisor
        for my_sub_step in range(0, -divisor, -1):
            new_dict_info[my_dt_lo + my_sub_step * time_delta_hi] = my_portion
        my_dt_lo += time_delta_lo

    return new_dict_info


def decrease_time_resolution_of_regular_cumulative_data(dict_info, start_lo, end_lo,
                                                        time_delta_lo, time_delta_hi):
    """ Use the high resolution to create the low resolution """
    logger = getLogger('TORRENTpy.tf')
    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        logger.error("Decrease Resolution: Time Deltas are not multiples of each other.")
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        logger.error("Decrease Resolution: Low resolution lower than higher resolution "
                     "{} < {}.".format(time_delta_lo, time_delta_hi))
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_portion = 0.0
        for my_sub_step in range(0, -divisor, -1):
            my_portion += dict_info[my_dt_lo + my_sub_step * time_delta_hi]
        new_dict_info[my_dt_lo] = my_portion
        my_dt_lo += time_delta_lo

    return new_dict_info


def rescale_time_resolution_of_regular_mean_data(dict_data,
                                                 start_data, end_data, time_delta_data,
                                                 time_delta_res,
                                                 start_simu, end_simu, time_delta_simu):

    if time_delta_data > time_delta_res:  # i.e. information resolution too low to generate simu timeseries
        my_tmp_dict = increase_time_resolution_of_regular_mean_data(dict_data, start_data, end_data,
                                                                    time_delta_data, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_data == time_delta_res (time_delta_data < time_delta_res cannot be true because use of GCD)
        my_tmp_dict = dict_data

    if time_delta_simu > time_delta_res:  # i.e. information resolution too high to generate simu timeseries
        my_new_dict = decrease_time_resolution_of_regular_mean_data(my_tmp_dict, start_simu, end_simu,
                                                                    time_delta_simu, time_delta_res)
    else:  # i.e. information resolution suitable to generate simu timeseries
        # i.e. time_delta_simu == time_delta_res (time_delta_simu < time_delta_res cannot be true because use of GCD)
        my_new_dict = decrease_time_resolution_of_regular_mean_data(my_tmp_dict, start_simu, end_simu,
                                                                    time_delta_simu, time_delta_res)
        # use decrease_data_time_resolution anyway for the only purpose to reduce the size of the dict
        # to the only required DateTimes in the simulation period

    return my_new_dict


def increase_time_resolution_of_regular_mean_data(dict_info, start_lo, end_lo,
                                                  time_delta_lo, time_delta_hi):
    """ Use the low resolution to create the high resolution """
    logger = getLogger('TORRENTpy.tf')

    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        logger.error("Increase Resolution: Time Deltas are not multiples of each other.")
        raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        logger.error("Increase Resolution: Low resolution lower than higher resolution "
                     "{} < {}.".format(time_delta_lo, time_delta_hi))
        raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_value = dict_info[my_dt_lo]
        for my_sub_step in range(0, -divisor, -1):
            new_dict_info[my_dt_lo + my_sub_step * time_delta_hi] = my_value
        my_dt_lo += time_delta_lo

    return new_dict_info


def decrease_time_resolution_of_regular_mean_data(dict_info, start_lo, end_lo,
                                                  time_delta_lo, time_delta_hi):
    """ Use the high resolution to create the low resolution """
    logger = getLogger('TORRENTpy.tf')

    my_dt_lo = start_lo
    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        logger.error("Decrease Resolution: Time Deltas are not multiples of each other.")
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        logger.error("Decrease Resolution: Low resolution lower than higher resolution "
                     "{} < {}.".format(time_delta_lo, time_delta_hi))
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    new_dict_info = dict()
    while (start_lo <= my_dt_lo) and (my_dt_lo <= end_lo):
        my_values = 0.0
        for my_sub_step in range(0, -divisor, -1):
            my_values += dict_info[my_dt_lo + my_sub_step * time_delta_hi]
        new_dict_info[my_dt_lo] = my_values / divisor
        my_dt_lo += time_delta_lo

    return new_dict_info
