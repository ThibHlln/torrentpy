import numpy
import scipy.stats
import logging
from itertools import izip

from scripts.simuClasses import *
import postprocPlot as ppP
import scripts.simuRunSingle as sRS
import scripts.simuFiles as sF


def main(catchment, outlet, gauge):
    # Format given parameters
    catchment = catchment.capitalize()
    outlet = outlet.upper()

    # Location of the different needed directories
    root = "C:/PycharmProjects/Python/CatchmentSimulationFramework/"
    os.chdir(root)  # define parent directory as root in order to use only relative paths after this
    spec_directory = "scripts/specs/"
    input_directory = "in/"
    output_directory = "out/"

    # Check if combination catchment/outlet is coherent by using the name of the input folder
    if not os.path.exists("{}{}_{}".format(input_directory, catchment, outlet)):
        raise Exception("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Set up the plotting session (either with .simulation file or through the console)
    data_datetime_start, data_datetime_end, data_time_step_in_min, \
        simu_datetime_start, simu_datetime_end, simu_time_step_in_min, \
        plot_datetime_start, plot_datetime_end = \
        ppP.set_up_plotting(catchment, outlet, input_directory)

    # Precise the specific folders to use in the directories
    input_folder = "{}{}_{}/".format(input_directory, catchment, outlet)
    output_folder = "{}{}_{}_{}_{}/".format(output_directory, catchment, outlet,
                                            simu_datetime_start.strftime("%Y%m%d"),
                                            simu_datetime_end.strftime("%Y%m%d"))

    # Determine gauged waterbody associated to the hydrometric gauge
    gauged_waterbody, gauged_area = ppP.find_waterbody_from_gauge(input_folder, catchment, outlet, gauge)

    # Create a logger
    sRS.setup_logger(
        catchment, gauged_waterbody, 'SinglePerformance.main', 'performance', output_folder, is_single_run=True)
    logger = logging.getLogger('SinglePerformance.main')
    logger.warning("Starting performance assessment for {} {} {}.".format(catchment, outlet, gauge))

    # Create a Network object from network and waterBodies files
    my_df_info = pandas.read_csv('{}{}_{}.information'.format(output_folder, catchment, outlet), index_col=0)
    if my_df_info.get_value('AddUp', 'Value') == 'True':
        adding_up = True
    else:
        adding_up = False
    my__network = Network(catchment, outlet, input_folder, spec_directory, adding_up=adding_up)

    # Collect the observed (OBS) and modelled (MOD) discharge data
    df_flows_obs = pandas.read_csv('{}{}_{}_{}.flow'.format(output_folder, catchment, gauged_waterbody, gauge))
    df_flows_mod = pandas.read_csv('{}{}_{}.outputs'.format(output_folder, catchment, gauged_waterbody))

    nda_flows_obs = df_flows_obs['flow'].values
    if my__network.modeUp:
        nda_flows_mod = df_flows_mod['r_out_q_h2o'].values
    else:
        nda_flows_mod = df_flows_mod['r_out_q_h2o'].values + df_flows_mod['c_out_q_h2o'].values

    # Assess the performance of the model
    my_dict_results = dict()
    logger.info("Calculating rate of missing observations.")
    my_dict_results['PercentMissing'] = calculate_missing(nda_flows_obs)
    logger.info("Calculating upstream drainage area.")
    my_dict_results['DrainageArea'] = calculate_drainage_area(
        my__network, input_folder, catchment, outlet, gauged_waterbody)

    if my_dict_results['PercentMissing'] <= 30.0:
        logger.info("Calculating Nash-Sutcliffe efficiency (NSE).")
        my_dict_results['NSE'] = calculate_nse(nda_flows_obs, nda_flows_mod)
        logger.info("Calculating BIAS.")
        my_dict_results['BIAS'] = calculate_bias(nda_flows_obs, nda_flows_mod)
        logger.info("Calculating modified NSE (C2M).")
        my_dict_results['C2M'] = calculate_c2m(nda_flows_obs, nda_flows_mod)
    else:
        my_dict_results['NSE'] = -999.0
        my_dict_results['BIAS'] = -999.0
        my_dict_results['C2M'] = -999.0

    my_df_results = pandas.DataFrame.from_dict(my_dict_results, orient='index')
    my_df_results.index.name = "Indicator"
    my_df_results.columns = ["Value"]
    my_df_results.to_csv('{}{}_{}.performance'.format(output_folder, catchment, gauged_waterbody), sep=',')

    # Generate flow duration curve
    logger.info("Calculating flow frequencies.")
    flows_obs, flows_mod = listwise_deletion(nda_flows_obs, nda_flows_mod)
    flows_obs_ord, flows_freq_obs = calculate_flow_frequency(flows_obs)
    flows_mod_ord, flows_freq_mod = calculate_flow_frequency(flows_mod)

    logger.info("Plotting Flow Duration Curve.")
    ppP.plot_flow_duration_curve(flows_obs_ord, flows_freq_obs,
                                 flows_mod_ord, flows_freq_mod,
                                 output_folder, catchment, gauged_waterbody, gauge)
    logger.info("Plotting Logarithmic Flow Duration Curve.")
    ppP.plot_flow_duration_curve_log(flows_obs_ord, flows_freq_obs,
                                     flows_mod_ord, flows_freq_mod,
                                     output_folder, catchment, gauged_waterbody, gauge)

    logger.warning("Ending performance assessment for {} {} {}.".format(catchment, outlet, gauge))


def calculate_missing(flows, criterion=-99.0):
    total_length = len(flows)
    # Count the steps that are missing values
    length_not_missing = 0.0
    for a in flows:
        if not a == criterion:
            length_not_missing += 1.0
    # Calculate percentage of missing values
    missing = (total_length - length_not_missing) / total_length * 100.0

    return missing


def calculate_drainage_area(my__network, in_folder, catchment, outlet, gauged_wb):
    # Find all the waterbodies upstream of the gauge, including the gauged waterbody
    all_wb = ppP.determine_gauging_zone(my__network, in_folder, catchment, outlet, gauged_wb)
    # Collect the catchment descriptors
    my_dict_desc = sF.get_nd_from_file(my__network, in_folder, extension='descriptors', var_type=float)
    # Calculate the total upstream drainage area using the descriptor files
    drainage_area = 0.0
    for waterbody in all_wb:
        drainage_area += my_dict_desc[waterbody]['area']

    return drainage_area


def delete_missing(flows, criterion=-99.0):
    # Remove the steps that are missing values
    list_val = list()
    for a in flows:
        if not a == criterion:
            list_val.append(a)
    nda_flows_val = numpy.asarray(list_val)

    return nda_flows_val


def listwise_deletion(flows_obs, flows_mod, criterion=-99.0):
    # Remove the steps that are missing observations
    list_obs = list()
    list_mod = list()
    for a, b in izip(flows_obs, flows_mod):
        if not a == criterion:
            list_obs.append(a)
            list_mod.append(b)
    nda_flows_obs = numpy.asarray(list_obs)
    nda_flows_mod = numpy.asarray(list_mod)

    return nda_flows_obs, nda_flows_mod


def calculate_nse(flows_obs, flows_mod):

    # Remove the steps that are missing observations
    nda_flows_obs, nda_flows_mod = listwise_deletion(flows_obs, flows_mod)

    # calculate mean of observations
    mean_flow_obs = numpy.mean(nda_flows_obs)

    # calculate Nash-Sutcliffe Efficiency
    nse = 1 - (numpy.sum((nda_flows_obs - nda_flows_mod) ** 2) / numpy.sum((nda_flows_obs - mean_flow_obs) ** 2))

    return nse


def calculate_bias(flows_obs, flows_mod):

    # Remove the steps that are missing observations
    nda_flows_obs, nda_flows_mod = listwise_deletion(flows_obs, flows_mod)

    # calculate bias
    bias = numpy.sum(nda_flows_obs - nda_flows_mod) / numpy.sum(nda_flows_obs)

    return bias


def calculate_c2m(flows_obs, flows_mod):

    # Remove the steps that are missing observations
    nda_flows_obs, nda_flows_mod = listwise_deletion(flows_obs, flows_mod)

    # calculate mean of observations
    mean_flow_obs = numpy.mean(nda_flows_obs)

    # calculate C2M, bounded formulation of NSE
    f = numpy.sum((nda_flows_obs - nda_flows_mod) ** 2)
    f0 = numpy.sum((nda_flows_obs - mean_flow_obs) ** 2)
    c2m = (1 - (f / f0)) / (1 + (f / f0))

    return c2m


def calculate_flow_frequency(flows):

    # order the flows from slowest to quickest
    flows_ordered = numpy.sort(flows)
    # rank the flows
    flows_ranked = scipy.stats.rankdata(flows_ordered, method='max')
    # calculate rank complementary
    flows_ranked_comp = (len(flows) + 1) - flows_ranked
    # calculate frequency
    flow_frequencies = flows_ranked_comp / float(len(flows))

    return flows_ordered, flow_frequencies


if __name__ == '__main__':
    my_catchment = raw_input('Name of the catchment? ')
    my_outlet = raw_input('European Code (EU_CD) of the catchment? [format IE_XX_##X######] ')
    my_gauge = raw_input('Code of the hydrometric gauge? [#####] ')
    main(my_catchment, my_outlet, my_gauge)
