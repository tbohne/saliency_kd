#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple

from saliency_kd.config import ONTOLOGY_PREFIX, FUSEKI_URL
from saliency_kd.connection_controller import ConnectionController


class KnowledgeGraphQueryTool:
    """
    Library of predefined SPARQL queries and response processing for accessing useful information stored in
    the knowledge graph hosted on a Fuseki server.
    """

    def __init__(self, kg_url: str = FUSEKI_URL) -> None:
        """
        Initializes the KG query tool.

        :param kg_url: URL of the server hosting the knowledge graph
        """
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url)

    def complete_ontology_entry(self, entry: str) -> str:
        """
        Completes the ontology entry for the specified concept / relation.

        :param entry: ontology entry (concept / relation) to be completed
        :return: completed ontology entry
        """
        return "<" + self.ontology_prefix.replace('#', '#' + entry) + ">"

    def query_all_fault_desc(self, verbose: bool = True) -> List[Tuple[str, str]]:
        """
        Queries all symbolic fault descriptions stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all fault descriptions stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all symbolic fault descriptions")
            print("####################################")
        sensor_fault_entry = self.complete_ontology_entry('SensorFault')
        desc_entry = self.complete_ontology_entry('fault_desc')
        name_entry = self.complete_ontology_entry('name')
        s = f"""
            SELECT ?fault_name ?fault_desc WHERE {{
                ?sensor_fault a {sensor_fault_entry} .
                ?sensor_fault {desc_entry} ?fault_desc .
                ?sensor_fault {name_entry} ?fault_name .
            }}
            """
        return [(row['fault_name']['value'], row['fault_desc']['value'])
                for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_information_by_name(self, name: str, verbose: bool = True) -> List[Tuple[str, str, str]]:
        """
        Queries the symbolic fault information stored in the knowledge graph for the specified fault name.

        :param name: name of the fault
        :param verbose: if true, logging is activated
        :return: fault information stored in the knowledge graph for the specified name
        """
        if verbose:
            print("####################################")
            print("QUERY: all symbolic fault information by name")
            print("####################################")
        sensor_fault_entry = self.complete_ontology_entry('SensorFault')
        desc_entry = self.complete_ontology_entry('fault_desc')
        name_entry = self.complete_ontology_entry('name')
        severity_entry = self.complete_ontology_entry('severity')
        s = f"""
            SELECT ?fault_name ?fault_desc ?severity WHERE {{
                ?sensor_fault a {sensor_fault_entry} .
                ?sensor_fault {desc_entry} ?fault_desc .
                ?sensor_fault {name_entry} ?fault_name .
                ?sensor_fault {severity_entry} ?severity .
                FILTER(STR(?fault_name) = "{name}")
            }}
            """
        return [(row['fault_name']['value'], row['fault_desc']['value'], row['severity']['value'])
                for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    @staticmethod
    def print_res(res: List[str]) -> None:
        """
        Prints the specified query results.

        :param res: list of query results
        """
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool()
    qt.print_res(qt.query_all_fault_desc())
