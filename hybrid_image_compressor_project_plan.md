# Hybrid Image Compressor — Project Plan

## Project Goal

Build a custom image compression tool that combines:

1. **Truncated Singular Value Decomposition (SVD)** for lossy image compression.
2. **Quantization** to reduce the precision required to store matrix factors.
3. **Huffman Coding** for lossless entropy compression.
4. A custom compressed image format such as `.dyimg`.

The final system should support:

```bash
python compress.py input.png output.dyimg --rank 40
python decompress.py output.dyimg reconstructed.png
```

The project should demonstrate both **Computational Linear Algebra** and **Data Structures & Algorithms** concepts.

---

# 1. Core Idea

For an image channel represented by a matrix:

\[
A \in \mathbb{R}^{m \times n}
\]

compute its SVD:

\[
A = U\Sigma V^T
\]

Instead of storing the full decomposition, retain only the first \(k\) singular values and vectors:

\[
A_k = U_k\Sigma_kV_k^T
\]

where:

- \(U_k\) is \(m \times k\)
- \(\Sigma_k\) contains \(k\) singular values
- \(V_k^T\) is \(k \times n\)

For RGB images, perform this independently for:

- Red
- Green
- Blue

The retained matrices are then quantized and Huffman encoded.

---

# 2. Compression Pipeline

```text
Original Image
      |
      v
Load RGB pixels
      |
      v
Split into R, G, B matrices
      |
      v
Compute truncated SVD
      |
      v
U_k, Sigma_k, V_k^T
      |
      v
Quantize numerical values
      |
      v
Convert values to bytes/symbols
      |
      v
Build Huffman frequency table
      |
      v
Build Huffman tree
      |
      v
Encode bitstream
      |
      v
Write custom .dyimg file
```

---

# 3. Decompression Pipeline

```text
.dyimg file
    |
    v
Read metadata/header
    |
    v
Read Huffman tree/frequencies
    |
    v
Decode compressed bitstream
    |
    v
Recover quantized SVD data
    |
    v
Dequantize U, Sigma, V^T
    |
    v
Reconstruct RGB matrices
    |
    v
A_k = U_k Sigma_k V_k^T
    |
    v
Clamp values to [0, 255]
    |
    v
Save reconstructed image
```

---

# 4. Computational Linear Algebra Concepts

## SVD

The main compression method is truncated SVD.

Use the fact that the best rank-\(k\) approximation of a matrix under the Frobenius norm is obtained by retaining its largest \(k\) singular values.

\[
A_k = \sum_{i=1}^{k}\sigma_i u_i v_i^T
\]

This lets you discard components associated with smaller singular values.

### Concepts demonstrated

- Singular Value Decomposition
- Low-rank approximation
- Orthogonal matrices
- Singular values
- Matrix multiplication
- Matrix norms
- Approximation error
- Storage complexity

---

# 5. DSA Concepts

## Huffman Coding

Huffman coding should be implemented manually rather than using a compression library.

### Data structures

- Min heap / priority queue
- Binary tree
- Hash map / dictionary
- Bitstream
- Byte arrays

### Algorithm

1. Count symbol frequencies.
2. Insert all symbols into a min heap.
3. Remove the two least-frequent symbols.
4. Merge them into a new tree node.
5. Push the new node into the heap.
6. Repeat until one node remains.
7. Traverse the tree to generate prefix codes.

Example:

```text
Symbol frequencies

12 -> 50
27 -> 21
41 -> 14
93 -> 8
```

Possible Huffman codes:

```text
12 -> 0
27 -> 10
41 -> 110
93 -> 111
```

More common symbols receive shorter codes.

---

# 6. Recommended Technology Stack

## First version

Use Python.

Libraries:

```text
numpy
Pillow
struct
heapq
argparse
```

Optional:

```text
matplotlib
pytest
```

Avoid compression libraries for Huffman coding because the goal is to implement the data structure yourself.

---

# 7. Suggested Repository Structure

```text
hybrid-image-compressor/
|
├── README.md
├── requirements.txt
|
├── compress.py
├── decompress.py
|
├── src/
│   ├── __init__.py
│   │
│   ├── image_io.py
│   ├── svd.py
│   ├── quantization.py
│   ├── huffman.py
│   ├── bitstream.py
│   └── file_format.py
|
├── tests/
│   ├── test_svd.py
│   ├── test_huffman.py
│   ├── test_quantization.py
│   └── test_roundtrip.py
|
├── examples/
│   ├── original/
│   └── reconstructed/
|
└── benchmarks/
    └── benchmark.py
```

---

# 8. Module Responsibilities

## `image_io.py`

Responsibilities:

- Load images
- Convert images to RGB
- Split images into R/G/B matrices
- Combine matrices back into an image
- Clamp output to valid pixel values

Functions could include:

```python
load_image(path)
split_channels(image)
combine_channels(r, g, b)
save_image(image, path)
```

---

## `svd.py`

Responsibilities:

- Compute SVD
- Select rank \(k\)
- Reconstruct matrices

Initial implementation:

```python
U, S, VT = np.linalg.svd(A, full_matrices=False)

Uk = U[:, :k]
Sk = S[:k]
VTk = VT[:k, :]
```

Later versions can replace NumPy's full SVD with your own approximation.

---

## `quantization.py`

Floating-point SVD matrices are expensive to store.

Quantization converts them into smaller integer representations.

Example:

```text
float32
    |
    v
normalized range
    |
    v
int16
```

You will need to store enough metadata to reverse the mapping.

Possible approach:

\[
q = \text{round}\left(\frac{x-x_{\min}}{x_{\max}-x_{\min}}(2^b-1)\right)
\]

where \(b\) is the number of quantization bits.

Start with:

```text
16-bit quantization
```

Later try:

```text
8-bit
12-bit
16-bit
```

and compare reconstruction quality.

---

## `huffman.py`

Create a node structure:

```python
class HuffmanNode:
    def __init__(self, symbol=None, frequency=0, left=None, right=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right
```

Use Python's:

```python
heapq
```

for the min heap.

Required operations:

```text
build_frequency_table()
build_huffman_tree()
generate_codes()
encode()
decode()
```

---

## `bitstream.py`

Huffman codes are sequences of bits, not strings.

Do not permanently store:

```text
"010110101001..."
```

as text.

Instead pack them into bytes.

For example:

```text
01011010 -> 0x5A
```

Implement:

```text
BitWriter
BitReader
```

This is a useful systems-programming component of the project.

---

## `file_format.py`

Responsible for serializing and deserializing your `.dyimg` format.

Possible layout:

```text
+---------------------------+
| Magic Number              |
+---------------------------+
| Version                   |
+---------------------------+
| Width                     |
+---------------------------+
| Height                    |
+---------------------------+
| Number of Channels        |
+---------------------------+
| Rank k                    |
+---------------------------+
| Quantization Metadata     |
+---------------------------+
| Huffman Metadata          |
+---------------------------+
| Compressed Bitstream      |
+---------------------------+
```

---

# 9. Custom `.dyimg` File Format

Start with a simple binary format.

Possible header:

```text
DYIM                  4 bytes
VERSION               1 byte
WIDTH                 4 bytes
HEIGHT                4 bytes
CHANNELS              1 byte
RANK                   2 bytes
QUANTIZATION_BITS      1 byte
```

Then store information needed to reconstruct each channel.

Do not optimize the format too early.

Get a working round-trip first.

---

# 10. Development Roadmap

## Phase 1 — Basic SVD Compressor

Goal:

Compress and reconstruct an image using truncated SVD.

Tasks:

- [ ] Load an image using Pillow
- [ ] Convert to RGB
- [ ] Split into three matrices
- [ ] Compute SVD of each channel
- [ ] Keep only the first \(k\) components
- [ ] Reconstruct each channel
- [ ] Combine RGB matrices
- [ ] Save reconstructed image

Example command:

```bash
python compress_demo.py cat.png --rank 50
```

At this stage, do not worry about creating an actual compressed file.

---

# 11. Phase 2 — Measure Compression Quality

Add metrics.

## Compression Ratio

\[
\text{Compression Ratio}
=
\frac{\text{Original Size}}
{\text{Compressed Size}}
\]

## Space Savings

\[
\text{Savings}
=
1-\frac{\text{Compressed Size}}
{\text{Original Size}}
\]

## Frobenius Reconstruction Error

\[
\frac{\|A-A_k\|_F}{\|A\|_F}
\]

Also consider:

- MSE
- PSNR

Generate results like:

```text
Rank:                  40
Original dimensions:   1920 x 1080
Original file size:    4.20 MB
Compressed size:       0.82 MB
Space saved:           80.5%
Relative error:        4.2%
```

---

# 12. Phase 3 — Build Huffman Coding

Build Huffman separately before integrating it with SVD.

Test with text first.

Example:

```text
AAAAABBBBCCD
```

Make sure:

```text
decode(encode(data)) == data
```

Then test arbitrary byte arrays.

Required components:

- [ ] Frequency dictionary
- [ ] Huffman node
- [ ] Min heap
- [ ] Tree construction
- [ ] Code generation
- [ ] Encoding
- [ ] Decoding
- [ ] Bit packing

---

# 13. Phase 4 — Quantization

Convert SVD matrices into compact integer representations.

Try:

```text
float64
float32
int16
uint8
```

Compare:

- Storage
- Reconstruction error
- Compression ratio

A good starting point is `int16`.

---

# 14. Phase 5 — Integrate SVD + Huffman

Pipeline:

```text
SVD factors
    |
    v
Quantization
    |
    v
Serialization
    |
    v
Byte stream
    |
    v
Huffman coding
```

Then verify:

```text
original image
      |
      v
compress
      |
      v
image.dyimg
      |
      v
decompress
      |
      v
reconstructed.png
```

---

# 15. Phase 6 — Create CLI

Example usage:

```bash
python compress.py input.png output.dyimg --rank 40
```

Possible arguments:

```text
--rank
--quality
--quantization-bits
--show-stats
```

Decompression:

```bash
python decompress.py output.dyimg output.png
```

---

# 16. Phase 7 — Automatic Rank Selection

Instead of forcing the user to select \(k\), allow a quality threshold.

The energy preserved by rank \(k\) can be approximated with:

\[
\text{Energy}(k)
=
\frac{\sum_{i=1}^{k}\sigma_i^2}
{\sum_{i=1}^{r}\sigma_i^2}
\]

Example:

```bash
python compress.py image.png image.dyimg --energy 0.95
```

The program chooses the smallest \(k\) retaining at least 95% of the singular-value energy.

This is a strong computational linear algebra feature.

---

# 17. Phase 8 — Implement Your Own Truncated SVD

After the full system works with `numpy.linalg.svd`, replace it with your own approximation.

Possible progression:

## Version A

Use NumPy SVD.

## Version B

Implement power iteration.

For a matrix \(A\), dominant right singular vectors are eigenvectors of:

\[
A^TA
\]

Power iteration:

\[
x_{k+1}
=
\frac{A^TAx_k}
{\|A^TAx_k\|}
\]

The corresponding singular value is:

\[
\sigma = \sqrt{\lambda}
\]

## Version C

Use deflation to compute multiple dominant singular vectors.

## Version D

Implement randomized SVD.

This allows you to compare:

```text
NumPy full SVD
vs
Custom power-iteration SVD
vs
Randomized SVD
```

Measure:

- runtime
- reconstruction error
- compression ratio

---

# 18. Phase 9 — Adaptive Block Compression

This is an excellent advanced extension.

Instead of applying one rank to the whole image:

```text
Entire image -> rank 40
```

split the image into blocks:

```text
+-----+-----+
| B1  | B2  |
+-----+-----+
| B3  | B4  |
+-----+-----+
```

Estimate complexity in each block.

Detailed blocks:

```text
higher rank
```

Simple blocks:

```text
lower rank
```

Possible complexity measures:

- variance
- singular-value decay
- gradient magnitude

This creates a much more realistic compression algorithm.

---

# 19. Phase 10 — Optional Web Interface

After the algorithm is complete, create a frontend.

Possible stack:

```text
React
FastAPI
Python compression backend
```

Interface:

```text
+--------------------------------------+
| Upload Image                         |
+--------------------------------------+

Compression Rank
10 -------[====|=========]------- 100

Original               Compressed
[ image ]               [ image ]

Original Size: 4.2 MB
Compressed Size: 0.8 MB

Space Saved: 81%
PSNR: 32.4 dB
```

Allow the user to change rank interactively.

---

# 20. Useful Experiments

Run the same image at ranks:

```text
5
10
20
40
80
160
```

Record:

```text
rank
compressed size
compression ratio
Frobenius error
PSNR
runtime
```

Plot:

```text
Rank vs File Size
Rank vs Reconstruction Error
Rank vs Runtime
```

---

# 21. Complexity Analysis

Include algorithmic analysis in the final README.

For a matrix:

\[
A \in \mathbb{R}^{m \times n}
\]

full SVD roughly costs:

\[
O(\min(mn^2,m^2n))
\]

For truncated or iterative methods, cost can be significantly reduced when:

\[
k \ll \min(m,n)
\]

Huffman construction with \(s\) symbols costs approximately:

\[
O(s \log s)
\]

Encoding \(N\) symbols is approximately:

\[
O(N)
\]

assuming code lookup is constant time.

---

# 22. Testing Plan

## Huffman tests

```text
empty input
one repeated symbol
all unique symbols
random bytes
large file
```

Always verify:

```python
decoded == original
```

---

## SVD tests

Check:

```text
k = full rank
```

should reconstruct very close to the original matrix.

Verify reconstruction dimensions.

Verify increasing \(k\) lowers reconstruction error.

---

## End-to-End Test

For every test image:

```text
image.png
   |
compress
   |
image.dyimg
   |
decompress
   |
output.png
```

Ensure:

- output dimensions are correct
- channels are correct
- file can always be decoded
- reconstruction quality behaves as expected

---

# 23. Suggested Milestones

## Milestone 1

Working low-rank image reconstruction.

## Milestone 2

Compression statistics and error metrics.

## Milestone 3

Standalone Huffman encoder/decoder.

## Milestone 4

Quantized SVD representation.

## Milestone 5

Custom `.dyimg` format.

## Milestone 6

Full compression/decompression CLI.

## Milestone 7

Automatic rank selection.

## Milestone 8

Custom truncated-SVD implementation.

## Milestone 9

Benchmark suite.

## Milestone 10

Optional GUI/web app.

---

# 24. Minimum Viable Product

The MVP should support:

```bash
python compress.py photo.png photo.dyimg --rank 40
python decompress.py photo.dyimg restored.png
```

and print:

```text
Compression complete.

Original size:       3.84 MB
Compressed size:     0.91 MB
Space saved:         76.3%
Rank:                40
Relative error:      0.047
```

The compressed `.dyimg` should contain enough information that decompression does **not** require the original image.

---

# 25. Version Progression

A good development strategy is:

```text
V1
SVD image reconstruction

V2
Real serialized SVD file

V3
Quantization

V4
Huffman compression

V5
Custom .dyimg format

V6
Automatic rank selection

V7
Custom power-iteration/truncated SVD

V8
Adaptive block compression

V9
Web interface
```

Do not attempt all features at once.

Make every version functional before moving to the next one.

---

# 26. What Not to Do Initially

Avoid these until the base compressor works:

- GPU acceleration
- JPEG comparison internals
- Neural-network compression
- Complex GUI
- Multithreading
- Custom SVD implementation
- Adaptive blocks

First prove that this works:

```text
Image -> SVD -> serialize -> deserialize -> reconstruct image
```

Then add optimization.

---

# 27. Resume Description

Once the project is complete, a resume bullet could look like:

> Built a custom image compression codec combining truncated singular value decomposition, numerical quantization, and Huffman entropy coding; implemented binary serialization, priority-queue-based Huffman trees, reconstruction-error analysis, and a custom compressed image format.

A stronger version after implementing your own numerical methods:

> Developed an image compression codec using truncated SVD and Huffman entropy coding, implementing iterative singular-vector estimation, binary serialization, quantization, and adaptive low-rank reconstruction while benchmarking compression ratio, image error, and runtime.

---

# 28. Best Starting Task

Start with a single grayscale image.

Your first target should be:

```python
image = load_grayscale_image("test.png")

U, S, VT = np.linalg.svd(image, full_matrices=False)

k = 30

compressed = (
    U[:, :k],
    S[:k],
    VT[:k, :]
)

reconstructed = (
    U[:, :k]
    @ np.diag(S[:k])
    @ VT[:k, :]
)
```

Once this works:

1. Support RGB.
2. Calculate reconstruction error.
3. Serialize the SVD factors.
4. Add quantization.
5. Build Huffman coding.
6. Combine everything into `.dyimg`.

That sequence will keep the project manageable while ensuring every stage teaches a concrete concept.
