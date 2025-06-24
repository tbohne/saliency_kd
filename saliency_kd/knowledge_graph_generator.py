#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid

from nesy_diag_ontology.fact import Fact
from owlready2 import *
from rdflib import Namespace, RDF

from saliency_kd.config import FUSEKI_URL, ONTOLOGY_PREFIX
from saliency_kd.connection_controller import ConnectionController

SYMBOLIC_FAULT_INFO_EOGVerticalSignal = {
    1: {
        "name": "class_1",
        "fault_desc": "the signal only significantly increases / decreases over time, not abruptly (comparatively small slope); more or less a fuzzy line that might be increasing or decreasing over time; there might be smaller ups and downs in between",
        "severity": "X"
    },
    2: {  # TODO: not centroid-refined
        "name": "class_2",
        "fault_desc": "very straight beginning, then going up (positive peak @~200), keeping that a while, then going down below the starting values (huge negative drop), stabilizing there",
        "severity": "X"
    },
    3: {  # TODO: not centroid-refined
        "name": "class_3",
        "fault_desc": "very similar to class_2, same structure, but not as extreme - a bit more fuzzy as well, but very hard to distinguish",
        "severity": "X"
    },
    4: {  # TODO: not centroid-refined
        "name": "class_4",
        "fault_desc": "again, very similar to class_2 and class_3 structure-wise, but even weaker and a bit wider between increase and drop; starts relatively straight @~0, peaks @>100, later stabilized @~-100",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "straight, stable start (except noise) @~0, then a significant high-slope drop @~-200, roughly holding that for a period; finally, it rises to a positive peak far above the starting values @~200 with a high slope, stabilizing on the high values roughly below the peak (except noise)",
        "severity": "X"
    },
    6: {  # TODO: not centroid-refined
        "name": "class_6",
        "fault_desc": "more or less straight, then a heavy drop below the starting values, stabilizing on low values, i.e., straight high,  ~90 degree drop, straight low",
        "severity": "X"
    },
    7: {  # TODO: not centroid-refined
        "name": "class_7",
        "fault_desc": "sort of straight, drop, keeping that, increase, starting and ending exactly on the same level - 'bath tub'",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "straight (except noise) for a while @~0, then significantly and steeply up to a peak @~200 before a drop follows briefly back to about the level of the starting values; this is followed by a significant high-slope drop way below the starting values; on this low level @~-200, the signal stabilizes except for noise",
        "severity": "X"
    },
    9: {
        "name": "class_9",
        "fault_desc": "very straight start (except noise), then it goes up to a positive peak, roughly holding that for some time, then high-slope drop way below the starting values, roughly holding that for a while (a little shorter than the positive peak); afterwards, the signal goes up again to the starting values or even slightly above with a high slope, stabilizing there for the rest of the signal (except noise)",
        "severity": "X"
    },
    10: {
        "name": "class_10",
        "fault_desc": "very straight start (except noise) @~0, then a quick drop way below the starting values @~-200 before rising to a significant positive peak (way above the starting values) @~400, roughly holding that for a while; afterwards, an intense drop way below the starting values @~-200; on this minimum level, the signal stabilizes (except noise)",
        "severity": "X"
    },
    11: {  # TODO: not centroid-refined
        "name": "class_11",
        "fault_desc": "straight start, up, holding that for a while, then about twice as much down, holding that as well, and up again - stabilizing roughly on a level like the starting values",
        "severity": "X"
    },
    12: {
        "name": "class_12",
        "fault_desc": "very straight start (except noise) @~0, then the signal goes up to a quick, intense and very high amplitude peak @~400, followed by going down again (not necessarily as steep) to roughly the same level as the starting values (<100 away), i.e., a straight signal with one intense positive peak",
        "severity": "X"
    }
}

SYMBOLIC_FAULT_INFO_ElectricDevices = {
    1: {  # "b" in the paper
        "name": "class_1",
        "fault_desc": "activity only starts towards the end of the signal, two peaks",
        "severity": "X"
    },
    2: {  # "c" in the paper
        "name": "class_2",
        "fault_desc": "no area of inactivity, there's a permanent up and down (oscillation)",
        "severity": "X"
    },
    3: {  # "e" in the paper
        "name": "class_3",
        "fault_desc": "activity leaning towards the second half of the signal, a few peaks, usually larger ones accompanied by smaller ones",
        "severity": "X"
    },
    4: {  # "f" in the paper
        "name": "class_4",
        "fault_desc": "no or little activity in the first half, high activity (peak) towards the end of the signal",
        "severity": "X"
    },
    5: {  # "d" in the paper
        "name": "class_5",
        "fault_desc": "no activity until the very end of the signal, there's a block of high activity (a wider, rectangular shape)",
        "severity": "X"
    },
    6: {  # "g" in the paper
        "name": "class_6",
        "fault_desc": "two peaks in the middle of the signal, the first one larger than the second",
        "severity": "X"
    },
    7: {  # "a" in the paper
        "name": "class_7",  # TODO: hard to distinguish
        "fault_desc": "a lot of activity starting roughly at the middle of the signal, spreading towards the end, some inactivity might be in between",
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
    for class_idx in range(1, len(SYMBOLIC_FAULT_INFO_EOGVerticalSignal.keys()) + 1):
        kg_gen.extend_knowledge_graph_with_sensor_fault_data(
            SYMBOLIC_FAULT_INFO_EOGVerticalSignal[class_idx]['name'],
            SYMBOLIC_FAULT_INFO_EOGVerticalSignal[class_idx]['fault_desc'],
            SYMBOLIC_FAULT_INFO_EOGVerticalSignal[class_idx]['severity']
        )
