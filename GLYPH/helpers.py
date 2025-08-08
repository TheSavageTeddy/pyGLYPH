from sage.all import *
import secrets
from Crypto.Cipher import AES
from Crypto.Util.number import *
from math import log2, ceil, comb

'''
returns random integer between a and b inclusive
asserts b >= a
'''
def randint(a:int, b:int) -> int:
    return secrets.choice(range(a,b+1))

def infinity_norm(poly, mod):
    # Get coefficients as integers in centered range [-mod//2, mod//2]
    coeffs = []
    for c in poly.list():
        c_int = int(c)
        if c_int > mod//2:
            c_int -= mod
        coeffs.append(c_int)
    return max(abs(c) for c in coeffs)

def gen_bounded_polynomial(coeff_bound, degree, poly_ring, disallow_coeffs = []):
        coeffs = []
        for _ in range(degree):
            while True:
                c = randint(-coeff_bound, coeff_bound)
                if c not in disallow_coeffs:
                    coeffs.append(c)
                    break
        return poly_ring(coeffs)

def randomplease(aes_cipher, counter):
    """
    Generate the next 64 bits of randomness via AES-CTR.
    `aes_cipher` is an AES.new(key, AES.MODE_ECB) instance,
    `counter` is an integer that you increment each call.
    Returns (rnd64, new_counter).
    """
    ctr_block = counter.to_bytes(AES.block_size, 'big')
    stream = aes_cipher.encrypt(ctr_block)
    rnd64 = int.from_bytes(stream[:8], 'big')
    return rnd64, counter + 1

def prepare_poly_for_hash(poly, m):
    polylen = len(poly.list()) * 2
    length = polylen + len(m)
    buf = bytearray(length)

    coeffs = poly.list()
    for i in range(len(coeffs)):
        x = coeffs[i].lift()
        base = 2 * i
        for j in range(2):
            buf[base + j] = x & 0xFF
            x >>= 8
    
    buf[polylen:] = m

    return buf

def poly2bytes(b, poly, degree=1023):
    '''
    Assumes all coefficients of `poly` are in
    [-b, b].
    Given a polynomial and the bounds of its coefficients `b`,
    where all of its coefficients should be in `[-b, b]`,
    and the degree of the polynomial, serialises the
    polynomial into optimally into bytes by offsetting
    the polynomial coefficients to [0, 2b] by adding `b`,
    converting to base `b` format, then converting to bytes.
    '''
    bytes_int = 0
    
    q = poly.parent().base_ring().order()
    coeffs_range = 2*b + 1

    coeffs = poly.list()
    for i in range(len(coeffs)):
        x = coeffs[i].lift()
        # poly coeffs are initially in [0, q)
        # we change it to [-q//2, q//2)
        if abs(x - q) < x:
            x = x - q
        
        # offset to [0, 2b] by adding b
        x = x + b
        
        bytes_int += x
        # dont shift on last iteration
        if i != len(coeffs) - 1:
            bytes_int *= coeffs_range
    
    poly_bytes = long_to_bytes(bytes_int)

    bytes_len = ceil((degree + 1) * log2(coeffs_range) / 8)
    return poly_bytes.rjust(bytes_len, b"\x00")

def bytes2poly(b, byte_data, S, num_coeffs):
    '''
    Given bounds of the polynomial's coefficients `b`,
    where all of its coefficients should be in `[-b, b]`,
    the raw bytes data, S, the quotient ring of polynomials,
    and the number of coefficients the polynomial should have,
    unpacks the bytes data into coefficients of polynomial as
    packed by `poly2bytes`, and returns a polynomial
    as an element of S.
    '''
    
    coeffs_range = 2 * b + 1

    bytes_int = bytes_to_long(byte_data)

    coeffs = []
    for _ in range(num_coeffs):
        x = bytes_int % coeffs_range
        bytes_int //= coeffs_range

        # undo +b shift
        x = x - b

        coeffs.append(x)

    # reverse to correct poly coeffs order
    coeffs.reverse()

    return S(coeffs)

comb_cache = {}

def ccomb(n, k):
    '''
    Return comb(n, k)
    caching the result in `comb_cache` so future calls with the same
    (n,k) are not recomputed for efficiency.
    '''
    key = (n, k)
    cached = comb_cache.get(key)
    if cached:
        return cached

    r = comb(n, k)
    comb_cache[key] = r
    return r

def encode_k_sparse_poly(poly, k: int, n: int) -> bytes:
    '''
    Given polynomial with `k` non-zero coefficients, and
    `n`, the total number of coefficients, uses the
    combinatorial number system to encode the polynomial
    into bytes. Assumes coefficients are either -1, 0, or 1.
    This is used to optimally encode `c` in RLWE.

    https://en.wikipedia.org/wiki/Combinatorial_number_system
    '''

    # k bits for sign (-1 or 1), and another
    # log_2(comb(n, k)) bits for position
    bytes_required = ceil((k + log2(ccomb(n, k))) / 8)

    # convert from comb(n, k) to N
    signs = 0
    q = poly.parent().base_ring().order()
    coeffs = poly.list()
    N = 0
    k_count = k
    for i, coeff in enumerate(coeffs):
        c = n - i # 1-indexed
        # coeff must be -1, 0, or 1
        assert (coeff == -1 or coeff == 0 or coeff == 1)
        if coeff != 0:
            N += ccomb(c, k_count)
            k_count -= 1

            signs <<= 1
            if coeff == -1:
                signs |= 0
            else:
                signs |= 1

    # put sign bits as last k bits
    N <<= k
    N |= signs

    return long_to_bytes(N).rjust(bytes_required, b"\x00")

def decode_k_sparse_poly(poly_bytes: bytes, k: int, n: int, S) -> bytes:
    '''
    Given bytes encoded by `encode_k_sparse_poly`,
    k, the number of non-zero coefficients in the polynomial,
    n, the number of coefficients in the polynomial,
    return decoded polynomial as element of S
    '''
    
    bytes_required = ceil((k + log2(comb(n, k))) / 8)
    assert len(poly_bytes) == bytes_required

    unpacked_int = bytes_to_long(poly_bytes)
    signs = unpacked_int & (2**k - 1)
    N = unpacked_int >> k

    coeffs = [0 for _ in range(n)]
    k_count = k

    for i in range(k):
        # find maximal c_k such that comb(c_k, k) < N
        # using binary search
        # then subtract and repeat
        mi = 0
        mx = n + 1
        c_maximal = None
        while True:
            mid = (mi + mx) // 2
            r = ccomb(mid, k_count)

            # too high
            if r > N:
                mx = mid
            else:
                r_one_higher = ccomb(mid + 1, k_count)
                if r <= N and r_one_higher > N:
                    c_maximal = mid
                    break
                else:
                    # too low
                    mi = mid
        
        N -= r
        idx = -(c_maximal - n)
        
        sign_bit = (signs >> (k_count-1)) & 1
        if sign_bit == 1:
            coeffs[idx] = 1
        else:
            coeffs[idx] = -1

        k_count -= 1
    
    return S(coeffs)

    


