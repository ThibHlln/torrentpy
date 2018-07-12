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

from logging import getLogger
from csv import DictReader

from ..inout import open_csv_rb


class Model(object):
    def __init__(self, category, identifier):
        # category of the Model (catchment, river, or lake)
        self.category = category
        # name of the Model within the category
        self.identifier = identifier
        # list of the names for the inputs of the Model
        self.inputs_names = list()
        # list of the names for the parameters of the Model
        self.parameters_names = list()
        # list of the names for the constants of the Model
        self.constants_names = list()
        # list of the names for the states of the Model
        self.states_names = list()
        # list of the names for the processes of the Model
        self.processes_names = list()
        # list of the names for the outputs of the Model
        self.outputs_names = list()
        # dict of values for the parameters of the Model
        self.parameters = None
        # dict of values for the constants of the Model
        self.constants = None
        # reference to the Link object it works on
        self.link = None

    def _set_constants_with_file(self, input_folder):
        """
        This method get the list of the names for the constants of the Model in its specification file in the
        specifications folder. Then, the methods reads the constants values in the constant file for the Model located
        in the specifications folder.

        :param input_folder: path to the input folder where to find the constants file
        :return: dictionary containing the constants names and values
            {key: constant_name, value: constant_value}
        """
        logger = getLogger('TORRENTpy.md')
        if self.constants_names:
            try:
                my_dict = dict()
                with open_csv_rb('{}{}.constants'.format(input_folder, self.identifier)) as my_file:
                    my_reader = DictReader(my_file)
                    for row in my_reader:
                        try:
                            if row['ConstantName'] in self.constants_names:
                                try:
                                    my_dict[row['ConstantName']] = float(row['ConstantValue'])
                                except KeyError:
                                    logger.error(
                                        "The column header 'ConstantValue' is not present in the constants file.")
                                    raise Exception(
                                        "The column header 'ConstantValue' is not present in the constants file.")
                        except KeyError:
                            logger.error("The column header 'ConstantName' is not present in the constants file.")
                            raise Exception("The column header 'ConstantName' is not present in the constants file.")
                    for name in self.constants_names:
                        if name not in my_dict:
                            logger.error("The constant {} is not available for {}.".format(name, self.identifier))
                            raise Exception("The constant {} is not available for {}.".format(name, self.identifier))

                self.constants = my_dict

            except IOError:
                logger.error("{}{}.constants does not exist.".format(input_folder, self.identifier))
                raise Exception("{}{}.constants does not exist.".format(input_folder, self.identifier))

    def _set_parameters_with_file(self, link, catchment, outlet, input_folder):
        """
        This method get the list of the names for the parameters of the Model in its specification file in the
        specifications folder. Then, the methods reads the parameters values in the parameter file for the Model located
        in the input folder. If this file does not exist, it uses the descriptors of the catchment that owns the Model
        in order to infer the parameters from the descriptors. In any case, it saves the parameters used in a file in
        the output folder.

        :param input_folder: path to the specification folder where to find the parameter file
        :return: dictionary containing the constants names and values
            {key: parameter_name, value: parameter_value}
        """
        logger = getLogger('TORRENTpy.md')
        if self.parameters_names:
            try:
                my_dict = dict()
                with open_csv_rb(
                        '{}{}_{}.{}{}.parameters'.format(
                            input_folder, catchment, outlet, self.identifier, self.category)) as my_file:
                    my_reader = DictReader(my_file)
                    found = False
                    for row in my_reader:
                        if row['WaterBody'] == link.name:
                            found = True
                            for name in self.parameters_names:
                                try:
                                    my_dict[name] = float(row[name])
                                except KeyError:
                                    logger.error("The {}{} parameter {} is not available for {}.".format(
                                        self.identifier, self.category, name, link.name))
                                    raise Exception("The {}{} parameter {} is not available for {}.".format(
                                        self.identifier, self.category, name, link.name))
                    if not found:
                        logger.error(
                            "The WaterBody {} is not available in the parameters file.".format(link.name))
                        raise Exception(
                            "The WaterBody {} is not available in the parameters file.".format(link.name))

                self.parameters = my_dict
                link.models_parameters.update(my_dict)

            except IOError:
                logger.error("{}{}.parameters does not exist.".format(input_folder, self.identifier))
                raise Exception("{}{}.parameters does not exist.".format(input_folder, self.identifier))
