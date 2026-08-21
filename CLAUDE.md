# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This repo currently contains only a design document: `hybrid_image_compressor_project_plan.md`. No source code, tests, or build tooling exist yet. The plan describes a hybrid image compressor combining truncated SVD, quantization, and Huffman coding into a custom `.dyimg` file format. Treat the plan as the source of truth for architecture until code is written.

## Planned CLI

```bash
python compress.py input.png output.dyimg --rank 40
python decompress.py output.dyimg reconstructed.png
```

A compressed `.dyimg` must be self-contained — decompression cannot require the original image or any sidecar metadata.

Additional planned flags: `--quality`, `--quantization-bits`, `--show-stats`, and `--energy <fraction>` (auto-select the smallest rank `k` such that `sum(σ_i²)_{i≤k} / sum(σ_i²) ≥ fraction`).

## Planned Architecture

The pipeline is split into single-responsibility modules under `src/`:

- `image_io.py` — load/save via Pillow, split/combine RGB channels, clamp to `[0, 255]`.
- `svd.py` — truncated SVD per channel; initially `np.linalg.svd(A, full_matrices=False)`, later replaced by custom power-iteration / randomized SVD.
- `quantization.py` — map float SVD factors (`U_k`, `Σ_k`, `V_k^T`) to integers (start with int16) using per-matrix min/max; store enough metadata to invert.
- `huffman.py` — **must be implemented manually** (min-heap via `heapq`, binary tree, code table). Do not use `gzip`, `zlib`, or other compression libraries for entropy coding — that's the DSA learning goal.
- `bitstream.py` — `BitWriter` / `BitReader` that pack Huffman codes into bytes. Never persist bits as ASCII `"01"` strings.
- `file_format.py` — serialize/deserialize the `.dyimg` binary layout.

Top-level `compress.py` and `decompress.py` are thin CLIs that orchestrate these modules.

### `.dyimg` header layout

```
DYIM              4 bytes  (magic)
VERSION           1 byte
WIDTH             4 bytes
HEIGHT            4 bytes
CHANNELS          1 byte
RANK              2 bytes
QUANTIZATION_BITS 1 byte
[quantization metadata]
[huffman metadata]
[compressed bitstream]
```

### Data flow

Compress: RGB split → truncated SVD per channel → quantize `U_k`, `Σ_k`, `V_k^T` → serialize to bytes → build Huffman tree over those bytes → bit-pack → write `.dyimg`.

Decompress: read header → rebuild Huffman tree → decode bitstream → dequantize → reconstruct `A_k = U_k Σ_k V_k^T` per channel → clamp to `[0, 255]` → save.

## Development Order (Enforce This)

The plan is explicit that features must land in this sequence — each stage must round-trip end-to-end before the next begins:

1. Grayscale SVD reconstruction (no file format yet).
2. RGB support + reconstruction error metrics (Frobenius, MSE, PSNR).
3. Standalone Huffman encoder/decoder — test with text like `"AAAAABBBBCCD"` and verify `decode(encode(data)) == data` on random bytes before integrating.
4. Quantization (start at int16).
5. `.dyimg` serialization.
6. Full compress/decompress CLI.
7. Auto rank selection via singular-value energy.
8. Custom truncated SVD (power iteration → deflation → randomized).

Explicitly deferred until the base pipeline works: GPU acceleration, multithreading, adaptive block compression, custom SVD, web UI.

## Tech Stack Constraints

Python only for v1. Allowed libs: `numpy`, `Pillow`, `struct`, `heapq`, `argparse`. Optional: `matplotlib`, `pytest`. Do not pull in `scipy.sparse.linalg`, `gzip`, `zlib`, or similar shortcuts — replacing them is the point of the project.

## Testing

Planned layout: `tests/test_svd.py`, `tests/test_huffman.py`, `tests/test_quantization.py`, `tests/test_roundtrip.py`. Key invariants to assert:

- Huffman: empty input, single repeated symbol, all-unique symbols, random bytes, large file — always `decoded == original`.
- SVD: at `k = full rank`, reconstruction is near-exact; increasing `k` monotonically lowers Frobenius error.
- End-to-end: `compress → decompress` preserves dimensions and channel count for every fixture image.

No test runner is set up yet; once `pytest` is added, run the suite with `pytest` and a single test with `pytest tests/test_huffman.py::test_name`.
