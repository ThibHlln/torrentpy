import matplotlib.pyplot as plt
import csv
import time
import datetime
import calendar
import pandas
import numpy as np
from matplotlib import dates


def plot_hydro_hyeto(my__network, my__time_frame, dict_meteo, dict_desc, dict__data_frames,
                     in_folder, catchment, outlet,
                     logger):

    # Get the average rainfall data over the catchment
    my_rain_mm = np.empty(shape=(len(my__time_frame.series), 0), dtype=np.float64)
    my_area_m2 = np.empty(shape=(0, 1), dtype=np.float64)

    for link in my__network.links:
        my_rain_mm = np.c_[my_rain_mm, np.asarray(dict_meteo[link]['rain'].tolist())]
        my_area_m2 = np.r_[my_area_m2, np.array([[dict_desc[link]['area']]])]
    my_rain_m = my_rain_mm / 1e3  # convert mm to m of rainfall
    area = np.sum(my_area_m2)  # get the total area of the catchment
    rainfall = my_rain_m.dot(my_area_m2)  # get a list of catchment rainfall in m3
    rainfall *= 1e3/area  # get rainfall in mm

    # Get the simulated flow at the outlet of the catchment
    my_simu_flow_m3s = np.empty(shape=(len(my__time_frame.series), 0), dtype=np.float64)
    my_simu_flow_m3s = np.c_[my_simu_flow_m3s, np.asarray(dict__data_frames['0000']['q_h2o'].tolist())]

    # Get the measured flow near the outlet of the catchment
    my_gauged_flow_m3s = np.empty(shape=(len(my__time_frame.series), 0), dtype=np.float64)
    my_gauged_flow_m3s = \
        np.c_[my_gauged_flow_m3s,
              np.append(np.zeros(shape=(1, 1), dtype=np.float64),
                        [np.asarray(pandas.read_csv("{}{}_{}.flow".format(in_folder, catchment, outlet),
                                                    index_col=0)['FLOW'].tolist())])]
    print 'hello'


    #
    #
    # # __________________ Parameters __________________
    #
    # # Input a string to make steps temporally explicit
    # starting_date = "01/01/2013 09:00:00 UTC"  # Get the timestamp for the starting date
    #
    # # Specify the starting and ending dates for the plot
    # plotting_start_date = "01/01/2013 09:00:00 UTC"
    # plotting_end_date = "01/01/2016 09:00:00 UTC"
    #
    # # Catchment size in sq km
    # catchment_area = 389
    #
    # # Graph Title
    # graph_title = "Hydrograph and Hyetograph for Dee catchment"
    #
    # # File title without extension
    # file_title = "HydroHyeto_Dee"
    #
    #
    # # __________________ Input Data processing __________________
    #
    # step = list()
    # rain_b = list()
    # rain_s = list()
    # flow_b = list()
    # flow_s = list()
    # flow_m = list()
    #
    # # Get the # of steps with their rainfall data and measured flow data
    # with open("inputs.csv", 'r') as my_file:
    #     reader = csv.DictReader(my_file)
    #     for line in reader:
    #         step.append(int(line['Step']))
    #         rain_b.append(float(line['Rain_B']))
    #         rain_s.append(float(line['Rain_S']))
    #         flow_b.append(float(line['Flow_B']) / (catchment_area * 1E+6) * 86400 * 1000)  # Have to convert m3/s into mm
    #         flow_s.append(float(line['Flow_S']) / (catchment_area * 1E+6) * 86400 * 1000)  # Have to convert m3/s into mm
    #         flow_m.append(float(line['Flow_M']) / (catchment_area * 1E+6) * 86400 * 1000)  # Have to convert m3/s into mm
    #
    # # For same steps as above, get simulated flow for all the behavioural parameter sets
    # # with open("outputs.csv", 'r') as my_file2:
    # #     reader2 = csv.reader(my_file2)
    # #     simulated_flow = list(reader2)
    #
    #
    # # __________________ Make Data temporally explicit __________________
    #
    # # Get a timestamp (float) from the string above
    # starting_timestamp = time.mktime(datetime.datetime.strptime(starting_date, "%d/%m/%Y %H:%M:%S %Z").timetuple())
    #
    # # Convert all the elements in step list into timestamp
    # step_timestamp = list()
    # for index in step:
    #     # add number of days from the starting time to starting time
    #     step_datetime_temp = datetime.datetime.utcfromtimestamp(starting_timestamp) + datetime.timedelta(days=index - 1)
    #     # convert datetime object into time tuple
    #     step_timetuple_temp = step_datetime_temp.timetuple()
    #     # convert time tuple to timestamp and add it to the list
    #     step_timestamp.append(calendar.timegm(step_timetuple_temp))
    #
    # step_date = list()
    # for stamp in step_timestamp:
    #     step_date.append(datetime.datetime.fromtimestamp(stamp))
    #
    # step_dict = dict()
    # for eltS, eltD in zip(step, step_date):
    #     step_dict[eltD] = eltS
    #
    # # __________________ Plot __________________
    #
    # # Create a general figure
    # fig = plt.figure(facecolor='white')
    # fig.patch.set_facecolor('#ffffff')
    # # fig.suptitle(graph_title)
    #
    # # Set the start/end for display in graph
    # # (convert string into datetime, THEN convert datetime into numerical value that matplotlib.pyplot.axis is using)
    # my_start_date = datetime.datetime.strptime(plotting_start_date, "%d/%m/%Y %H:%M:%S %Z")
    # my_end_date = datetime.datetime.strptime(plotting_end_date, "%d/%m/%Y %H:%M:%S %Z")
    # my_start_pyplotformat = dates.date2num(my_start_date)
    # my_end_pyplotformat = dates.date2num(my_end_date)
    #
    # my_start_step = step_dict[my_start_date]
    # my_end_step = step_dict[my_end_date]
    #
    # my_start_index = my_start_step - 1
    # my_end_index = my_end_step - 1
    #
    #
    # # __________________ Hyetograph __________________
    #
    # # Create a sub-figure for the hyetograph
    # fig1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])  # give the location of the graph (%: from left, from bottom, width, height)
    #
    # fig1.bar(step_date[my_start_index:my_end_index], rain_b[my_start_index:my_end_index],
    #          label='Hyetograph', width=1.0, facecolor='#4ec4f2', edgecolor='#ababab')
    # fig1.bar(step_date[my_start_index:my_end_index], rain_s[my_start_index:my_end_index],
    #          label='Hyetograph', width=1.0, facecolor='#0e90c3', edgecolor='#3fa3f0')#b5e95a
    # fig1.patch.set_facecolor('none')
    #
    # # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    # ax1 = plt.axis()
    # # Set the limits of the axes (here also invert the y-axis by swapping [2] & [3]
    # plt.axis((my_start_pyplotformat, my_end_pyplotformat, ax1[3]+1, ax1[2]))
    #
    #
    # fig1.spines['left'].set_visible(False)  # Remove axis line
    # fig1.spines['bottom'].set_visible(False)
    # # fig1.get_xaxis().set_visible(False)  # Remove X axis values labels and graduations
    # fig1.get_xaxis().set_ticklabels([])  # Remove X axis values only
    # # fig1.get_yaxis().set_ticks([])  # Remove Y axis graduations only
    #
    # fig1.yaxis.set_ticks_position('right')  # Choose location of axis (value + line): can take left, right, both
    # fig1.yaxis.set_label_position('right')
    # # fig1.set_yticks([0, 20, 40, 60, 80])  # Set customised graduations of the Y axis
    # fig1.set_ylabel('Rainfall (mm)')
    # fig1.yaxis.grid(b=True, which='major', linestyle=':')
    #
    # for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
    #     label.set_color('black')
    #     # label.set_rotation(45)
    #     label.set_fontsize(10)
    #
    # fig1.xaxis.set_ticks_position('top')
    #
    #
    # # __________________ Hydrograph __________________
    #
    # # Create a sub-figure for the hydrograph
    # fig2 = fig.add_axes([0.1, 0.2, 0.8, 0.7])
    #
    # # Plot the simulated flows as lines
    # fig2.plot(step_date[my_start_index:my_end_index], flow_b[my_start_index:my_end_index], color='#898989')
    # fig2.plot(step_date[my_start_index:my_end_index], flow_s[my_start_index:my_end_index], color='#0e73c3')#88c61a
    #
    # # Plot the measured flows as points
    # fig2.plot(step_date[my_start_index:my_end_index], flow_m[my_start_index:my_end_index],
    #           'x', markersize=2.0, label='Measured Flows', color='#ffc511')
    #
    # ax2 = plt.axis()  # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    # plt.axis((my_start_pyplotformat, my_end_pyplotformat, -0.2, ax2[3]))
    #
    # fig2.patch.set_facecolor('none')
    #
    # # fig2.fill_between(x, y, y2, color='#f5b171')  # could be use to fill between MIN curve and MAX curve
    #
    # fig2.spines['right'].set_visible(True)
    # fig2.spines['top'].set_visible(False)
    # fig2.yaxis.set_ticks_position('left')
    # fig2.xaxis.set_ticks_position('bottom')
    #
    # for label in fig2.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
    #     label.set_color('black')
    #     # label.set_rotation(45)
    #     label.set_fontsize(10)
    #
    # for label in fig2.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
    #     label.set_color('black')
    #     # label.set_rotation(45)
    #     label.set_fontsize(10)
    #
    # # fig2.set_yticks([0, 10, 20, 30, 40, 50])
    #
    # # fig2.set_xlabel("Time")
    # # fig2.set_ylabel(u"Discharge (m{}/s)".format(u"\u00B3"))
    # fig2.set_ylabel("River Discharge at the outlet (mm)")
    #
    # # leg = fig2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), frameon=False)
    #
    # # __________________ Display and Save __________________
    #
    # # Show in Tkinter
    # # plt.show()
    #
    # # Save image
    # fig.set_size_inches(11, 6)
    # fig.savefig('{}.png'.format(file_title), dpi=1500, facecolor=fig.get_facecolor(), edgecolor='none')
    #
