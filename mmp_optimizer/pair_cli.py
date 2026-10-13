"""Command-line access to measured paired-potency arithmetic."""
import argparse
import json
import sys
from .mmp_analysis import compare_potency_pair, UNIT_IN_MOLAR, ENDPOINTS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="mmp-pair-compare",
        description="Compare measured potencies from an independently verified structural matched pair."
    )
    parser.add_argument("--reference", type=float, required=True, help="Reference concentration")
    parser.add_argument("--analogue", type=float, required=True, help="Analogue concentration")
    parser.add_argument("--unit", choices=list(UNIT_IN_MOLAR), default="nM")
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS), default="IC50")
    args = parser.parse_args(argv)
    try:
        result = compare_potency_pair(args.reference, args.analogue, args.unit, args.endpoint)
    except (TypeError, ValueError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
