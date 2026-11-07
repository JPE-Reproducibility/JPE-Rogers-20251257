# Shipped embedding model — provenance

**Supporting reference; `README.md` governs.**

`all-MiniLM-L6-v2/` is the sentence-transformer model used by step 17
(`code/06c_validate_safety_embed.py`) to compute the safety embedding-distance measure
(Table D.12). It is shipped IN the package so a clean-room reviewer needs **no Hugging Face
cache and no network**.

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Pinned HF revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`
- License: **Apache-2.0** (redistributable)
- Integrity: `all-MiniLM-L6-v2.sha256` (verify with `cd models && shasum -a 256 -c all-MiniLM-L6-v2.sha256`)
- 06c loads it via `find_local_model_snapshot()`, which prefers this package copy over any HF cache.

Reviewers do NOT need `HF_HUB_OFFLINE=1` or a network connection: 06c finds this shipped model
first. (To instead download it fresh: `huggingface-cli download sentence-transformers/all-MiniLM-L6-v2
--revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41` — requires network; then verify the checksum.)
