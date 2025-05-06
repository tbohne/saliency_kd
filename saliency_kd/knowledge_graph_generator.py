#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid

from nesy_diag_ontology.fact import Fact
from owlready2 import *
from rdflib import Namespace, RDF

from saliency_kd.config import FUSEKI_URL, ONTOLOGY_PREFIX
from saliency_kd.connection_controller import ConnectionController

SYMBOLIC_FAULT_INFO = {
    1: {
        "name": "class_1",
        "fault_desc": "no obvious positive / negative peaks; on average, the signal roughly ends how it started",
        "severity": "X"
    }
}


class KnowledgeGraphGenerator:
    """
    Populates the ontology with instance data.
    """

    def __init__(self, kg_url: str = FUSEKI_URL, verbose: bool = True) -> None:
        """
        Initializes the KG generator.

        :param kg_url: URL of the knowledge graph server
        :param verbose: whether the ontology instance generator should log its actions
        """
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url, verbose=verbose)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.verbose = verbose

    def extend_knowledge_graph_with_sensor_fault_data(self, name: str, fault_desc: str, severity: str) -> None:
        """
        Extends the knowledge graph with semantic facts based on the present sensor fault information.

        :param name: name of the sensor fault
        :param fault_desc: description of the sensor fault
        :param severity: severity of the sensor fault
        """
        sensor_fault_uuid = "sensor_fault_" + str(uuid.uuid4())
        fact_list = [
            Fact((sensor_fault_uuid, RDF.type, self.onto_namespace["SensorFault"].toPython())),
            Fact((sensor_fault_uuid, self.onto_namespace.name, name), property_fact=True),
            Fact((sensor_fault_uuid, self.onto_namespace.severity, severity), property_fact=True),
            Fact((sensor_fault_uuid, self.onto_namespace.fault_desc, fault_desc), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    kg_gen = KnowledgeGraphGenerator()
    kg_gen.extend_knowledge_graph_with_sensor_fault_data(
        SYMBOLIC_FAULT_INFO[1]['name'], SYMBOLIC_FAULT_INFO[1]['fault_desc'], SYMBOLIC_FAULT_INFO[1]['severity']
    )
