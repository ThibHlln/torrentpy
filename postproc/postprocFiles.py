from collections import OrderedDict
from csv import DictReader, writer
from numpy import float64
from datetime import datetime, timedelta


def create_subset_flow_file(catchment, link, catchment_area, gauge, gauged_area,
                            my_tf, plot_dt_start, plot_dt_end,
                            in_folder, out_folder, logger):

    flow_label = 'flow'

    my_dt_series = [step for step in my_tf.series_data[1:] if (step >= plot_dt_start) and (step <= plot_dt_end)]

    if not gauged_area == -999.00:  # i.e. the gauged area is known
        try:
            my_original_flow_file = "{}{}_{}_{}.{}".format(in_folder, catchment, link, gauge, flow_label)
            my_subset_flow_file = "{}{}_{}_{}.{}".format(out_folder, catchment, link, gauge, flow_label)

            my_dict_flows = get_dict_discharge_series(my_original_flow_file,
                                                      plot_dt_start, plot_dt_end,
                                                      catchment_area, gauged_area)

            write_flow_file_from_dict(my_subset_flow_file, my_dict_flows, my_dt_series)

        except IOError:
            logger.info("{}{}_{}_{}.{} does not exist.".format(in_folder, catchment, link, gauge, flow_label))
    else:
        logger.info("Gauged area of {} for {}_{} is unknown.".format(gauge, catchment, link))


def get_dict_discharge_series(file_location, start_report, end_report, catchment_area, gauged_area):
    data_flow = read_flow_file(file_location)

    scaling_factor = catchment_area / gauged_area

    start_date = (start_report - timedelta(days=2)).date()
    end_date = (end_report + timedelta(days=1)).date()

    dict_flow = OrderedDict()
    for dt in data_flow.iterkeys():
        d = dt.date()
        if (start_date <= d) and (d <= end_date):
            dict_flow[dt] = data_flow[dt] * scaling_factor

    return rescale_time_resolution_of_irregular_mean_data(dict_flow, start_report, end_report,
                                                          timedelta(days=1), timedelta(hours=1))


def read_flow_file(file_location):
    return read_csv_time_series_with_missing_check(file_location, key_header='DATETIME', val_header='FLOW')


def read_csv_time_series_with_missing_check(csv_file, key_header, val_header):
    try:
        with open(csv_file, 'rb') as my_file:
            my_dict_data = OrderedDict()
            my_reader = DictReader(my_file)
            try:
                for row in my_reader:
                    try:
                        if row[val_header] != '':  # not an empty string (that would mean missing data)
                            if float64(row[val_header]) != -99.0:  # flag for missing data
                                my_dict_data[datetime.strptime(row[key_header], "%Y-%m-%d %H:%M:%S")] = \
                                    float64(row[val_header])
                    except ValueError:
                        raise Exception('Field {} in {} cannot be converted to float '
                                        'at {}.'.format(val_header, csv_file, row[key_header]))
            except KeyError:
                raise Exception('Field {} or {} does not exist in {}.'.format(key_header, val_header, csv_file))
        return my_dict_data
    except IOError:
        raise Exception('File {} could not be found.'.format(csv_file))


def increase_time_resolution_of_irregular_mean_data(dict_info, time_delta_lo, time_delta_hi):
    """
    Create high resolution mean data from lower resolution mean data
    using backwards duplication.
    """
    new_dict_info = dict()
    # get the series of DateTime in the data
    my_dts = dict_info.keys()
    for i, my_dt in enumerate(my_dts[1:]):
        # determine the duration of the cumulative data between the two time steps
        my_delta = my_dt - my_dts[i]
        if my_delta >= timedelta(seconds=1.5 * time_delta_lo.total_seconds()):
            my_delta = time_delta_lo
        # determine the number of hours the cumulative data has to be spread over
        (divisor, remainder) = divmod(int(my_delta.total_seconds()), int(time_delta_hi.total_seconds()))
        if remainder != 0:
            raise Exception("Increase Resolution: Time Deltas are not multiples of each other.")
        elif divisor < 1:
            raise Exception("Increase Resolution: Low resolution lower than higher resolution "
                            "{} < {}.".format(my_delta, time_delta_hi))
        # determine the high resolution value
        try:
            my_value = float(dict_info[my_dt])
        except ValueError:  # no data for this time step
            my_value = ''
        # spread the hourly value backwards
        for my_sub_step in xrange(0, -divisor, -1):
            if new_dict_info.get(my_dt + my_sub_step * time_delta_hi):  # should not happen
                raise Exception("Increase Resolution: Overwriting already existing data for datetime.")
            else:
                new_dict_info[my_dt + my_sub_step * time_delta_hi] = my_value

    return new_dict_info


def decrease_time_resolution_of_irregular_mean_data(dict_info, dt_start, dt_end, time_delta_hi, time_delta_lo):
    """ Creates low resolution cumulative data from high resolution cumulative data
    using arithmetic mean. """
    my_dt = dt_start
    new_dict_info = OrderedDict()

    (divisor, remainder) = divmod(int(time_delta_lo.total_seconds()), int(time_delta_hi.total_seconds()))
    if remainder != 0:
        raise Exception("Decrease Resolution: Time Deltas are not multiples of each other.")
    elif divisor < 1:
        raise Exception("Decrease Resolution: Low resolution lower than higher resolution "
                        "{} < {}.".format(time_delta_lo, time_delta_hi))

    while (dt_start <= my_dt) and (my_dt <= dt_end):
        try:
            my_values = 0.0
            for my_sub_step in xrange(0, -divisor, -1):
                my_values += dict_info[my_dt + my_sub_step * time_delta_hi]
            new_dict_info[my_dt] = my_values / divisor
            my_dt += time_delta_lo
        except KeyError:  # at least one of the values is not available (i.e. missing value)
            my_dt += time_delta_lo
        except TypeError:  # at least one of the values was not a float [string] (i.e. missing value)
            my_dt += time_delta_lo

    return new_dict_info


def rescale_time_resolution_of_irregular_mean_data(dict_data, start_data, end_data, time_delta_lo, time_delta_hi):
    my_tmp_dict = increase_time_resolution_of_irregular_mean_data(dict_data, time_delta_lo, time_delta_hi)
    my_new_dict = decrease_time_resolution_of_irregular_mean_data(my_tmp_dict, start_data, end_data,
                                                                  time_delta_hi, time_delta_lo)

    return my_new_dict


def write_flow_file_from_dict(csv_file, discharge, timeseries):
    with open(csv_file, 'wb') as my_file:
        my_writer = writer(my_file, delimiter=',')
        my_writer.writerow(['DateTime', 'flow'])
        for my_dt in timeseries:
            try:
                my_writer.writerow([my_dt, '%e' % discharge[my_dt]])
            except KeyError:
                my_writer.writerow([my_dt, '%e' % -99.0])
