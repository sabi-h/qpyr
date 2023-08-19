from typing import List

import numpy as np
from numpy.polynomial import polynomial


def get_generator_polynomial(deg: int) -> List[int]:
    result = [1]
    for i in range(1, deg+1):
        result = polynomial.polymul(result, [-i, 1])
    return result


def encode(message: List[int], number_of_ecc_symbols: int) -> List[int]:
    """Returns message with ecc symbols appended.
    :param message: message polynomial p(x)
    :param number_of_ecc_symbols: number of ecc symbols m
    """
    k = len(message)
    m = number_of_ecc_symbols
    n = k + m
    message_muliplier = [0] * (m) + [1]  # x^m
    message_raised_to_m = polynomial.polymul(message, message_muliplier)  # p(x) * x^m
    generator_polynomial = get_generator_polynomial(m)
    quotient, remainder = polynomial.polydiv(message_raised_to_m, generator_polynomial)
    print(
        f'generator polynomial: {generator_polynomial}',
        f'quotient: {quotient}',
        f'remainder: {remainder}',
    )
    codeword = np.concatenate((message, remainder))
    return codeword.tolist()



if __name__ == '__main__':
    encode(message=[2,3,-5,1], number_of_ecc_symbols=2)
