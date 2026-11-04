"""Tests for the design-system consistency check.

The system is no longer hard-locked, so check-lock.py must behave like an
advisory reviewer:

  * default run      -> prints warnings, exits 0 (never blocks a build)
  * --strict         -> exits 1 when there are warnings (opt-in CI gate)
  * --update         -> refreshes the baseline checksums

The checks themselves still matter, so they must still fire:
  * an unsanctioned file in docs/brand/assets/
  * a sanctioned asset that went missing
  * a required token removed from design-tokens.css
  * a reference to a removed 2.0 asset
  * a file changed since the last sanctioned baseline

Run:
    uv run --no-project --with pytest pytest packages/brand-tools/tests -q
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[1]
SCRIPT = HERE / "check-lock.py"
BASELINE = HERE / "design-system.baseline.json"

spec = importlib.util.spec_from_file_location("check_lock", SCRIPT)
check_lock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_lock)  # type: ignore[union-attr]


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """A minimal copy of the repo shape the checker reads."""
    (tmp_path / "docs/brand/assets").mkdir(parents=True)
    (tmp_path / "packages/brand-tools").mkdir(parents=True)
    shutil.copy(ROOT / "docs/brand/design-tokens.css", tmp_path / "docs/brand/design-tokens.css")
    for svg in (ROOT / "docs/brand/assets").glob("*.svg"):
        shutil.copy(svg, tmp_path / "docs/brand/assets" / svg.name)
    shutil.copy(BASELINE, tmp_path / "packages/brand-tools/design-system.baseline.json")
    shutil.copy(ROOT / "docs/brand/DESIGN-SYSTEM.md", tmp_path / "docs/brand/DESIGN-SYSTEM.md")
    for rel in (
        "docs/brand/brand-theme.md",
        "docs/brand/preview/design-system-3-1.png",
        *check_lock.ACTIVE_TEMPLATES,
    ):
        src = ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
    # every tracked file must exist in the sandbox, or the checker reports it missing
    for rel in check_lock.TRACKED:
        src = ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy(src, dst)
    return tmp_path


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the checker against a sandbox root."""
    cmd = [sys.executable, str(SCRIPT), *args]
    env = dict(os.environ)
    env["PH_CHECK_ROOT"] = str(root)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_clean_repo_reports_no_warnings() -> None:
    warnings, errors = check_lock.collect(ROOT)
    assert errors == [], f"unexpected hard errors: {errors}"
    assert warnings == [], f"unexpected warnings: {warnings}"


def test_unsanctioned_asset_is_a_warning_not_an_error(sandbox: Path) -> None:
    (sandbox / "docs/brand/assets/rogue-mark.svg").write_text("<svg/>")
    warnings, errors = check_lock.collect(sandbox)
    assert any("unsanctioned asset" in w for w in warnings)
    assert errors == []


def test_missing_sanctioned_asset_is_a_warning(sandbox: Path) -> None:
    (sandbox / "docs/brand/assets/emblem-book-heart.svg").unlink()
    warnings, errors = check_lock.collect(sandbox)
    assert any("missing asset" in w for w in warnings)
    assert errors == []


def test_missing_required_token_is_a_warning(sandbox: Path) -> None:
    css = sandbox / "docs/brand/design-tokens.css"
    css.write_text(css.read_text().replace("--forest-night:", "--gone-night:"))
    warnings, errors = check_lock.collect(sandbox)
    assert any("missing token --forest-night" in w for w in warnings)
    assert errors == []


def test_removed_asset_reference_is_a_warning(sandbox: Path) -> None:
    (sandbox / "docs/brand/notes.md").write_text("see wordmark-primary.svg\n")
    warnings, errors = check_lock.collect(sandbox)
    assert any("removed asset" in w for w in warnings)
    assert errors == []


def test_changed_file_since_baseline_is_a_warning(sandbox: Path) -> None:
    css = sandbox / "docs/brand/design-tokens.css"
    css.write_text(css.read_text() + "\n/* tweak */\n")
    warnings, errors = check_lock.collect(sandbox)
    assert any("changed since baseline" in w for w in warnings)
    assert errors == []


def test_default_run_exits_zero_with_warnings(sandbox: Path) -> None:
    (sandbox / "docs/brand/assets/rogue-mark.svg").write_text("<svg/>")
    result = run(sandbox)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "warning" in result.stdout.lower()


def test_strict_run_exits_nonzero_with_warnings(sandbox: Path) -> None:
    (sandbox / "docs/brand/assets/rogue-mark.svg").write_text("<svg/>")
    result = run(sandbox, "--strict")
    assert result.returncode == 1, result.stdout + result.stderr


def test_strict_run_exits_zero_on_clean_repo(sandbox: Path) -> None:
    result = run(sandbox, "--strict")
    assert result.returncode == 0, result.stdout + result.stderr


def test_update_rewrites_baseline_checksums(sandbox: Path) -> None:
    css = sandbox / "docs/brand/design-tokens.css"
    css.write_text(css.read_text() + "\n/* tweak */\n")
    result = run(sandbox, "--update")
    assert result.returncode == 0, result.stdout + result.stderr
    baseline = json.loads(
        (sandbox / "packages/brand-tools/design-system.baseline.json").read_text()
    )
    assert "docs/brand/design-tokens.css" in baseline


def test_version_token_is_named_system_version() -> None:
    """The old --ph-lock-version token is gone; the version is no longer a lock."""
    css = (ROOT / "docs/brand/design-tokens.css").read_text()
    assert "--ph-system-version:" in css
    assert "--ph-lock-version" not in css


def test_stale_showcase_reference_is_an_advisory_warning(sandbox: Path) -> None:
    guide = sandbox / "docs/brand/DESIGN-SYSTEM.md"
    guide.write_text("Design System 3.1\npreview/design-system-3-0.png\n")
    warnings, errors = check_lock.collect(sandbox)
    assert any("stale showcase reference" in warning for warning in warnings)
    assert errors == []


def test_gold_led_guidance_is_an_advisory_warning(sandbox: Path) -> None:
    theme = sandbox / "docs/brand/brand-theme.md"
    theme.parent.mkdir(parents=True, exist_ok=True)
    theme.write_text("Gold leads, green answers.\n")
    warnings, errors = check_lock.collect(sandbox)
    assert any("green-led" in warning for warning in warnings)
    assert errors == []


def test_google_fonts_runtime_link_is_an_advisory_warning(sandbox: Path) -> None:
    guide = sandbox / "docs/brand/doop-guideline.md"
    guide.write_text('<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet">\n')
    warnings, errors = check_lock.collect(sandbox)
    assert any("Google Fonts" in warning for warning in warnings)
    assert errors == []


def test_active_template_google_fonts_link_is_an_advisory_warning(sandbox: Path) -> None:
    template = sandbox / "content/threads/templates/quote-card.html"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text('<link href="https://fonts.gstatic.com/s/inter" rel="preload">\n')
    warnings, errors = check_lock.collect(sandbox)
    assert any("active template" in warning for warning in warnings)
    assert errors == []
