"""Measured potency comparison for a user-confirmed matched molecular pair.

This module does not identify structural matched pairs, infer transformation
rules, predict unmeasured activities, or establish assay comparability.
"""
import math

UNIT_IN_MOLAR = {"pM": 1e-12, "nM": 1e-9, "uM": 1e-6, "mM": 1e-3, "M": 1.0}
ENDPOINTS = frozenset({"IC50", "EC50", "Ki", "Kd"})


def compare_potency_pair(reference, analogue, unit="nM", endpoint="IC50"):
    """Compare positive measured concentrations in the same assay and units.

    delta_p_activity = pActivity(analogue) - pActivity(reference).
    fold_shift = reference / analogue; >1 indicates lower analogue concentration.
    Users must establish structural MMP status and comparability independently.
    """
    if unit not in UNIT_IN_MOLAR:
        raise ValueError("Unsupported unit; choose pM, nM, uM, mM, or M")
    if endpoint not in ENDPOINTS:
        raise ValueError("Unsupported endpoint; choose IC50, EC50, Ki, or Kd")
    concentrations = []
    for label, value in (("reference", reference), ("analogue", analogue)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(label + " must be a numeric concentration")
        if not math.isfinite(value) or value <= 0:
            raise ValueError(label + " must be positive and finite")
        molar = value * UNIT_IN_MOLAR[unit]
        if not math.isfinite(molar) or molar <= 0:
            raise ValueError(label + " is outside the supported numeric range")
        concentrations.append(molar)
    ref_molar, analogue_molar = concentrations
    p_ref = -math.log10(ref_molar)
    p_analogue = -math.log10(analogue_molar)
    delta = p_analogue - p_ref
    fold = ref_molar / analogue_molar
    if not math.isfinite(fold) or fold <= 0:
        raise ValueError("Fold shift is outside the supported numeric range")
    return {
        "endpoint": endpoint,
        "unit": unit,
        "reference": reference,
        "analogue": analogue,
        "p_reference": p_ref,
        "p_analogue": p_analogue,
        "delta_p_activity": delta,
        "fold_shift": fold,
        "interpretation": (
            "Analogue has a lower measured concentration"
            if delta > 0 else "Analogue has a higher measured concentration"
            if delta < 0 else "Both measured concentrations are equal"
        ),
        "limitations": (
            "Arithmetic only. Requires equivalent assays and a structurally confirmed matched pair; "
            "does not predict activity or assess efficacy, toxicity, or synthetic feasibility."
        ),
    }
