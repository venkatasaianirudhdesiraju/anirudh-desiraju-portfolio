"""DataGuard: declarative data-quality checks for pandas DataFrames."""
from .engine import CheckResult, Report, validate, load_rules

__all__ = ["CheckResult", "Report", "validate", "load_rules"]
__version__ = "0.1.0"
