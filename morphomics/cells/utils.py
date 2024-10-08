"""Contains all the commonly used functions and data useful for multiple tmd modules."""

# Copyright (C) 2022  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

term_dict = {"x": 0, "y": 1, "z": 2}

# Definition of tree types
TYPE_DCT = {"soma": 1, "basal": 3, "apical": 4, "axon": 2, "glia": 7}

SOMA_TYPE = 1

class LoadNeuronError(Exception):
    """
    Captures the exception of failing to load a single neuron
    """

class TmdError(Exception):
    """Specific exception raised by TMD."""
