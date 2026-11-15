"""sw_enose: a software-defined electronic nose. Everything is MODELLED unless provenance says measured."""
from .data import ReceptorParams, load_params, synthetic_params
from .array import ReceptorArray
from .pipeline import Pipeline
from .bio import BiomimeticNose, SparseMemory, BIOLOGY
from .air import (AIR_TO_MUCUS, HenryTable, MissingHenryConstant, air_to_liquid,
                  concentration_vector_from_air, load_henry_csv, ppb_for_liquid, synthetic_henry_table)
from .coverage import NoCoverageInformation, describe, restrict_to_tested, support
from .panels import ACID_CARBONS, ACID_MEASURED_HENRY, ACID_SERIES, EVOCATIVE_PANEL
from .separability import (describe_gap, nearest_centroid_accuracy, pairwise_similarity,
                           stage_accuracies)
from .uncertainty import (efficacy_sensitivity, resample_efficacy, seed_floor, stage_sensitivity,
                          sweep_summary, verdict)

__all__ = ["ReceptorParams", "load_params", "synthetic_params", "ReceptorArray", "Pipeline",
           "BiomimeticNose", "SparseMemory", "BIOLOGY",
           "HenryTable", "load_henry_csv", "synthetic_henry_table", "air_to_liquid",
           "concentration_vector_from_air", "ppb_for_liquid", "MissingHenryConstant", "AIR_TO_MUCUS",
           "support", "describe", "restrict_to_tested", "NoCoverageInformation",
           "resample_efficacy", "efficacy_sensitivity", "stage_sensitivity", "seed_floor",
           "sweep_summary", "verdict",
           "ACID_SERIES", "ACID_CARBONS", "ACID_MEASURED_HENRY", "EVOCATIVE_PANEL",
           "pairwise_similarity", "stage_accuracies", "describe_gap",
           "nearest_centroid_accuracy"]
