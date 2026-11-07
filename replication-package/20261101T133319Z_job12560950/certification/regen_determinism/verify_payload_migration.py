#!/usr/bin/env python3
"""verify_payload_migration.py -- payload-authority check run by the certification harness before a reference is frozen.

Requiring the freshly clean-room-regenerated payload manifest to be BYTE-IDENTICAL to the committed
manifest is correct for a no-change recertification, but it makes an INTENDED, reviewed payload
migration (most recently 116 -> 118 files) structurally impossible: a legitimate payload change
would be fatal because it cannot equal the stale baseline.

This verifier therefore takes two paths:

  * NO CHANGE  -- if the fresh manifest equals the committed (BEFORE) manifest exactly (same paths AND
    hashes), payload-neutrality is confirmed and this check exits 0. It preserves the strict guarantee for a
    recertification where nothing is supposed to change.

  * MIGRATION  -- if they differ, the change is authorized ONLY by a deliberately reviewed migration
    record that pins the ENTIRE reviewed target and the exact delta:
        - the record parses and its target_manifest_sha256 is a real sha256 (not a PENDING_REGEN
          placeholder) that EQUALS sha256(fresh manifest file)  -> the fresh build reproduces the
          reviewed target manifest exactly (determinism against the reviewed target, not the stale one);
        - prior_file_count == #entries(BEFORE); target_file_count == #entries(fresh) == #entries(inventory);
        - the declared added/removed file sets EXACTLY equal the actual presence delta.
    Any mismatch -- or a record still marked PENDING_REGEN -- fails closed, so a silent/unreviewed drift
    can never pass, while a reviewed migration can.

`added` / `removed` entries may be a plain path string or an object {"path": ..., "sha256": ...};
when a sha256 is given it must equal the fresh manifest's hash for that path, so the record pins the
CONTENT of each added file and not only its name.

SIGN-OFF AND MODES
------------------
A migration record whose sign-off fields are not filled in (status != REVIEWED, a reviewer containing
"PENDING", or a non-ISO review_date) is UNSIGNED. An unsigned record:

  * FAILS by default -- the mode a seal, a final build and an unattended certification run use;
  * is refused outright by --final, whatever the environment says;
  * is accepted, with a loud banner, ONLY when FDA_ALLOW_UNSIGNED_MIGRATION=1 is set in the
    environment and --final is not passed. That exists so a stage-1 REHEARSAL can be run on the
    cluster before the author signs; its banner says in so many words that the run it authorizes
    must not be sealed or deposited.

Determinism (gen1 == gen2), the reviewed inventory match, and the contract/privacy gates are enforced
separately in stage 1 (steps A1/A3); this verifier adds the reviewed-target/migration-record authority.

Exit 0 = authorized (no-change, reviewed migration, or rehearsal-authorized unsigned migration);
exit 1 = fail closed.
"""
import argparse
import hashlib
import json
import os
import re
import sys

_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+(.*)$")

UNSIGNED_ENV = "FDA_ALLOW_UNSIGNED_MIGRATION"


def _norm(path):
    """Normalize a payload path to be relative to the simulated_data/ root, so the committed manifest
    (synthetic_pipeline/simulated_data/...), the fresh manifest, and the inventory (simulated_data/...)
    compare on equal footing regardless of the leading prefix."""
    p = path.strip()
    m = re.search(r"(?:^|.*?/)simulated_data/(.*)$", p)
    return m.group(1) if m else p


def _read_manifest(path):
    """-> dict {normalized_path: hash}. Accepts '<sha256>  <path>' lines (path may contain spaces)."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln.strip():
                continue
            m = _LINE.match(ln)
            if not m:
                # a manifest line that cannot be parsed is a hard error, not a silent skip
                raise ValueError(f"unparseable manifest line in {path}: {ln[:80]!r}")
            key = _norm(m.group(2))
            if key in out:
                # a duplicate path would be silently collapsed into the dict, hiding a doubled entry
                raise ValueError(f"duplicate manifest path (would collapse): {key!r} in {path}")
            out[key] = m.group(1).lower()
    return out


def _read_inventory(path):
    out = set()
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                key = _norm(ln)
                if key in out:
                    raise ValueError(f"duplicate inventory path: {key!r} in {path}")
                out.add(key)
    return out


def _entry_path(entry):
    """An added/removed entry is either a path string or {"path": ..., "sha256": ...}."""
    if isinstance(entry, dict):
        return _norm(str(entry.get("path", "")))
    return _norm(str(entry))


def _entry_sha(entry):
    if isinstance(entry, dict):
        s = str(entry.get("sha256", "")).strip().lower()
        return s if re.fullmatch(r"[0-9a-f]{64}", s) else None
    return None


def _signoff_state(rec):
    """-> (signed: bool, reasons: [str]). An unfilled sign-off field leaves the record UNSIGNED."""
    reasons = []
    status = str(rec.get("status", "")).strip()
    reviewer = str(rec.get("reviewer", "")).strip()
    review_date = str(rec.get("review_date", "")).strip()
    if status.upper() != "REVIEWED":
        reasons.append(f"status != REVIEWED (got {status!r})")
    if not reviewer:
        reasons.append("reviewer is empty")
    elif "PENDING" in reviewer.upper():
        reasons.append(f"reviewer is a placeholder (got {reviewer!r})")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_date):
        reasons.append(f"review_date is not ISO YYYY-MM-DD (got {review_date!r})")
    return (not reasons), reasons


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True, help="previously committed payload sha256 manifest")
    ap.add_argument("--fresh", required=True, help="freshly clean-room-regenerated payload sha256 manifest")
    ap.add_argument("--inventory", required=True, help="reviewed expected-files inventory")
    ap.add_argument("--record", required=True, help="PAYLOAD_MIGRATION_RECORD.json")
    ap.add_argument("--final", action="store_true",
                    help="seal/final mode: an UNSIGNED migration record is refused even if "
                         f"{UNSIGNED_ENV}=1 is set in the environment.")
    a = ap.parse_args()

    for f in (a.before, a.fresh, a.inventory):
        if not os.path.isfile(f):
            print(f"FAIL: required input missing: {f}")
            return 1

    try:
        before = _read_manifest(a.before)
        fresh = _read_manifest(a.fresh)
        inventory = _read_inventory(a.inventory)
    except ValueError as e:  # unparseable line, or a duplicate path -> fail closed, do not collapse
        print(f"FAIL: {e}")
        return 1

    # ---- NO-CHANGE path -------------------------------------------------------------------------
    if before == fresh:
        # An unchanged payload is still only authorized by a record that describes IT: when a
        # record is on file it must match the shipped payload's file count and manifest sha256 and
        # must be signed, so the gate cannot pass on a record that describes a different payload.
        print(f"PAYLOAD-NEUTRAL: fresh build byte-identical to the committed manifest "
              f"({len(fresh)} files).")
        if not os.path.isfile(a.record):
            print("PAYLOAD-NEUTRAL: no migration record on file; none is required for an "
                  "unchanged payload.")
            return 0
        try:
            rec = json.load(open(a.record, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"FAIL: could not parse migration record: {e}")
            return 1
        rec_sha = str(rec.get("target_manifest_sha256", "")).strip().lower()
        fresh_sha = _sha256_file(a.fresh)
        rec_n = rec.get("target_file_count", None)
        stale = []
        if rec_sha != fresh_sha:
            stale.append(f"record target_manifest_sha256 {rec_sha[:12] or '(unset)'}... != "
                         f"shipped manifest sha256 {fresh_sha[:12]}...")
        try:
            if int(rec_n) != len(fresh):
                stale.append(f"record target_file_count {rec_n} != shipped payload count {len(fresh)}")
        except (TypeError, ValueError):
            stale.append(f"record target_file_count is not an integer (got {rec_n!r})")
        if stale:
            for r in stale:
                print(f"FAIL: the migration record on file does not describe the shipped payload -- {r}")
            print("FAIL: an unchanged payload is still only authorized by a record that describes IT. "
                  "Regenerate the record for the shipped payload (naming any added/removed files) and "
                  "have the author review it.")
            return 1
        signed, signoff_reasons = _signoff_state(rec)
        rehearsal = (not a.final) and os.environ.get(UNSIGNED_ENV, "") == "1"
        if not signed and not rehearsal:
            for r in signoff_reasons:
                print(f"FAIL: the record describing the shipped payload is UNSIGNED -- {r}")
            print("FAIL: the shipped payload is not author-authorized. Set status=REVIEWED with a "
                  f"reviewer name and an ISO review_date (for a REHEARSAL only, {UNSIGNED_ENV}=1).")
            return 1
        if not signed:
            print(f"!! {UNSIGNED_ENV}=1: unchanged payload accepted on an UNSIGNED record "
                  "(REHEARSAL only -- do not seal, certify or deposit).")
        print(f"PAYLOAD-NEUTRAL: the record on file describes this payload "
              f"({len(fresh)} files, {fresh_sha[:12]}...)"
              f"{' and is signed.' if signed else ' but is NOT signed (rehearsal).'}")
        return 0

    # ---- MIGRATION path -------------------------------------------------------------------------
    print(f"payload changed vs committed baseline (before={len(before)} files, fresh={len(fresh)} files) "
          f"-> a reviewed migration record is REQUIRED")
    if not os.path.isfile(a.record):
        print(f"FAIL: payload changed but no migration record at {a.record}")
        return 1
    try:
        rec = json.load(open(a.record, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: could not parse migration record: {e}")
        return 1

    tgt_sha = str(rec.get("target_manifest_sha256", "")).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", tgt_sha):
        print(f"FAIL: migration record target_manifest_sha256 is not a finalized sha256 "
              f"(got {rec.get('target_manifest_sha256')!r}); the migration is not yet reviewed/finalized "
              f"(e.g. still PENDING_REGEN until the payload is regenerated and the reviewed fixed-inventory "
              f"manifest is committed).")
        return 1

    fresh_sha = _sha256_file(a.fresh)
    if fresh_sha != tgt_sha:
        print(f"FAIL: fresh manifest sha256 {fresh_sha[:12]}... != reviewed target_manifest_sha256 "
              f"{tgt_sha[:12]}... -- the fresh build does NOT reproduce the reviewed target payload.")
        return 1

    ok = True

    def _check(cond, msg):
        nonlocal ok
        if not cond:
            print("FAIL:", msg)
            ok = False

    # R2 F6: a mechanically self-consistent record is NOT enough -- require genuine human review. The
    # record must declare status=REVIEWED and carry a nonempty reviewer, ISO date, and rationale, so a
    # migration cannot be relabeled "authorized" without anyone reviewing it. The one documented
    # relaxation is the rehearsal escape hatch below, which never applies in --final mode.
    signed, signoff_reasons = _signoff_state(rec)
    rehearsal = (not a.final) and os.environ.get(UNSIGNED_ENV, "") == "1"
    if not signed:
        if not rehearsal:
            for r in signoff_reasons:
                print(f"FAIL: migration record is UNSIGNED -- {r}")
            print("FAIL: an unsigned payload migration record cannot authorize a certification run, a seal or a "
                  "final build. The author must set status=REVIEWED with a reviewer name and an ISO "
                  f"review_date. For a REHEARSAL only, set {UNSIGNED_ENV}=1 (refused under --final).")
            return 1
        print("=" * 78)
        print(f"!! {UNSIGNED_ENV}=1: proceeding on an UNSIGNED payload migration record.")
        for r in signoff_reasons:
            print(f"!!   unsigned because: {r}")
        print("!! This is a REHEARSAL authorization only. The payload migration has NOT been reviewed")
        print("!! by the author, so anything this run produces must NOT be sealed, certified or")
        print("!! deposited. Re-run with a signed record before stage 2.")
        print("=" * 78)
    _check(bool(str(rec.get("reason", "")).strip()), "migration record has empty reason/rationale")

    _check(int(rec.get("prior_file_count", -1)) == len(before),
           f"prior_file_count {rec.get('prior_file_count')} != committed baseline count {len(before)}")
    _check(int(rec.get("target_file_count", -1)) == len(fresh),
           f"target_file_count {rec.get('target_file_count')} != fresh count {len(fresh)}")
    _check(len(fresh) == len(inventory),
           f"fresh count {len(fresh)} != reviewed inventory count {len(inventory)}")
    _check(set(fresh.keys()) == inventory,
           "fresh payload file set does not equal the reviewed inventory file set")

    declared_added = {_entry_path(x) for x in rec.get("added", [])}
    declared_removed = {_entry_path(x) for x in rec.get("removed", [])}
    actual_added = set(fresh.keys()) - set(before.keys())
    actual_removed = set(before.keys()) - set(fresh.keys())
    _check(declared_added == actual_added,
           f"declared added {sorted(declared_added)} != actual added {sorted(actual_added)}")
    _check(declared_removed == actual_removed,
           f"declared removed {sorted(declared_removed)} != actual removed {sorted(actual_removed)}")

    # Where the record pins an added file's sha256, the fresh build must reproduce that content.
    for entry in rec.get("added", []):
        want = _entry_sha(entry)
        if want is None:
            continue
        key = _entry_path(entry)
        got = fresh.get(key)
        _check(got == want,
               f"added {key}: fresh sha256 {got} != the sha256 pinned in the migration record {want}")

    if not ok:
        return 1
    verdict = ("MIGRATION AUTHORIZED: reviewed migration" if signed else
               "MIGRATION REHEARSAL-AUTHORIZED (record UNSIGNED -- do not seal, certify or deposit "
               "anything this run produces): migration")
    print(f"{verdict} {rec.get('prior_file_count')} -> "
          f"{rec.get('target_file_count')} files (added {sorted(actual_added)}, "
          f"removed {sorted(actual_removed)}); fresh build reproduces the reviewed target manifest "
          f"(sha256 {fresh_sha[:12]}...). reviewer={rec.get('reviewer')} date={rec.get('review_date')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
