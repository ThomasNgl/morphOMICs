import warnings
import pandas as pd
import os
from morphomics.new_io import load_swc

class Population:
    """A Population object is a container for Neurons.

    Args:
        name (str): The name of the Population.
        neurons (list[tmd.Neuron.Neuron.Neuron]): A list of neurons to include in the Population.
    """
    def __init__(self, info_frame = None, extension = ".swc",
               cells = None, 
               folder_path = None,
               name = None, 
               conditions = {'Region' : None,
                             'Condition' : None,
                             'Model' : None,
                             'Time' : None,
                             'Sex' : None,
                             'Animal' : None}
                ):
        if name is None:
            self.name =  os.path.basename(folder_path)
        self.folder_path = folder_path
        self.conditions = conditions

        self.cells = pd.Dataframe()
        if info_frame is not None:
            self.cells = info_frame
            # Read the swc files and add them in the column swc_array.

            self.cells['swc_array'] = self.cells['file_path'].apply(lambda file_path: swc_to_data(
                                                                            read_swc(file_path))
                                                                    )
            # Get a column composed of Neuron instances.
            assert filtration_function in [
                "radial_distances",
                "path_distances",
            ], "Currently, TMD is only implemented with either radial_distances or path_distances"

            self.cells['cell'] = self.cells['swc_array'].apply(lambda swc_arr: swc_to_cell(swc_arr)
                                                                    )
        if cells is not None:
            self.cells = pd.concat((self.cells, cells))

    def set_barcodes(self, filtration_function = 'rdial_distances'):
        self.cells['barcodes'] = self.cells['cell'].apply(lambda tree_list: )