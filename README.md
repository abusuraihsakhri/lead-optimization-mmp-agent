# Lead Optimization MMP Agent

A lightweight paired-potency comparison tool with a separate, legacy generic audit workflow. The web comparator works without a backend; the audit endpoints require Python and FastAPI.

**Scope:** This project does **not** identify matched molecular pairs from structures, fragment SMILES, predict unmeasured potency, perform QSAR model training, infer bioisosteric transformations, evaluate patentability, or validate clinical decisions. Users must independently confirm that two compounds constitute a structural matched pair and that their measurements come from comparable assays.

## Browser application

Open [web/index.html](web/index.html) in a modern browser. On a configured GitHub Pages deployment, the web application can also be served as a static site. A public Pages URL is not listed until deployment has been verified.

1. Enter two positive, measured concentration values for the reference and analogue compounds.
2. Select a common concentration unit (pM, nM, µM, mM, or M) and endpoint (IC50, EC50, Ki, or Kd).
3. Calculate the pActivity difference and fold shift; export the numeric comparison as CSV.

The calculation uses:

- `pActivity = −log10(concentration in mol/L)`
- `ΔpActivity = pActivity(analogue) − pActivity(reference)`
- `fold shift = reference concentration / analogue concentration`

A positive delta corresponds to a lower analogue concentration. It is **not** a prediction of efficacy, toxicity, binding selectivity, or synthetic feasibility. Compare like-for-like endpoints measured under suitable assay conditions.

The web page also contains an explicitly labeled **legacy server audit** for generic numerical flags. It is unavailable without a running FastAPI backend and never fabricates an offline result.

## Python installation

Requires Python 3.10 or newer:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

Compare two measured values from the terminal:

```bash
mmp-pair-compare --reference 100 --analogue 10 --unit nM --endpoint IC50
```

For this example, the reference and analogue have pIC50 values of 7 and 8 respectively, a ΔpIC50 of +1 and a tenfold shift.

The same calculation is accessible as Python:

```python
from mmp_optimizer.mmp_analysis import compare_potency_pair
result = compare_potency_pair(100, 10, unit="nM", endpoint="IC50")
print(result["delta_p_activity"])
```

## Legacy audit and API

The existing CLI and endpoints remain available. They use **fixed generic thresholds** and descriptor matching; these have not been validated as chemistry standards.

```bash
# Linux / macOS — generate a unique runtime signing key
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

python cli.py audit --task-id T001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000/` for the browser UI with optional backend access. API endpoints include `/health`, `/api/audit`, `/api/chat`, and `/metrics` (JSON counters). The alternate `mmp_optimizer` CLI and server are retained for compatibility.

### Docker

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

The Compose configuration **requires** a runtime key; it no longer provides a fixed production secret. See `.env.example` for supported variables. Do not commit a populated `.env` file or reuse previous example keys for production.

## Security and data handling

- Paired-potency calculations and CSV generation happen locally in the browser, without any request to a server.
- The optional audit form sends its submitted values to the same-origin FastAPI service. Do not enter patient-identifiable or confidential data.
- The server performs **pattern-based** identifier checks; this is **not** comprehensive PHI detection, formal de-identification, or a HIPAA compliance guarantee.
- Legacy audit events use an HMAC-SHA256 chain **kept only in process memory**. Restarting the process clears it; it is not a durable, externally attested audit record.
- `GET /api/audit/logs` is disabled unless `AUDIT_READ_TOKEN` is configured. If enabled, clients must supply that value in the `X-Audit-Token` header. Only use the service behind an appropriate authenticated and encrypted access boundary.
- The mock language-model adapter does not perform LLM inference or scientific validation. External model providers are **not implemented**; requesting one raises an error rather than silently returning mock output.

## Development and verification

CI tests Python 3.10–3.12, package installation, compilation, dependency consistency, unit tests, an HTML-script syntax check, and test-only HMAC integrity. The static web page uses standards-based HTML/CSS/JavaScript without a frontend build system or external assets. The repository provides a GitHub Pages deployment workflow; Pages hosting must be enabled and verified separately.

The `enrichment.py` modules are legacy numeric threshold placeholders, **not** functioning QSAR training or retrosynthesis systems. See the source for exact behaviors.

## License

[MIT](LICENSE).
