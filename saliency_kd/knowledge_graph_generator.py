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
        "fault_desc": "the signal only increases / decreases over time, but not abrupt, relatively small slope); more or less a fuzzy increasing or decreasing line, there might be smaller ups and downs",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "very straight beginning, then going up (positive peak), keeping that a while, then going down below the starting values (huge negative drop), stabilizing there",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "very similar to class_2, same structure, but not as extreme - a bit more fuzzy as well, but very hard to distinguish",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "again, very similar to class_2 and class_3 structure-wise, but even weaker and a bit wider between increase and drop",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "straight, stable start, then significantly drop, holding that for a period, then a positive peak far above the starting values, stabilizing on the high values",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "more or less straight, then a heavy drop below the starting values, stabilizing on low values, i.e., straight high,  ~90 degree drop, straight low",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "sort of straight, drop, keeping that, increase, starting and ending exactly on the same level - 'bath tub'",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "straight for a while, then significantly up, before almost immediately a drop follows roughly back to the starting values; then a slight delay before going significantly below the starting values, holding that",
        "severity": "X"
    },
    9: {
        "name": "class_9",
        "fault_desc": "very straight start, quick dip, then up, holding that, then a drop way below the starting values, holding that, and up again to the starting values or above, stabilizing there",
        "severity": "X"
    },
    10: {
        "name": "class_10",
        "fault_desc": "very straight start, then a quick drop, then rising to a significant positive peak, holding that for a while, then a drop way below the starting values, stabilizing there",
        "severity": "X"
    },
    11: {
        "name": "class_11",
        "fault_desc": "straight start, up, holding that for a while, then about twice as much down, holding that as well, and up again - stabilizing roughly on a level like the starting values",
        "severity": "X"
    },
    12: {
        "name": "class_12",
        "fault_desc": "very straight start, then a quick, intense and VERY high amplitude peak (up and down again) - very straight after again on the same level or slightly below starting values",
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
    for class_idx in range(1, 13):
        kg_gen.extend_knowledge_graph_with_sensor_fault_data(
            SYMBOLIC_FAULT_INFO[class_idx]['name'],
            SYMBOLIC_FAULT_INFO[class_idx]['fault_desc'],
            SYMBOLIC_FAULT_INFO[class_idx]['severity']
        )
