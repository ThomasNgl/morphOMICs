"""TMD package.

A python package for the topological analysis of neurons.
"""

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

import importlib.metadata
from morphomics import tmd  # noqa

from morphomics.tmd import utils  # noqa
from morphomics.tmd.io import io  # noqa
from morphomics.tmd.Neuron import Neuron  # noqa
from morphomics.tmd.Population import Population  # noqa
from morphomics.tmd.Soma import Soma  # noqa
from morphomics.tmd.Topology import analysis  # noqa
from morphomics.tmd.Topology import distances  # noqa
from morphomics.tmd.Topology import methods  # noqa
from morphomics.tmd.Topology import statistics  # noqa
from morphomics.tmd.Topology import vectorizations  # noqa
from morphomics.tmd.Tree import Tree  # noqa

#__version__ = importlib.metadata.version("TMD")
