# Copyright (c) 2022 Project Nayuki
# All rights reserved. Contact Nayuki for licensing.
# https://www.nayuki.io/page/reed-solomon-error-correcting-code-decoder


from typing import Iterable, List, Optional


class BinaryField:
    """A Galois field of the form GF(2^n/mod). Each element of this kind of field is a
    polynomial of degree less than n where each monomial coefficient is either 0 or 1.
    Both the field and the elements are immutable and thread-safe."""

    def __init__(self, mod):
        """Constructs a binary field with the given modulus. The modulus must have
        degree at least 1. Also the modulus must be irreducible (not factorable) in Z_2,
        but this critical property is not checked by the constructor."""
        if mod <= 1:
            raise ValueError("Invalid modulus")

        # The modulus of this field represented as a string of bits in natural order.
        # For example, the modulus x^5 + x^1 + x^0 is represented by the integer value 0b100011 (binary) or 35 (decimal).
        self.modulus = mod

        # The number of (unique) elements in this field. It is a positive power of 2, e.g. 2, 4, 8, 16, etc.
        # The size of the field is equal to 2 to the power of the degree of the modulus.
        self.size = 1 << (mod.bit_length() - 1)

    def zero(self):
        return 0

    def one(self):
        return 1

    def equals(self, x, y):
        return self._check(x) == self._check(y)

    def negate(self, x):
        return self._check(x)

    def add(self, x, y):
        return self._check(x) ^ self._check(y)

    def subtract(self, x, y):
        return self.add(x, y)

    def multiply(self, x, y):
        self._check(x)
        self._check(y)
        result = 0
        while y != 0:
            if y & 1 != 0:
                result ^= x
            x <<= 1
            if x >= self.size:
                x ^= self.modulus
            y >>= 1
        return result

    def reciprocal(self, w):
        # Extended Euclidean GCD algorithm
        x = self.modulus
        y = self._check(w)
        if y == 0:
            raise ValueError("Division by zero")
        a = 0
        b = 1
        while y != 0:
            q, r = self._divide_and_remainder(x, y)
            if q == self.modulus:
                q = 0
            x, y = y, r
            a, b = b, (a ^ self.multiply(q, b))
        if x == 1:
            return a
        else:  # All non-zero values must have a reciprocal
            raise AssertionError("Field modulus is not irreducible")

    # Returns a new tuple containing the pair of values (x div y, x mod y).
    def _divide_and_remainder(self, x, y):
        quotient = 0
        ylen = y.bit_length()
        for i in reversed(range(x.bit_length() - ylen + 1)):
            if x.bit_length() == ylen + i:
                x ^= y << i
                quotient |= 1 << i
        return (quotient, x)

    # Checks if the given object is the correct type and within the
    # range of valid values, and returns the same value.
    def _check(self, x):
        if not isinstance(x, int):
            raise TypeError()
        if not (0 <= x < self.size):
            raise ValueError("Not an element of this field: " + str(x))
        return x


class ReedSolomon:
    """Performs Reed-Solomon encoding and decoding. This object can encode a message into a codeword.
    The codeword can have some values modified by external code. Then this object can try
    to decode the codeword, and under some circumstances can reproduce the original message.
    This class is immutable and thread-safe, but the argument arrays passed into methods are not thread-safe."""

    def __init__(self, field, gen, msglen, ecclen, genpoly=None):
        """Constructs a Reed-Solomon encoder-decoder with the specified field, generator, and lengths."""
        if msglen <= 0 or ecclen <= 0:
            raise ValueError("Invalid message or ECC length")

        # The field for message and codeword values, and for performing arithmetic operations on values.
        self.f = field

        # Generator polynomial
        self.genpoly = genpoly

        # An element of the field whose powers generate all the non-zero elements of the field.
        self.generator = gen

        # The number of values in each message. A positive integer.
        self.message_len = msglen

        # The number of error correction values to expand the message by. A positive integer.
        self.ecc_len = ecclen

        # The number of values in each codeword, equal to message_len + ecc_len. Always at least 2.
        self.codeword_len = msglen + ecclen

    def encode(self, message) -> Iterable[int]:
        """Returns a new sequence representing the codeword produced by encoding the specified message.
        If the message has the correct length and all its values are
        valid in the field, then this method is guaranteed to succeed."""

        if len(message) != self.message_len:
            raise ValueError("Invalid message length")

        # Make the generator polynomial (this doesn't depend on the message)
        genpoly = self._make_generator_polynomial() if not self.genpoly else self.genpoly

        # Compute the remainder ((message(x) * x^ecclen) mod genpoly(x)) by performing polynomial division.
        # Process message bytes (polynomial coefficients) from the highest monomial power to the lowest power
        eccpoly = [self.f.zero()] * self.ecc_len
        for msgval in reversed(message):
            factor = self.f.add(msgval, eccpoly[-1])
            del eccpoly[-1]
            eccpoly.insert(0, self.f.zero())
            for j in range(self.ecc_len):
                eccpoly[j] = self.f.subtract(eccpoly[j], self.f.multiply(genpoly[j], factor))

        # Negate the remainder, then concatenate with message polynomial
        return message + [self.f.negate(val) for val in eccpoly]

    # Computes the generator polynomial by multiplying powers of the generator value:
    # genpoly(x) = (x - gen^0) * (x - gen^1) * ... * (x - gen^(ecclen-1)).
    # The resulting array of coefficients is in little endian, i.e. from lowest to highest power, except
    # that the very highest power (the coefficient for the x^ecclen term) is omitted because it's always 1.
    # The result of this method can be pre-computed because it doesn't depend on the message to be encoded.
    def _make_generator_polynomial(self):
        # Start with the polynomial of 1*x^0, which is the multiplicative identity
        result = [self.f.one()] + [self.f.zero()] * (self.ecc_len - 1)
        genpow = self.f.one()
        for i in range(self.ecc_len):
            # At this point, genpow == generator^i.
            # Multiply the current genpoly by (x - generator^i)
            for j in reversed(range(self.ecc_len)):
                result[j] = self.f.multiply(self.f.negate(genpow), result[j])
                if j >= 1:
                    result[j] = self.f.add(result[j - 1], result[j])

            genpow = self.f.multiply(self.generator, genpow)
        # print(f"generator polynomial: {result}")
        # return [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
        return result


def encode(msg: int | str | list, ecclen: int = 0, genpoly: Optional[List[int]] = None) -> Iterable[int]:
    """Encode a message into a codeword.

    Args:
        msg (int|str|list): message to encode
        ecclen (int, optional): number of error correcting codewords. Defaults to length of message.
    """
    msg_list = list(str(msg)) if isinstance(msg, int | str) else msg
    ecclen = ecclen if ecclen > 0 else len(msg_list)

    if all(map(lambda x: isinstance(x, str), msg_list)):
        msg_list = [ord(c) for c in msg_list]

    field = BinaryField(0x11D)
    # field = BinaryField(2**10)
    generator = 0x02
    msglen = len(msg_list)
    rs = ReedSolomon(field, generator, msglen, ecclen, genpoly)

    codeword = rs.encode(msg_list)
    return codeword


if __name__ == "__main__":
    # --- Format information encoding ---
    msg = [0, 0, 1, 0, 1]
    genpoly = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
    codeword = encode(msg, ecclen=10, genpoly=genpoly)
    print("codeword", codeword)
    expected_result = msg + [0, 0, 1, 1, 0, 1, 1, 1, 0, 0]
    assert codeword == expected_result
