import unittest
from datetime import datetime
import pickle
import torrentpy
from torrentpy import models


class TestAddModelToKB(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.nw1 = pickle.load(open(r"examples/in/CatchmentSemiDistributedName_OutletName/"
                                    r"CatchmentSemiDistributedName_OutletName.network.pickled", 'rb'))

        self.nw2 = pickle.load(open(r"examples/in/CatchmentSemiDistributedName_OutletName/"
                                    r"CatchmentSemiDistributedName_OutletName.network.pickled", 'rb'))

        self.tf = torrentpy.TimeFrame(
            dt_data_start=datetime.strptime('01/01/2008 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_data_end=datetime.strptime('31/12/2012 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_save_start=datetime.strptime('01/06/2009 09:00:00', '%d/%m/%Y %H:%M:%S'),
            dt_save_end=datetime.strptime('31/01/2010 09:00:00', '%d/%m/%Y %H:%M:%S'),
            data_increment_in_minutes=1440,
            save_increment_in_minutes=1440,
            simu_increment_in_minutes=60,
            expected_simu_slice_length=150,
            warm_up_in_days=0
        )

        self.kb = torrentpy.KnowledgeBase()
        self.kb.add_catchment_model('SMARTSHADOW', models.SMARTc)
        self.kb.add_river_model('SMARTSHADOW', models.SMARTr)

        self.db1 = torrentpy.DataBase(
            self.nw1, self.tf, self.kb,
            in_format='csv',
            meteo_cumulative=['rain', 'peva'],
            meteo_average=['airt', 'soit'],
            contamination_cumulative=['m_no3', 'm_nh4', 'm_p_ino', 'm_p_org'],
            contamination_average=[]
        )

        self.db2 = torrentpy.DataBase(
            self.nw2, self.tf, self.kb,
            in_format='csv',
            meteo_cumulative=['rain', 'peva'],
            meteo_average=['airt', 'soit'],
            contamination_cumulative=['m_no3', 'm_nh4', 'm_p_ino', 'm_p_org'],
            contamination_average=[]
        )

        for link in self.nw1.links:
            link.extra.update(
                {'aar': 1200, 'r-o_ratio': 0.45, 'r-o_split': (0.10, 0.15, 0.15, 0.30, 0.30)}
            )

        for link in self.nw2.links:
            link.extra.update(
                {'aar': 1200, 'r-o_ratio': 0.45, 'r-o_split': (0.10, 0.15, 0.15, 0.30, 0.30)}
            )

        self.nw1.set_links_models(
            self.kb,
            catchment_h='SMART', river_h='SMART',
            catchment_q='INCA', river_q='INCA'
        )

        self.nw2.set_links_models(
            self.kb,
            catchment_h='SMARTSHADOW', river_h='SMARTSHADOW',
            catchment_q='INCA', river_q='INCA'
        )

    def test_outlet_node(self):
        # get the first simulation slice
        my_simu_slice = self.tf.simu_slices[0]

        # get initial conditions
        my_last_lines1 = dict()
        for link in self.nw1.links:
            my_last_lines1[link.name] = dict()
            for model in link.all_models:
                my_last_lines1[link.name].update(model.initialise(link))
        for node in self.nw1.nodes:
            my_last_lines1[node.name] = dict()
        my_last_lines2 = dict()
        for link in self.nw1.links:
            my_last_lines2[link.name] = dict()
            for model in link.all_models:
                my_last_lines2[link.name].update(model.initialise(link))
        for node in self.nw1.nodes:
            my_last_lines2[node.name] = dict()

        # initialise data structures for the simulation slice
        self.db1.set_db_for_links_and_nodes(my_simu_slice)
        self.db2.set_db_for_links_and_nodes(my_simu_slice)

        # transfer initial conditions into the DataBase
        for link in self.nw1.links:
            self.db1.simulation[link.name][my_simu_slice[0]].update(my_last_lines1[link.name])
        for node in self.nw1.nodes:
            self.db1.simulation[node.name][my_simu_slice[0]].update(my_last_lines1[node.name])
        for link in self.nw2.links:
            self.db2.simulation[link.name][my_simu_slice[0]].update(my_last_lines2[link.name])
        for node in self.nw2.nodes:
            self.db2.simulation[node.name][my_simu_slice[0]].update(my_last_lines2[node.name])

        # run the Models in the Network for the simulation slice
        self.nw1._run(self.db1, self.tf, my_simu_slice)
        self.nw2._run(self.db2, self.tf, my_simu_slice)

        # round all values to 12 decimals
        for dt in self.db1.simulation['0000']:
            for var in self.db1.simulation['0000'][dt]:
                self.db1.simulation['0000'][dt][var] = round(self.db1.simulation['0000'][dt][var], 12)
        for dt in self.db2.simulation['0000']:
            for var in self.db2.simulation['0000'][dt]:
                self.db2.simulation['0000'][dt][var] = round(self.db2.simulation['0000'][dt][var], 12)

        # compare
        self.assertDictEqual(
            self.db1.simulation['0000'],
            self.db2.simulation['0000']
        )


if __name__ == '__main__':
    unittest.main()
