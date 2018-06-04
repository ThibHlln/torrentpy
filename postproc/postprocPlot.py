from pandas import DataFrame
import numpy as np
import matplotlib as mpl
from matplotlib import dates
import matplotlib.pyplot as plt
import logging
import argparse

from scripts.simuClasses import *
import postprocFiles as ppF
import scripts.simuFiles as sF
import scripts.simuRunSingle as sRS


def main(catchment, outlet, gauge, root):
    # Format catchment and outlet names
    catchment = catchment.capitalize()
    outlet = outlet.upper()

    # Location of the different needed directories
    spec_directory = ''.join([root, "/scripts/specs/"])
    input_directory = ''.join([root, "/in/"])
    output_directory = ''.join([root, "/out/"])

    # Check if combination catchment/outlet is coherent by using the name of the input folder
    if not os.path.exists("{}{}_{}".format(input_directory, catchment, outlet)):
        raise Exception("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Set up the plotting session (either with .simulation file or through the console)
    data_datetime_start, data_datetime_end, data_time_gap_in_min, \
        simu_datetime_start, simu_datetime_end, simu_time_gap_in_min, \
        plot_datetime_start, plot_datetime_end = \
        set_up_plotting(catchment, outlet, input_directory)

    # Precise the specific folders to use in the directories
    input_folder = "{}{}_{}/".format(input_directory, catchment, outlet)
    output_folder = "{}{}_{}_{}_{}/".format(output_directory, catchment, outlet,
                                            simu_datetime_start.strftime("%Y%m%d"),
                                            simu_datetime_end.strftime("%Y%m%d"))

    # Determine gauged waterbody associated to the hydrometric gauge
    gauged_waterbody, gauged_area = find_waterbody_from_gauge(input_folder, catchment, outlet, gauge)

    # Create a logger
    sRS.setup_logger(catchment, gauged_waterbody, 'SinglePlot.main', 'plot', output_folder, is_single_run=True)
    logger = logging.getLogger('SinglePlot.main')
    logger.warning("Starting plotting for {} {} {}.".format(catchment, outlet, gauge))

    # Create a TimeFrame object
    my__time_frame = TimeFrame(data_datetime_start, data_datetime_end,
                               int(data_time_gap_in_min), int(simu_time_gap_in_min), 0)

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, spec_directory)

    # Read the rainfall files
    rainfall, catchment_area = \
        read_meteo_files(my__network, my__time_frame,
                         catchment, outlet,
                         'rain',
                         data_datetime_start, data_datetime_end,
                         gauged_waterbody,
                         input_folder, output_folder)

    # Read the potential evapotranspiration files (in order to create .lumped.peva files)
    read_meteo_files(my__network, my__time_frame,
                     catchment, outlet,
                     'peva',
                     data_datetime_start, data_datetime_end,
                     gauged_waterbody,
                     input_folder, output_folder)

    # Create a subset of the input discharge file
    ppF.create_subset_flow_file(catchment, outlet, catchment_area, gauge, gauged_area,
                                my__time_frame, plot_datetime_start, plot_datetime_end,
                                input_folder, output_folder, logger)

    # Read the flow files
    gauged_flow_m3s, simu_flow_m3s = \
        read_flow_files(my__time_frame,
                        catchment,
                        gauge, gauged_waterbody,
                        output_folder)

    # Plot the desired graphs
    plot_daily_hydro_hyeto(my__time_frame,
                           output_folder, catchment, gauge, gauged_waterbody,
                           rainfall, gauged_flow_m3s, simu_flow_m3s,
                           plot_datetime_start, plot_datetime_end)

    logger.warning("Ending plotting for {} {} {}.".format(catchment, outlet, gauge))


def set_up_plotting(catchment, outlet, input_dir):
    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}/{}_{}.simulation".format(input_dir, catchment, outlet,
                                                                          catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()

    try:
        question_start_data = my_answers_df.get_value('data_start_datetime', 'ANSWER')
    except KeyError:
        question_start_data = raw_input('Starting date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_data = my_answers_df.get_value('data_end_datetime', 'ANSWER')
    except KeyError:
        question_end_data = raw_input('Ending date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_data_time_gap = my_answers_df.get_value('data_time_gap_min', 'ANSWER')
    except KeyError:
        question_data_time_gap = raw_input('Time gap for data? [integer in minutes] ')
    try:
        data_time_gap_in_min = float(int(question_data_time_gap))
    except ValueError:
        raise Exception("The data time gap is invalid. [not an integer]")
    try:
        question_start_simu = my_answers_df.get_value('simu_start_datetime', 'ANSWER')
    except KeyError:
        question_start_simu = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_simu = datetime.datetime.strptime(question_start_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_simu = my_answers_df.get_value('simu_end_datetime', 'ANSWER')
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_simu_time_gap = my_answers_df.get_value('simu_time_gap_min', 'ANSWER')
    except KeyError:
        question_simu_time_gap = raw_input('Time gap for simulation? [integer in minutes] ')
    try:
        simu_time_gap_in_min = float(int(question_simu_time_gap))
    except ValueError:
        raise Exception("The simulation time gap is invalid. [not an integer]")
    try:
        question_start_plot = my_answers_df.get_value('plot_start_datetime', 'ANSWER')
    except KeyError:
        question_start_plot = raw_input('Starting date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_plot = datetime.datetime.strptime(question_start_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The plot starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_plot = my_answers_df.get_value('plot_end_datetime', 'ANSWER')
    except ValueError:
        question_end_plot = raw_input('Ending date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_plot = datetime.datetime.strptime(question_end_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The plot ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    # Check if temporal information is consistent
    if datetime_start_data > datetime_end_data:
        raise Exception("The data time frame is inconsistent.")

    if datetime_start_simu > datetime_end_simu:
        raise Exception("The simulation time frame is inconsistent.")

    if datetime_start_plot > datetime_end_plot:
        raise Exception("The plotting time frame is inconsistent.")

    if datetime_start_simu < datetime_start_data:
        raise Exception("The simulation start is earlier than the data start.")
    if datetime_end_simu > datetime_end_data:
        raise Exception("The simulation end is later than the data end.")

    if datetime_start_plot < datetime_start_simu:
        raise Exception("The plotting start is earlier than the simulation start.")
    if datetime_end_plot > datetime_end_simu:
        raise Exception("The plotting end is later than the simulation end.")

    if data_time_gap_in_min % simu_time_gap_in_min != 0.0:
        raise Exception("The data time gap is not a multiple of the simulation time gap.")

    return datetime_start_data, datetime_end_data, data_time_gap_in_min, \
        datetime_start_simu, datetime_end_simu, simu_time_gap_in_min, \
        datetime_start_plot, datetime_end_plot


def find_waterbody_from_gauge(in_folder, catchment, outlet, gauge):

    dict_gauges = dict()
    try:
        with open('{}{}_{}.gauges'.format(in_folder, catchment, outlet)) as my_file:
            my_reader = csv.DictReader(my_file)
            for line in my_reader:
                dict_gauges[line['Gauge']] = (line['Waterbody'], line['GaugedAreaSqKM'])

    except IOError:
        raise Exception('{}{}_{}.gauges'.format(in_folder, catchment, outlet))

    try:
        gauged_waterbody = dict_gauges[gauge][0]
        gauged_area = float(dict_gauges[gauge][1]) * 1e6  # converts km2 into m2
    except KeyError:
        raise Exception('Gauge {} is not in the gauges file for {} {}.'.format(gauge, catchment, outlet))

    return gauged_waterbody, gauged_area


def determine_gauging_zone(my__network, in_folder, catchment, outlet, gauged_waterbody):

    # Check if node is in the network
    if gauged_waterbody not in my__network.links:
        raise Exception('Waterbody {} is not in the network of {} {}.'.format(gauged_waterbody, catchment, outlet))

    # Import the connectivity file in a dictionary
    dict_connectivity = dict()
    try:
        with open('{}{}_{}.connectivity'.format(in_folder, catchment, outlet)) as my_file:
            my_reader = csv.DictReader(my_file)
            for line in my_reader:
                if line['WaterBody'] not in dict_connectivity:
                    dict_connectivity[line['WaterBody']] = [line['NeighbourUp']]
                else:
                    dict_connectivity[line['WaterBody']].append(line['NeighbourUp'])
    except IOError:
        raise Exception('{}{}_{}.connectivity does not exist.'.format(in_folder, catchment, outlet))

    # Determine the gauging zone upstream of the gauge
    all_links = list()
    links_to_be_processed = [gauged_waterbody]

    while links_to_be_processed:
        all_links.extend(links_to_be_processed)
        links_being_processed = links_to_be_processed[:]
        for link in links_being_processed:
            if link in dict_connectivity:
                links_to_be_processed.extend(dict_connectivity[link])
            links_to_be_processed.remove(link)

    return all_links


def read_meteo_files(my__network, my__time_frame,
                     catchment, outlet,
                     meteo_type,
                     dt_start_data, dt_end_data,
                     gauged_wb,
                     in_folder, out_folder):
    logger = logging.getLogger('SinglePlot.main')
    logger.info("Reading {} files.".format(meteo_type.lower()))

    my_time_dt = my__time_frame.series_data[1:]
    my_time_st = [my_dt.strftime('%Y-%m-%d %H:%M:%S') for my_dt in my_time_dt]

    # Get the average aerial meteo data over the catchment
    links_in_zone = determine_gauging_zone(my__network, in_folder, catchment, outlet, gauged_wb)

    my_data_mm = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    my_area_m2 = np.empty(shape=(0, 1), dtype=np.float64)
    my_dict_desc = sF.get_nd_from_file(my__network, in_folder, extension='descriptors', var_type=float)

    for link in links_in_zone:
        try:
            my_df_inputs = pandas.read_csv("{}{}_{}_{}_{}.{}".format(in_folder, catchment, link,
                                                                     dt_start_data.strftime("%Y%m%d"),
                                                                     dt_end_data.strftime("%Y%m%d"),
                                                                     meteo_type.lower()),
                                           index_col=0)
        except IOError:
            raise Exception("No {} file for {}_{}_{}_{} in {}.".format(
                meteo_type,
                catchment, link, dt_start_data.strftime("%Y%m%d"), dt_end_data.strftime("%Y%m%d"),
                in_folder))
        my_data_mm = \
            np.c_[my_data_mm, np.asarray(my_df_inputs['{}'.format(meteo_type.upper())].loc[my_time_st].tolist())]
        my_area_m2 = \
            np.r_[my_area_m2, np.array([[my_dict_desc[link]['area']]])]
    my_data_m = my_data_mm / 1e3  # convert mm to m of meteo data
    catchment_area = np.sum(my_area_m2)  # get the total area of the catchment
    meteo_data = my_data_m.dot(my_area_m2)  # get a list of catchment meteo data in m3
    meteo_data *= 1e3 / catchment_area  # get meteo data in mm

    # Save the meteo data lumped at the catchment scale in file
    DataFrame({'DATETIME': my__time_frame.series_data[1:],
               '{}'.format(meteo_type.upper()): meteo_data.ravel()}).set_index('DATETIME').to_csv(
        '{}{}_{}.lumped.{}'.format(out_folder, catchment, gauged_wb, meteo_type.lower()), float_format='%e')

    return meteo_data, catchment_area


def read_flow_files(my__time_frame,
                    catchment,
                    gauge, gauged_wb,
                    out_folder):
    logger = logging.getLogger('SinglePlot.main')
    logger.info("Reading flow files.")

    my_time_dt = my__time_frame.series_data[1:]
    my_time_st = [my_dt.strftime('%Y-%m-%d %H:%M:%S') for my_dt in my_time_dt]

    # Get the simulated flow at the outlet of the catchment
    simu_flow_m3s = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    my_df_node = pandas.read_csv("{}{}_{}.outputs".format(out_folder, catchment, gauged_wb), index_col=0)
    simu_flow_m3s = np.c_[simu_flow_m3s, np.asarray(my_df_node['r_out_q_h2o'].loc[my_time_st].tolist())]

    # Get the measured flow near the outlet of the catchment
    gauged_flow_m3s = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    gauged_flow_m3s = \
        np.c_[gauged_flow_m3s,
              np.asarray(pandas.read_csv("{}{}_{}_{}.flow".format(out_folder, catchment, gauged_wb, gauge),
                                         index_col=0)['flow'].loc[my_time_st].tolist())]

    return gauged_flow_m3s, simu_flow_m3s


def plot_daily_hydro_hyeto(my__tf,
                           out_folder, catchment, gauge, gauged_wb,
                           rain, flow_gauged, flow_simulated,
                           dt_start_plot, dt_end_plot):

    logger = logging.getLogger('SinglePlot.main')
    logger.info("Plotting Hyetograph and Hydrograph.")

    my_time_dt = my__tf.series_data[1:]

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')
    fig.suptitle('{} {} ({})'.format(catchment, gauged_wb, gauge))

    # set the default plotting parameters
    font = {
        'weight': 'normal',
        'size': 10,
        'family': 'sans-serif',
        'sans-serif': 'Helvetica'
    }
    mpl.rc('font', **font)
    mpl.rcParams['axes.linewidth'] = 0.3
    mpl.rcParams['xtick.major.width'] = 0.3
    mpl.rcParams['xtick.minor.width'] = 0.3
    mpl.rcParams['ytick.major.width'] = 0.3
    mpl.rcParams['ytick.minor.width'] = 0.3
    mpl.rcParams['grid.linewidth'] = 0.5
    mpl.rcParams['grid.linestyle'] = ':'

    dt_start_data = my_time_dt[0]
    dt_end_data = my_time_dt[-1]

    pyplot_start_data = dates.date2num(dt_start_plot)
    pyplot_end_data = dates.date2num(dt_end_plot)

    if dt_start_data <= dt_start_plot:
        start_diff = dt_start_plot - dt_start_data
        index_start = start_diff.days
    else:
        raise Exception("The start date for plotting is out of bound.")

    if dt_end_plot <= dt_end_data:
        end_diff = dt_end_data - dt_end_plot
        index_end = - (1 + end_diff.days)
    else:
        raise Exception("The end date for plotting is out of bound.")

    # __________________ Hyetograph __________________

    # Create a sub-figure for the hyetograph
    fig1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])  # give location of the graph (%: from left, from bottom, width, height)

    fig1.bar(my_time_dt[index_start:index_end], rain[index_start:index_end],
             label='Hyetograph', facecolor='#4ec4f2', edgecolor='#4ec4f2', linewidth=0)
    fig1.patch.set_facecolor('none')

    # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    ax1 = plt.axis()
    # Set the limits of the axes (here also invert the y-axis by swapping [2] & [3]
    plt.axis((pyplot_start_data, pyplot_end_data, ax1[3]+1, ax1[2]))

    fig1.spines['left'].set_visible(False)  # Remove axis line
    fig1.spines['bottom'].set_visible(False)
    fig1.get_xaxis().set_ticklabels([])  # Remove X axis values only

    fig1.yaxis.set_ticks_position('right')  # Choose location of axis (value + line): can take left, right, both
    fig1.yaxis.set_label_position('right')
    fig1.set_ylabel('Rainfall (mm)')
    fig1.yaxis.grid(b=True, which='major', linestyle=':', dashes=(1, 5))

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.xaxis.set_ticks_position('top')

    # __________________ Hydrograph __________________

    # Create a sub-figure for the hydrograph
    fig2 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig2.plot(my_time_dt[index_start:index_end], flow_simulated[index_start:index_end], color='#898989',
              label='Modelled', linewidth=0.5)

    # Plot the measured flows as points
    fig2.plot(my_time_dt[index_start:index_end], flow_gauged[index_start:index_end],
              'x', markersize=0.5, label='Observed', color='#ffc511')

    ax2 = plt.axis()  # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    plt.axis((pyplot_start_data, pyplot_end_data, -0.2, ax2[3]))

    fig2.patch.set_facecolor('none')

    # fig2.fill_between(x, y, y2, color='#f5b171')  # could be use to fill between MIN curve and MAX curve

    fig2.spines['right'].set_visible(True)
    fig2.spines['top'].set_visible(False)
    fig2.yaxis.set_ticks_position('left')
    fig2.xaxis.set_ticks_position('bottom')

    for label in fig2.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig2.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig2.set_ylabel(u"River Discharge at the outlet (m{}/s)".format(u"\u00B3"))

    fig2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), frameon=False)

    # __________________ Display and Save __________________

    # Show in Tkinter
    # plt.show()

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.hyeto.hydro.pdf'.format(out_folder, catchment, gauged_wb),
                format='pdf', facecolor=fig.get_facecolor(), edgecolor='none')


def plot_flow_duration_curve(obs_flows, obs_frequencies,
                             mod_flows, mod_frequencies,
                             out_folder, catchment, gauged_wb, gauge):

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')
    fig.suptitle('{} {} ({})'.format(catchment, gauged_wb, gauge))

    # set the default plotting parameters
    font = {
        'weight': 'normal',
        'size': 10,
        'family': 'sans-serif',
        'sans-serif': 'Helvetica'
    }
    mpl.rc('font', **font)
    mpl.rcParams['axes.linewidth'] = 0.3
    mpl.rcParams['xtick.major.width'] = 0.3
    mpl.rcParams['xtick.minor.width'] = 0.3
    mpl.rcParams['ytick.major.width'] = 0.3
    mpl.rcParams['ytick.minor.width'] = 0.3
    mpl.rcParams['grid.linewidth'] = 0.5
    mpl.rcParams['grid.linestyle'] = ':'

    # __________________ FDC Modelled __________________

    # Create a sub-figure for the hydrograph
    fig1 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig1.plot(mod_frequencies, mod_flows, color='#898989', label='Modelled', linewidth=0.7)
    fig1.plot(obs_frequencies, obs_flows, color='#ffc511', label='Observed', linewidth=0.7)

    fig1.patch.set_facecolor('none')

    fig1.yaxis.set_ticks_position('left')
    fig1.xaxis.set_ticks_position('bottom')

    for label in fig1.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.set_xlabel("Fraction of flow equalled or exceeded (-)")
    fig1.set_ylabel(u"River Discharge (m{}/s)".format(u"\u00B3"))
    fig1.legend(loc='center', bbox_to_anchor=(0.9, 0.9), frameon=False)

    # __________________ Save __________________

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.fdc.pdf'.format(out_folder, catchment, gauged_wb),
                format='pdf', facecolor=fig.get_facecolor(), edgecolor='none')


def plot_flow_duration_curve_log(obs_flows, obs_frequencies,
                                 mod_flows, mod_frequencies,
                                 out_folder, catchment, gauged_wb, gauge):

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')
    fig.suptitle('{} {} ({})'.format(catchment, gauged_wb, gauge))

    # set the default plotting parameters
    font = {
        'weight': 'normal',
        'size': 10,
        'family': 'sans-serif',
        'sans-serif': 'Helvetica'
    }
    mpl.rc('font', **font)
    mpl.rcParams['axes.linewidth'] = 0.3
    mpl.rcParams['xtick.major.width'] = 0.3
    mpl.rcParams['xtick.minor.width'] = 0.3
    mpl.rcParams['ytick.major.width'] = 0.3
    mpl.rcParams['ytick.minor.width'] = 0.3
    mpl.rcParams['grid.linewidth'] = 0.5
    mpl.rcParams['grid.linestyle'] = ':'

    # __________________ FDC Modelled __________________

    # Create a sub-figure for the hydrograph
    fig1 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig1.semilogy(mod_frequencies, mod_flows, color='#898989', label='Modelled', linewidth=0.7)
    fig1.semilogy(obs_frequencies, obs_flows, color='#ffc511', label='Observed', linewidth=0.7)

    fig1.patch.set_facecolor('none')

    fig1.yaxis.set_ticks_position('left')
    fig1.xaxis.set_ticks_position('bottom')

    for label in fig1.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.set_xlabel("Fraction of flow equalled or exceeded (-)")
    fig1.set_ylabel(u"River Discharge (m{}/s)".format(u"\u00B3"))
    fig1.legend(loc='center', bbox_to_anchor=(0.9, 0.9), frameon=False)

    # __________________ Save __________________

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.fdc.log.pdf'.format(out_folder, catchment, gauged_wb),
                format='pdf', facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == '__main__':
    # Define the root of the CSF
    csf_root = os.path.realpath('../..')  # move to parent directory of this current python file

    # Collect the arguments of the program call
    parser = argparse.ArgumentParser(description="simulate hydrology and water quality "
                                                 "for one catchment and one time period")
    parser.add_argument('catchment', type=str,
                        help="name of the catchment")
    parser.add_argument('outlet', type=str,
                        help="european code of the catchment outlet [format IE_XX_##X######]")
    parser.add_argument('gauge', type=str,
                        help="code of the hydrometric gauge [5-digit code]")
    parser.set_defaults(add_up=True)

    args = parser.parse_args()

    # Run the main() function
    main(args.catchment, args.outlet, args.gauge, csf_root)
