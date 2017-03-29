from pandas import DataFrame
import sys
import csv
import datetime


def get_data_frame_for_daily_meteo_data(catchment, link, time_steps, meteo_folder):

    my_start = time_steps[0].year + '%02d' % time_steps[0].month + '%02d' % time_steps[0].day
    my_end = time_steps[1].year + '%02d' % time_steps[1].month + '%02d' % time_steps[1].day

    my_meteo_data_types = ["rain", "peva"]

    my__data_frame = DataFrame(index=time_steps, columns=my_meteo_data_types)

    for meteo_type in my_meteo_data_types:
        try:
            with open("{}{}_{}_{}_{}_{}.csv".format(meteo_folder, catchment,
                                                    link, my_start, my_end, meteo_type)) as my_file:
                my_reader = csv.DictReader(my_file)

                for row in my_reader:
                    file_datetime = datetime.datetime(int(row['YEAR']), int(row['MONTH']), int(row['DAY']),
                                                      int(row['HOURS']), int(row['MINUTES']), int(row['SECONDS']))

                    my__data_frame.set_value(file_datetime, meteo_type, float(row[meteo_type.upper()]))

        except EnvironmentError:
            sys.exit("{}{}_{}_{}_{}_{}.csv does not exist.".format(meteo_folder, catchment,
                                                                   link, my_start, my_end, meteo_type))

    return my__data_frame
