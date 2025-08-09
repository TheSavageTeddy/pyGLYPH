# pyGLYPH

Post quantum signature scheme GLYPH, implemented in Python.

Includes AGLYPH, a multi-signature version of GLYPH.

Original paper: [GLYPH: A New Instantiation of the GLP Digital Signature
Scheme](https://eprint.iacr.org/2017/766.pdf)

## Requirements

The code is written in Python using SageMath and will require `sage` to run.
Please follow Sage's [installation guide](https://doc.sagemath.org/html/en/installation/index.html) to install it.

We also require `pycryptodome`, and optionally `tqdm` for tests. You can install these by doing `sage --pip install -r requirements.txt`.

## Usage

## Tests

Unit and fuzzing tests for sage are directly in the `glyph.sage` and `aglyph.sage` files.
Run tests:
```
sage GLYPH/glyph.sage
sage AGLYPH/aglyph.sage
```

Example:
```
➜ sage GLYPH/glyph.sage
unit tests - constant msg: 100%|███████████████████████████| 1000/1000 [01:59<00:00,  8.39it/s]
fuzzing tests - random msgs: 100%|█████████████████████████| 1000/1000 [02:02<00:00,  8.13it/s]

➜ sage AGLYPH/aglyph.sage 
same message: 100%|██████████████████████████████████████████| 100/100 [18:20<00:00, 11.01s/it]
fuzzed message: 100%|████████████████████████████████████████| 100/100 [18:26<00:00, 11.06s/it]

```



## Benchmarking

Benchmarking can be run with the `bench.sage` files in both `GLYPH` and `AGLYPH`.
```
sage AGLYPH/bench.sage
sage GLYPH/bench.sage
```

Example:
```
➜ sage GLYPH/bench.sage 

--- GLYPH Benchmarks (running 100 iterations) ---

--- Key Generation ---
Key Generation: 100%|████████████████████████████████████████| 100/100 [00:01<00:00, 98.83it/s]
Removed 12 outliers.
Mean:       7.442314 ms
Median:     7.436021 ms
Std Dev:    0.233748 ms

--- Signing ---
Signing: 100%|███████████████████████████████████████████████| 100/100 [00:06<00:00, 14.76it/s]
Removed 5 outliers.
Mean:       50.393637 ms
Median:     40.514500 ms
Std Dev:    30.494781 ms

--- Verification ---
Verification: 100%|██████████████████████████████████████████| 100/100 [00:07<00:00, 13.23it/s]
Removed 13 outliers.
Mean:       6.946790 ms
Median:     6.929292 ms
Std Dev:    0.094228 ms

Results saved to bench_results_glyph.json

```

```
➜ sage AGLYPH/bench.sage

--- AGLYPH Benchmarks (running 100 iterations) ---

--- Key Generation ---
Key Generation: 100%|███████████████████████████████████████| 100/100 [00:00<00:00, 260.66it/s]
Removed 12 outliers.
Mean:       2.613677 ms
Median:     2.608250 ms
Std Dev:    0.040964 ms

--- Signing ---
Signing: 100%|███████████████████████████████████████████████| 100/100 [00:01<00:00, 70.79it/s]
Removed 8 outliers.
Mean:       9.552615 ms
Median:     9.561625 ms
Std Dev:    0.106122 ms

--- Verification ---
Verification: 100%|██████████████████████████████████████████| 100/100 [00:01<00:00, 59.30it/s]
Removed 2 outliers.
Mean:       3.712636 ms
Median:     3.762728 ms
Std Dev:    0.163909 ms

Results saved to bench_results_aglyph.json

```

## Function info

### GLYPH

`GLYPH` is the class for the signature scheme. Its methods will be detailed below.

`_keygen`
- Generates private and public key for signing and verification.
        The format of these keys are polynomials under the quotient ring R, where\
            public_key = t = a*s + e\
            private_key = (s, e)\
        Returns tuple `(public_key, private_key)`.

`keygen`
- Generates private and public key for signing and verification.
        The format of these keys are raw bytes.
        Secret key polynomial `s` and `e` are directly concatenated.
        Returns tuple `(public_key, private_key)`.

`_sign`
- Given a message `m` in bytes, and private key tuple `(s, e)`,
        signs message `m` and returns signature tuple
        `(c, z1, z2)`.

`sign`
- Given a message `m` in bytes, and private key in bytes,
        signs message `m` and returns signature in bytes.

`_verify`
- Given a message `msg` in bytes, signature in tuple of polynomials `(c, z1, z2)`,
        and public key polynomial `t`, verifies if the signature for the message is valid.
        That is, returns `True` given `sig` if `msg` was signed by `public_key`,
        otherwise returns `False`.

`verify`
- Given a message `msg` in bytes, signature bytes,
        and public key in bytes, verifies if the signature for the message is valid.
        That is, returns `True` given `sig` if `msg` was signed by `public_key`,
        otherwise returns `False`.

`polyhash`
- Given polynomial `poly` and message in bytes `m`,
        deterministically hashes both the `poly` and `m`,
        and returns the hash digest in bytes.


