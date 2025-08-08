from sage.all import *
import secrets
from Crypto.Cipher import AES
from Crypto.Util.number import *

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

'''
Assumes all coefficients of `poly` are in
[-b, b]
'''
def poly2bytes(b, poly, degree=1023):
    bytes_int = 0
    
    q = poly.parent().base_ring().order()
    coeffs_range = 2*b + 1

    coeffs = poly.list()
    for i in range(len(coeffs)):
        x = coeffs[i].lift()
        if abs(x - q) < x:
            x = x - q
        
        # offset to [0, 2b+1] by adding b
        x = x + b
        
        bytes_int += x
        # dont shift on last iteration
        if i != len(coeffs) - 1:
            bytes_int <<= coeffs_range.bit_length()
    
    poly_bytes = long_to_bytes(bytes_int)

    # pad front with null for fixed length
    poly_bytes = poly_bytes.rjust((2*b + 1).bit_length() * (degree + 1) // 8, b"\x00")
    return poly_bytes

def bytes2poly(b, byte_data, S, num_coeffs):
    """
    Reconstructs a polynomial from bytes.

    Args:
        b: bound on coefficient absolute values.
        byte_data: bytes from `poly2bytes`.
        S: the polynomial ring to reconstruct the poly in (e.g. `self.S`).
        num_coeffs: number of coefficients (e.g. `self.n`). should be degree - 1

    Returns:
        A polynomial in ring S.
    """
    coeffs_range = 2 * b + 1
    bits_per_coeff = coeffs_range.bit_length()

    # Convert bytes to integer
    bytes_int = bytes_to_long(byte_data)

    coeffs = []
    for _ in range(num_coeffs):
        # Get the lowest bits_per_coeff bits
        x = bytes_int & ((1 << bits_per_coeff) - 1)
        bytes_int >>= bits_per_coeff

        # Undo the +b shift
        x = x - b

        coeffs.append(x)

    # Reverse to correct order
    coeffs.reverse()

    return S(coeffs)






