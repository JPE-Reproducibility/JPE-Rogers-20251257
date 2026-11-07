using YAML
using PackageScanner
using JSON
using Dates

function rm_git(extract_dir)
    for (root, dirs, files) in walkdir(extract_dir)
        if ".git" in dirs
            git_path = joinpath(root, ".git")
            @info "Removing git repository: $git_path"
            rm(git_path, recursive=true, force=true)
            filter!(d -> d != ".git", dirs)
            return 0
        end
    end
end

# Read configuration
vars = YAML.load_file(joinpath(ENV["GITHUB_WORKSPACE"], "_variables.yml"))
@info "Configuration loaded" vars

dest_path = joinpath(ENV["GITHUB_WORKSPACE"], "replication-package")

# ── Skip fetch entirely if package is already present locally ─────────
already_have_package = isdir(dest_path) && !isempty(readdir(dest_path))

# ── Remote path: download via public Dropbox link ─────────────────────
url = let u = get(ENV, "DROPBOX_DOWNLOAD_URL", nothing)
    (isnothing(u) || isempty(u)) ? nothing : u
end

downloaded_ok = if already_have_package
    @info "Package already present at $dest_path — skipping download/copy"
    true
elseif !isnothing(url)
    @info "Downloading package from secret Dropbox link..."
    t0 = time()
    try
        run(`curl -fsSL --retry 5 --retry-delay 10 --retry-all-errors --connect-timeout 30 -C - -o package.zip $url`)
        @info "Download complete in $(round(time()-t0, digits=1))s"
        true
    catch e
        @error "curl download failed, will try local fallback" exception=e
        false
    end
else
    @info "No remote link configured — using local Dropbox path"
    false
end

# ── Local fallback: copy from Dropbox Apps folder ─────────────────────
if !downloaded_ok
    source_path = joinpath(ENV["JPE_DBOX_APPS"], vars["dropbox_rel_path"], "replication-package")
    @info "Copying package from local Dropbox..." source_path
    if !isdir(source_path)
        error("Package not found at $source_path")
    end
    isdir(dest_path) && rm(dest_path; recursive=true, force=true)
    PackageScanner.mycp(source_path, dest_path; recursive=true, force=true)
    @info "✓ Package copied from local Dropbox"
end

# ── Unzip downloaded archive (remote path only) ───────────────────────
if downloaded_ok && isfile("package.zip")
    @info "Unzipping Dropbox folder archive..."
    tmp_dir = mktempdir()
    try
        run(`unzip -oq package.zip -d $tmp_dir`)
    catch e
        @warn "unzip exited non-zero (may still be okay)" exception=e
    end
    rm("package.zip"; force=true)

    # Find all ZIPs inside the Dropbox folder
    candidates = filter(readdir(tmp_dir; join=true)) do f
        isfile(f) && endswith(lowercase(f), ".zip")
    end

    isdir(dest_path) && rm(dest_path; recursive=true, force=true)
    mkpath(dest_path)

    if isempty(candidates)
        # No nested ZIP — the author's Dropbox folder contained the
        # replication package's files/subfolders directly (not a .zip),
        # so the extracted tmp_dir already *is* the package.
        @info "No nested ZIP found — using extracted folder contents directly as the package"
        for f in readdir(tmp_dir; join=true)
            cp(f, joinpath(dest_path, basename(f)); force=true)
        end
        rm_git(dest_path)
    else
        @info "Found $(length(candidates)) ZIP(s) to extract" candidates

        for pkg_zip in candidates
            @info "Unzipping $pkg_zip..."
            try
                run(`unzip -oq $pkg_zip -d $dest_path`)
                if isdir(dest_path)
                    rm_git(dest_path)
                end
            catch e
                @warn "unzip of $pkg_zip exited non-zero" exception=e
            end
        end
    end

    rm(tmp_dir; recursive=true, force=true)
    @info "✓ Unzip complete"
end

if !isdir(dest_path)
    error("Package directory not found at $dest_path after download/copy step")
end

# ── Fetch the paper source (mirrors the replication-package fetch above) ──
# See JPE-Reproducibility/JPE.jl#34. Fetches whichever folder preprocess()
# chose (paper_source_subfolder in _variables.yml: paper-author/ if the
# author uploaded one, #30, else the legacy paper-appendices/) into
# paper-source/ in the workspace. Best-effort: failures here must not
# abort the package precheck, which is the primary purpose of this run --
# Stage C/D consumers just see no paper-source/ and skip accordingly.
paper_dest_path = joinpath(ENV["GITHUB_WORKSPACE"], "paper-source")
already_have_paper = isdir(paper_dest_path) && !isempty(readdir(paper_dest_path))

paper_url = let u = get(ENV, "PAPER_DOWNLOAD_URL", nothing)
    (isnothing(u) || isempty(u)) ? nothing : u
end

paper_downloaded_ok = if already_have_paper
    @info "Paper source already present at $paper_dest_path — skipping download/copy"
    true
elseif !isnothing(paper_url)
    @info "Downloading paper source from secret Dropbox link..."
    try
        run(`curl -fsSL --retry 5 --retry-delay 10 --retry-all-errors --connect-timeout 30 -C - -o paper.zip $paper_url`)
        true
    catch e
        @warn "paper source curl download failed, will try local fallback" exception=e
        false
    end
else
    @info "No remote paper link configured — using local Dropbox path"
    false
end

if !paper_downloaded_ok
    try
        paper_source_path = joinpath(ENV["JPE_DBOX_APPS"], vars["dropbox_rel_path"], vars["paper_source_subfolder"])
        if isdir(paper_source_path)
            isdir(paper_dest_path) && rm(paper_dest_path; recursive=true, force=true)
            PackageScanner.mycp(paper_source_path, paper_dest_path; recursive=true, force=true)
            @info "✓ Paper source copied from local Dropbox"
        else
            @warn "Paper source not found at $paper_source_path — skipping (no paper available for Stage C)"
        end
    catch e
        @warn "Could not fetch paper source — skipping (no paper available for Stage C)" exception=e
    end
elseif isfile("paper.zip")
    @info "Unzipping paper source archive..."
    tmp_dir = mktempdir()
    try
        run(`unzip -oq paper.zip -d $tmp_dir`)
    catch e
        @warn "unzip of paper source exited non-zero (may still be okay)" exception=e
    end
    rm("paper.zip"; force=true)

    isdir(paper_dest_path) && rm(paper_dest_path; recursive=true, force=true)
    mkpath(paper_dest_path)
    for f in readdir(tmp_dir; join=true)
        cp(f, joinpath(paper_dest_path, basename(f)); force=true)
    end
    rm_git(paper_dest_path)
    rm(tmp_dir; recursive=true, force=true)
    @info "✓ Paper source unzip complete"
end

# ── Stage C: LLM claims extraction (JPE-Reproducibility/JPE.jl#34) ────
# Shared helpers (claude CLI invocation, prompt, JSON schema) are
# spliced in verbatim from claims_runner_helpers.jl -- see JPE.jl's
# write_runner_script for the single source of truth.

# Standalone Stage C claims-extraction helpers (JPE-Reproducibility/JPE.jl#34).
#
# This file's source text is spliced verbatim into the generated
# runner_precheck.jl script (see write_runner_script in preprocess.jl) so
# Stage C runs inside JULIA_RUNNER_ENV wherever that script executes -- local
# machine or the self-hosted gh-runner, both of which already have `claude`
# CLI logged into the JPE Claude Pro account. It is also `include`d normally
# into the JPE module (see JPE.jl), so the standalone entry point that still
# needs it (`extract_paper_claims`, for a manual/local-only re-run) shares
# this source rather than a duplicated copy that could drift out of sync.
#
# Every function here must stay self-contained: no JPE.jl internals (no DB
# calls, no DataFrameRow access, no interactive RadioMenu), since the
# generated script only has YAML/PackageScanner/JSON/Dates loaded, not
# JPE.jl itself.

"""
    claude_binary()

Path to the `claude` CLI, resolved via `PATH`.
"""
claude_binary() = Sys.which("claude")

"""
    claude_jpe_config_dir()

The `CLAUDE_CONFIG_DIR` used by the `claude-jpe` shell alias (the JPE Claude
Pro account, distinct from the user's personal one -- see
`~/.config/fish/functions/claude-jpe.fish`). Falls back to `~/.claude-jpe` if
`CLAUDE_CONFIG_DIR` isn't already set in the environment (e.g. when this is
called from a session that isn't itself a nested claude-jpe invocation).
"""
claude_jpe_config_dir() = get(ENV, "CLAUDE_CONFIG_DIR", joinpath(homedir(), ".claude-jpe"))

"""
    CLAIMS_JSON_SCHEMA

JSON schema passed to `claude -p --json-schema` to force structured claims
output: data sources (with access date / URL/DOI if the paper gives one),
general data processing steps (file loading/merging/cleaning/filtering
applied before any specific table -- the part Stage D cross-references
against Stage A's "which code loads which data" findings), and per-table
specs (estimator, outcome variable, key regressors, controls, fixed effects,
clustering, sample restriction, data source) plus per-figure descriptions.
Unknown/unstated fields must be `null`, not guessed.

Schema shape informed by benjamin-kohler/social_science_replicability's
PaperSummary/TableSpec/RegressionSpec (src/models/schemas.py) -- notably its
`data_processing_steps` (general vs. per-table) and `controls` distinct from
the regressor(s) of interest. Not adopted from there: PDF-page vision input
(irrelevant -- we use tex, not PDF) and its no-results-leakage validation
(irrelevant -- that guards against their blind-replication agent seeing the
answer; we have no such agent to protect, Stage D is allowed to see
everything).
"""
const CLAIMS_JSON_SCHEMA = """
{"type":"object","properties":{
"data_sources":{"type":"array","items":{"type":"object","properties":{
  "name":{"type":"string"},"access_date":{"type":["string","null"]},"url_or_doi":{"type":["string","null"]}
},"required":["name","access_date","url_or_doi"]}},
"data_processing_steps":{"type":"array","items":{"type":"object","properties":{
  "description":{"type":"string"},"variables_involved":{"type":"array","items":{"type":"string"}}
},"required":["description","variables_involved"]}},
"tables":{"type":"array","items":{"type":"object","properties":{
  "label":{"type":"string"},"title":{"type":["string","null"]},"estimator":{"type":["string","null"]},
  "outcome_var":{"type":["string","null"]},"key_regressors":{"type":"array","items":{"type":"string"}},
  "controls":{"type":"array","items":{"type":"string"}},
  "fixed_effects":{"type":"array","items":{"type":"string"}},"clustering":{"type":["string","null"]},
  "sample_restriction":{"type":["string","null"]},"data_source":{"type":["string","null"]}
},"required":["label","title","estimator","outcome_var","key_regressors","controls","fixed_effects","clustering","sample_restriction","data_source"]}},
"figures":{"type":"array","items":{"type":"object","properties":{
  "label":{"type":"string"},"description":{"type":"string"}
},"required":["label","description"]}}
},"required":["data_sources","data_processing_steps","tables","figures"]}
"""

"""
    claims_extraction_prompt(paper_text_path::String)

The prompt given to `claude -p` for the claims-extraction call. Points at the
flattened paper text by path (read via the `Read` tool) rather than embedding
it inline, so the shell command itself stays short regardless of paper size.
"""
function claims_extraction_prompt(paper_text_path::String)
    """
    Read the flattened LaTeX paper source at $paper_text_path and extract a
    structured summary of its empirical claims, for a static plausibility
    cross-check against the paper's replication package (no code execution
    involved -- this is not a reproducibility check). Follow the provided
    JSON schema exactly. For each table, fill in as many structured fields as
    the text actually supports; use null for anything the paper doesn't
    specify. Do not invent or guess values that aren't in the text.

    Resolve cross-references before extracting: when the text says "see
    Appendix H" or "controls listed in Table A3" or "as defined in Section
    2", go find that content elsewhere in the flattened text (it has already
    been inlined) and extract the actual content there -- do not leave a
    reference unresolved. For `controls`, enumerate every control variable
    individually rather than writing an aggregate description like
    "socio-demographic controls".

    Skip purely conceptual figures that have no replicable data behind them
    (flow diagrams, conceptual frameworks, schematics, screenshots, photos,
    maps) -- only extract figures that plot actual data or model output.
    """
end

"""
    build_claude_claims_cmd(paper_text_path::String; effort = "medium")

The `Cmd` for the headless claims-extraction call. Split out from
`run_claude_claims_extraction` so the flags are testable without actually
invoking `claude` (no live API/CLI calls in tests).

Uses `--safe-mode` (not `--bare`, which strictly requires `ANTHROPIC_API_KEY`
and would break the Pro-subscription OAuth auth this relies on) to drop
CLAUDE.md/memory/hooks overhead, and restricts tools to `Read` only --
a single turn, no agentic loop, to keep this cheap under a Pro quota.

Uses `addenv` (not `setenv`, which replaces the *entire* child environment
with just the pairs given) so the override merges with the inherited
environment -- `claude` still needs `HOME`/`PATH` etc. to find its
credentials, or it fails immediately with "Not logged in".

Passes `--add-dir` for the directory containing `paper_text_path` to
explicitly grant `Read` access to it. This call happens to work without it
today (the prompt states the full absolute path verbatim, which `--safe-mode`
appears to auto-approve), but Stage D's identical setup silently returned
empty results once its prompt stopped doing that (see `build_crosscheck_cmd`)
-- `--add-dir` makes the grant explicit instead of relying on that heuristic.
"""
function build_claude_claims_cmd(paper_text_path::String; effort::String = "medium")
    bin = claude_binary()
    isnothing(bin) && error("claude CLI not found on PATH")

    addenv(
        `$bin -p $(claims_extraction_prompt(paper_text_path))
         --output-format json --tools Read --safe-mode --effort $effort
         --add-dir $(dirname(paper_text_path))
         --json-schema $CLAIMS_JSON_SCHEMA`,
        "CLAUDE_CONFIG_DIR" => claude_jpe_config_dir(),
    )
end

"""
    run_claude_claims_extraction(paper_text_path::String; effort = "medium")

Run the headless claims-extraction call and return
`(claims = <parsed structured_output>, cost_usd = <reported cost>)`.
"""
function run_claude_claims_extraction(paper_text_path::String; effort::String = "medium")
    cmd = build_claude_claims_cmd(paper_text_path; effort = effort)
    out = read(cmd, String)
    parsed = JSON.parse(out)

    get(parsed, "is_error", true) == false || error("claude -p failed: $(get(parsed, "result", "unknown error"))")

    return (claims = parsed["structured_output"], cost_usd = get(parsed, "total_cost_usd", missing))
end


# ── Stage D: claims-vs-package crosscheck (JPE-Reproducibility/JPE.jl#38) ──
# Shared helpers spliced in verbatim from crosscheck_runner_helpers.jl,
# same reasoning as Stage C above. Only the prompt/schema/cmd/scoring
# functions are defined here -- the actual Stage D run happens below,
# after Stage A has produced report-data-dependencies.md.

# Stage D: matching + coverage scoring (JPE-Reproducibility/JPE.jl#29).
#
# Self-contained like claims_runner_helpers.jl (see that file's header): this
# file's source text is spliced verbatim into the generated runner_precheck.jl
# script (see write_runner_script in preprocess.jl) so Stage D runs right
# after Stage C, in the same script execution, wherever that executes --
# local machine or the self-hosted gh-runner. That matters because the
# runner's own "commit and push results" step (or preprocess()'s local-mode
# commit) does a plain `git add .` right after the script finishes -- for
# crosscheck.json/report-crosscheck.md to be included in that commit, they
# must already exist on disk by the time the script returns, not require a
# separate DE-triggered, DB-backed call afterwards (that's what
# `run_paper_crosscheck` in crosscheck.jl is, now just a manual/force-rerun
# path on top of these same functions).
#
# Reads Stage A (report-data-dependencies.md), Stage B (report-readme-structure.md
# -- optional, degrades gracefully if absent: JPE-Reproducibility/PackageScanner.jl#17
# not yet merged at the time this was written), and Stage C (claims.json) outputs
# from the paper's generated/ folder, and runs a single headless `claude -p` call
# (same budget discipline as Stage C: --safe-mode, single turn, no agentic Read/Grep
# loop) to produce a per-claim verdict (Matched/Plausible/Missing) with file-level
# supporting evidence.
#
# Coverage percentages are computed in Julia from the verdicts, not asked of the
# model -- deterministic and auditable. The denominator is the claims Stage C
# extracted; if Stage C missed something, it is invisible to this score (documented
# in the report's caveats section, not silently papered over).
#
# SCOPE DEVIATION from issue #29: without raw code file *content* in the prompt
# (deliberately excluded to keep this single-turn/cheap, consistent with the
# "static plausibility, not line-level verification" scope), the model cannot
# produce honest file:line citations as the issue describes. Verdicts cite
# supporting *files* only, never line numbers -- flagged here and in the report's
# caveats rather than having the model fabricate a line it never saw.
#
# Every function here must stay self-contained: no JPE.jl internals (no DB
# calls, no DataFrameRow access, no interactive RadioMenu), matching
# claims_runner_helpers.jl's constraint for the same reason.

const CROSSCHECK_JSON_SCHEMA = """
{"type":"object","properties":{
"verdicts":{"type":"array","items":{"type":"object","properties":{
  "claim_type":{"type":"string","enum":["data_source","table","figure"]},
  "claim_label":{"type":"string"},
  "verdict":{"type":"string","enum":["Matched","Plausible","Missing"]},
  "rationale":{"type":"string"},
  "supporting_files":{"type":"array","items":{"type":"string"}}
},"required":["claim_type","claim_label","verdict","rationale","supporting_files"]}},
"orphan_code_files":{"type":"array","items":{"type":"string"}}
},"required":["verdicts","orphan_code_files"]}
"""

"""
    PLAUSIBLE_CREDIT

Weight given to a "Plausible" verdict when computing coverage percentages:
`Matched` = 1.0, `Plausible` = `PLAUSIBLE_CREDIT`, `Missing` = 0.0. This single
constant determines the headline coverage number more than any prompt wording
-- change it here if the scoring convention should differ.
"""
const PLAUSIBLE_CREDIT = 0.5

"""
    read_or_placeholder(path::String, placeholder::String)

`read(path, String)` if `path` exists, else `placeholder`. Used so a missing
optional input (e.g. Stage B's report, if that package's precheck predates
PackageScanner.jl#17) degrades gracefully instead of erroring.
"""
read_or_placeholder(path::String, placeholder::String) = isfile(path) ? read(path, String) : placeholder

"""
    crosscheck_prompt(bundle_dir::String)

The prompt for the Stage D matching call. Points at the input bundle by
directory (read via the `Read` tool) rather than embedding content inline.
Deliberately excludes raw replication-package code content -- only Stage
A/B/C's already-computed findings and file manifests -- to keep this a
single turn, no agentic exploration loop.
"""
function crosscheck_prompt(bundle_dir::String)
    """
    Read the files in $bundle_dir:
    - claims.json: structured claims extracted from the paper (Stage C).
    - data_dependencies.md: which data files are referenced by which code files (Stage A).
    - readme_structure.md: README section checklist and data citation coverage (Stage B).
      If this says "(not available)", Stage B wasn't run for this package -- proceed
      without it, don't penalize claims for its absence.
    - code_manifest.txt / data_manifest.txt: file listings of the replication package.

    For each claim in claims.json (each data source, table, and figure), assess
    whether the package's code/data could plausibly implement it, based ONLY on the
    evidence in these files -- you do not have the code's actual content, only file
    listings and Stage A/B's findings. Assign one of:
    - "Matched": Stage A/B's findings directly support the claim (e.g. a data source
      the claim names is referenced by a specific code file per data_dependencies.md).
    - "Plausible": no direct evidence, but nothing contradicts it and the package's
      file listing is consistent with the claim (e.g. a plausibly-named script exists
      but Stage A didn't trace a direct reference).
    - "Missing": no file in the package is plausibly connected to the claim at all.

    Cite supporting files by name in `supporting_files` -- you cannot see line
    numbers, so never invent them or claim line-level evidence.

    Also list `orphan_code_files`: code files in code_manifest.txt that have no
    plausible connection to any claim in claims.json (candidates for "what is this
    code actually doing" follow-up by the human replicator).

    This is a static plausibility check, not a reproducibility check -- you are not
    running any code, and should not speculate about whether the code runs correctly
    or produces correct numbers.
    """
end

"""
    build_crosscheck_cmd(bundle_dir::String; effort = "medium")

Same budget-conscious shape as `build_claude_claims_cmd` (Stage C): `--safe-mode`
(not `--bare`, which would require an API key and break the Pro-subscription
OAuth auth this relies on), `Read`-only tools, single turn, `--json-schema`
forcing `CROSSCHECK_JSON_SCHEMA`. Split out from `run_claude_crosscheck` so the
flags are testable without actually invoking `claude`.

Uses `addenv` (not `setenv`, which replaces the *entire* child environment
with just the pairs given) so the override merges with the inherited
environment -- `claude` still needs `HOME`/`PATH` etc. to find its
credentials, or it fails immediately with "Not logged in".

Passes `--add-dir bundle_dir` to explicitly grant `Read` access to the bundle.
Without it, every `Read` call against files under `bundle_dir` is silently
denied (`--safe-mode` doesn't auto-approve reads the way it does when a full
absolute path is stated verbatim in the prompt, as Stage C's prompt does) --
with `--json-schema` forcing a schema-valid response regardless, the model
just returns empty `verdicts`/`orphan_code_files` with no visible error.
"""
function build_crosscheck_cmd(bundle_dir::String; effort::String = "medium")
    bin = claude_binary()
    isnothing(bin) && error("claude CLI not found on PATH")

    addenv(
        `$bin -p $(crosscheck_prompt(bundle_dir))
         --output-format json --tools Read --safe-mode --effort $effort
         --add-dir $bundle_dir
         --json-schema $CROSSCHECK_JSON_SCHEMA`,
        "CLAUDE_CONFIG_DIR" => claude_jpe_config_dir(),
    )
end

"""
    run_claude_crosscheck(bundle_dir::String; effort = "medium")

Run the headless crosscheck call and return
`(result = <parsed structured_output>, cost_usd = <reported cost>)`.
"""
function run_claude_crosscheck(bundle_dir::String; effort::String = "medium")
    cmd = build_crosscheck_cmd(bundle_dir; effort = effort)
    out = read(cmd, String)
    parsed = JSON.parse(out)

    get(parsed, "is_error", true) == false || error("claude -p failed: $(get(parsed, "result", "unknown error"))")

    return (result = parsed["structured_output"], cost_usd = get(parsed, "total_cost_usd", missing))
end

"""
    compute_coverage(verdicts::Vector)

Deterministic coverage percentages from the per-claim verdicts: `Matched` = full
credit, `Plausible` = `PLAUSIBLE_CREDIT`, `Missing` = zero credit. Computed in
Julia (never asked of the model) so the number is auditable directly from the
verdicts list, not a free-floating model claim. Returns overall coverage plus a
breakdown by `claim_type` (`data_source`/`table`/`figure`).
"""
function compute_coverage(verdicts::Vector)
    credit(v) = v["verdict"] == "Matched" ? 1.0 : (v["verdict"] == "Plausible" ? PLAUSIBLE_CREDIT : 0.0)

    function pct(vs)
        isempty(vs) && return missing
        round(100 * sum(credit, vs) / length(vs), digits = 1)
    end

    by_type = Dict{String,Any}()
    for t in unique(v["claim_type"] for v in verdicts)
        by_type[t] = pct(filter(v -> v["claim_type"] == t, verdicts))
    end

    return Dict("overall" => pct(verdicts), "by_claim_type" => by_type, "n_claims" => length(verdicts))
end

"""
    render_crosscheck_report(verdicts, coverage, orphan_code_files)

Render `report-crosscheck.md`: a mandatory caveats section (static plausibility
only -- no code execution, file-level not line-level citations, coverage is
relative to what Stage C extracted), a coverage summary table, per-claim verdict
detail, and orphan code files.
"""
function render_crosscheck_report(verdicts::Vector, coverage::Dict, orphan_code_files::Vector)
    io = IOBuffer()
    println(io, "### Paper vs. Code/Data Crosscheck\n")
    println(io, "_Generated on $(Dates.now())_\n")
    println(io, """
    **Caveats (read before using this report):**
    - **Static plausibility only, not a reproducibility check.** No code was executed.
      This cannot catch logic bugs, wrong coefficients, or silently incorrect results.
    - **File-level citations only, not line-level.** The model did not see code file
      contents -- only Stage A/B's pre-computed findings and file listings. Any
      "supporting file" below is a plausibility signal, not a verified line reference.
    - **Coverage is relative to what Stage C extracted from the paper**, not to the
      paper's true full content. A claim Stage C missed is invisible to this score.
    """)

    println(io, "#### Coverage\n")
    println(io, "| Category | Coverage | n claims |")
    println(io, "|----------|----------|----------|")
    for (t, p) in coverage["by_claim_type"]
        n = count(v -> v["claim_type"] == t, verdicts)
        println(io, "| $t | $(p)% | $n |")
    end
    println(io, "| **Overall** | **$(coverage["overall"])%** | $(coverage["n_claims"]) |\n")

    println(io, "#### Per-Claim Detail\n")
    for v in verdicts
        icon = v["verdict"] == "Matched" ? "✅" : (v["verdict"] == "Plausible" ? "🟡" : "❌")
        println(io, "$icon **$(v["claim_type"]): $(v["claim_label"])** — $(v["verdict"])")
        println(io, "- $(v["rationale"])")
        if !isempty(v["supporting_files"])
            println(io, "- supporting files: ", join("`" .* v["supporting_files"] .* "`", ", "))
        end
        println(io)
    end

    println(io, "#### Orphan Code (no traceable connection to any claim)\n")
    if isempty(orphan_code_files)
        println(io, "None found.")
    else
        for f in orphan_code_files
            println(io, "- `$f`")
        end
    end

    return String(take!(io))
end


if true
    claims_dir = joinpath(ENV["GITHUB_WORKSPACE"], "generated")
    mkpath(claims_dir)
    claims_json_path = joinpath(claims_dir, "claims.json")
    claims_report_path = joinpath(claims_dir, "report-claims-extraction.md")

    if isfile(claims_json_path)
        @info "claims.json already exists — skipping Stage C re-extraction"
    elseif !isdir(paper_dest_path) || isempty(readdir(paper_dest_path))
        @warn "no paper source available — skipping Stage C claims extraction"
        open(claims_report_path, "w") do rio
            println(rio, "# Stage C: Claims Extraction")
            println(rio, "")
            println(rio, "**Skipped**: no paper source was available (`paper-source/` empty or missing).")
        end
    else
        tex_result = PackageScanner.extract_latex_text(paper_dest_path)
        if tex_result.ambiguous
            @warn "ambiguous paper source — multiple candidate main .tex files, skipping Stage C"
            open(claims_report_path, "w") do rio
                println(rio, "# Stage C: Claims Extraction")
                println(rio, "")
                println(rio, "**Skipped**: ambiguous paper source — multiple candidate main `.tex` files were found, and this unattended run cannot pick one:")
                println(rio, "")
                for root in tex_result.roots
                    println(rio, "- `$root`")
                end
                println(rio, "")
                println(rio, "Resolve manually from a JPE.jl session with `extract_paper_claims(paperID; main_files=[...])`, then re-run preprocess.")
            end
        elseif isempty(tex_result.roots)
            @warn "no .tex source found under paper-source/ — skipping Stage C claims extraction"
            open(claims_report_path, "w") do rio
                println(rio, "# Stage C: Claims Extraction")
                println(rio, "")
                println(rio, "**Skipped**: no `.tex` source found under `paper-source/`. PDF fallback is not implemented.")
            end
        else
            flattened_path = joinpath(paper_dest_path, "_flattened.tex")
            write(flattened_path, tex_result.text)
            try
                extraction = run_claude_claims_extraction(flattened_path)
                open(claims_json_path, "w") do jio
                    JSON.print(jio, extraction.claims, 2)
                end
                open(claims_report_path, "w") do rio
                    println(rio, "# Stage C: Claims Extraction")
                    println(rio, "")
                    println(rio, "**Done** ($(Dates.now())). Extraction cost: \$$(extraction.cost_usd)")
                end
                @info "✓ Stage C claims extraction complete, cost \$$(extraction.cost_usd)"
            catch e
                @warn "Stage C claims extraction failed" exception=e
                open(claims_report_path, "w") do rio
                    println(rio, "# Stage C: Claims Extraction")
                    println(rio, "")
                    println(rio, "**Failed**: $e")
                end
            finally
                rm(flattened_path, force=true)
            end
        end
    end
end

# ── PackageScanner precheck ────────────────────────────────────────────
if true
    pkg_size     = vars["package_size_gb"]
    max_pkg_size = vars["package_max_pkg_size_gb"]
    max_file_size = vars["package_max_file_size_gb"]

    if pkg_size > max_pkg_size
        @info "Package >$(max_pkg_size) GB — using partial extraction mode"
        pkg_dir, manifest = PackageScanner.prepare_package_for_precheck(
            dest_path, size_threshold_gb=max_file_size, interactive=false)
        PackageScanner.precheck_package(pkg_dir, pre_manifest=manifest,
                                        no_data_scan=["__MACOSX", "renv"])
    else
        @info "Unzipping files in $dest_path"
        try
            zips = PackageScanner.read_and_unzip_directory(dest_path)
            @info "Unzipped $(length(zips)) file(s)"
        catch e
            @warn "Unzip had issues (may be okay)" exception=e
        end
        @info "Running precheck on $dest_path"
        PackageScanner.precheck_package(dest_path, no_data_scan=["__MACOSX", "renv"])
        @info "✓ Precheck complete"
    end

    # ── Force-track classified code files even under `data/` dirs ─────
    # JPEtemplate's .gitignore excludes **/data/*, which can hide
    # genuine author code (already flagged as code by classify_files)
    # from git. List those paths, relative to the repo root, so a
    # later `git add -f` step can force-track them.
    program_files_txt = joinpath(ENV["GITHUB_WORKSPACE"], "generated", "program-files.txt")
    if isfile(program_files_txt)
        force_add_exclude = vcat(["__MACOSX", "renv"], ["__pycache__"])
        rels = String[]
        for line in eachline(program_files_txt)
            isempty(strip(line)) && continue
            if !any(occursin(pat, line) for pat in force_add_exclude)
                # These files have never been committed before (that's
                # the whole reason they need force-adding), so their
                # content has never passed through a secret check.
                # Redact in place before it's staged -- same
                # SECRET_PATTERNS the secrets report already scanned
                # this content with, so a redaction here always agrees
                # with what report-secrets.md flagged.
                try
                    original = read(line, String)
                    redacted = PackageScanner.redact_secrets(original)
                    if redacted != original
                        write(line, redacted)
                        @warn "Redacted possible secret(s) in $line before force-adding to git"
                    end
                catch e
                    @warn "Could not check $line for secrets before force-add — leaving as-is" exception=e
                end
                push!(rels, relpath(line, ENV["GITHUB_WORKSPACE"]))
            end
        end
        open(joinpath(ENV["GITHUB_WORKSPACE"], "generated", "force-add-files.txt"), "w") do fio
            for rel in rels
                println(fio, rel)
            end
        end
        @info "✓ Wrote $(length(rels)) path(s) to generated/force-add-files.txt"
    end

    # ── Stage D: claims-vs-package crosscheck (JPE-Reproducibility/JPE.jl#38) ──
    # Must run here, before the "cap oversized reports" step below --
    # that step replaces a large report-data-dependencies.md with a
    # short placeholder + Dropbox link, which would starve this of
    # its main evidence source. Requires claims.json (Stage C, above)
    # to already exist -- silently skipped otherwise (e.g. Stage C
    # was disabled, or found no usable paper source).
    if true
        gen_dir = joinpath(ENV["GITHUB_WORKSPACE"], "generated")
        crosscheck_claims_path = joinpath(gen_dir, "claims.json")
        crosscheck_json_path = joinpath(gen_dir, "crosscheck.json")
        crosscheck_report_path = joinpath(gen_dir, "report-crosscheck.md")

        if !isfile(crosscheck_claims_path)
            @info "no claims.json — skipping Stage D crosscheck"
        elseif isfile(crosscheck_json_path)
            @info "crosscheck.json already exists — skipping Stage D re-run"
        else
            bundle_dir = mktempdir()
            try
                cp(crosscheck_claims_path, joinpath(bundle_dir, "claims.json"))
                write(joinpath(bundle_dir, "data_dependencies.md"),
                      read_or_placeholder(joinpath(gen_dir, "report-data-dependencies.md"), "(not available)"))
                write(joinpath(bundle_dir, "readme_structure.md"),
                      read_or_placeholder(joinpath(gen_dir, "report-readme-structure.md"), "(not available)"))
                write(joinpath(bundle_dir, "code_manifest.txt"),
                      read_or_placeholder(joinpath(gen_dir, "program-files-manifest.csv"),
                                           read_or_placeholder(joinpath(gen_dir, "program-files.txt"), "(not available)")))
                write(joinpath(bundle_dir, "data_manifest.txt"),
                      read_or_placeholder(joinpath(gen_dir, "data-files-manifest.csv"), "(not available)"))

                extraction = run_claude_crosscheck(bundle_dir)
                verdicts = extraction.result["verdicts"]
                orphan_code_files = extraction.result["orphan_code_files"]
                coverage = compute_coverage(verdicts)

                open(crosscheck_json_path, "w") do jio
                    JSON.print(jio, Dict("verdicts" => verdicts, "coverage" => coverage,
                                          "orphan_code_files" => orphan_code_files), 2)
                end
                write(crosscheck_report_path, render_crosscheck_report(verdicts, coverage, orphan_code_files))
                @info "✓ Stage D crosscheck complete, cost \$$(extraction.cost_usd), overall coverage $(coverage["overall"])%"
            catch e
                @warn "Stage D crosscheck failed" exception=e
                open(crosscheck_report_path, "w") do rio
                    println(rio, "### Paper vs. Code/Data Crosscheck")
                    println(rio, "")
                    println(rio, "**Failed**: $e")
                end
            finally
                rm(bundle_dir, recursive=true, force=true)
            end
        end
    end

    # ── Cap oversized generated report files ───────────────────────────
    # A full copy goes to a permanent Dropbox link (see large_reports_url
    # in _variables.yml) instead of a GitHub Actions artifact: paper repos
    # are private and authors never get repo access, so an artifact link
    # would be unreachable to them -- and artifacts expire after 90 days
    # regardless. The Dropbox folder link does not expire.
    let max_bytes = 5 * 1024 * 1024
        gen_dir = joinpath(ENV["GITHUB_WORKSPACE"], "generated")
        reports_url = get(vars, "large_reports_url", nothing)
        if isdir(gen_dir) && !isnothing(reports_url) && haskey(ENV, "JPE_DBOX_APPS")
            reports_dest = joinpath(ENV["JPE_DBOX_APPS"], vars["dropbox_rel_path"], "large-reports")
            for f in readdir(gen_dir; join=true)
                (isfile(f) && endswith(f, ".md")) || continue
                sz = filesize(f)
                sz > max_bytes || continue
                fname = basename(f)
                lines = countlines(f)
                size_mb = round(sz / 1024^2, digits=1)
                mkpath(reports_dest)
                cp(f, joinpath(reports_dest, fname); force=true)
                open(f, "w") do fio
                    println(fio, "> **Note**: This list contains $lines entries ($size_mb MB) — too large to embed in the report.")
                    println(fio, "> The full list is available here: <$reports_url>")
                end
                @info "Capped $fname ($size_mb MB, $lines lines) — full copy sent to Dropbox"
            end
        end
    end
else
    @info "run_checks=false — package fetched, skipping PackageScanner precheck"
end
