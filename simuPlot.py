import matplotlib.pyplot as plt
import csv
import time
import datetime
import calendar
import sys
import os
import logging
from pandas import DataFrame
import pandas
import numpy as np
from matplotlib import dates

from simuClasses import *
import simuFiles as sF


def main():
    # Location of the different needed folders
    root = os.path.realpath('..')  # move to parent directory of this current python file
    os.chdir(root)  # define parent directory as root in order to use only relative paths after this
    specifications_folder = "specs/"
    input_folder = "in/"
    output_folder = "out/"

    # Ask user for information on simulation
    question_catch = raw_input('Name of the catchment? ')
    catchment = question_catch.capitalize()

    question_outlet = raw_input('European Code (EU_CD) of the catchment? [format IE_XX_##X######] ')
    outlet = question_outlet.upper()

    if not os.path.isfile('{}{}_{}.network'.format(input_folder, catchment, outlet)):
        # Check if combination catchment/outlet is coherent by using the name of the network file
        sys.exit("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Create a logger
    # # Logger levels: debug < info < warning < error < critical
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create a file handler
    if os.path.isfile('{}{}_{}.log'.format(output_folder, catchment, outlet)):
        os.remove('{}{}_{}.log'.format(output_folder, catchment, outlet))
    handler = logging.FileHandler('{}{}_{}.log'.format(output_folder, catchment, outlet))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}.simulation".format(input_folder, catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()
        logger.info("There is not {}{}_{}.simulation available.".format(input_folder, catchment, outlet))

    try:
        question_start_data = my_answers_df.loc['start_datetime_simu', 'ANSWER']
    except KeyError:
        question_start_data = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_end_data = my_answers_df.loc['end_datetime_simu', 'ANSWER']
    except KeyError:
        question_end_data = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_data_time_step = my_answers_df.loc['data_time_step_min', 'ANSWER']
    except KeyError:
        question_data_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        data_time_step_in_min = float(int(question_data_time_step))
    except ValueError:
        sys.exit("The data time step is invalid. [not an integer]")

    try:
        question_simu_time_step = my_answers_df.loc['simu_time_step_min', 'ANSWER']
    except KeyError:
        question_simu_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        simu_time_step_in_min = float(int(question_simu_time_step))
    except ValueError:
        sys.exit("The time step is invalid. [not an integer]")

    try:
        question_start_plot = my_answers_df.loc['start_datetime_plot', 'ANSWER']
    except KeyError:
        question_start_plot = raw_input('Starting date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_plot = datetime.datetime.strptime(question_start_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The plot starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    try:
        question_end_plot = my_answers_df.loc['end_datetime_plot', 'ANSWER']
    except ValueError:
        question_end_plot = raw_input('Ending date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_plot = datetime.datetime.strptime(question_end_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        sys.exit("The plot ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    logger.info("{} # Initialising.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    # Create a TimeFrame object
    my__time_frame = TimeFrame(datetime_start_data, datetime_end_data,
                               int(data_time_step_in_min), int(simu_time_step_in_min))

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, specifications_folder)

    # Plot the desired graphs
    plot_daily_hydro_hyeto(my__network, my__time_frame,
                           input_folder, output_folder, catchment, outlet,
                           datetime_start_plot, datetime_end_plot,
                           logger)


def plot_daily_hydro_hyeto(my__network, my__time_frame,
                           in_folder, out_folder, catchment, outlet,
                           dt_start_plot, dt_end_plot,
                           logger):

    logger.info("{} # Reading results files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    # Get the average rainfall data over the catchment
    my_rain_mm = np.empty(shape=(len(my__time_frame.series_data), 0), dtype=np.float64)
    my_area_m2 = np.empty(shape=(0, 1), dtype=np.float64)

    my_dict_desc = sF.get_dict_floats_from_file("descriptors", catchment, outlet, my__network, in_folder)
    for link in my__network.links:
        try:
            my_df_inputs = pandas.read_csv("{}{}_{}.inputs".format(out_folder, catchment, link), index_col=0)
        except IOError:
            sys.exit("No inputs summary for {}_{} in {}.".format(catchment, link, out_folder))
        my_rain_mm = np.c_[my_rain_mm, np.asarray(my_df_inputs['c_in_rain'].tolist())]

        my_area_m2 = np.r_[my_area_m2, np.array([[my_dict_desc[link]['area']]])]
    my_rain_m = my_rain_mm / 1e3  # convert mm to m of rainfall
    catchment_area = np.sum(my_area_m2)  # get the total area of the catchment
    rainfall = my_rain_m.dot(my_area_m2)  # get a list of catchment rainfall in m3
    rainfall *= 1e3/catchment_area  # get rainfall in mm

    # Get the simulated flow at the outlet of the catchment
    simu_flow_m3s = np.empty(shape=(len(my__time_frame.series_data), 0), dtype=np.float64)
    my_df_node = pandas.read_csv("{}{}_0000.node".format(out_folder, catchment), index_col=0)
    simu_flow_m3s = np.c_[simu_flow_m3s, np.asarray(my_df_node['q_h2o'].tolist())]

    # Get the measured flow near the outlet of the catchment
    gauged_flow_m3s = np.empty(shape=(len(my__time_frame.series_data), 0), dtype=np.float64)
    gauged_flow_m3s = \
        np.c_[gauged_flow_m3s,
              np.asarray(pandas.read_csv("{}{}_{}.flow".format(out_folder, catchment, outlet),
                                         index_col=0)['flow'].tolist())]

    logger.info("{} # Plotting.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    # Plot

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')

    dt_start_data = my__time_frame.series_data[1]
    dt_end_data = my__time_frame.series_data[-1]

    pyplot_start_data = dates.date2num(dt_start_plot)
    pyplot_end_data = dates.date2num(dt_end_plot)

    if dt_start_data <= dt_start_plot:
        start_diff = dt_start_plot - dt_start_data
        index_start = 1 + start_diff.days
    else:
        sys.exit("The start date for plotting is out of bound.")

    if dt_end_plot <= dt_end_data:
        end_diff = dt_end_data - dt_end_plot
        index_end = - (1 + end_diff.days)
    else:
        sys.exit("The end date for plotting is out of bound.")

    # __________________ Hyetograph __________________

    # Create a sub-figure for the hyetograph
    fig1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])  # give location of the graph (%: from left, from bottom, width, height)

    fig1.bar(my__time_frame.series_data[index_start:index_end], rainfall[index_start:index_end],
             label='Hyetograph', width=1.0, facecolor='#4ec4f2', edgecolor='#4ec4f2')
    fig1.patch.set_facecolor('none')

    # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    ax1 = plt.axis()
    # Set the limits of the axes (here also invert the y-axis by swapping [2] & [3]
    plt.axis((pyplot_start_data, pyplot_end_data, ax1[3]+1, ax1[2]))

    fig1.spines['left'].set_visible(False)  # Remove axis line
    fig1.spines['bottom'].set_visible(False)
    # fig1.get_xaxis().set_visible(False)  # Remove X axis values labels and graduations
    fig1.get_xaxis().set_ticklabels([])  # Remove X axis values only
    # fig1.get_yaxis().set_ticks([])  # Remove Y axis graduations only

    fig1.yaxis.set_ticks_position('right')  # Choose location of axis (value + line): can take left, right, both
    fig1.yaxis.set_label_position('right')
    # fig1.set_yticks([0, 20, 40, 60, 80])  # Set customised graduations of the Y axis
    fig1.set_ylabel('Rainfall (mm)')
    fig1.yaxis.grid(b=True, which='major', linestyle=':')

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.xaxis.set_ticks_position('top')

    # __________________ Hydrograph __________________

    # Create a sub-figure for the hydrograph
    fig2 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig2.plot(my__time_frame.series_data[index_start:index_end], simu_flow_m3s[index_start:index_end], color='#898989')

    # Plot the measured flows as points
    fig2.plot(my__time_frame.series_data[index_start:index_end], gauged_flow_m3s[index_start:index_end],
              'x', markersize=2.0, label='Measured Flows', color='#ffc511')

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

    # fig2.set_yticks([0, 10, 20, 30, 40, 50])

    # fig2.set_xlabel("Time")
    fig2.set_ylabel(u"River Discharge at the outlet (m{}/s)".format(u"\u00B3"))
    # fig2.set_ylabel("River Discharge at the outlet (mm)")

    # leg = fig2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), frameon=False)

    # __________________ Display and Save __________________

    # Show in Tkinter
    # plt.show()

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.png'.format(out_folder, catchment, outlet),
                dpi=1500, facecolor=fig.get_facecolor(), edgecolor='none')


if __name__ == '__main__':
    main()
