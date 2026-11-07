# Committed Parameter Rights and Disclosure Review

**Supporting reference; `README.md` governs.**

The public simulator consumes four committed inputs
(`simulation_parameters.json`, `pc_effects.parquet`, `public_master_skeleton.parquet`,
and `simulation_schema_contract.json`). They are not generic code and must not
inherit the code license classification automatically.

Three DISTINCT authorities govern these inputs, and they must not be conflated
(external-audit R2 Finding 9). Each is recorded and evidenced separately; none
stands in for another. Redistribution rights are attested by the author/provider;
privacy is checked by the disclosure suite; the Data Editor grants technical
acceptance. **The Data Editor does not grant redistribution rights.**

## (a) Redistribution rights — author/provider-attested, settled at source freeze

`certification/COMMITTED_PARAMETER_RIGHTS.csv` is the controlling rights ledger. A
final build fails unless every row is `APPROVED_TO_SHIP`. The two public-design
inputs (`pc_effects.parquet`, `public_master_skeleton.parquet`) rest on public-source
bases. The two restricted-derived inputs — `simulation_parameters.json` and
`simulation_schema_contract.json` — are ARTIFACT-CONTENT-bound: their `evidence`
field is `ARTIFACT_RIGHTS:certification/rights_evidence/<name>.rights.json`, a
versioned JSON evidence document (schema `artifact_rights/v1`) that carries an
affirmative `determination` of `APPROVED_FOR_REDISTRIBUTION` by a named,
non-Data-Editor rights reviewer (the author, as sole redistribution-rights holder
over these author-generated abstractions), bound to the artifact's own sha256.

This is the authority `gen_deposited_file_rights.py` gates on. It fails closed
unless the evidence document exists under `certification/rights_evidence/`, uses
schema `artifact_rights/v1`, names the exact committed artifact, declares an
`artifact_sha256` equal to the committed artifact's actual bytes, records a
non-empty reviewer / reviewer role / date / rights basis / content seal, and has a
`determination` of `APPROVED_FOR_REDISTRIBUTION` by a reviewer whose role is NOT
the Data Editor. Because both the artifact and its rights-evidence document exist
at source freeze, this determination is settled then — it is decoupled from the
privacy audit in (b) and from the Data-Editor acceptance in (c), and it is not
bound to a not-yet-existing package ZIP. A bare `APPROVED_TO_SHIP` status is not
sufficient on its own: the artifact-bound evidence must verify.

## (b) Privacy review — package-bound, post-seal; NOT a rights determination

The confidential disclosure suite is run on the sealed package, in the authorized
environment, after the source is frozen. It is author-side release machinery and is
not part of the deposit. It
demonstrates that the committed inputs recompute exactly from the authorized inputs
and are one-record stable for both `simulation_parameters.json` and
`simulation_schema_contract.json`. This is a disclosure-risk check on the sealed
package. It is NOT a redistribution-rights determination and it neither sets nor
promotes the rights rows in (a).

## (c) Data-Editor technical acceptance — NOT a rights determination

`simulation_schema_contract.json` contains only paths, column names, coarse data
kinds, formats, rounded per-column cardinalities for the Nexis inputs, and row-count
approximations — two significant figures, set one rounding step above the nearest two-significant-figure value, so the real extract is smaller by half a step to one and a half steps — for the
author-created aggregate analysis interfaces and Nexis inputs. It does not contain
MarketScan raw-table names, raw proprietary values, or extraction logic; MarketScan
extraction remains an operation carried out at NBER (the deposited `gen_00b_marketscan_extraction.py`,
run there by the provider).

The row-count approximation (two significant figures plus one rounding step) is a deliberate privacy
protection, and it requires the Data Editor's written TECHNICAL acceptance because
the formal JPE procedure requests identical row counts; the NBER-executed MarketScan
route likewise awaits the Data Editor's written route-sufficiency decision. This
technical acceptance is NOT a redistribution-rights determination: the Data Editor
grants technical acceptance of the rounded dimensions and of the NBER-executed
route, and does not grant redistribution rights and does not set or promote the
author-attested rights rows in (a) (now author-signed `APPROVED_TO_SHIP`).

**On the content seal (external-audit R4 F6).** The `source_content_seal`/`artifact_sha256` in each
`rights_evidence/*.rights.json` is NOT itself rights evidence: it only BINDS the author's representation to
the exact bytes it concerns. The rights basis is the author representation (`basis_type =
author_representation`); it is factually supportable only under the actual MarketScan/Nexis/Dimensions/WRDS
license terms for derived aggregates. Because these two artifacts are restricted-derived, a dated written
IU research-data/licensing (or provider) confirmation is the preferred basis and would upgrade
`basis_type` to `independent_review`; until then the author representation is a disclosed deviation the
Data Editor may challenge. For public files, `certification/PUBLIC_SOURCE_PROVENANCE.csv` is the parallel
provenance ledger (source URL/DOI, version, provider checksum, local SHA, redistribution basis); final
certification requires it complete plus an independent re-download/provider-record cross-check (R4 F5).
