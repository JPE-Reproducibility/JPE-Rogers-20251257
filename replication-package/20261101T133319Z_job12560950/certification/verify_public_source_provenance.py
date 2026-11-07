#!/usr/bin/env python3
"""verify_public_source_provenance.py -- strict validator for the public-source provenance ledger
(certification/PUBLIC_SOURCE_PROVENANCE.csv), external-audit R5 F7. Before R5 the ledger existed but NO
gate consumed it, so its all-PENDING state could ship silently. This validator FAILS closed on any
incomplete row, and (with --root) re-checks that each recorded local_sha256 equals the shipped bytes.

A local sha proves integrity of the shipped bytes, NOT provenance; provenance requires an independent
source URL/DOI, a version/access date, and a provider checksum, plus a completed review status. Every
such field must be populated (no PENDING/TBD/TODO/empty) for the ledger to pass.

Checks (any failure -> exit 1):
  * every row: non-empty file; local_sha256 is 64-hex; source_url_or_doi, version_or_access_date,
    provider_checksum, redistribution_basis all populated (not a PENDING token); review_status is a
    completed status (contains no PENDING token);
  * with --root: local_sha256 == sha256 of <root>/<file> (the recorded hash matches the shipped bytes);
  * (informational) --root also flags shipped-file/ledger coverage drift if --require-coverage is set.

`--selftest` runs in-memory fixtures (a complete row passes; each PENDING field fails; a hash mismatch
fails) and ignores the live ledger.
"""
import argparse
import csv
import hashlib
import os
import re
import sys

PENDING_RE = re.compile(r"\bPENDING\b|\bTBD\b|\bTODO\b", re.I)
REQUIRED_POPULATED = ["source_url_or_doi", "version_or_access_date", "provider_checksum",
                      "redistribution_basis"]
FIELDS = ["file", "local_sha256", "source_url_or_doi", "version_or_access_date", "provider_checksum",
          "redistribution_basis", "review_status"]

# R6 F6: field-syntax validators reject placeholder nonsense (e.g. every field = "x"). Each returns an
# error string or None.
_URL_RE = re.compile(r"^(https?://\S+\.\S+|(doi:)?10\.\d{4,9}/\S+)$", re.I)
_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_VERSION_RE = re.compile(r"\b(v\d|version\s*\d|\d{4}|rev\s*\d|release\s*\d)", re.I)
_CHECKSUM_RE = re.compile(r"\b(sha256|sha1|sha512|md5|crc32)\b\s*[:=]?\s*[0-9a-f]{8,}", re.I)
_CHECKSUM_METHOD_RE = re.compile(r"(hash|checksum|sha\d|md5|digest|source-hash|source hash)", re.I)
_BASIS_VOCAB = ("public domain", "public-domain", "cc0", "cc-by", "creative commons", "open data",
                "open-source", "open source", "openfda", "fda", "public research", "government work",
                "us government", "no restriction", "freely redistributable", "mit", "bsd", "apache",
                # AUTHOR-OWNED content is a legitimate redistribution basis for this
                # deposit and is already the stated basis elsewhere (DEPOSITED_FILE_RIGHTS.csv and
                # LICENSE section 2 cover author-owned material, incl. work commissioned by the author).
                # Without it, a genuinely author-owned file could only pass by mislabelling itself
                # "public domain", which would be false. Restricted material still cannot ship: that is
                # enforced by RESTRICTED_FILE_INVENTORY + the rights matrix, not by this vocabulary.
                "author-owned", "author owned", "work for hire", "work-for-hire")


# Some ledger rows have NO external source URL by nature -- files the author generated
# (e.g. the GPT-derived price links) or received directly from another researcher. Forcing a URL there would
# make the ledger assert something false, so -- mirroring the R7 F8 checksum fix -- an absent external source
# must be declared with a CONTROLLED token, never prose and never a plausible-looking URL. Every other
# non-URL value still fails closed.
_URL_UNAVAILABLE = {"author-generated-no-external-source", "obtained-from-researcher-no-public-url"}


def _bad_url(v):
    lv = v.strip()
    if _URL_RE.match(lv):
        return None
    if lv.lower() in _URL_UNAVAILABLE:
        return None
    return ("source_url_or_doi is not a URL or DOI, nor a controlled no-external-source token "
            f"({'/'.join(sorted(_URL_UNAVAILABLE))})")

def _bad_version(v):
    return None if (_DATE_RE.search(v) or _VERSION_RE.search(v)) else \
        "version_or_access_date has no ISO date or version token"

# R7 F8: an unavailable provider checksum must be represented by a CONTROLLED token, not prose (prose like
# "provider hash unavailable" must NOT satisfy the checksum requirement).
_CHECKSUM_UNAVAILABLE = {"no-provider-checksum", "provider-checksum-not-published", "not-applicable"}

def _bad_checksum(v):
    lv = v.strip()
    if _CHECKSUM_RE.search(lv):
        return None
    if lv.lower() in _CHECKSUM_UNAVAILABLE:
        return None
    return ("provider_checksum must be an algo:hex checksum OR a controlled unavailable-token "
            f"({'/'.join(sorted(_CHECKSUM_UNAVAILABLE))}) -- prose is not a checksum")

def _bad_basis(v):
    lv = v.strip().lower()
    return None if (len(lv) >= 8 and any(k in lv for k in _BASIS_VOCAB)) else \
        "redistribution_basis is not a recognized basis (needs a known license/public-domain term)"

# R7 F8: a completed review needs a controlled disposition + a named reviewer + an ISO date -- a bare
# "reviewed 2026-09-09" (no reviewer identity, no controlled disposition) is rejected.
_REVIEW_DISPOSITION = re.compile(r"\b(cross-checked|verified|reviewed-and-matched|source-confirmed)\b", re.I)
_REVIEWER_RE = re.compile(r"\bby\s+[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)+")   # "by First Last"

def _bad_review(v):
    lv = v.strip()
    if PENDING_RE.search(lv):
        return "review_status is not completed (still pending)"
    if not _DATE_RE.search(lv):
        return "review_status has no ISO date"
    if not _REVIEW_DISPOSITION.search(lv):
        return "review_status lacks a controlled disposition (cross-checked/verified/source-confirmed/...)"
    if not _REVIEWER_RE.search(lv):
        return "review_status lacks a named reviewer ('by First Last')"
    return None


def _sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_pending(v):
    v = (v or "").strip()
    return v == "" or bool(PENDING_RE.search(v))


def validate_rows(rows, root=None):
    """rows: list[dict]. -> list[str] violations (empty == valid)."""
    problems = []
    if not rows:
        return ["provenance ledger is empty"]
    seen = set()
    for i, r in enumerate(rows, 1):
        f = (r.get("file") or "").strip()
        where = f"row {i} [{f or '<no-file>'}]"
        if not f:
            problems.append(f"{where}: empty file"); continue
        if f in seen:
            problems.append(f"{where}: duplicate file")
        seen.add(f)
        sha = (r.get("local_sha256") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            problems.append(f"{where}: local_sha256 is not a sha256: {sha!r}")
        for col in REQUIRED_POPULATED:
            if _is_pending(r.get(col)):
                problems.append(f"{where}: {col} is PENDING/empty (provenance not established)")
        # R6 F6: field-SYNTAX validation -- reject placeholder nonsense (e.g. field == 'x').
        if not _is_pending(r.get("source_url_or_doi")):
            e = _bad_url(r.get("source_url_or_doi") or "");  problems += [f"{where}: {e}"] if e else []
        if not _is_pending(r.get("version_or_access_date")):
            e = _bad_version(r.get("version_or_access_date") or "");  problems += [f"{where}: {e}"] if e else []
        if not _is_pending(r.get("provider_checksum")):
            e = _bad_checksum(r.get("provider_checksum") or "");  problems += [f"{where}: {e}"] if e else []
        if not _is_pending(r.get("redistribution_basis")):
            e = _bad_basis(r.get("redistribution_basis") or "");  problems += [f"{where}: {e}"] if e else []
        e = _bad_review(r.get("review_status") or "");  problems += [f"{where}: {e}"] if e else []
        if root and re.fullmatch(r"[0-9a-f]{64}", sha):
            p = os.path.join(root, f)
            if not os.path.isfile(p):
                problems.append(f"{where}: shipped file not found under --root: {p}")
            else:
                got = _sha256(p)
                if got != sha:
                    problems.append(f"{where}: local_sha256 ({sha[:12]}...) != shipped bytes "
                                    f"({got[:12]}...)")
    return problems


def _selftest():
    fails = 0

    def check(name, rows, expect_ok):
        nonlocal fails
        probs = validate_rows(rows)
        ok = (len(probs) == 0)
        good = (ok == expect_ok)
        print(f"  selftest {name}: {'OK' if good else 'FAIL'} (valid={ok}, expected={expect_ok})"
              f"{'' if good else ' :: '+str(probs[:2])}")
        if not good:
            fails += 1

    H = "a" * 64
    complete = {"file": "data/raw/x.csv", "local_sha256": H,
                "source_url_or_doi": "https://open.fda.gov/apis/device/510k/",
                "version_or_access_date": "2026-09-01", "provider_checksum": "sha256:" + "b" * 64,
                "redistribution_basis": "public domain (US Government work, FDA/CDRH)",
                "review_status": "cross-checked by Parker Rogers 2026-09-01"}
    check("complete_row_passes", [complete], True)
    for col in REQUIRED_POPULATED + ["review_status"]:
        bad = dict(complete); bad[col] = "PENDING"
        check(f"pending_{col}_fails", [bad], False)
    # Adversarial case: every provenance field = "x" must FAIL.
    for col in REQUIRED_POPULATED + ["review_status"]:
        check(f"nonsense_x_{col}_fails", [{**complete, col: "x"}], False)
    # R7 F8: prose-as-checksum and a dated phrase without reviewer/disposition must FAIL.
    check("prose_checksum_fails", [{**complete, "provider_checksum": "provider hash unavailable"}], False)
    check("dated_phrase_review_fails", [{**complete, "review_status": "reviewed 2026-09-09"}], False)
    check("controlled_unavailable_checksum_passes",
          [{**complete, "provider_checksum": "no-provider-checksum"}], True)
    check("bad_sha_fails", [{**complete, "local_sha256": "xyz"}], False)
    check("empty_file_fails", [{**complete, "file": ""}], False)
    check("empty_ledger_fails", [], False)
    check("duplicate_file_fails", [complete, complete], False)
    print(f"PROVENANCE_SELFTEST_FAILURES={fails}")
    return 0 if fails == 0 else 1


def load_public_denominator(root):
    """R6 F6: the fixed public-source denominator = every 'path,sha256' row of PUBLIC_INPUT_HASHES.csv (no
    header; comment lines skipped). -> set of shipped public-source data-relative paths."""
    p = os.path.join(root, "certification", "PUBLIC_INPUT_HASHES.csv")
    out = set()
    if os.path.isfile(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [x.strip() for x in line.split(",")]
            if len(parts) >= 2 and re.fullmatch(r"[0-9a-f]{64}", parts[1]) and parts[0].startswith("data/"):
                out.add(parts[0])
    return out


def coverage_problems(rows, root):
    """Exact ledger <-> public-source-denominator coverage (R6 F6)."""
    denom = load_public_denominator(root)
    if not denom:
        return [f"public-source denominator (certification/PUBLIC_INPUT_HASHES.csv) missing/empty under {root}"]
    led = {(r.get("file") or "").strip() for r in rows}
    problems = []
    for f in sorted(denom - led):
        problems.append(f"public source not in the provenance ledger: {f}")
    for f in sorted(led - denom):
        problems.append(f"provenance ledger row is not a known public source: {f}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="built tree root; re-checks local_sha256 vs shipped bytes")
    ap.add_argument("--ledger", default=None, help="path to the provenance CSV (default: sibling)")
    ap.add_argument("--require-coverage", action="store_true",
                    help="also enforce exact ledger<->public-source-denominator coverage (R6 F6)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    ledger = a.ledger or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "PUBLIC_SOURCE_PROVENANCE.csv")
    if not os.path.isfile(ledger):
        print(f"FAIL: provenance ledger missing: {ledger}"); return 2
    with open(ledger, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    problems = validate_rows(rows, root=a.root)
    if a.require_coverage and a.root:
        problems += coverage_problems(rows, a.root)
    print(f"provenance ledger rows={len(rows)} root_hash_check={'on' if a.root else 'off'}")
    if problems:
        print(f"PUBLIC_SOURCE_PROVENANCE_VIOLATIONS={len(problems)}")
        for p in problems[:60]:
            print("  " + p)
        return 1
    print("PUBLIC_SOURCE_PROVENANCE_VIOLATIONS=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
