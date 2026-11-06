# DataGuard — declarative data-quality checks for pandas

Bad data breaks pipelines silently. DataGuard validates CSV / Parquet / Excel / JSON against a small YAML
rules file, prints a summary, writes a **self-contained HTML report**, and **exits non-zero** so it can gate
CI/CD or an Airflow task.

```
$ python -m dataguard check examples/ct_scans.csv --rules examples/ct_rules.yaml --html report.html
FAILED  score=66.7%  errors=5  warnings=1  rows=500
  [ERROR] scan_id.unique: 2 bad — composite key [['S00049'], ['S00049']]
  [ERROR] patient_id.regex: 1 bad — regex='^P\d{6}$' ['BAD-ID']
  [ERROR] kvp.max: 1 bad — max=140 ['400']
  [WARN]  dose_mgy.outlier_z: 1 bad — robust |z| > 5 ['95.0']
```

## Rules
```yaml
table:
  min_rows: 100
  unique: [scan_id]            # composite keys allowed
  no_extra_columns: false
columns:
  patient_id: {type: string, required: true, regex: "^P\\d{6}$"}
  kvp:        {type: number, min: 70, max: 140}
  dose_mgy:   {type: number, max_null_pct: 1, outlier_z: 5}   # robust (median/MAD) z-score
  status:     {allowed: [ok, retake, rejected]}
  scanned_at: {type: datetime, not_future: true}
```
Column checks: `required, type (string|number|integer|boolean|datetime), min, max, min_length, max_length,
regex, allowed, unique, not_future, max_null_pct (warn), outlier_z (warn)`.

## Commands
```bash
pip install -r requirements.txt
python -m dataguard infer good_data.csv -o rules.yaml     # bootstrap rules from a known-good file
python -m dataguard check new_data.csv --rules rules.yaml --html report.html [--json] [--strict]
pytest -q
```

## Use from Python
```python
from dataguard import validate, load_rules
report = validate(df, load_rules("rules.yaml"))
assert report.passed, report.errors
```

## Ideas to extend
Great-Expectations-style data docs, Slack alerts, drift checks between two snapshots, a FastAPI service,
Spark backend for large tables.
