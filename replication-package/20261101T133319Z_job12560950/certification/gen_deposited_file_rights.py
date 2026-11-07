#!/usr/bin/env python3
"""gen_deposited_file_rights.py -- Phase-6 matrix (b): the DEPOSITED-FILE rights matrix.

Maps EVERY shipped member (the reviewed PUBLIC_PACKAGE_ALLOWLIST) to exactly one affirmative-SHIP
rights row: rights_class, redistribution basis, and the evidence source. Fails if any member has no
basis, or if any EXCLUDED (restricted) file is on the ship list. Emits DEPOSITED_FILE_RIGHTS.csv +
a LICENSE-basis summary.

Data members (2026-09-17). RESTRICTED_FILE_INVENTORY.csv states a DISPOSITION (ships / ships
SANITIZED / EXCLUDED), which answers "does this file ship?" but NOT "on what right?". A shipped data
member therefore takes its `basis` from an actual redistribution basis, in this order:
  1. `certification/PUBLIC_SOURCE_PROVENANCE.csv:redistribution_basis` -- the per-file provenance
     ledger (public-domain US Government work; CC0; third-party academic data published openly by
     its authors with a citation request; author-owned hand-coded or model-assisted work product);
  2. DERIVED_DATA_BASIS below -- the explicit basis for author-created derived outputs that the
     shipped programs REGENERATE from public FDA inputs, which by design are not in the provenance
     ledger (their bytes are not a download and are not deterministically pre-hashable).
The inventory disposition is still recorded alongside the basis, and an EXCLUDED file still fails.
A data member with neither a ledger row nor a DERIVED_DATA_BASIS entry fails closed (NEEDS-ROW).

Usage: python3 certification/gen_deposited_file_rights.py [--root .]   (exit 0 = every member has a basis)
"""
import argparse, csv, datetime, hashlib, json, os, re, sys

# Redistribution-rights evidence for a restricted-derived committed parameter is bound to the
# ARTIFACT's own content (knowable at source-freeze, before any candidate ZIP exists), NOT to a
# not-yet-existing candidate. Evidence docs live ONLY under this reviewed root.
RIGHTS_EVIDENCE_ROOT = os.path.join('certification', 'rights_evidence')
RIGHTS_SCHEMA = 'artifact_rights/v1'
RIGHTS_PASS = 'APPROVED_FOR_REDISTRIBUTION'
_ISO_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# Explicit redistribution bases for the shipped data members that the pipeline REGENERATES from
# public FDA inputs (so they carry no download-provenance row). Keys are exact allowlist paths or,
# for the frozen entity-resolution artifacts, a path prefix. Every basis names the right relied on,
# not a disposition.
_FDA_DERIVED = ('author-created derived dataset, computed by the shipped programs in '
                'code/00_generate_data/ from public-domain FDA sources (the 510(k) and PMA '
                'releasable databases and the MAUDE MDR files); contains no third-party licensed '
                'content, and the author owns the compilation')
_DEDUPE_ARTIFACT = ('author-created model artifact (pandas_dedupe learned settings and the labelled '
                    'training pairs) fitted on public-domain FDA firm and device names; author-owned, '
                    'reviewed byte-by-byte in certification/NONTABULAR_DATA_AUTHORITY.csv')
DERIVED_DATA_BASIS = {
    'data/raw/unique_devices_thr_75.csv': _FDA_DERIVED,
    'data/raw/unique_firms_thr_75.csv': _FDA_DERIVED,
    'data/raw/unique_firms_in_PC_thr_75.csv': _FDA_DERIVED,
    'data/raw/adverse_event_panel_by_PC_full.csv': _FDA_DERIVED,
    'data/derived/adverse_event_panel_by_PC_full.csv': _FDA_DERIVED,
    'data/derived/Applicant_Device_data.csv': _FDA_DERIVED,
    'data/derived/AD_data_applicant_df_oct22_24.csv': _FDA_DERIVED,
    'data/derived/AD_data_applicant_df2_oct22_24.csv': _FDA_DERIVED,
    'data/derived/LBD_ApprovalTime_Both_oct22_24.csv': _FDA_DERIVED,
    'data/derived/Adv_Event_2020_2022.csv': _FDA_DERIVED,
    'data/derived/All_Adverse_Event_Manufacturers_Deduped.csv': _FDA_DERIVED,
}
DERIVED_DATA_BASIS_PREFIXES = (
    ('data/derived/dedupe_settings', _DEDUPE_ARTIFACT),
)


def load_public_source_bases(path):
    """-> {allowlist path: redistribution_basis} from the public-source provenance ledger."""
    out = {}
    if os.path.isfile(path):
        for r in csv.DictReader(open(path, encoding='utf-8')):
            f = (r.get('file') or '').strip()
            b = (r.get('redistribution_basis') or '').strip()
            if f and b:
                out[f] = b
    return out


def data_member_basis(m, public_bases):
    """The real redistribution basis for a shipped data/ member, or None if there is none."""
    b = public_bases.get(m)
    if b:
        return f'{b} [PUBLIC_SOURCE_PROVENANCE]'
    b = DERIVED_DATA_BASIS.get(m)
    if b:
        return f'{b} [DERIVED_DATA_BASIS]'
    for pref, basis in DERIVED_DATA_BASIS_PREFIXES:
        if m.startswith(pref):
            return f'{basis} [DERIVED_DATA_BASIS]'
    return None

def _sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def _artifact_rights_evidence_ok(evidence, member, root):
    """Redistribution-RIGHTS evidence for a restricted-derived committed-parameter member. This is a
    property of the artifact's CONTENT -- settled at source-freeze, decoupled from the package-bound
    PRIVACY audit and from Data-Editor TECHNICAL acceptance (external-audit R2 F1/F2/F9). The evidence
    field must be exactly 'ARTIFACT_RIGHTS:<relpath>' where <relpath>:
      - is a SAFE relative path (no absolute, no '..', no symlink) resolving strictly UNDER
        certification/rights_evidence/ within root (rejects the abs / '../' escape the prior token allowed);
      - is a versioned JSON evidence document (schema 'artifact_rights/v1') that carries an affirmative
        determination for THIS artifact, bound to the artifact's own sha256, by a named non-DataEditor
        rights authority.
    Fails closed on a bad path, missing/unreadable/malformed doc, wrong schema, non-PASS determination, an
    artifact_sha256 that does not equal the actual committed artifact bytes, an empty reviewer/role/date/
    basis/seal, an invalid date, or a reviewer_role that is the Data Editor (who grants technical, not
    redistribution, acceptance). Returns (ok, reason)."""
    ev = (evidence or '').strip()
    m = re.match(r'^ARTIFACT_RIGHTS:(.+)$', ev)
    if not m:
        return (False, "evidence is not of form ARTIFACT_RIGHTS:<relpath>")
    rel = m.group(1).strip()
    if os.path.isabs(rel) or rel.startswith('/') or '..' in rel.replace('\\', '/').split('/'):
        return (False, f'unsafe evidence path (absolute or ..): {rel!r}')
    root_abs = os.path.realpath(root)
    evroot_abs = os.path.realpath(os.path.join(root_abs, RIGHTS_EVIDENCE_ROOT))
    p_abs = os.path.realpath(os.path.join(root_abs, rel))
    if p_abs != evroot_abs and not p_abs.startswith(evroot_abs + os.sep):
        return (False, f'evidence path escapes {RIGHTS_EVIDENCE_ROOT}/: {rel!r}')
    # reject a symlink anywhere on the declared path (realpath containment already blocks escape, but be strict)
    if os.path.islink(os.path.join(root_abs, rel)):
        return (False, f'evidence path is a symlink: {rel!r}')
    if not os.path.isfile(p_abs):
        return (False, f'rights evidence document not found: {rel}')
    try:
        doc = json.load(open(p_abs, encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        return (False, f'rights evidence document is not valid JSON: {type(e).__name__}')
    if not isinstance(doc, dict) or doc.get('schema') != RIGHTS_SCHEMA:
        return (False, f"rights evidence schema != {RIGHTS_SCHEMA}")
    if str(doc.get('determination', '')).strip() != RIGHTS_PASS:
        return (False, f"determination != {RIGHTS_PASS} (got {doc.get('determination')!r})")
    if str(doc.get('artifact', '')).strip() != member:
        return (False, f"evidence artifact {doc.get('artifact')!r} != member {member!r}")
    art_abs = os.path.join(root_abs, member)
    if not os.path.isfile(art_abs):
        return (False, f'the artifact itself is missing: {member}')
    declared = str(doc.get('artifact_sha256', '')).strip().lower()
    if not re.fullmatch(r'[0-9a-f]{64}', declared):
        return (False, 'artifact_sha256 is not a 64-hex digest')
    actual = _sha256_file(art_abs)
    if actual != declared:
        return (False, f'artifact_sha256 mismatch for {member} '
                       f'(evidence {declared[:12]}..., actual {actual[:12]}...)')
    for f in ('reviewer', 'reviewer_role', 'rights_basis', 'source_content_seal'):
        if not str(doc.get(f, '')).strip():
            return (False, f'empty required field: {f}')
    # R3 F8: the source_content_seal must be a real content hash bound to the artifact -- not just any
    # nonempty string. It must equal the artifact's own sha256 content seal.
    seal = str(doc.get('source_content_seal', '')).strip().lower()
    if not re.fullmatch(r'[0-9a-f]{64}', seal):
        return (False, 'source_content_seal is not a 64-hex content hash')
    if seal != actual:
        return (False, 'source_content_seal does not equal the artifact content hash')
    # R3 F8: parse the date as a real calendar date -- a regex alone accepted 2026-99-99.
    dstr = str(doc.get('date', '')).strip()
    if not _ISO_DATE.match(dstr):
        return (False, 'date is not ISO YYYY-MM-DD')
    try:
        datetime.date.fromisoformat(dstr)
    except ValueError:
        return (False, f'date is not a valid calendar date: {dstr}')
    if 'data editor' in str(doc.get('reviewer_role', '')).lower():
        return (False, 'reviewer_role is the Data Editor, who grants technical (not redistribution) acceptance')
    # R3 F8: rights are an AUTHOR REPRESENTATION unless an independent provider/licensing review is cited.
    if str(doc.get('basis_type', '')).strip().lower() not in ('author_representation', 'independent_review'):
        return (False, "basis_type must be 'author_representation' or 'independent_review' (R3 F8)")
    return (True, f"artifact-bound rights evidence verified ({rel}; basis_type={doc.get('basis_type')})")

def load_allowlist(p):
    return [l.strip() for l in open(p) if l.strip() and not l.startswith('#')]

def load_inventory(p):
    disp = {}
    if os.path.isfile(p):
        for r in csv.DictReader(open(p)):
            f = (r.get('file') or '').strip()
            if f:
                disp[f] = (r.get('public_package') or '').strip()
    return disp

def load_parameter_rights(path):
    rows = {}
    if os.path.isfile(path):
        for r in csv.DictReader(open(path)):
            rows[(r.get('file') or '').strip()] = r
    return rows


def classify(m, disp, parameter_rights, root='.', public_bases=None):
    """-> (rights_class, redistribution, basis/evidence). One affirmative row per member."""
    public_bases = public_bases or {}
    d = disp.get(m)
    if d and 'EXCLUD' in d.upper():
        return ('RESTRICTED', 'DO-NOT-SHIP', 'RESTRICTED_FILE_INVENTORY: EXCLUDED')   # must not appear
    if m.startswith('synthetic_pipeline/_synthetic_source_internal/'):
        r = parameter_rights.get(m)
        if not r:
            return ('committed-parameter', 'NEEDS-ROW', 'missing COMMITTED_PARAMETER_RIGHTS row')
        status = (r.get('status') or '').strip()
        if status != 'APPROVED_TO_SHIP':
            return ('committed-parameter', 'NEEDS-ROW',
                    f"COMMITTED_PARAMETER_RIGHTS status={status or '<blank>'}")
        # Restricted-derived committed parameters (rounded/smoothed DGP params; restricted
        # aggregate-interface dimensions) require VERIFIABLE, ARTIFACT-CONTENT-BOUND redistribution-rights
        # evidence -- a bare APPROVED_TO_SHIP status is NOT sufficient. This is settled at source-freeze
        # (the artifact + its rights evidence both exist), so it does NOT deadlock the --final build on a
        # not-yet-existing candidate (R2 F1); the candidate-bound PRIVACY audit is separate. Public-source-
        # derived committed inputs (public design/skeleton) keep the status-only basis.
        is_restricted_derived = 'restricted' in (r.get('content_class') or '').lower()
        if is_restricted_derived:
            ok, why = _artifact_rights_evidence_ok(r.get('evidence') or '', m, root)
            if not ok:
                return ('committed-parameter', 'NEEDS-ROW',
                        f"restricted-derived committed parameter needs verified artifact-bound rights "
                        f"evidence ({why})")
            return ('committed-parameter', 'redistributable',
                    f"COMMITTED_PARAMETER_RIGHTS: {r.get('redistribution_basis', '').strip()} "
                    f"[{why}]")
        return ('committed-parameter', 'redistributable',
                f"COMMITTED_PARAMETER_RIGHTS: {r.get('redistribution_basis', '').strip()}")
    # data files: the inventory says WHETHER it ships; the ledger/table says ON WHAT RIGHT.
    if m.startswith('data/'):
        if not d:
            return ('data-UNSPECIFIED', 'NEEDS-ROW',
                    'every shipped data member requires an explicit RESTRICTED_FILE_INVENTORY row')
        basis = data_member_basis(m, public_bases)
        if not basis:
            return ('data-UNSPECIFIED', 'NEEDS-ROW',
                    'shipped data member has no redistribution basis: add a '
                    'PUBLIC_SOURCE_PROVENANCE.csv row or a DERIVED_DATA_BASIS entry')
        san = 'SANITIZED' in d.upper()
        return ('public-data' if not san else 'sanitized-public',
                'redistributable', f'{basis}; disposition {d}')
    if m.startswith('synthetic_pipeline/simulated_data/'):
        return ('synthetic-data', 'redistributable', 'author-generated synthetic (no restricted values; audit_simulated_data)')
    if m.startswith('models/'):
        return ('third-party-model', 'redistributable-under-license', 'shipped model license (e.g. all-MiniLM-L6-v2 Apache-2.0)')
    # Author-drawn exhibits and their editable sources. A `.drawio` file is diagram XML, not a
    # rendered image, so the image regex further down never reached it and it fell through to
    # UNCLASSIFIED. This rule sits BEFORE the output/ prefix so the basis is right wherever the
    # file is listed (it lives in manual_figures/, beside the .png it renders to, rather than in
    # output/figures/, which would misclassify it as a pipeline product).
    if m.endswith('.drawio'):
        return ('author-figure', 'redistributable',
                'author-created editable figure source (draw.io diagram XML authored by the author; '
                'no third-party content)')
    if m.startswith('manual_figures/') and re.search(r'\.(png|pdf|jpg|jpeg|svg)$', m):
        return ('author-figure', 'redistributable',
                'author-drawn manuscript exhibit, copied rather than regenerated by run_all.py')
    if m.startswith('output/'):
        return ('author-output', 'redistributable', 'author-generated exhibit from the pipeline')
    if m.startswith('output-simulated/'):
        return ('synthetic-output', 'redistributable',
                'author-generated synthetic-route reference exhibit (regenerated on shipped simulated_data; no restricted values)')
    if m.startswith('paper/'):
        return ('author-manuscript', 'redistributable', 'author-authored manuscript + build')
    if (m.startswith(('code/', 'synthetic_pipeline/', 'certification/', 'r_scripts/', 'docker/'))
            or re.search(r'\.(py|R|r|sh|sql|do)$', m) or m in ('run_all.py', 'config.py')):
        return ('author-code', 'redistributable', 'author-authored code')
    # README.pdf is the typeset copy of README.md, not a manuscript exhibit; it is classified with
    # the documentation it duplicates rather than falling through to the generic image rule below.
    if m == 'README.pdf':
        return ('author-doc/config', 'redistributable',
                'author-authored documentation (typeset copy of README.md)')
    # A supplementary evidence archive: author-generated material retained as the record behind a
    # documented claim, which the pipeline never reads. Shipped as one archive rather than as its
    # individual members because it is evidence rather than input, so the deposit hashes it as a
    # single object. Its contents and their provenance are described in the document it supports.
    if re.search(r'\.zip$', m):
        return ('author-evidence-archive', 'redistributable',
                'author-generated evidence archive (model responses obtained by the author through '
                'the OpenAI API, author-authored analysis scripts, and their outputs); no '
                'third-party content and no restricted values')
    if re.search(r'\.(md|txt|csv|json|lock|tsv|yml|yaml)$', m) or m in ('.dockerignore', 'LICENSE.txt'):
        return ('author-doc/config', 'redistributable', 'author-authored doc/config/manifest')
    if re.search(r'\.(png|pdf|jpg|jpeg)$', m):
        return ('author-figure', 'redistributable', 'author-created figure')
    return ('UNCLASSIFIED', 'NEEDS-ROW', 'no rule matched')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='certification/DEPOSITED_FILE_RIGHTS.csv')
    a = ap.parse_args(); root = os.path.abspath(a.root)
    members = load_allowlist(os.path.join(root, 'certification/PUBLIC_PACKAGE_ALLOWLIST.txt'))
    disp = load_inventory(os.path.join(root, 'RESTRICTED_FILE_INVENTORY.csv'))
    parameter_rights = load_parameter_rights(
        os.path.join(root, 'certification/COMMITTED_PARAMETER_RIGHTS.csv'))
    public_bases = load_public_source_bases(
        os.path.join(root, 'certification/PUBLIC_SOURCE_PROVENANCE.csv'))
    rows, gaps, restricted_shipping = [], [], []
    cls_count = {}
    for m in members:
        rc, redis, basis = classify(m, disp, parameter_rights, root, public_bases)
        rows.append((m, rc, redis, basis))
        cls_count[rc] = cls_count.get(rc, 0) + 1
        if redis == 'NEEDS-ROW':
            gaps.append(m)
        if rc == 'RESTRICTED':
            restricted_shipping.append(m)
    with open(os.path.join(root, a.out), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['file', 'rights_class', 'redistribution', 'basis'])
        for r in sorted(rows): w.writerow(r)
    print(f"=== deposited-file rights matrix: {len(rows)} members ===")
    for c in sorted(cls_count): print(f"  {cls_count[c]:5d}  {c}")
    if restricted_shipping:
        print(f"FAIL -- {len(restricted_shipping)} RESTRICTED (EXCLUDED) file(s) on the ship list:")
        for m in restricted_shipping[:20]: print("   ", m)
        return 1
    if gaps:
        print(f"FAIL -- {len(gaps)} member(s) with NO rights basis:")
        for m in gaps[:30]: print("   ", m)
        return 1
    print(f"PASS -- every member has exactly one affirmative-SHIP rights row. matrix: {a.out}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
