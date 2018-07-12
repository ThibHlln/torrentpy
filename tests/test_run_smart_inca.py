import unittest
from datetime import datetime
import torrentpy


class TestNetworkRun(unittest.TestCase):
    def setUp(self):
        self.nw = torrentpy.Network(
            catchment='CatchmentSemiDistributedName',
            outlet='OutletName',
            in_fld='examples/in/CatchmentSemiDistributedName_OutletName/',
            out_fld='examples/out/CatchmentSemiDistributedName_OutletName/',
            variable_h='q_h2o',
            variables_q=['c_no3', 'c_nh4', 'c_dph', 'c_pph', 'c_sed'],
            water_quality=True,
        )

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

        self.db = torrentpy.DataBase(
            self.nw, self.tf, self.kb,
            in_format='csv',
            meteo_cumulative=['rain', 'peva'],
            meteo_average=['airt', 'soit'],
            contamination_cumulative=['m_no3', 'm_nh4', 'm_p_ino', 'm_p_org'],
            contamination_average=[]
        )

        for link in self.nw.links:
            link.extra.update(
                {'aar': 1200, 'r-o_ratio': 0.45, 'r-o_split': (0.10, 0.15, 0.15, 0.30, 0.30)}
            )

        self.nw.set_links_models(
            self.kb,
            catchment_h='SMART', river_h='SMART',
            catchment_q='INCA', river_q='INCA'
        )

        self.expected_outcome = {
            datetime.strptime('2009-06-05 11:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.00021558786339130227,
                                                                            'c_nh4': 7.983949388237407e-10,
                                                                            'c_no3': 2.2383278327914216e-05,
                                                                            'q_h2o': 3.0065280249051445,
                                                                            'c_dph': 3.914368612138995e-06,
                                                                            'c_pph': 2.579737734876026e-05},
            datetime.strptime('2009-06-05 12:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.00034406399133697743,
                                                                            'c_nh4': 1.0848625730016494e-05,
                                                                            'c_no3': 0.00018798949885419445,
                                                                            'q_h2o': 2.0514450704409817,
                                                                            'c_dph': 6.196384750143706e-05,
                                                                            'c_pph': 4.029409491738285e-05},
            datetime.strptime('2009-06-05 13:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.0009359409710245761,
                                                                            'c_nh4': 7.444163490987917e-06,
                                                                            'c_no3': 0.00015130435797813712,
                                                                            'q_h2o': 3.0074221193089734,
                                                                            'c_dph': 4.791032090851252e-05,
                                                                            'c_pph': 0.00010604292791482049},
            datetime.strptime('2009-06-05 14:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.003008199862771426,
                                                                            'c_nh4': 3.4579170358881274e-05,
                                                                            'c_no3': 0.0006620102589153735,
                                                                            'q_h2o': 2.063757863627895,
                                                                            'c_dph': 0.00020828009969673134,
                                                                            'c_pph': 0.00030987905119267834},
            datetime.strptime('2009-06-05 15:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.003755776014319036,
                                                                            'c_nh4': 2.3585863951482863e-05,
                                                                            'c_no3': 0.0004985070949053843,
                                                                            'q_h2o': 3.050141297608301,
                                                                            'c_dph': 0.00015043433113933884,
                                                                            'c_pph': 0.00039828698111166975},
            datetime.strptime('2009-06-05 16:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.014347392527287053,
                                                                            'c_nh4': 5.9916126630496284e-05,
                                                                            'c_no3': 0.0012939157310117217,
                                                                            'q_h2o': 2.105660092167754,
                                                                            'c_dph': 0.0003731817648859144,
                                                                            'c_pph': 0.001461872438874848},
            datetime.strptime('2009-06-05 17:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.012562678814405741,
                                                                            'c_nh4': 4.062985481051762e-05,
                                                                            'c_no3': 0.0009532138093833013,
                                                                            'q_h2o': 3.152458558046265,
                                                                            'c_dph': 0.0002638237096239806,
                                                                            'c_pph': 0.0012922957747844087},
            datetime.strptime('2009-06-05 18:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.04518795484899722,
                                                                            'c_nh4': 8.225338112442179e-05,
                                                                            'c_no3': 0.0019318989800966538,
                                                                            'q_h2o': 2.189038365787803,
                                                                            'c_dph': 0.0005100290066311981,
                                                                            'c_pph': 0.004457792562727915},
            datetime.strptime('2009-06-05 19:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.03599167237234772,
                                                                            'c_nh4': 5.5503931186651754e-05,
                                                                            'c_no3': 0.0014067402539598148,
                                                                            'q_h2o': 3.325650568873484,
                                                                            'c_dph': 0.0003565302382029201,
                                                                            'c_pph': 0.003367874583607178},
            datetime.strptime('2009-06-05 20:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.08998746745040836,
                                                                            'c_nh4': 0.00010024306526301778,
                                                                            'c_no3': 0.0024784438651160373,
                                                                            'q_h2o': 2.320663427188651,
                                                                            'c_dph': 0.000600957613030069,
                                                                            'c_pph': 0.007728176821426419},
            datetime.strptime('2009-06-05 21:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.06999868167084113,
                                                                            'c_nh4': 6.741219363968291e-05,
                                                                            'c_no3': 0.0017925259246382328,
                                                                            'q_h2o': 3.557787911919933,
                                                                            'c_dph': 0.00041736915247398917,
                                                                            'c_pph': 0.005822712729080773},
            datetime.strptime('2009-06-05 22:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.12511671714819234,
                                                                            'c_nh4': 0.00011409495976475016,
                                                                            'c_no3': 0.0029148647286299993,
                                                                            'q_h2o': 2.4911590788914664,
                                                                            'c_dph': 0.0006518415619319346,
                                                                            'c_pph': 0.010508731162246746},
            datetime.strptime('2009-06-05 23:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.09659257329814139,
                                                                            'c_nh4': 7.655206196420863e-05,
                                                                            'c_no3': 0.002099315861844693,
                                                                            'q_h2o': 3.83482954623,
                                                                            'c_dph': 0.00045090710842870374,
                                                                            'c_pph': 0.007900486738563977},
            datetime.strptime('2009-06-06 00:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.154268587553034,
                                                                            'c_nh4': 0.0001245758180328029,
                                                                            'c_no3': 0.003252941437497534,
                                                                            'q_h2o': 2.691294096890235,
                                                                            'c_dph': 0.0006738535355478688,
                                                                            'c_pph': 0.011945144610970142},
            datetime.strptime('2009-06-06 01:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.11864380255798984,
                                                                            'c_nh4': 8.345651935154434e-05,
                                                                            'c_no3': 0.0023364207681183906,
                                                                            'q_h2o': 4.143096422454678,
                                                                            'c_dph': 0.00046495179880737595,
                                                                            'c_pph': 0.00896710825003826},
            datetime.strptime('2009-06-06 02:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.17965155785471723,
                                                                            'c_nh4': 0.00013244139825800948,
                                                                            'c_no3': 0.003510901598041752,
                                                                            'q_h2o': 2.9120850044380715,
                                                                            'c_dph': 0.000676690159327481,
                                                                            'c_pph': 0.010954206664337298},
            datetime.strptime('2009-06-06 03:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.13783539726050661,
                                                                            'c_nh4': 8.862698118617684e-05,
                                                                            'c_no3': 0.0025168832632526043,
                                                                            'q_h2o': 4.47349671849528,
                                                                            'c_dph': 0.00046609536664728315,
                                                                            'c_pph': 0.0082153997260441},
            datetime.strptime('2009-06-06 04:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.2024046023053978,
                                                                            'c_nh4': 0.0001382845638632625,
                                                                            'c_no3': 0.0037051839056710862,
                                                                            'q_h2o': 3.1478240652206098,
                                                                            'c_dph': 0.0006673305271697271,
                                                                            'c_pph': 0.00872166326631132},
            datetime.strptime('2009-06-06 05:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.15502632336398328,
                                                                            'c_nh4': 9.245391676932681e-05,
                                                                            'c_no3': 0.0026523092663909642,
                                                                            'q_h2o': 4.820936560784333,
                                                                            'c_dph': 0.00045905173093235043,
                                                                            'c_pph': 0.006537240409630423},
            datetime.strptime('2009-06-06 06:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.2231037124985986,
                                                                            'c_nh4': 0.00014255075415881357,
                                                                            'c_no3': 0.003849030406124923,
                                                                            'q_h2o': 3.3953561367765057,
                                                                            'c_dph': 0.0006505143522057711,
                                                                            'c_pph': 0.007620069177141804},
            datetime.strptime('2009-06-06 07:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.17065061442109405,
                                                                            'c_nh4': 9.523219527636435e-05,
                                                                            'c_no3': 0.0027520643963378113,
                                                                            'q_h2o': 5.182579637588884,
                                                                            'c_dph': 0.00044702302849313174,
                                                                            'c_pph': 0.005708410495216091},
            datetime.strptime('2009-06-06 08:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.2557224689824646,
                                                                            'c_nh4': 0.00014557785051774605,
                                                                            'c_no3': 0.003952868809158466,
                                                                            'q_h2o': 3.652895391688126,
                                                                            'c_dph': 0.0006294017709430221,
                                                                            'c_pph': 0.008620269451532159},
            datetime.strptime('2009-06-06 09:00:00', '%Y-%m-%d %H:%M:%S'): {'c_sed': 0.1951563382686926,
                                                                            'c_nh4': 9.718678714757282e-05,
                                                                            'c_no3': 0.0028235483045349337,
                                                                            'q_h2o': 5.556679372109293,
                                                                            'c_dph': 0.0004321459408504057,
                                                                            'c_pph': 0.006452120853013679}
        }

    def test_outlet_node(self):
        # get the first simulation slice
        my_simu_slice = self.tf.simu_slices[0]

        # get initial conditions
        my_last_lines = dict()
        for link in self.nw.links:
            my_last_lines[link.name] = dict()
            for model in link.all_models:
                my_last_lines[link.name].update(model.initialise(link))
        for node in self.nw.nodes:
            my_last_lines[node.name] = dict()

        # initialise data structures for the simulation slice
        self.db.set_db_for_links_and_nodes(my_simu_slice)

        # transfer initial conditions into the DataBase
        for link in self.nw.links:
            self.db.simulation[link.name][my_simu_slice[0]].update(my_last_lines[link.name])
        for node in self.nw.nodes:
            self.db.simulation[node.name][my_simu_slice[0]].update(my_last_lines[node.name])

        # run the Models in the Network for the simulation slice
        self.nw._run(self.db, self.tf, my_simu_slice)

        # collect results for the outlet node '0000' for a specific period
        my_nd = dict()
        for dt in self.expected_outcome:
            my_nd[dt] = self.db.simulation['0000'][dt]

        # compare
        self.assertEqual(
            self.expected_outcome,
            my_nd
        )


if __name__ == '__main__':
    unittest.main()
