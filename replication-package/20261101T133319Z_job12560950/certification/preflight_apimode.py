#!/usr/bin/env python3
"""Positive preflight assertions for the synthetic-route certification harness.

Two POSITIVE checks (not "absence of an error message"):

  1. rpy2 loaded in **API mode**: assert
     `rpy2.rinterface_lib.openrlib.cffi_mode is rpy2.rinterface_lib.openrlib.CFFI_MODE.API`.
     (ABI-mode fallback is fragile — one R error corrupts the session. The
     DYLD_INSERT_LIBRARIES=$R_HOME/lib/libR.dylib preload forces API mode.)

  2. The embedding model resolves to the **packaged** copy: load the shipped
     06c model resolver from the archive and require it returns exactly
     `<archive>/models/all-MiniLM-L6-v2`, with NO `.cache/huggingface` anywhere
     in the resolved path (no network / no private HF cache).

Usage:
    python3 certification/preflight_apimode.py <archive_root> [--require-model]

Exit 0 iff all requested checks pass; non-zero (and a FAIL line) otherwise.
The harness runs this under BOTH interpreters; --require-model is passed only
for the embedding sub-env interpreter (the one that runs step 17 / 06c).
"""
import importlib.util
import os
import sys
from pathlib import Path


def check_api_mode() -> bool:
    try:
        import rpy2.rinterface_lib.openrlib as openrlib
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: could not import rpy2.rinterface_lib.openrlib: {e}")
        return False
    mode = getattr(openrlib, "cffi_mode", None)
    # cffi_mode is a CFFI_MODE enum member (e.g. <CFFI_MODE.API: 'API'>); the enum class is not
    # necessarily an attribute of openrlib, so compare by the member's .name (falling back to repr).
    mode_name = getattr(mode, "name", None) or str(mode).rsplit(".", 1)[-1].split(":")[0].strip(" '<>")
    print(f"rpy2 cffi_mode = {mode!r}  (require API)")
    if mode_name != "API":
        print("FAIL: rpy2 is NOT in API mode (ABI fallback or unknown). "
              "Set DYLD_INSERT_LIBRARIES=$R_HOME/lib/libR.dylib (see HOW_TO §0).")
        return False
    # Positively exercise R so a broken API binding surfaces now, not mid-run.
    try:
        import rpy2.robjects as ro
        ver = ro.r("R.version.string")[0]
        print(f"rpy2 API mode OK; R = {ver}")
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: rpy2 API-mode R call failed: {e}")
        return False
    return True


def check_model(archive: Path) -> bool:
    resolver_path = archive / "code" / "06c_validate_safety_embed.py"
    if not resolver_path.exists():
        print(f"FAIL: 06c resolver not found at {resolver_path}")
        return False
    # Load the shipped 06c module by path (its name has digits) and call its resolver.
    spec = importlib.util.spec_from_file_location("_c06c_resolver", resolver_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: could not import the shipped 06c module: {e}")
        return False
    if not hasattr(mod, "find_local_model_snapshot"):
        print("FAIL: 06c has no find_local_model_snapshot()")
        return False
    try:
        resolved = Path(mod.find_local_model_snapshot()).resolve()
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: find_local_model_snapshot() raised: {e}")
        return False
    expected = (archive / "models" / "all-MiniLM-L6-v2").resolve()
    print(f"resolved model = {resolved}")
    print(f"expected model = {expected}")
    if resolved != expected:
        print("FAIL: model did not resolve to the packaged copy under the archive.")
        return False
    if ".cache/huggingface" in str(resolved) or ".cache/huggingface" in os.environ.get("HF_HOME", ""):
        print("FAIL: a Hugging Face cache path is involved — must be offline/packaged only.")
        return False
    print("packaged-model resolution OK (no HF cache)")
    return True


def main() -> int:
    args = sys.argv[1:]
    require_model = "--require-model" in args
    positionals = [a for a in args if not a.startswith("--")]
    if not positionals:
        print("FAIL: usage: preflight_apimode.py <archive_root> [--require-model]")
        return 2
    archive = Path(positionals[0]).resolve()
    ok = check_api_mode()
    if require_model:
        ok = check_model(archive) and ok
    print("PREFLIGHT PASS" if ok else "PREFLIGHT FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
