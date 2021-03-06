#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

def sumar_epydoc(a,b):
    """
    Suma los dos números pasados como argumento.
    
    Realiza la suma de dos números y devuelve el resultado.

    @param a: primer número a sumar.

        Lista con opciones posibles:

        - 1: opción 1
        - 2: opción 2

    @param b: segundo número a sumar.
    @return: a + b

    """
    return a + b
    
def sumar_rst(a,b):
    """
    Suma los dos números pasados como argumento.
    
    Realiza la suma de dos números y devuelve el resultado.

    :param a: primer número a sumar.

        Lista con opciones posibles:

        - 1: opción 1
        - 2: opción 2
    :type a: int or float
    :param b: segundo número a sumar.
    :type b: int or float
    :return: a + b
    :rtype: int or float

    """
    return a + b

def sumar_numpy(a,b):
    """
    Suma los dos números pasados como argumento.
    
    Realiza la suma de dos números y devuelve el resultado.
    
    Parameters
    ----------
    a : int or float
        primer número a sumar.

        Lista con opciones posibles:

        - 1: opción 1
        - 2: opción 2

    b : int or float
        segundo número a sumar.

    Returns
    -------
    int or float
        a + b

    """
    return a + b

def sumar_google(a,b):
    """
    Suma los dos números pasados como argumento.
    
    Realiza la suma de dos números y devuelve el resultado.

    Args:
        a (int or float): primer número a sumar.

            Lista con opciones posibles:

            - 1: opción 1
            - 2: opción 2

        b (int or float): segundo número a sumar.

    Returns:
        int or float: a + b

    """
    return a + b

if __name__ == '__main__':
    print(sumar_rst(3,4))
