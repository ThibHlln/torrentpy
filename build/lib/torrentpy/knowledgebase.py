from logging import getLogger

from .models import *
from .models.model import Model


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
            if isinstance(class_definition, Model):
                self._catchment_models[name] = class_definition
            else:
                logger.error("{} class definition is not an instance of the Model class.".format(name))
                raise Exception("{} class definition is not an instance of the Model class.".format(name))
        else:
            logger.error(
                "{} already exists in the Catchment KnowledgeBase, please choose a different name.".format(name))
            raise Exception(
                "{} already exists in the Catchment KnowledgeBase, please choose a different name.".format(name))

    def add_river_model(self, name, class_definition):
        logger = getLogger('TORRENTpy.kb')

        if name not in self._river_models:
            if isinstance(class_definition, Model):
                self._river_models[name] = class_definition
            else:
                logger.error("{} class definition is not an instance of the Model class.".format(name))
                raise Exception("{} class definition is not an instance of the Model class.".format(name))
        else:
            logger.error(
                "{} already exists in the River KnowledgeBase, please choose a different name.".format(name))
            raise Exception(
                "{} already exists in the River KnowledgeBase, please choose a different name.".format(name))

    def add_lake_model(self, name, class_definition):
        logger = getLogger('TORRENTpy.kb')

        if name not in self._lake_models:
            if isinstance(class_definition, Model):
                self._lake_models[name] = class_definition
            else:
                logger.error("{} class definition is not an instance of the Model class.".format(name))
                raise Exception("{} class definition is not an instance of the Model class.".format(name))
        else:
            logger.error("{} already exists in the Lake KnowledgeBase, please choose a different name.".format(name))
            raise Exception("{} already exists in the Lake KnowledgeBase, please choose a different name.".format(name))
