# eth-pq-multi-sig

Ethereum post quantum multi signatures

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

```



## Benchmarking

## Function info

`RLWE` is the class for the signature scheme. Its methods will be detailed below.

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


