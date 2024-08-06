"""
Python module that contains the functions
about reading and writing files.
"""
from __future__ import print_function

import os, glob
import numpy as np
import re
import pandas as _pd
from scipy import sparse as sp
from scipy.sparse import csgraph as cs
from operator import itemgetter
from morphomics.utils import save_obj

# The following codes were adapted from TMD:
# https://github.com/BlueBrain/TMD
from morphomics.tmd.io.swc import SWC_DCT
from morphomics.tmd.io.swc import read_swc, swc_to_data


class LoadNeuronError(Exception):
    """
    Captures the exception of failing to load a single neuron
    """



def read_swc(file_path, line_delimiter="\n"):
    """Load a swc file containing a list of sections, into a 'Data' format."""
    # Read all data from file.
    try:
        assert file_path.endswith((".swc"))
    except AssertionError:
        raise Warning("{} is not a valid swc file".format(file_path))
    except LoadNeuronError:
        return np.nan
    with open(file_path, "r", encoding="utf-8") as f:
        read_data = f.read()

    # Split data per lines
    split_data = read_data.split(line_delimiter)

    # Clean data from comments and empty lines
    split_data = [a for a in split_data if "#" not in a]
    split_data = [a for a in split_data if a != ""]

    return np.array(split_data)


def swc_to_data(data_swc):
    """Transform swc to np.array to be used in make_tree."""
    expected_data = re.compile(
        r"^\s*([-+]?\d*\.\d+|[-+]?\d+)"
        r"\s*([-+]?\d*\.\d+|[-+]?\d+)\s"
        r"*([-+]?\d*\.\d+|[-+]?\d+)\s*"
        r"([-+]?\d*\.\d+|[-+]?\d+)\s*"
        r"([-+]?\d*\.\d+|[-+]?\d+)\s*"
        r"([-+]?\d*\.\d+|[-+]?\d+)\s*"
        r"([-+]?\d*\.\d+|[-+]?\d+)\s*$"
    )

    data = []

    for dpoint in data_swc:
        if expected_data.match(dpoint.replace("\r", "")):
            segment_point = np.array(
                expected_data.match(dpoint.replace("\r", "")).groups(), dtype=float
            )

            # make the radius diameter
            segment_point[SWC_DCT["radius"]] = 2.0 * segment_point[SWC_DCT["radius"]]

            data.append(segment_point)

    return np.array(data)


def get_infoframe(
    folder_location,
    extension=".swc",
    filtration_function="radial_distances",
    conditions=[],
):
    """Loads all data contained in input directory that ends in `extension`.

    Args:
        folder_location (string): the path to the main directory which contains .swc files
        extension (str, optional): last strings of the .swc files. NLMorphologyConverter results have "nl_corrected.swc" as extension. Defaults to ".swc".
        if .swc files are arranged in some pre-defined hierarchy:
        conditions (list of strings): list encapsulating the folder hierarchy in folder_location

    Returns:
        DataFrame: dataframe containing conditions, 'file_name', 'file_path' and 'neuron'
    """

    print("You are now loading the 3D reconstructions (.swc files) from this folder: \n%s\n"%folder_location)
    
    assert filtration_function in [
        "radial_distances",
        "path_distances",
    ], "Currently, TMD is only implemented with either radial_distances or path_distances"

    # get all the file paths in folder_location
    filepaths = glob.glob(
        "%s%s/*%s" % (folder_location, "/*" * len(conditions), extension)
    )
    # convert the filepaths to array for metadata
    file_info = np.array(
        [_files.replace(folder_location, "").split("/")[1:] for _files in filepaths]
    )

    # create the dataframe for the population of cells
    info_frame = _pd.DataFrame(data=file_info, columns=conditions + ["file_name"])
    info_frame["file_path"] = filepaths
    
    print("Found %d files..." % len(filepaths))
    # print a sample of file names
    nb_files = len(filepaths)
    if nb_files > 0:
        print("Sample filenames:")
        for _ii in range(min(5, nb_files)): print(filepaths[_ii])
        print(" ")
    else:
        print("There are no files in folder_location! Check the folder_location in parameters file or the path to the parameters file.")

    return info_frame

