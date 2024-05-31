#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2024-05-30
# @Filename: convert.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import struct

from typing import Sequence


def data_to_string(
    data: Sequence[int],
    msb_first: bool = True,
    endianness: str = "=",
) -> bytes:
    r"""Converts a list of unsigned 16-bit integers to a string of bytes.

    Parameters
    ----------
    data
        A list of 16-bit unsigned integers.
    msb_first
        If `True`, the sequence is understood as ordered from most significant
        byte to least significant byte. If `False`, LSB to MSB.
    endianness
        The endianness of the data. Defaults to the system endianness (``=``).
        Valid values are ``=`` (system endianness), ``<`` (little-endian),
        and ``>`` (big-endian).

    Returns
    -------
    bytes
        A string of bytes.

    Example
    -------
    .. code-block:: python

        >>> data_to_string([10, 20], msb_first=True, endianness="<")
        b'\x14\x00\n\x00'

        >>> data_to_string([10, 20], msb_first=False, endianness="<")
        b'\n\x00\x14\x00'

    """

    if msb_first:
        data_ordered = data[::-1]
    else:
        data_ordered = data

    return struct.pack(f"{endianness}" + ("H" * len(data)), *data_ordered)


def data_to_uint16(data: int, endianness: str = "=") -> int:
    """Converts an unsigned 16-bit integer to an integer.

    This essentially handles the possibility that the data is not in the system
    endianness.

    Parameters
    ----------
    data
        The 16-bit unsigned integer.
    endianness
        The endianness of the data. Defaults to the system endianness (``=``).
        Valid values are ``=`` (system endianness), ``<`` (little-endian),
        and ``>`` (big-endian).

    Returns
    -------
    int
        The 16-bit unsigned integer.

    """

    return struct.unpack("=H", data_to_string([data], endianness=endianness))[0]


def data_to_uint32(data: tuple[int, int], **kwargs) -> int:
    """Converts a tuple of two 16-bit unsigned integers to a 32-bit unsigned integer.

    Parameters
    ----------
    data
        A tuple of two 16-bit unsigned integers.
    kwargs
        Additional arguments to pass to `.data_to_string`.

    Returns
    -------
    int
        The 32-bit unsigned integer.

    """

    return struct.unpack("=I", data_to_string(data, **kwargs))[0]


def data_to_int32(data: tuple[int, int], **kwargs) -> int:
    """Converts a tuple of two 16-bit unsigned integers to a 32-bit signed integer.

    Parameters
    ----------
    data
        A tuple of two 16-bit unsigned integers.
    kwargs
        Additional arguments to pass to `.data_to_string`.

    Returns
    -------
    int
        The 32-bit signed integer.

    """

    return struct.unpack("=i", data_to_string(data, **kwargs))[0]


def data_to_float32(data: tuple[int, int], **kwargs) -> float:
    """Converts a tuple of two 16-bit unsigned integers to a 32-bit float.

    Parameters
    ----------
    data
        A tuple of two 16-bit unsigned integers.
    kwargs
        Additional arguments to pass to `.data_to_string`.

    Returns
    -------
    float
        The 32-bit float.

    """

    return struct.unpack("=f", data_to_string(data, **kwargs))[0]
