import pandas


def get_df_flow_data_from_file(catchment, link, gauge, my_tf, in_folder, logger):

    flow_label = 'flow'

    my__data_frame = pandas.DataFrame(index=my_tf.series_data[1:], columns=[flow_label]).fillna(-99.0)

    try:
        my_flow_df = pandas.read_csv("{}{}_{}_{}.{}".format(in_folder, catchment, link, gauge, flow_label),
                                     converters={'FLOW': str})

        my_flow_df['DATETIME'] = my_flow_df['DATETIME'].apply(pandas.to_datetime)
        my_flow_df['DATETIME'] = my_flow_df['DATETIME'].dt.date
        my_flow_df.set_index('DATETIME', inplace=True)

        for my_dt_data in my_tf.series_data[1:]:  # ignore first value which is for the initial conditions
            try:
                my_value = my_flow_df.get_value(my_dt_data.date(), flow_label.upper())
                my__data_frame.set_value(my_dt_data, flow_label, float(my_value))
            except KeyError:  # could only be raised for .get_value(), when index or column does not exist
                my__data_frame.set_value(my_dt_data, flow_label, float(-99.0))
            except ValueError:  # could only be raised for float(), when my_value is not a number
                my__data_frame.set_value(my_dt_data, flow_label, float(-99.0))

    except IOError:
        logger.info("{}{}_{}.{} does not exist.".format(in_folder, catchment, link, flow_label))

    return my__data_frame
