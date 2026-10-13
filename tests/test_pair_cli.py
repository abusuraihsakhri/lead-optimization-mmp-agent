"""CLI comparison result and validation regression tests."""
import json
from mmp_optimizer.pair_cli import main


def test_cli_json(capsys):
    assert main(["--reference", "100", "--analogue", "10", "--unit", "nM"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["delta_p_activity"] == 1.0 or abs(result["delta_p_activity"]-1)<1e-12


def test_cli_rejects_zero(capsys):
    assert main(["--reference", "0", "--analogue", "10"]) == 2
    assert "positive" in capsys.readouterr().err
