from csv import DictReader, writer
from datetime import datetime
from os import path, makedirs, sep, rename
from shutil import copyfile, rmtree
from glob import glob


# select type of configuration to create
lumped = False
semi_l = False
semi_d = True

# infer the name of the setup file
if lumped:
    setup_file = 'folders_l.setup'
elif semi_l:
    setup_file = 'folders_sd.setup'
else:
    setup_file = 'folders_sd.setup'

# define folder paths
in_directory = 'C:/PycharmProjects/Python/CatchmentSimulationFramework/in'
out_directory = 'C:/PycharmProjects/Python/CatchmentSimulationFramework/out'

rain_folder = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/out/meteo/rain/dly/sub_basins'
peva_folder = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/out/meteo/peva/dly/sub_basins'
temp_folder = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/out/meteo/temp/dly/sub_basins'
flow_folder = 'D:/Google_Drive/05_HydrologicalModelling/1_Simulations_PaperOne/20170801_Simulations/RUN_5_CALIB/Gauging_Data/All_Processed'

geo_folder = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/out/geo'
hydro_folder = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/out/hydro'
hydro_db = 'C:/PycharmProjects/Python/HydroMeteoGeoPreProcessing/db/hydro'

# read in the list of catchments file
dict_catchments = dict()
with open(sep.join([in_directory, setup_file]), 'rb') as my_file:
    my_reader = DictReader(my_file)
    for row in my_reader:
        if lumped:  # use PeriodSimu since files were created as a subset of semi-distributed files
            dict_catchments['_'.join([row['Catchment'], row['Outlet']])] = {
                'OverallOutlet': row['OverallOutlet'],
                'Outlet': row['Outlet'],
                'Gauge': row['Gauge'],
                'StartData': datetime.strptime(row['PeriodSimu'].split(' ')[0], "%d/%m/%Y").replace(hour=0),
                'EndData': datetime.strptime(row['PeriodSimu'].split(' ')[1], "%d/%m/%Y").replace(hour=0),
                'StartSimu': datetime.strptime(row['PeriodSimu'].split(' ')[0], "%d/%m/%Y").replace(hour=0),
                'EndSimu': datetime.strptime(row['PeriodSimu'].split(' ')[1], "%d/%m/%Y").replace(hour=0)
            }
        else:
            dict_catchments['_'.join([row['Catchment'], row['Outlet']])] = {
                'OverallOutlet': row['OverallOutlet'],
                'Outlet': row['Outlet'],
                'Gauge': row['Gauge'],
                'StartData': datetime.strptime(row['PeriodData'].split(' ')[0], "%d/%m/%Y").replace(hour=0),
                'EndData': datetime.strptime(row['PeriodData'].split(' ')[1], "%d/%m/%Y").replace(hour=0),
                'StartSimu': datetime.strptime(row['PeriodSimu'].split(' ')[0], "%d/%m/%Y").replace(hour=0),
                'EndSimu': datetime.strptime(row['PeriodSimu'].split(' ')[1], "%d/%m/%Y").replace(hour=0)
            }

# proceed for each catchment
for catchment in dict_catchments:

    # create the input folder
    if path.exists(sep.join([in_directory, catchment])):
        rmtree(sep.join([in_directory, catchment]))
        makedirs(sep.join([in_directory, catchment]))
    else:
        makedirs(sep.join([in_directory, catchment]))

    # get list of all waterbodies in catchment
    my_sub_basins = list()
    with open(sep.join([hydro_folder, '{}.waterbodies'.format(catchment)]), 'rb') as my_file:
        my_reader = DictReader(my_file)
        for row in my_reader:
            my_sub_basins.append('_'.join([catchment.split('_IE_')[0], row['WaterBody']]))

    for sub_basin in my_sub_basins:
        # bring in the meteo data
        my_rain_file = '{}_{}_{}.rain'.format(sub_basin, dict_catchments[catchment]['StartData'].strftime("%Y%m%d"),
                                              dict_catchments[catchment]['EndData'].strftime("%Y%m%d"))
        copyfile(
            sep.join([rain_folder, my_rain_file]),
            sep.join([in_directory, catchment, my_rain_file]))

        my_peva_file = '{}_{}_{}.peva'.format(sub_basin, dict_catchments[catchment]['StartData'].strftime("%Y%m%d"),
                                              dict_catchments[catchment]['EndData'].strftime("%Y%m%d"))
        copyfile(
            sep.join([peva_folder, my_peva_file]),
            sep.join([in_directory, catchment, my_peva_file]))

        my_soit_file = '{}_{}_{}.soit'.format(sub_basin, dict_catchments[catchment]['StartData'].strftime("%Y%m%d"),
                                              dict_catchments[catchment]['EndData'].strftime("%Y%m%d"))
        copyfile(
            sep.join([temp_folder, my_soit_file]),
            sep.join([in_directory, catchment, my_soit_file]))

        my_airt_file = '{}_{}_{}.airt'.format(sub_basin, dict_catchments[catchment]['StartData'].strftime("%Y%m%d"),
                                              dict_catchments[catchment]['EndData'].strftime("%Y%m%d"))
        copyfile(
            sep.join([temp_folder, my_airt_file]),
            sep.join([in_directory, catchment, my_airt_file]))

    # bring in the hydro connectivity data
    for extension in ['connectivity', 'waterbodies', 'network']:
        my_hydro_file = '{}.{}'.format(catchment, extension)
        copyfile(
            sep.join([hydro_folder, my_hydro_file]),
            sep.join([in_directory, catchment, my_hydro_file]))
    for extension in ['pdf', 'gv']:
        my_hydro_file = '{}.{}'.format(catchment, extension)
        try:
            copyfile(
                sep.join([hydro_folder, my_hydro_file]),
                sep.join([in_directory, catchment, my_hydro_file]))
        except IOError:
            pass

    # bring in the geo data (potentially as a subset of original file)
    for extension in ['descriptors']:
        if lumped:  # i.e. it is a lumped catchment, there are geo files created for each lumped catchment
            my_geo_file = '{}.{}'.format(catchment, extension)

            copyfile(
                sep.join([geo_folder, my_geo_file]),
                sep.join([in_directory, catchment, my_geo_file]))
        elif semi_d:  # i.e. it is a semi-distributed catchment, so need to query file of overall outlet in catchment
            if dict_catchments[catchment]['OverallOutlet'] == dict_catchments[catchment]['Outlet']:
                # i.e. file in geo folder is the one I want, because same catchment I am talking about, just copy it
                my_geo_file = '{}.{}'.format(catchment, extension)

                copyfile(
                    sep.join([geo_folder, my_geo_file]),
                    sep.join([in_directory, catchment, my_geo_file]))
            else:  # i.e. need to generate a subset of the original file
                my_dict_original = dict()

                my_geo_file = '{}_{}.{}'.format(catchment.split('_IE_')[0], dict_catchments[catchment]['OverallOutlet'],
                                                extension)
                my_subset_geo_file = '{}.{}'.format(catchment, extension)

                with open(sep.join([geo_folder, my_geo_file]), 'rb') as my_file:
                    my_reader = DictReader(my_file)
                    my_field_names = my_reader.fieldnames[:]
                    my_field_names.remove('EU_CD')
                    for row in my_reader:
                        my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])] = [row['EU_CD']]
                        for field in my_field_names:
                            my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])].append(row[field])

                with open(sep.join([in_directory, catchment, my_subset_geo_file]), 'wb') as my_file:
                    my_writer = writer(my_file)
                    my_writer.writerow(['EU_CD'] + my_field_names)
                    for sub_basin in my_sub_basins:
                        try:
                            my_writer.writerow(my_dict_original[sub_basin])
                        except KeyError:
                            raise Exception('{} is not in the {} file in the geo folder.'.format(sub_basin, extension))
        elif semi_l:  # i.e. it is a semi-lumped catchment, so need to query lumped file and replicate descriptors
            my_dict_original = dict()

            catchment_outlet_l = catchment.replace('_IE_', '_l_IE_')
            catchment_l = catchment_outlet_l.split('_IE_')[0]
            outlet_l = catchment_outlet_l.split('_l_')[1]

            my_geo_file_l = '{}.{}'.format(catchment_outlet_l, extension)
            my_geo_file_sd = '{}_{}.{}'.format(catchment.split('_IE_')[0], dict_catchments[catchment]['OverallOutlet'],
                                               extension)
            my_subset_geo_file = '{}.{}'.format(catchment, extension)

            with open(sep.join([geo_folder, my_geo_file_sd]), 'rb') as my_file:  # get specific descriptors first
                my_reader = DictReader(my_file)
                my_field_names = ['EU_CD', 'stream_length', 'wb_type', 'area']
                for row in my_reader:
                    my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])] = list()
                    for field in my_field_names:
                        my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])].append(row[field])

            with open(sep.join([geo_folder, my_geo_file_l]), 'rb') as my_file:  # replicate other lumped descriptors
                my_reader = DictReader(my_file)
                fields = [field for field in my_reader.fieldnames[:] if field not in my_field_names]
                my_field_names += fields
                count = 0
                for row in my_reader:
                    if count > 0:
                        raise Exception('Lumped descriptors file contains more than one data line.')
                    for sub_basin in my_sub_basins:
                        for field in fields:
                            my_dict_original[sub_basin].append(row[field])
                    count += 1

            with open(sep.join([in_directory, catchment, my_subset_geo_file]), 'wb') as my_file:
                my_writer = writer(my_file)
                my_writer.writerow(my_field_names)
                for sub_basin in my_sub_basins:
                    try:
                        my_writer.writerow(my_dict_original[sub_basin])
                    except KeyError:
                        raise Exception('{} is not in the {} file in the geo folder.'.format(sub_basin, extension))

    for extension in ['loadings', 'applications']:
        if lumped:  # i.e. it is a lumped catchment, there are geo files created for each lumped catchment
            my_geo_file = '{}.{}'.format(catchment, extension)

            copyfile(
                sep.join([geo_folder, my_geo_file]),
                sep.join([in_directory, catchment, my_geo_file]))
        else:  # i.e. it is a semi-d / semi-l catchment, so need to query file of overall outlet in catchment
            if dict_catchments[catchment]['OverallOutlet'] == dict_catchments[catchment]['Outlet']:
                # i.e. file in geo folder is the one I want, because same catchment I am talking about, just copy it
                my_geo_file = '{}.{}'.format(catchment, extension)

                copyfile(
                    sep.join([geo_folder, my_geo_file]),
                    sep.join([in_directory, catchment, my_geo_file]))
            else:  # i.e. need to generate a subset of the original file
                my_dict_original = dict()

                my_geo_file = '{}_{}.{}'.format(catchment.split('_IE_')[0], dict_catchments[catchment]['OverallOutlet'],
                                                extension)
                my_subset_geo_file = '{}.{}'.format(catchment, extension)

                with open(sep.join([geo_folder, my_geo_file]), 'rb') as my_file:
                    my_reader = DictReader(my_file)
                    my_field_names = my_reader.fieldnames[:]
                    my_field_names.remove('EU_CD')
                    for row in my_reader:
                        my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])] = [row['EU_CD']]
                        for field in my_field_names:
                            my_dict_original['_'.join([catchment.split('_IE_')[0], row['EU_CD']])].append(row[field])

                with open(sep.join([in_directory, catchment, my_subset_geo_file]), 'wb') as my_file:
                    my_writer = writer(my_file)
                    my_writer.writerow(['EU_CD'] + my_field_names)
                    for sub_basin in my_sub_basins:
                        try:
                            my_writer.writerow(my_dict_original[sub_basin])
                        except KeyError:
                            raise Exception('{} is not in the {} file in the geo folder.'.format(sub_basin, extension))

    # bring in the discharge data and rename it
    my_files = glob(sep.join([flow_folder, '{}*.csv'.format(dict_catchments[catchment]['Gauge'])]))
    if not len(my_files) == 1:
        raise Exception('No/MoreThanOne discharge data file available for {}.'.format(dict_catchments[catchment]['Gauge']))
    my_flow_file = my_files[0].split(sep)[-1]

    copyfile(
        sep.join([flow_folder, my_flow_file]),
        sep.join([in_directory, catchment, my_flow_file]))
    rename(sep.join([in_directory, catchment, my_flow_file]),
           sep.join([in_directory, catchment, '{}_{}.flow'.format(catchment, dict_catchments[catchment]['Gauge'])]))

    # read in the gauge database file to get the gauged area
    if lumped:
        c = catchment
    else:
        c = catchment.replace('_IE_', '_l_IE_')

    g_area = 0.0
    with open(sep.join([hydro_db, 'HydrometricGaugesInfo.csv']), 'rb') as my_file:
        my_reader = DictReader(my_file)
        count_b = 0
        for row in my_reader:
            if (row['Catchment'] == c) and (row['Gauge'] == dict_catchments[catchment]['Gauge']):
                g_area += float(row['GaugedAreaSqKM'])
                count_b += 1
        if count_b != 1:
            raise Exception('Gauges Information file does not contain suitable row for {}.'.format(catchment))

    # create a .gauges file
    with open(sep.join([in_directory, catchment, '{}.gauges'.format(catchment)]), 'wb') as my_file:
        my_writer = writer(my_file)
        my_writer.writerow(['Gauge', 'Waterbody', 'GaugedAreaSqKM'])
        my_writer.writerow([dict_catchments[catchment]['Gauge'], dict_catchments[catchment]['Outlet'], g_area])

    # create a .simulation file
    my_settings = [
        ('data_start_datetime',     dict_catchments[catchment]['StartData'].strftime("%d/%m/%Y %H:%M:%S")),
        ('data_end_datetime',       dict_catchments[catchment]['EndData'].strftime("%d/%m/%Y %H:%M:%S")),
        ('data_time_gap_min',       1440),
        ('simu_start_datetime',     dict_catchments[catchment]['StartSimu'].strftime("%d/%m/%Y %H:%M:%S")),
        ('simu_end_datetime',       dict_catchments[catchment]['EndSimu'].strftime("%d/%m/%Y %H:%M:%S")),
        ('simu_time_gap_min',       60),
        ('plot_start_datetime',     dict_catchments[catchment]['StartSimu'].strftime("%d/%m/%Y %H:%M:%S")),
        ('plot_end_datetime',       dict_catchments[catchment]['EndSimu'].strftime("%d/%m/%Y %H:%M:%S"))
    ]

    with open(sep.join([in_directory, catchment, '{}.simulation'.format(catchment)]), 'wb') as my_file:
        my_writer = writer(my_file)
        my_writer.writerow(['QUESTION', 'ANSWER'])
        for settings in my_settings:
            my_writer.writerow([settings[0], settings[1]])
