#!/usr/bin/env python

import argparse
from collections import defaultdict
import json
import networkx as nx
import requests
import responses
import sys
import time


def add_new_node(graph, label, version=""):
    if graph.has_node(label) and version == "":
        return
    graph.add_node(label, label=label, version=version)


def add_new_edge(graph, u, v, bytes_transferred):
    if graph.has_edge(u, v):
        return
    graph.add_edge(u, v, bytes_transferred=bytes_transferred)


def next_peer(direction_tag, node_info):
    if direction_tag in node_info and node_info[direction_tag]:
        for peer in node_info[direction_tag]:
            yield peer


def get_next_peers(topology):
    results = []
    for key in topology:

        curr = topology[key]
        if curr is None:
            continue

        for peer in next_peer("inboundPeers", curr):
            results.append(peer["nodeId"])

        for peer in next_peer("outboundPeers", curr):
            results.append(peer["nodeId"])

    return results


def update_results(graph, parent_info, parent_key, results, is_inbound):
    direction_tag = "inboundPeers" if is_inbound else "outboundPeers"
    for peer in next_peer(direction_tag, parent_info):
        other_key = peer["nodeId"]

        results[direction_tag][other_key] = peer
        add_new_node(graph, parent_key)
        add_new_node(graph, other_key, peer["version"])
        add_new_edge(graph, parent_key, other_key, peer["bytesWritten"] + peer["bytesRead"])

    if "numTotalInboundPeers" in parent_info:
        results["totalInbound"] = parent_info["numTotalInboundPeers"]
    if "numTotalOutboundPeers" in parent_info:
        results["totalOutbound"] = parent_info["numTotalOutboundPeers"]


def send_requests(peer_list, params, requestUrl):
    for key in peer_list:
        params["node"] = key
        requests.get(url=requestUrl, params=params)


def check_results(data, graph, merged_results):
    if "topology" not in data:
        raise ValueError("stellar-core is missing survey nodes."
                         "Are the public keys surveyed valid?")

    topology = data["topology"]

    for key in topology:

        curr = topology[key]
        if curr is None:
            continue

        merged = merged_results[key]

        update_results(graph, curr, key, merged, True)
        update_results(graph, curr, key, merged, False)

    return get_next_peers(topology)


def write_graph_stats(graph, outputFile):
    stats = {}
    stats[
        "average_shortest_path_length"
    ] = nx.average_shortest_path_length(graph)
    stats["average_clustering"] = nx.average_clustering(graph)
    stats["clustering"] = nx.clustering(graph)
    stats["degree"] = dict(nx.degree(graph))
    with open(outputFile, 'w') as outfile:
        json.dump(stats, outfile)


def analyze(args):
    G = nx.read_graphml(args.graphmlAnalyze)
    write_graph_stats(G, args.graphStats)
    sys.exit(0)


def run_survey(args):
    G = nx.Graph()
    merged_results = defaultdict(lambda: {
        "totalInbound": 0,
        "totalOutbound": 0,
        "inboundPeers": {},
        "outboundPeers": {}
    })

    URL = args.node

    PEERS = URL + "/peers"
    SURVEY_REQUEST = URL + "/surveytopology"
    SURVEY_RESULT = URL + "/getsurveyresult"
    STOP_SURVEY = URL + "/stopsurvey"

    duration = int(args.duration)
    PARAMS = {'duration': duration}

    add_new_node(G,
                 requests
                 .get(URL + "/scp?limit=0&fullkeys=true")
                 .json()
                 ["you"],
                 requests.get(URL + "/info").json()["info"]["build"])

    # reset survey
    r = requests.get(url=STOP_SURVEY)

    peer_list = []
    if args.nodeList:
        # include nodes from file
        f = open(args.nodeList, "r")
        for node in f:
            peer_list.append(node.rstrip('\n'))

    PEERS_PARAMS = {'fullkeys': "true"}
    r = requests.get(url=PEERS, params=PEERS_PARAMS)

    data = r.json()
    peers = data["authenticated_peers"]

    # seed initial peers off of /peers endpoint
    if peers["inbound"]:
        for peer in peers["inbound"]:
            peer_list.append(peer["id"])
    if peers["outbound"]:
        for peer in peers["outbound"]:
            peer_list.append(peer["id"])

    sent_requests = set()

    while True:
        send_requests(peer_list, PARAMS, SURVEY_REQUEST)

        for peer in peer_list:
            sent_requests.add(peer)

        peer_list = []

        # allow time for results
        time.sleep(1)

        r = requests.get(url=SURVEY_RESULT)
        data = r.json()

        result_node_list = check_results(data, G, merged_results)

        if "surveyInProgress" in data and data["surveyInProgress"] is False:
            break

        # try new nodes
        for key in result_node_list:
            if key not in sent_requests:
                peer_list.append(key)

        # retry for incomplete nodes
        for key in merged_results:
            node = merged_results[key]
            if node["totalInbound"] > len(node["inboundPeers"]):
                peer_list.append(key)
            if node["totalOutbound"] > len(node["outboundPeers"]):
                peer_list.append(key)

    if nx.is_empty(G):
        print("Graph is empty!")
        sys.exit(0)

    write_graph_stats(G, args.graphStats)

    nx.write_graphml(G, args.graphmlWrite)

    with open(args.surveyResult, 'w') as outfile:
        json.dump(merged_results, outfile)


@responses.activate
def run_surey_on_mock_network(args):
    # Mock network has three nodes.
    args.node = "http://127.0.0.1:8080"
    args.duration = 25
    responses.add(responses.GET,
                  "http://127.0.0.1:8080/stopsurvey",
                  json={},
                  status=404)
    with open("mock/peers.json") as peers_json:
        responses.add(responses.GET,
                      "http://127.0.0.1:8080/peers?fullkeys=true",
                      json=json.load(peers_json),
                      status=404)
    with open("mock/scp.json") as scp_json:
        responses.add(responses.GET,
                      "http://127.0.0.1:8080/scp?limit=0&fullkeys=true",
                      json=json.load(scp_json),
                      status=404)
    with open("mock/info.json") as info_json:
        responses.add(responses.GET,
                      "http://127.0.0.1:8080/info",
                      json=json.load(info_json),
                      status=404)
    responses.add(responses.GET,
                  "http://127.0.0.1:8080/surveytopology?duration=25&"
                  "node="
                  "GA52O3SMLSF7NI2L2Q2GG6KIOGZHAHIIRBWKOL2NWN6WUJ7U3PYDG4TS",
                  json={},
                  status=404)
    responses.add(responses.GET,
                  "http://127.0.0.1:8080/surveytopology?duration=25&"
                  "node="
                  "GB54X4OZVHLN5J3ILF5UZBIXJSBR4M23WBQRUFFL7DDFJIZ5FKIBLP7Y",
                  json={},
                  status=404)
    with open('mock/getsurveyresult.json') as result_json:
        responses.add(responses.GET,
                      'http://127.0.0.1:8080/getsurveyresult',
                      json=json.load(result_json),
                      status=404)
    run_survey(args)


def main():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-gs",
                    "--graphStats",
                    required=True,
                    help="output file for graph stats")

    subparsers = ap.add_subparsers()

    parser_survey = subparsers.add_parser('survey',
                                          help="run survey and "
                                               "analyze results")
    parser_survey.add_argument("-n",
                               "--node",
                               required=True,
                               help="address of initial survey node")
    parser_survey.add_argument("-d",
                               "--duration",
                               required=True,
                               help="duration of survey in seconds")
    parser_survey.add_argument("-sr",
                               "--surveyResult",
                               required=True,
                               help="output file for survey results")
    parser_survey.add_argument("-gmlw",
                               "--graphmlWrite",
                               required=True,
                               help="output file for graphml file")
    parser_survey.add_argument("-nl",
                               "--nodeList",
                               help="optional list of seed nodes")
    parser_survey.set_defaults(func=run_survey)

    parser_survey = subparsers.add_parser('mocksurvey',
                                          help="run survey and "
                                               "analyze results "
                                               "on a mock network")
    parser_survey.add_argument("-sr",
                               "--surveyResult",
                               required=True,
                               help="output file for survey results")
    parser_survey.add_argument("-gmlw",
                               "--graphmlWrite",
                               required=True,
                               help="output file for graphml file")
    parser_survey.add_argument("-nl",
                               "--nodeList",
                               help="optional list of seed nodes")
    parser_survey.set_defaults(func=run_surey_on_mock_network)

    parser_analyze = subparsers.add_parser('analyze',
                                           help="write stats for "
                                                "the graphml input graph")
    parser_analyze.add_argument("-gmla",
                                "--graphmlAnalyze",
                                help="input graphml file")
    parser_analyze.set_defaults(func=analyze)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
