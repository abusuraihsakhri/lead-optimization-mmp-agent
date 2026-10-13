"""
Automated Pytest for lead-optimization-mmp-agent Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import pytest
from enrichment import (
    QsarModelTrainingPipelineEngine,
    ImplementationEngine,
    DependenciesEngine,
    AidrivenRetrosyntheticAnalysisWithReactionPredictionEngine,
    LeadoptimizationmmpagentEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0

def test_enrichment_suite_returns_unique_results():
    """Verify that deduplicated suite returns exactly 5 unique engine results."""
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) == 5

def test_enrichment_suite_rejects_nan():
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    with pytest.raises(ValueError, match="NaN"):
        suite.execute_all(primary_val=float("nan"), secondary_val=0.5)

def test_enrichment_suite_rejects_inf():
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    with pytest.raises(ValueError, match="finite"):
        suite.execute_all(primary_val=float("inf"), secondary_val=0.5)

def test_enrichment_suite_rejects_non_numeric():
    suite = LeadoptimizationmmpagentEnrichmentSuite()
    with pytest.raises(TypeError, match="numeric"):
        suite.execute_all(primary_val="not_a_number", secondary_val=0.5)
