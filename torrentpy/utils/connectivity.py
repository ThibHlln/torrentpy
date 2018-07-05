# -*- coding: utf-8 -*-

# This file is part of TORRENTpy - An open-source tool for TranspORt thRough the catchmEnt NeTwork
# Copyright (C) 2018  Thibault Hallouin (1)
#
# (1) Dooge Centre for Water Resources Research, University College Dublin, Ireland
#
# TORRENTpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TORRENTpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TORRENTpy. If not, see <http://www.gnu.org/licenses/>.

from csv import DictReader, writer
import os
try:
    from graphviz import Digraph
except ImportError:
    Digraph = None


def network_from_connectivity(in_fld, catchment, outlet, plot=False):

    dict_network, list_nodes = _create_network(
        _read_connectivity_file('{}{}_{}.connectivity'.format(in_fld, catchment, outlet)),
        outlet
    )

    _write_nodes_links_network_in_csv(
        '{}{}_{}.network'.format(in_fld, catchment, outlet),
        dict_network
    )

    if plot:
        _plot_graph_network(
            '{}{}_{}'.format(in_fld, catchment, outlet),
            dict_network,
            list_nodes,
            _read_waterbodies_file('{}{}_{}.waterbodies'.format(in_fld, catchment, outlet))
        )


def _write_nodes_links_network_in_csv(file_path, dict_link_and_surrounding_nodes):
    """
    This function creates a CSV file describing the hydrological connectivity as a nodes-links network.
    It creates one line per waterbody. The first column contains the 'NodeDown' as a 4-digit code,
    the second the 'WaterBody' name, and the third column the 'NodeUp' as a 4-digit code.

    :param dict_link_and_surrounding_nodes: key: waterbody, val: tup(code of node downstream, code of node upstream)
    :type dict_link_and_surrounding_nodes: dict
    :param file_path: location where to save the CSV file
    :type file_path: str
    """
    with open(file_path, 'wb') as my_file:
        my_writer = writer(my_file, delimiter=',')
        my_writer.writerow(['NodeDown', 'WaterBody', 'NodeUp'])
        for key in dict_link_and_surrounding_nodes:
            my_writer.writerow([dict_link_and_surrounding_nodes[key][0], key, dict_link_and_surrounding_nodes[key][1]])


def _create_network(list_consecutive_links_up, outlet):
    """
    This function reads a CSV file containing the hydrological connectivity of a given network.
    It can only read CSV file containing the headers 'WaterBody' and 'NeighbourUp'.

    :param list_consecutive_links_up: list of tuples for each couple of connected WaterBodies
    :type list_consecutive_links_up: list
    :param outlet: name of the outlet WaterBody
    :type outlet: list
    :return: a dictionary with key: waterbody, val: tup(code of node downstream, code of node upstream)
    :rtype: dict
    """
    list_nodes = list()
    dict_consecutive_links_down = dict()
    dict_link_to_node_down = dict()
    dict_link_and_surrounding_nodes = dict()
    future_rivers = list()

    for tup in list_consecutive_links_up:
        dict_consecutive_links_down[tup[1]] = tup[0]

    # create the nodes-links network by defining the nodes codes and linking nodes with up link and down link
    river_outlet = [outlet]
    node_code = 0
    dict_link_to_node_down[outlet] = '%04d' % node_code  # format integer to get a 4-digit code
    list_nodes.append('%04d' % node_code)

    rivers = river_outlet[:]

    while rivers:
        for river in rivers:
            node_code += 1
            list_nodes.append('%04d' % node_code)
            dict_link_and_surrounding_nodes[river] = (dict_link_to_node_down[river], '%04d' % node_code)
            for key in dict_consecutive_links_down:
                if dict_consecutive_links_down[key] == river:
                    dict_link_to_node_down[key] = '%04d' % node_code
                    future_rivers.append(key)
        del rivers[:]
        rivers = future_rivers[:]
        del future_rivers[:]

    return dict_link_and_surrounding_nodes, list_nodes


def _read_connectivity_file(file_path):
    """
    This function reads a CSV file containing the hydrological connectivity of a given network.
    It can only read CSV file containing the headers 'WaterBody' and 'NeighbourUp'.

    :param file_path: location of the CSV file containing the hydrological connectivity of the network
    :type file_path: str
    :return: all the tuples ( "WaterBodyDown", "WaterBodyUp" ) in the connectivity file
    :rtype: list
    """
    list_consecutive_links_up = list()

    with open(file_path) as my_file:
        my_reader = DictReader(my_file)
        for line in my_reader:
            try:
                list_consecutive_links_up.append((line['WaterBody'], line['NeighbourUp']))
            except KeyError:
                raise Exception("The headers of the connectivity file do not comply with 'WaterBody' and ' NeighbourUp")

    return list_consecutive_links_up


def _plot_graph_network(path_for_plot, dict_link_and_surrounding_nodes, list_nodes, dict_waterbodies):
    """
    This function creates a visual representation of the nodes-links network in the form of a PDF document.
    Using the package 'graphviz', this function also outputs a second file (without extension) which is
    the DOT source code for this nodes-links network.

    N.B.: nodes are called 'nodes' in graphviz, while links are called 'edges'

    :param path_for_plot: location where the PDF and DOT source code file should be saved
    :type path_for_plot: str
    :param dict_link_and_surrounding_nodes: key: WaterBody, val: tup(code of node downstream, code of node upstream)
    :type dict_link_and_surrounding_nodes: dict
    :param list_nodes: list of the 4-digit codes in the network
    :type list_nodes: list
    :param dict_waterbodies: dict ( key: WaterBody,
        value: tup( WaterBody Type [1 for river, 2 for lake], OPTIONAL Headwater Status [1 for True, 0 for False] )
    :type dict_waterbodies: dict
    :return: NOTHING, only creates PDF file and DOT source code file
    """
    # check if graphviz is available
    if not Digraph:
        raise Exception("Setting the argument 'plot' to True in util 'network_from_connectivity' "
                        "requires the package 'graphviz', please install it and retry, "
                        "or do use this optional argument.")

    # Using GraphViz to visualise the graph structure
    my_graph = Digraph(format='pdf', comment='Catchment')

    for node in list_nodes:
        my_graph.node(node, fontcolor='white', fontname='helvetica', fontsize='11.0',
                      color='#7f7f7f', style='filled', fillcolor='#7f7f7f')

    for river in dict_link_and_surrounding_nodes:
        if dict_waterbodies[river][0] == 1:  # it is a river
            my_graph.edge(dict_link_and_surrounding_nodes[river][1], dict_link_and_surrounding_nodes[river][0],
                          label=river, color='#2d74b6', fontcolor='#2d74b6', fontsize='11.0', fontname='helvetica')
        elif dict_waterbodies[river][0] == 2:  # it is a lake
            my_graph.edge(dict_link_and_surrounding_nodes[river][1], dict_link_and_surrounding_nodes[river][0],
                          label=river, color='#203864', fontcolor='#203864', fontsize='11.0', fontname='helvetica')
        else:  # it is something else
            my_graph.edge(dict_link_and_surrounding_nodes[river][1], dict_link_and_surrounding_nodes[river][0],
                          label=river, color='black', fontcolor='black', fontsize='11.0', fontname='helvetica')

    # print my_graph.source

    my_graph.render(path_for_plot)  # create pdf
    if os.path.isfile(path_for_plot + '.gv'):
        os.remove(path_for_plot + '.gv')
    os.rename(path_for_plot, path_for_plot + '.gv')  # .gv is an extension for DOT files


def _read_waterbodies_file(file_path):
    """
    This function reads a CSV file containing the waterbodies of a given network.

    :param file_path: location of the CSV file containing the waterbodies of the network
    :type file_path: str
    :return: dictionary containing:
        key: "WaterBody",
        value: tup( WaterBody Type [1 for river, 2 for lake], OPTIONAL Headwater Status [1 for True, 0 for False] )
    :rtype: dict
    """
    dict_waterbodies = dict()

    with open(file_path) as my_file:
        my_reader = DictReader(my_file)

        for line in my_reader:
            if line.get('HeadwaterStatus'):
                dict_waterbodies[line['WaterBody']] = (int(line['WaterBodyTypeCode']), int(line['HeadwaterStatus']))
            else:
                dict_waterbodies[line['WaterBody']] = (int(line['WaterBodyTypeCode']),)

    return dict_waterbodies
