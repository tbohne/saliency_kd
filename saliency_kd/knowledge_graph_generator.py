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

SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll = {  # concatenated roll, pitch and yaw accelerations
    1: {
        "name": "class_1",
        "fault_desc": "potentially straight (noisy), then steadily up towards a peak, then quickly down below the starting values and a bit noisy up again; steady but noisy rise, at some point straight before way more up to a peak, then heavily down again; being low, then rising steadily towards a peak, then slightly down to a plateau, then noisy ups and downs",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "straight, then drop to bottom, up again towards a peak, down a bit and up to another peak; drop down and up again, straight, down again, then a small-slope noisy increase until a peak; going down from the peak, noisy, but relatively stable, only relatively minor ups and downs, some peaks",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "starting low, slowly but steadily going up to a positive peak or plateau, afterwards down again; very straight plateau, then going upwards to a noisy peak, then down and straight noisy plateau; then up again to some noisy peak, afterwards noisy down again;",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "starting high, very small slope downwards trend until at bottom; starting from bottom, going steadily upwards until a peak or plateau, then down again and up again, noisy; starting noisy high, down to a noisy plateau and up to a positive noisy plateau",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "starting mid lvl, going up, plateau, then going down a bit, then straight (noisy); going up a bit, very straight long plateau, then small-slope down again and finally up again; starting high, plateau, smaller slope and straight downwards trend",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "starting straight, upwards and huge drop afterwards, then up again to a peak and down again, noisy but straight; starting relatively low and straight, climbing up (small slope), reaching a very straight and long plateau; sharp drop, slowly climbing up again, stabilizing on high values, straight",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "starting relatively high, then drops quickly, going up again to a clear positive peak, then noisy down again, straight plateau; starting straight and noisy with smaller ups and downs, steadily downwards trend to a negative peak, then going significantly up to a peak and down again after, afterwards sort of straight; straight, going downwards, valley, up again, stabilizing, bit noisy downwards trend",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "briefly straight, up to peak, very small slope downwards trend; starting low, going up, then noisy straight, then up to a huge peak and way downwards again, slowly rising afterwards; relatively straight, rising to a peak, followed by going down to a valley and noisy up again in the end",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll_LLM = {  # concatenated roll, pitch and yaw accelerations
    # no raw values allowed, only pos / neg and shape
    1: {
        "name": "class_1",
        "fault_desc": "starting mildly negative, slips to a deeper negative dip; then a fairly smooth, almost linear climb through zero up to a pronounced positive peak; afterwards a fast fall into a broad, rather flat negative shelf; shallow, noisy recovery toward the neighbourhood of zero; brisk surge to a second, high positive hill, then an undulating descent to mid-positive ground; sudden plunge into a long, very even and deeply negative plateau; finally a long, steady ascent to the overall tallest positive crest, followed by a gentle, jittery glide down that ends slightly below the zero line;",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "begins a little above zero, turns modestly downwards and reaches a first deep negative trough; strong, steady rise to a medium positive summit; small retreat to near-zero, fresh leap to another positive hump; sharp, noisy dive to the overall deepest valley; long irregular wander within the lower negative zone; slow, stumbling climb with brief plateaus that bursts into a short but very high positive spike; swift slide to mid-negative, then a wavy path with minor bumps and dips; last broad ascent to a tall positive ridge and a final, gentle drop that ends just under the zero line;",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "starts on a flat, moderately negative ledge that sags a little further; steady, step-wise climb through zero into a wide, smooth positive plateau; mild, orderly drift down to mid-positive, then a brief slip into a narrow negative shelf that stays almost perfectly level; sudden jump back to small positives, followed by another climb to a series of rounded positive tops; gradual descent through scattered noise into mixed territory around zero; a few sharp downward stabs into the negative side, each quickly reclaimed; one more brisk up-swing to a high positive crest, after which the signal meanders with alternating little bumps and dips and settles just under zero;",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "begins on a flat, low positive ledge, creeps higher to a modest positive ridge; rolls smoothly downhill, crosses zero and keeps sliding into a fairly even, mid-negative bench; sinks a bit more to a deeper, still very flat negative plateau; slow, noisy recovery through the negative ranks and over zero into a broad, medium-high positive table; soft wavering decline that hovers around low positive; renewed descent, slipping back into a rough, mid-negative valley with short spikes; bounces briskly up to a moderate positive hump, drops again into the deepest, noisy negative dip of the record; long, ragged climb to a late positive plateau, then an orderly fade that ends in the low positives;",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "starts modestly positive, leaps almost instantly to a tall, very flat positive mesa; abrupt, steep fall into shallow negatives, drifts even lower to a straighter negative shelf; slow, noisy rise through zero into a low, uneven positive bump; small, wavering slide back to neutral; long, smooth plunge into the broadest, deepest negative plain where it stays rather level; sudden, energetic jump to a second tall positive plateau, followed by a slow, gently rippled glide down across zero into a mild negative tail;",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "opens with a perfectly flat, small positive strip; rapid escalation into a high positive peak, then a head-long dive to a sharp and deep negative trough; energetic climb to another tall positive summit, succeeded by a rolling decline that settles in an extended, very flat mid-negative shelf; lazy, noisy drift upward, wandering about the zero line; renewed, orderly rise to a moderate positive crest and a cushioned descent; a second, shorter plunge into a new but slightly higher negative plateau; final, unhurried climb that produces a neat, medium-high positive table and finishes with a mild, downward taper;",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "begins on a short, low positive bench, slopes rapidly downward into a long, steep negative canyon; vigorous, almost linear climb to a broad high positive hilltop; rolls off, wobbling back into mid-negatives with erratic bumps; hesitant lift followed by scattered ripples around zero; sudden, powerful surge to the record’s highest positive spike; sharp slide to mixed territory, then a string of gentle positive mounds; extended, noisy descent through successive negative plateaus that hit a late, deep trough; strong rebound to a final medium-high positive shelf, ending with a soft dip towards neutrality;",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "starts on a fairly level, moderate negative terrace; nudges slightly lower, then mounts a smooth, sustained climb to a broad, high positive summit; slow, almost symmetrical glide downward, crossing zero and sliding into a deep, choppy negative basin; measured climb to a small positive knoll, quick fall to a flat, shallow negative ledge; abrupt, steep ascent to the overall tallest positive crest; prolonged, gently wavy descent that sinks back into a multi-step negative plateau; gradual lifting out of the depths, passing zero once more to reach a modest positive ridge, and finally a quiet easing down that ends just above the zero mark.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll_LLM_Attempt_Two = {  # concatenated roll, pitch and yaw accelerations
    # no raw values allowed + also no pos / neg information, shape only
    1: {
        "name": "class_1",
        "fault_desc": "starting mid-low, shallow dip to a first little valley, then a long smooth climb that ends in a broad high-standing hump; afterwards a steep plunge to a deep trough, then restless up-and-down motion that settles into a rather flat low terrace; renewed climb to a middle-sized crest, brief sag, then a second taller and wider crest; from there a slow choppy descent, ending in several step-like drops that form a straight very-low plateau; finally a last climb to a sharp peak, followed by a wavering slide back toward the middle with a small noisy tail-off;",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "tiny rise out of the start, quick slip into a pronounced deep pit; strong steady ascent to a broad lofty ridge, then rolling down through bumpy mid-ground; next, another clear climb to a tall top, immediately followed by a fast tumble through a jagged low valley that flattens briefly; gentle ripples around mid-low, then a moderate surge that carries the trace to a middle-high shelf; a sharper push produces an even higher, fairly level summit, which is cut short by a long staircase-like fall to a second broad low table; after some jitter the line ramps all the way back to a high peak, drifts down, wobbles in mid-range and finishes in a small uneven decline;",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "begins on a flat low shelf, inches a bit lower, then arches upward through zero into a modest knoll; accelerates into a steep climb that tops out on a high, slightly noisy plateau; slips back in stages to mid-level, hops sideways, then drops abruptly onto a very even deep terrace; vigorous rebound carries it to a mid-high bench, followed by a secondary lift to another high but rough crest; from there the trace meanders downward, hits scattered little pits and short flat spots, eventually sinks onto another narrow low ledge; a late-stage burst rockets up to a sharp twin-peaked crown, which is chased by a sudden plunge to a broad low floor and some short rattling wiggles;",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "starts on a small flat perch, climbs smoothly to a rounded high hilltop, then glides down past mid-range into an extended slanted descent that ends on a nearly level deep shelf; stays there for a while, then mounts a long steady ramp that leads to a wide twin-topped summit; rolls off that summit, slipping through several noisy middle benches before dropping into another steep ravine with a short flat bottom; a quick rebound hurdles the trace back above mid-line where it wavers, then a final dip and a mild recovery bring it to rest on a modest, slightly uneven plateau;",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "kicks off with a jump onto a high, broad ledge, holding almost flat; abruptly dives past mid-range into a choppy negative hill-side which spreads out into a low, slightly sloping table; a modest rebound creates a middling bump, followed by a steady ramp to a gentle rounded summit; a gradual mottled descent sends the curve into an elongated deep valley that becomes an extended, perfectly flat floor; a sudden step up hoists it to a mid-high shelf, then another rise creates a broad tall ridge; it trickles downward through ripples, plunges again into a long, rough hollow, and ends with tiny wavers on a shallow low shelf;",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "begins as an absolutely flat low strip, then bursts upward in one continuous surge to a narrow high peak; tumbles straight through neutral into a deep bowl, climbs back in a smooth arc to a mid-high knob, and quickly slides down to mid-low; drift and small jerks lead to a very long, dead-flat deep terrace; from that terrace the line tilts upward in a slow staircase, crossing mid-range into a gentle hilly patch; a second very flat, deep bench appears, equally long; finally a calm, steady climb lifts the trace onto a broad high balcony that tapers away in a mild, orderly fall;",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "flat high start, slow gentle sag that accelerates into a pronounced deep canyon; swift rebound climbs beyond neutral into a lofty ridge, then slides off one side into choppy midlands with brief dips; a short pop upward precedes a noisy decline that flattens into a long, rolling low plain; a powerful surge then rockets the curve to its highest crown, after which it drifts down through irregular terraces and shallow bowls; several small wavy crests and troughs follow, ending in a mild staggered descent and a quiet low-lying tail;",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "opens on a short flat low bench, dips a touch deeper, then embarks on a long, smooth ascent to a broad, rounded summit; a gentle, asymmetric glide brings it back toward mid-line, continuing into a saw-toothed slide that settles on a slightly tilted deep shelf; a modest rebound forms a small mid-level hump, after which the signal falls onto a perfectly flat shallow step; suddenly it vaults upward in a strong run that reaches the highest, quite flat crest; from that crest a slow rolling descent sets in, peppered with little ripples and a brief mid-way resting step; later a smaller climb appears, ending in a short, even ledge, then another high ridge grows and finally fades into a long, undulating downturn with a soft noisy finish.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll_LLM_Attempt_Three = {  # concatenated roll, pitch and yaw accelerations
    # everything allowed, also raw values
    1: {
        "name": "class_1",
        "fault_desc": "starting slightly below zero, dipping a little further, then climbing steadily into a broad +2 peak; afterwards gliding all the way down into a long, noisy –1 ½ valley; a shallow sub-zero shelf follows; next comes a second rise to a lower, rounded positive shoulder, then a gentle slide; a brief uptick is cut short by an abrupt plunge into a flat, deep-negative plateau; from that floor the curve recovers in a smooth swing to its highest crest a little above +2, then trickles downward in small oscillations and ends with a modest bump that sinks back under zero;",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "begins with a tiny positive hump, then drops quickly into a –2 trough; rebounds in one clean arc to a strong +1 ¾ ridge, eases back toward the mid-line and stalls; pushes upward again to a second, slightly higher but noisy summit, then slides into another deep hollow; a modest recovery stumbles and the trace collapses to its lowest –2.2 pit; from there it grinds upward, culminating in a four-point crest above +2; a rapid retreat takes it into fresh negatives, a final small climb appears, and the record finishes in gentle, fading ripples around zero;",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "opens on a quiet –0.8 shelf, slips a little deeper, then marches upward in a smooth ramp to a tall +1.7 plateau; slopes down to a low-positive ledge, then drops abruptly into an extended, ruler-straight –1.0 bench; rises again in steps to a moderate positive table and on to a noisy second crest, settles briefly, then plunges into a twin negative well; finishes with uneven under-zero ripples;",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "starts on a mid-level +0.8 mesa that bulges to about +1.6, then tilts slowly downward through zero; glides ever deeper until it locks into a long, flat shelf near –1.6; climbs steadily back, breaks the surface and forms a broad rounded plateau around +1.5; slips away, wavers near baseline and sinks once more to a ragged negative trough; vaults fast to a brief positive spike, tumbles to its deepest –1.9 pit, then executes a final steep ascent to a late +1.8 summit and drifts down in small after-shocks;",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "after a modest +0.4 start it leaps into a tall near-2 plateau, then drops abruptly to hover round zero; continues downward into a noisy –1 valley where it meanders; a gentle climb brings it to a flat hump just above +1 before sagging again; a prolonged slide settles into a wide, flat trench close to –1.8; a sharp rebound carries it to a second broad top near +1.8, which quickly decays, leaving a slow, rippling descent in the negative region;",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "begins with a dozen perfectly flat points at +0.23, then accelerates upward into a sharp +2 crest; plunges head-long through zero into a –1.9 pit; rebounds strongly to a second peak about +1.7, only to slump into an extended, ruler-straight shelf at –1.4; creeps upward in small rolling waves to a low dome around +1.4; slips back into another flat –1.25 bench and finally climbs a gentle staircase that peaks just below +1.4 before ebbing away quietly;",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "opens on a flat +0.8 plateau, falls steeply into a –2 trough, swings back in a vigorous arc to a +1.7 crest and slides through choppy mid-range undulations; a second dive bottoms near –1.6, followed by a powerful surge that towers above +2.3; this summit collapses into jittery oscillations that drag the trace back into the –1.7 basin; in the closing scene it climbs again to a late +1.5 ridge before losing altitude and ending a little below zero;",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "starts on a broad –0.8 table, then ramps steadily up to about +1.7; declines gradually, passing through zero and carving out a long negative slope that bottoms just below –1.4; a modest bounce gives a short positive bump, followed by a lean –0.5 perch; from this base the signal rockets to its tallest peak a bit over +2.2, then cascades back down into a long, uneven descent reaching –1.6; finally it drifts upward once more, forms a medium-height mound near +1.4 and coasts to rest just above the baseline.",
        "severity": "X"
    },
}

# TODO: very bad matching performance (!)
SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll_LLM_Realistic = {  # concatenated roll, pitch and yaw accelerations
    # everything allowed, also raw values
    1: {
        "name": "class_1",
        "fault_desc": "short shallow-negative lead-in, sinks to a first broad deep-negative shelf, then ramps up through zero to a high positive crest, collapses abruptly into a long deep-negative plateau with noisy ripple, drifts upward to a mid-positive hump, slides back to baseline, makes a second sudden plunge into a repeated deep-negative shelf, finally climbs all the way to a tall positive peak and eases down toward slightly negative end values",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "starts mildly positive, slips into a pronounced negative valley, rises steadily to a medium-high positive hill, falls again to a short negative dip, surges to a second higher positive ridge, tumbles into an extended very-negative trough, stages a late strong rally to its highest positive peak, then trails off with another quick descent into low-negative territory",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "begins on a low-negative step, edges further down to a shallow minimum, turns around and ascends through zero to a broad mid-positive plateau, drops abruptly to a flat mid-negative shelf, performs a second climb to a similar positive shelf, oscillates with several box-shaped steps of alternating sign, and coasts out close to baseline",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "moderate positive plateau at the start, gentle rise to a rounded high, long monotonic slide into a wide deep-negative bench, pauses there, then executes a smooth climb back to a symmetrical high positive shelf, followed by another extended descent that overshoots into its deepest negative excursion before drifting back upward toward weakly positive levels",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "short low-positive preamble, jumps quickly onto a tall flat positive mesa, breaks away into a steep dive that bottoms in the mid-negative range, meanders there with small saw-teeth, lifts gradually into a low positive shelf, dives much deeper to its most negative shelf, rebounds explosively to a second tall positive plateau, and finally decays step-wise toward a mild negative finish",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "long quiescent near-zero strip, smooth acceleration to a single high positive peak, sharp reversal into a deep negative chasm, strong recovery up to a mid-high positive shoulder, settles into a prolonged mid-negative shelf with minimal drift, then climbs staircase-like back to a broad positive roof and ends with a gentle downward taper",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "steady mid-positive ledge, rapid fall into a pronounced negative well, vigorous climb to a high positive summit, slides off into a noisy mid-negative dip, rebounds into several smaller positive bumps, repeats a sequence of shrinking negative swings, then finishes with a final modest positive rise followed by a slight sag toward zero",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "flat low-negative opening, slow acceleration to a long rounded positive summit, protracted downhill glide that crosses zero and levels out on a mid-negative shelf, short positive rebound, slips back to near-baseline, launches into its tallest positive spike, afterward descends steadily through a layered series of negative steps, and closes with a smooth climb to a medium positive plateau",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_UWaveGestureLibraryAll_LLM_FINAL = {  # concatenated roll, pitch and yaw accelerations
    1: {
        "name": "class_1",
        "fault_desc": "Beginning on a shallow negative plateau, the trace dips a little further at index 20, sweeps steadily upward to its earliest and tallest crest at index 58, plunges into a wide negative basin centred in the mid-70s, climbs again to a secondary summit about index 149, slides into another extended hollow spanning indices 171-178, then mounts a third marked peak at index 212 before fading in a gently noisy decline toward the negative side.",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "After a short flat positive start the curve makes a modest bump, dives to its deepest trough at index 29, rebounds to a middling crest around index 40, eases back, surges higher to a peak near index 63, slips into a choppy descent that bottoms just after index 100, suddenly rockets to its overall maximum at index 140, and thereafter undulates downward with smaller swings, ending a little below zero.",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "The record opens on a mild negative shelf, sinks slightly further at index 22, rises steadily through the axis to a first positive plateau topping out near index 69, collapses into an extended flat trench of almost constant depth from the high-70s through the 90s, climbs again to crests at indices 117 and 149 (the latter higher), eases back toward zero, falls to a deep pocket around index 185, and finishes with a hesitant recovery dotted with minor ripples.",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "Starting on a moderate positive ledge, the signal climbs to an early high at index 15, decays almost monotonically through zero in the mid-40s to a long level negative terrace centred on indices 80-90, then turns upward into a broad flat top around index 130, slips into a steep decline that bottoms near index 175, and finally rebounds to a smaller late-stage crest close to index 205 before easing off.",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "Opening just below zero, the trace rises through paired early peaks at indices 17 and 26 (the second higher), tumbles to its deepest valley at index 63, recovers into a long low-amplitude shelf straddling zero between roughly indices 80 and 110, pushes up to a moderate hump near index 120 and a broader plateau centred on 140, falls again into a prolonged negative table whose floor lies in the 160s, and ultimately stages a gradual comeback that tops out near index 225 before tapering away.",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "The curve begins on a flat positive shelf, plunges to its overall minimum at index 17, rebounds sharply to a strong crest near index 43, wavers and dips below zero in the 60s, sinks further to an extended negative plateau with a secondary floor at index 99, then climbs in a long stepped ascent to a gentle ridge spanning indices 120-150, finally drifting downward in small ripples while remaining above the axis.",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "Starting with a small positive plateau, the series collapses to a deep minimum at index 24, rockets to a tall peak at index 48, relaxes, swings negative again with a trough near index 98, falls still further to its lowest point at index 115, mounts a brisk ascent culminating in the global maximum around index 150, declines once more into the negative near index 175, and ends with a fresh climb peaking close to index 220 before subsiding.",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "Commencing on a gentle negative shelf the signal makes a minor dip to a local floor at index 9, accelerates upward to a sizeable crest at index 21, slides back through zero into a modest basin in the 50s, plunges to its deepest point at index 72, surges into a high plateau whose summit sits near index 89, declines gradually while oscillating, sinks into another negative pocket centred around index 123, rises to a small mid-range hump at index 162, drops briefly, then mounts a late powerful climb to a second major peak near index 200 before descending toward the end.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_Mallat_LLM = {
    1: {
        "name": "class_1",
        "fault_desc": "Starts at a moderately negative level with a shallow additional dip, then performs a long, almost linear climb that crosses zero and forms a first wide, fairly smooth positive mound; after a short, still–positive shoulder the curve slips back toward the zero line, hovers with small irregular ripples, drops through a shallow negative hollow, recovers into a noisy band around the negative baseline, and finally executes a very long, smooth ascent to the global, rounded positive maximum followed by a steady, monotone decline that ends in a pronounced negative trough.",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "Begins slightly negative and glides down a bit more, then undertakes a prolonged, regular rise through zero to a broad, gently undulating positive table; from there it lifts once more to a secondary, narrower crest, slips down in two steps to a mid-positive landing, falls abruptly toward the zero line, wiggles around it, dives into a deep but fairly smooth negative well, and finishes with a sequence of small, almost identical negative ripples.",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "Initiates in the lower negative range, flattens briefly, and then performs a long, steady climb that crosses zero, tops out in a gentle positive dome, hovers on a noisy shelf, relaxes slightly, climbs again into a second, smoother ridge, loses height in a staircase manner to a mild positive bench, plunges rapidly through zero into a broad negative basin with weak oscillations, then copies the earlier pattern: climbs to a late, tall but rounded positive hump and finally glides back down into a deep negative ending.",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "Starts negative with a minor extra sag, proceeds into an extended, rather linear lift through zero to a first wide positive plateau, steps up once more into a slightly higher but narrower crest, retreats in two stages to a near-zero terrace, slips underneath into a shallow negative dip, oscillates weakly, climbs anew to a late, highest rounded summit, and ends with a slow, almost linear descent that settles in a sizeable negative trough.",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "Opens modestly negative and dips a bit deeper, then runs up in a long, steady ramp that crosses zero, producing a broad, fairly flat positive shelf; after a short lull it rises again into a secondary, noisy bulge, declines in three small terraces toward the zero axis, slips into a mid-negative pocket, hovers with low-amplitude ripples, mounts a delayed, smooth surge to the global positive maximum, and finally fades away in a drawn-out, almost monotonic slide to a deep negative finish.",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "Commences in the lower negative zone, touches a slightly deeper minimum, then undergoes a prolonged straight ascent through zero to a spacious, gently wavy positive plateau; this is followed by an extra upward push into a tighter positive crest, a gradual two-step fall to a mild positive ledge, an abrupt dive into a broad negative valley with small, regular ripples, a late-stage smooth climb to the ultimate rounded peak, and a long, steady, almost linear descent that ends well below zero.",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "Begins slightly negative with a subtle further dip, executes a long, near-linear climb through zero into a very wide, softly undulating positive plain, steps higher into a narrow positive ridge, eases down to a mid-positive shoulder, drops rapidly toward zero, vibrates gently about the baseline, sinks into a deep but smooth negative bowl, stays there with small repetitive ripples, mounts a final smooth ascent to a broad, highest positive dome, and concludes with an extended, monotone glide back to a marked negative trough.",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "Starts in the negative range with a tiny extra sag, then follows a lengthy, almost linear rise through zero that builds a broad, slightly noisy positive shelf; gains additional height into a secondary, tighter crest, backs off in two stages to a near-zero landing, falls sharply into a wide negative basin, oscillates mildly, climbs late to the global rounded maximum, and finally drifts down in a slow, steady decline that settles in a pronounced negative well.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_Mallat_LLM_NEW = {
    1: {
        "name": "class_1",
        "fault_desc": "It begins slightly below the axis, slips a few samples lower, then swings upward in a long, smooth climb that crosses zero and reaches a first rounded crest near index 37; after a short, uneven shoulder it sags and meanders around small values, dives to its deepest negative dip at about index 74, recovers through a noisy mid-series hollow centred near index 137 and finally accelerates into its broadest rise, topping out at the global maximum around index 210, before gliding back down with gentle oscillations to finish negative.",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "Starting moderately negative it falls a touch further to a shallow bottom around index 7, reverses and rises steadily through zero to an initial summit near index 26, then keeps climbing into a taller wave whose tip—and overall peak—appears close to index 44; the trace then drops abruptly into a mid-run valley at index 47, drifts in low-amplitude ripples, turns negative during the third quarter, and mounts one last but smaller crest near index 221 before easing downward again toward the end.",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "From an already negative level the curve dips only briefly, then embarks on a long, smooth ascent that takes it through the origin and onto a broad plateau peaking near index 28; it undulates gently downward, swells into a second but slightly higher crest around index 59, slides into its deepest trough near index 74, and thereafter alternates smaller waves—with a late, lower maximum around index 220—before edging back below zero in the closing samples.",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "The trace opens negative and keeps falling until about index 7, then turns and climbs smoothly, crossing zero and forming a first prominent peak near index 37; after a minor dip and a brief secondary crest at index 44 it tumbles to its greatest negative excursion around index 74, rises again through a noisy shoulder, and eventually produces a sustained late-series surge whose highest point occurs close to index 214, after which it descends gradually with small ripples into the negative zone once more.",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "An initial, gentle slide to a minimum at index 6 is followed by a steady, almost linear rise that crosses the axis and crests for the first time near index 36; a noisy plateau gives way to an abrupt plunge to the main negative trough at about index 74, the waveform then recovers, oscillates around small values, and builds a long, smooth climb that peaks globally near index 210 before slipping back down below zero toward the finish.",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "Beginning slightly negative it drifts lower to a shallow bottom at index 7, then embarks on an extended climb, crossing zero and fanning out into a broad high zone whose top (and overall maximum) sits near index 61; from there it steps down through a series of ripples, plummets to its deepest dip around index 74, rebounds in a modest mid-range hump, and ends with a gentle rise that stalls near index 210 before tapering away with small undulations.",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "The curve starts negative, sinks a little further until about index 5, then rises steadily through zero, developing an initial bump around index 31 and reaching its tallest crest—just over twice the starting magnitude—near index 40; it then slips off that peak, oscillates downward into a shallow mid-series hollow centred roughly at index 72, spends a long spell hovering just below zero, and finally lifts into a subdued late peak around index 217 before sliding back into negative territory at the close.",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "After a brief dip the signal mounts a gentle, sustained ascent that crosses zero and tops out in a first rounded high near index 38; it relaxes slightly, then pushes on to its global maximum around index 44, descends quickly into a sharp trough at about index 74, spends the middle section wavering close to the axis, and eventually rises again into a broad late crest peaking close to index 210, from which it glides downward in small undulations to end below zero.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_InsectWingbeatSound_LLM = {
    1: {
        "name": "class_1",
        "fault_desc": "starts slightly above zero, slips almost linearly into a shallow negative band and sits there with low-amplitude wobble; without warning a very steep positive surge shoots to an extreme main peak, then falls back almost symmetrically to the old neighbourhood and even overshoots a little into the negative; a second, much smaller hump follows, afterwards the trace settles into a long, very flat but clearly deeper negative plateau with microscopic jitter and finishes still negative.",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "begins moderately negative, then performs a smooth, almost textbook ramp across zero up to a tall, broad positive apex; drifts back down through zero to a near-flat region around zero, makes a secondary medium-sized rise, afterwards decays gradually, ending in a long, gently sloping negative shelf that oscillates quietly around a mid-negative level.",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "opens inside a shallow negative corridor with tiny ripples, suddenly accelerates into a very steep climb that culminates in a single dominant high peak; the return is nearly as quick, plunging past zero into a steady mid-negative plateau; later it builds a secondary, only half-sized hill, then re-enters the earlier negative band and remains there in an unusually long, almost ruler-straight plateau with only fine-grained noise.",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "starts in a mild negative glide, holds a short flat section, then ramps sharply upward into a first positive dome; slips back toward zero but, before reaching it, turns into a broad second and even higher crest; from there the curve slides continuously into an extended, deep negative shelf with very little variation, interrupted only by two tiny positive blips, before ending still deep and flat.",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "begins clearly positive but immediately declines, crosses zero and cruises in a light negative trough; an abrupt, very steep ascent follows, forming the global maximum; a smooth descent takes the signal below one again and a medium-sized secondary hump appears; afterwards the trace drops into a mid-negative regime that slowly deepens and finally turns into a long, almost flat negative plateau with low-level jitter.",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "initial segment sits in mid-negative, then a dramatic, almost exponential climb leads to an isolated, tall positive peak; the decay is gentle at first, followed by undulating shoulders and two small positive bumps; eventually the curve dives back under zero and flattens out into a protracted deep-negative table where only fine noise is visible, ending there.",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "holds a very flat corridor close to −0.5 for quite some time, then shoots almost vertically into an exceptionally high positive spike; the fall is slower, producing a shoulder and a secondary medium crest; from there the signal slides back into its original negative band, executes a set of minor saw-tooth ripples, and finally levels out again around the same negative value it started from.",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "sits stably in a mid-negative shelf, then produces a smooth but powerful climb to a broad positive plateau, followed by a rounded descent; a second, slightly lower hill appears, after which the trace heads steadily downward into a deep negative region; there it locks onto a very flat floor with scarcely any movement and remains there until the end.",
        "severity": "X"
    },
    9: {
        "name": "class_9",
        "fault_desc": "opens with a medium positive overshoot that rapidly decays through zero into slight negativity; after a short quiet spell it mounts a long, steady ascent to a wide positive summit; the return is gradual, then the curve settles into a stair-like series of ever-deeper negative steps, finally stabilising in a flat mid-negative band with minor jitter.",
        "severity": "X"
    },
    10: {
        "name": "class_10",
        "fault_desc": "starts mildly negative, makes a small rounded positive bump, falls back to near zero, then accelerates into a pronounced, multi-sample climb that yields the global peak; the subsequent descent is gentle at first, then breaks into several small terraces before sliding into a deep, nearly horizontal negative plateau where it stays, showing only low-amplitude flicker.",
        "severity": "X"
    },
    11: {
        "name": "class_11",
        "fault_desc": "begins clearly positive with several small oscillatory swells, gradually trending upward into a modest multi-peak cluster; after a plateau the signal changes character and undertakes a slow but persistent decline, crosses zero and keeps falling into ever deeper negative territory; the last third is a long, steadily darkening negative slope that finally flattens, sitting very low with extremely small ripples.",
        "severity": "X"
    },
}

SYMBOLIC_FAULT_INFO_InsectWingbeatSound_LLM_NEW = {
    1: {
        "name": "class_1",
        "fault_desc": "It starts just above zero, sinks into a fairly long shallow negative basin, then rockets upward to its dominant summit around index 76, slides back down into a broad, almost flat negative plateau and, apart from a small secondary bump near index 164, finishes with only gentle low-level fluctuations.",
        "severity": "X"
    },
    2: {
        "name": "class_2",
        "fault_desc": "Beginning slightly below zero, it climbs sharply to its main crest near index 15, drops into a mid-level dip, rebounds to a smaller hill at about index 43, and then fades through progressively weaker ripples into an extended, gently declining negative stretch.",
        "severity": "X"
    },
    3: {
        "name": "class_3",
        "fault_desc": "The curve opens in weak negatives, accelerates into a steep mountain whose apex lies near index 40, plunges back through zero, rises into a broader but lower hill peaking around index 94, and finally decays into a long, nearly constant negative shelf with minor undulations.",
        "severity": "X"
    },
    4: {
        "name": "class_4",
        "fault_desc": "After a mild early slide that bottoms out near index 17, it surges to an initial peak at index 36, retreats all the way to a deep negative plateau, climbs again to its highest crest close to index 89, and then eases downward into a sustained low-lying, lightly fluctuating negative band.",
        "severity": "X"
    },
    5: {
        "name": "class_5",
        "fault_desc": "A modest positive start drifts below zero, followed by a single steep ramp to the tallest summit near index 64; the trace then slopes down through positive into negative territory, shows a secondary but much smaller swell centred on index 139, and finally settles on a broad, gently varying negative plain.",
        "severity": "X"
    },
    6: {
        "name": "class_6",
        "fault_desc": "Opening with a shallow decline, the signal swings into an explosive rise that tops out near index 34, descends through positive values to a brief sub-zero dip, arches into a noticeably smaller crest around index 83, and thereafter glides into an ever-flattening negative terrace peppered with small ripples.",
        "severity": "X"
    },
    7: {
        "name": "class_7",
        "fault_desc": "It begins as an almost level mild-negative plateau, leaps upward to a prominent maximum at about index 58, rolls downward past zero into a modest trough, rises again to a mid-sized hill near index 110, and then gradually subsides into a steady, lightly noisy negative table.",
        "severity": "X"
    },
    8: {
        "name": "class_8",
        "fault_desc": "Starting in moderate negatives and dipping slightly further, the trace sweeps upward into its dominant peak around index 43, glides downward toward zero, mounts a lower second peak near index 120, and finally descends smoothly into a deep, almost constant negative shelf with faint oscillations.",
        "severity": "X"
    },
    9: {
        "name": "class_9",
        "fault_desc": "Launching from a sizeable positive level, it cascades downward through zero into a broad negative basin, surges in a long climb to its highest summit close to index 75, and thereafter tapers away through a patchwork of smaller ripples into an extended, slowly deepening negative plateau.",
        "severity": "X"
    },
    10: {
        "name": "class_10",
        "fault_desc": "After a short flat negative opening it rises steadily to a modest crest near index 19, slips back below zero, accelerates into a sharp ascent that reaches the overall maximum around index 52, slopes downward across zero again, shows a minor bump roughly at index 109, and ends in a prolonged, gently drifting negative trench.",
        "severity": "X"
    },
    11: {
        "name": "class_11",
        "fault_desc": "Beginning with an undulating positive stretch that builds to its main peak near index 16, the series meanders downward through smaller crests, crosses zero in the seventies, and continues into a long descent that settles into a deep, almost stationary negative plateau with only slight low-amplitude noise.",
        "severity": "X"
    },
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
    for class_idx in range(1, len(SYMBOLIC_FAULT_INFO_Mallat_LLM_NEW.keys()) + 1):
        kg_gen.extend_knowledge_graph_with_sensor_fault_data(
            SYMBOLIC_FAULT_INFO_Mallat_LLM_NEW[class_idx]['name'],
            SYMBOLIC_FAULT_INFO_Mallat_LLM_NEW[class_idx]['fault_desc'],
            SYMBOLIC_FAULT_INFO_Mallat_LLM_NEW[class_idx]['severity']
        )
