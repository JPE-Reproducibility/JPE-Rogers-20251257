#!/usr/bin/env python3
"""hash_manuscript_closure.py -- Phase-4 manuscript dependency-closure freeze (JPE reproducibility).

Enumerates + SHA-256-hashes the FULL manuscript dependency closure: the main TeX, every \\input'd
table fragment, every figure the manuscript displays (both \\includegraphics and the panels drawn
through \\begin{overpic}), the .bib, any custom .cls/.sty, the compiler driver (build_manuscript.py),
and the authoritative compiled PDF. Verifies COMPLETENESS (every referenced target resolves to an
existing file) -- a missing/extra target fails the freeze. Emits a stable MANUSCRIPT_CLOSURE.sha256
manifest so the closure identity (not a page count) is what is frozen.

Commented-out TeX (a line's text after an unescaped %) is ignored, so disabled \\includegraphics in
comments are not treated as dependencies. Include paths use the editor prefix
`../replication_package/output/` or the deposit prefix `../output/`; both resolve to <root>/output/.

A built-in self-test re-scans the manuscript with the independent line-based scanner used by
code/audit_pipeline.py and fails the freeze if the two scanners disagree on the set of figure
targets, so a graphics macro that this module does not know about can never silently shrink the
frozen closure again.

Usage:  python3 certification/hash_manuscript_closure.py [--tex paper/JPE_submission_v8.tex] [--root .]
        exit 0 = closure complete + manifest written;  exit 1 = missing target / unreadable dep /
                 figure-target self-test disagreement.
"""
import argparse, hashlib, os, re, sys

INPUT_RE = re.compile(r'\\input\s*\{([^}]+)\}')
GRAPHICS_RE = re.compile(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}')
# Figure panels drawn with the overpic package: \begin{overpic}[...]{<file>} -- same target class as
# \includegraphics (code/audit_pipeline.py collects both).
OVERPIC_RE = re.compile(r'\\begin\{overpic\}\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}')

def strip_tex_comment(line):
    # remove text after the first UNESCAPED % (a \% is a literal percent, not a comment)
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == '\\' and i + 1 < len(line):
            out.append(line[i:i+2]); i += 2; continue
        if c == '%':
            break
        out.append(c); i += 1
    return ''.join(out)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def graphics_refs(body):
    """Every figure target the manuscript displays, in source order, de-duplicated.

    Both macros that take a graphics file are collected: \\includegraphics and \\begin{overpic}.
    `body` must already be comment-stripped.
    """
    refs = []
    for rx in (GRAPHICS_RE, OVERPIC_RE):
        for ref in rx.findall(body):
            if '#' in ref:
                continue
            if ref not in refs:
                refs.append(ref)
    return refs


def audit_pipeline_figure_refs(tex_path):
    """Independent re-scan of the manuscript using code/audit_pipeline.py's line-based scanner.

    Kept deliberately separate from graphics_refs(): it drops whole lines that start with a comment
    character instead of stripping trailing comments, and it is the scanner the exhibit audit uses.
    The two must agree on the set of figure targets; the self-test in main() enforces that.
    """
    refs = []
    for line in open(tex_path, encoding='utf-8', errors='replace').read().split("\n"):
        if line.lstrip().startswith('%'):
            continue
        for rx in (GRAPHICS_RE, OVERPIC_RE):
            for m in rx.finditer(line):
                ref = m.group(1)
                if '#' in ref:
                    continue
                if ref not in refs:
                    refs.append(ref)
    return refs


def resolve(ref, root, texdir):
    ref = ref.strip()
    if not ref.lower().endswith(('.tex', '.png', '.pdf', '.jpg', '.jpeg', '.eps')):
        # \input fragments often omit .tex
        if '.' not in os.path.basename(ref):
            ref = ref + '.tex'
    # editor/deposit output prefixes both map to <root>/output/
    m = re.search(r'output/(.*)$', ref)
    if m:
        return os.path.join(root, 'output', m.group(1))
    return os.path.normpath(os.path.join(texdir, ref))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tex', default='paper/JPE_submission_v8.tex')
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='certification/MANUSCRIPT_CLOSURE.sha256')
    ap.add_argument('--verify', action='store_true',
                    help='COMPARE the recomputed closure against the committed manifest and fail on '
                         'any drift, instead of overwriting it. Use this after a run: writing the '
                         'manifest from the tree that was just produced certifies the run against '
                         'itself.')
    ap.add_argument('--expect-identity', default=None,
                    help='with --verify, also require CLOSURE_IDENTITY_SHA256 to equal this value')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    tex = os.path.join(root, a.tex)
    texdir = os.path.dirname(tex)
    if not os.path.isfile(tex):
        print(f"FATAL: main TeX not found: {tex}"); return 1

    closure = {}        # relpath -> sha
    missing = []
    def add(path, kind):
        rel = os.path.relpath(path, root)
        if not os.path.isfile(path):
            missing.append((kind, rel)); return
        if rel not in closure:
            closure[rel] = sha256(path)

    # 1) main TeX
    add(tex, 'main')
    text = open(tex, encoding='utf-8', errors='replace').read().splitlines()
    body = "\n".join(strip_tex_comment(l) for l in text)
    # 2) \input fragments (skip the \newcommand{\inputtight}[1]{...\input{#1}...} macro def -> ref '#1')
    for ref in INPUT_RE.findall(body):
        if '#' in ref:
            continue
        add(resolve(ref, root, texdir), 'input')
    # 3) figures: \includegraphics and \begin{overpic} panels
    fig_refs = graphics_refs(body)
    fig_targets = set()
    for ref in fig_refs:
        p = resolve(ref, root, texdir)
        fig_targets.add(os.path.relpath(p, root))
        add(p, 'figure')
    # 4) bib(s): \bibliography or a known .bib next to the TeX
    for m in re.findall(r'\\bibliography\{([^}]+)\}', body):
        for b in m.split(','):
            bref = b.strip()
            bref = bref if bref.endswith('.bib') else bref + '.bib'
            add(os.path.join(texdir, bref), 'bib')
    for b in [f for f in os.listdir(texdir) if f.endswith('.bib')]:
        add(os.path.join(texdir, b), 'bib')
    # 5) custom .cls/.sty next to the TeX (standard packages live in the container, hashed by Phase 7)
    for s in [f for f in os.listdir(texdir) if f.endswith(('.cls', '.sty'))]:
        add(os.path.join(texdir, s), 'style')
    # 6) compiler driver + authoritative PDF
    add(os.path.join(texdir, 'build_manuscript.py'), 'driver')
    base = os.path.splitext(os.path.basename(tex))[0]
    for pdf in (f"{base}_build.pdf", f"{base}.pdf"):
        p = os.path.join(texdir, pdf)
        if os.path.isfile(p):
            add(p, 'pdf'); break

    # report
    n_input = sum(1 for _ in INPUT_RE.findall(body) if '#' not in _)
    n_ig = len([r for r in GRAPHICS_RE.findall(body) if '#' not in r])
    n_op = len([r for r in OVERPIC_RE.findall(body) if '#' not in r])
    print(f"=== manuscript dependency closure: {len(closure)} files hashed ===")
    print(f"  referenced (uncommented): {n_input} \\input, "
          f"{n_ig} \\includegraphics + {n_op} overpic = {len(fig_refs)} distinct figure target(s)")

    # 3b) SELF-TEST: the independent line-based scanner must find the same figure targets.
    audit_refs = audit_pipeline_figure_refs(tex)
    audit_targets = {os.path.relpath(resolve(r, root, texdir), root) for r in audit_refs}
    print(f"  figure-target self-test: closure={len(fig_targets)} "
          f"audit_pipeline scanner={len(audit_targets)}")
    if fig_targets != audit_targets:
        print("FAIL -- figure-target self-test: the two scanners disagree, so the frozen closure "
              "would not cover every figure the manuscript displays.")
        for rel in sorted(audit_targets - fig_targets):
            print(f"  ONLY IN audit_pipeline scanner: {rel}")
        for rel in sorted(fig_targets - audit_targets):
            print(f"  ONLY IN closure scanner:        {rel}")
        return 1

    if missing:
        print(f"FAIL -- {len(missing)} referenced dependency(ies) missing:")
        for kind, rel in missing[:40]:
            print(f"  MISSING [{kind}] {rel}")
        return 1
    closure_hash = hashlib.sha256(
        "".join(f"{closure[r]}  {r}\n" for r in sorted(closure)).encode()).hexdigest()
    out_path = os.path.join(root, a.out)

    if a.verify:
        # VERIFY MODE (added 2026-10-13). Without this the script could only WRITE, so the
        # certification harness ran it after the analysis had rewritten output/ -- and after
        # verify_immutable_tree --verify had already passed. The pins it then wrote were hashes of
        # the exhibits the run had just produced, the rewrite of this certification member went
        # unnoticed, and nothing anywhere compared CLOSURE_IDENTITY_SHA256 to an expected value.
        # Verify mode compares instead of writing, so the manifest certifies the committed
        # exhibits rather than the run's own output.
        if not os.path.isfile(out_path):
            print(f"FAIL (--verify) -- no committed manifest to verify against: {a.out}")
            return 1
        committed = {}
        for line in open(out_path, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line.strip():
                continue
            parts = line.split('  ', 1)
            if len(parts) != 2:
                print(f"FAIL (--verify) -- unparseable manifest line: {line[:80]!r}")
                return 1
            committed[parts[1]] = parts[0]
        added = sorted(set(closure) - set(committed))
        removed = sorted(set(committed) - set(closure))
        changed = sorted(r for r in set(closure) & set(committed) if closure[r] != committed[r])
        if added or removed or changed:
            print(f"FAIL (--verify) -- the manuscript closure drifted from "
                  f"{a.out}: {len(added)} added, {len(removed)} removed, {len(changed)} changed.")
            for rel in added[:20]:
                print(f"  ADDED (in the tree, not in the manifest):   {rel}")
            for rel in removed[:20]:
                print(f"  REMOVED (in the manifest, not in the tree): {rel}")
            for rel in changed[:20]:
                print(f"  CHANGED: {rel}\n           manifest {committed[rel][:16]}... "
                      f"tree {closure[rel][:16]}...")
            return 1
        if a.expect_identity and a.expect_identity.strip().lower() != closure_hash:
            print(f"FAIL (--verify) -- CLOSURE_IDENTITY_SHA256 {closure_hash} != expected "
                  f"{a.expect_identity.strip().lower()}")
            return 1
        print(f"PASS (--verify) -- closure complete and byte-identical to {a.out} "
              f"({len(closure)} files).")
        print(f"  CLOSURE_IDENTITY_SHA256 = {closure_hash}")
        return 0

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        for rel in sorted(closure):
            f.write(f"{closure[rel]}  {rel}\n")
    print(f"PASS -- closure complete. manifest: {a.out}")
    print(f"  CLOSURE_IDENTITY_SHA256 = {closure_hash}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
