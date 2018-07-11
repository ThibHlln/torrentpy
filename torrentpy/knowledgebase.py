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

from .models import *


class KnowledgeBase(object):
    def __init__(self):
        self._catchment_models = {
            'SMART': SMARTc,
            'INCA': INCAc
        }
        self._river_models = {
            'SMART': SMARTr,
            'INCA': INCAr
        }
        self._lake_models = {}

    def get_catchment_model(self, name):
        logger = getLogger('TORRENTpy.kb')
        if name in self._catchment_models:
            return self._catchment_models[name]
        else:
            logger.error("{} is not available in the Catchment KnowledgeBase.".format(name))
            raise Exception("{} is not available in the Catchment KnowledgeBase.".format(name))

    def get_river_model(self, name):
        logger = getLogger('TORRENTpy.kb')
        if name in self._river_models:
            return self._river_models[name]
        else:
            logger.error("{} is not available in the River KnowledgeBase.".format(name))
            raise Exception("{} is not available in the River KnowledgeBase.".format(name))

    def get_lake_model(self, name):
        logger = getLogger('TORRENTpy.kb')
        if name in self._lake_models:
            return self._lake_models[name]
        else:
            logger.exception("{} is not available in the Lake KnowledgeBase.".format(name))
            raise Exception("{} is not available in the Lake KnowledgeBase.".format(name))

    def add_catchment_model(self, name, class_definition):
        logger = getLogger('TORRENTpy.kb')

        if name not in self._catchment_models:
            if issubclass(class_definition, Model):
                self._catchment_models[name] = class_definition
            else:
                logger.error("{} class definition is not a subclass of the Model class.".format(name))
                raise Exception("{} class definition is not a subclass of the Model class.".format(name))
        else:
            logger.error(
                "{} already exists in the Catchment KnowledgeBase, please choose a different name.".format(name))
            raise Exception(
                "{} already exists in the Catchment KnowledgeBase, please choose a different name.".format(name))

    def add_river_model(self, name, class_definition):
        logger = getLogger('TORRENTpy.kb')

        if name not in self._river_models:
            if issubclass(class_definition, Model):
                self._river_models[name] = class_definition
            else:
                logger.error("{} class definition is not a subclass of the Model class.".format(name))
                raise Exception("{} class definition is not a subclass of the Model class.".format(name))
        else:
            logger.error(
                "{} already exists in the River KnowledgeBase, please choose a different name.".format(name))
            raise Exception(
                "{} already exists in the River KnowledgeBase, please choose a different name.".format(name))

    def add_lake_model(self, name, class_definition):
        logger = getLogger('TORRENTpy.kb')

        if name not in self._lake_models:
            if issubclass(class_definition, Model):
                self._lake_models[name] = class_definition
            else:
                logger.error("{} class definition is not a subclass of the Model class.".format(name))
                raise Exception("{} class definition is not a subclass of the Model class.".format(name))
        else:
            logger.error("{} already exists in the Lake KnowledgeBase, please choose a different name.".format(name))
            raise Exception("{} already exists in the Lake KnowledgeBase, please choose a different name.".format(name))
