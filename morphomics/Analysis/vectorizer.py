import numpy as np
import concurrent.futures
from functools import partial

from tmd.Topology import vectorizations

from morphomics.utils import norm_methods

class Vectorizer(object):
    
    def __init__(self, tmd, vect_parameters):
        """
        Initializes the Vectorizer instance.

        Parameters
        ----------
        tmd (list of list of pairs): the barcodes of trees
        parameters (dict): contains the parameters for each protocol that would be run
                            vect_parameters = {'vect_method_1 : { parameter_1_1: x_1_1, ..., parameter_1_n: x_1_n},
                                            ...
                                            'vect_method_m : { parameter_m_1: x_m_1, ..., parameter_m_n: x_m_n}
                                        } 

        Returns
        -------
        An instance of Vectorizer.
        """
        self.tmd = tmd
        self.vect_parameters = vect_parameters
        
    ## Private
    def _get_persistence_image_list(self, 
                                    norm_factor = 1,
                                    xlim = None,
                                    ylim = None,
                                    bw_method = None,
                                    weights = None,
                                    resolution = 100,
                                    parallel = False):
        
        # Get the persistence image of each barcode.
        if not parallel:
            pi_list = [vectorizations.persistence_image_data(ph = barcode, 
                                                            norm_factor = norm_factor,
                                                            xlim = xlim,
                                                            ylim = ylim,
                                                            bw_method = bw_method,
                                                            weights = weights,
                                                            resolution = resolution)
                        for barcode in self.tmd]

        else:
            partial_compute = partial(vectorizations.persistence_image_data,
                                            norm_factor = norm_factor,
                                            xlim = xlim,
                                            ylim = ylim,
                                            bw_method = bw_method,
                                            weights = weights,
                                            resolution = resolution)
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                pi_list = executor.map(partial_compute,
                                        self.tmd)
                pi_list = list(pi_list)
        
        return pi_list


    def _get_curve_vectorization_list(self,
                        curve_method = vectorizations.betti_curve,
                        t_list = None,
                        resolution = 1000,
                        parallel = False):
        
        # Get the curve vectorization for each barcode.
        if not parallel:
            c_list = []
            for barcode in self.tmd:
                c, _ = curve_method(barcode,
                                    t_list,
                                    resolution)
                c_list.append(c)
        else:
            partial_compute = partial(curve_method,
                                        bins = t_list,
                                        num_bins = resolution)
            
            with concurrent.futures.ProcessPoolExecutor() as executor:
                c_list = executor.map(partial_compute,
                                        self.tmd)
                c_list = list(c_list)
        
        return c_list
    

    def _curve_vectorization(self, 
                             curve_method,
                             curve_params):
        '''General method to compute vectorization for curve methods.

        Parameters
        ----------
        curve_method (method): the actual curve like vectorization method, the method has 2 parameters: (t_list, resolution).
                                example: _lifespan_curve.
        curve_params (dict): the parameters for the curve vectorization:
                            -rescale_lims (bool): True: adapt the boundaries of the barcode for each barcode
                                                False: choose the widest boundaries that include all barcodes 
                            -xlims (pair of double): the boundaries
                            -resolution (int): number of sub intervals between boudaries .aka. size of the output vector 
                            -norm_method (str): the method to normalize the vector

        Returns
        -------
        A numpy array of shape (nb barcodes, resolution) i.e. a vector for each barcode. 
        '''
        
        rescale_lims = curve_params["rescale_lims"]
        xlims = curve_params["xlims"]
        resolution = curve_params["resolution"]
        norm_method = curve_params["norm_method"]
        parallel = curve_params["parallel"]

        # Define the sub intervals of the curve
        if rescale_lims:
            t_list = None
        else:
            # get the birth and death distance limits for the curve
            _xlims, _ylims = vectorizations.get_limits(self.tmd)
            if xlims is None or xlims == "None":
                xlims = [np.min([_xlims[0], _ylims[0]]), np.max([_xlims[1], _ylims[1]])]
            t_list = np.linspace(xlims[0], xlims[1], resolution)
       
        # Get the curve
        curve_list = self._get_curve_vectorization_list(curve_method = curve_method, 
                                               t_list = t_list, 
                                               resolution = resolution,
                                               parallel = parallel)
        # normalize the curve
        curves = []
        for curve in curve_list:
            if len(curve) > 0:
                norm = norm_methods[norm_method](curve)
                curves.append(curve / norm)
            else:
                curves.append(np.nan)

        return np.array(curves)


    def _lifespan_curve(self,
                        barcode,
                        bins = None,
                        num_bins = 1000):
        # The vectorization called lifespan curve.
        # Returns the lifespan curve of a barcode and the sub intervals on which it was computed.
        if bins is None:
            bins = np.linspace(np.min(barcode), np.max(barcode), num_bins)
        else:
            bins = bins

        bar_differences = np.diff(barcode)
        lifespan_c = [np.sum([
                            float(bar_diff) if vectorizations._index_bar(bar, t) else 0.
                            for bar, bar_diff in zip(barcode, bar_differences)
                            ])
                        for t in bins
                    ]
        return lifespan_c, bins


    ## Public
    def persistence_image(self):
        '''This function takes information about barcodes, calculates persistence images based on specified
        parameters, and returns an array of images.
        
        Parameters
        ----------
            The 'rescale_lims' is a boolean. 
                True: adapt the boundaries of the barcode for each barcode
                False: choose the widest boundaries that include all barcodes 
            The `xlims` parameter used to specify the
        birth and death distance limits for the persistence images. If `xlims` is not provided as an
        argument when calling the function, it will default to the birth and death distance limits
        calculated from
        ylims
            The `ylims` parameter is used to specify the
        limits for the y-axis in the persistence images. If `ylims` is not provided as an argument when
        calling the function, it will default to `None` and then be set based
        bw_method
            The `bw_method` parameter is used to specify the
        bandwidth method for kernel density estimation when generating persistence images. It controls the
        smoothness of the resulting images by adjusting the bandwidth of the kernel used in the estimation
        process. Different bandwidth methods can result
        norm_method, optional
            The `norm_method` parameter specifies the method
        used for normalizing the persistence images. The default value is set to "sum", which means that the
        images will be normalized by dividing each pixel value by the sum of all pixel values in the image
        barcode_weight
            The `barcode_weight` parameter is used to specify
        weights for each barcode in the calculation of persistence images. If `barcode_weight` is provided,
        it will be used as weights for the corresponding barcode during the calculation. 
           The 'resolution' parameter is an integer that defines the number of pixels in a row and in a column of a persistence image.
           The 'parallel' parameter is a boolean that determines if the vectorizations should be computed in parallel or not.
        
        Returns
        -------
            The function returns a NumPy array of persistence images.
        

        '''

        pi_params = self.vect_parameters["persistence_image"]

        rescale_lims = pi_params["rescale_lims"]
        xlims=pi_params["xlims"]
        ylims=pi_params["ylims"]
        bw_method=pi_params["bw_method"]
        if bw_method == "None":
            bw_method = None
        barcode_weight=pi_params["barcode_weight"]
        if barcode_weight == "None":
            barcode_weight = None
        norm_method=pi_params["norm_method"]
        resolution=pi_params["resolution"]
        flatten = True
        parallel = pi_params["parallel"]

        print("Computing persistence images...")
        
        if rescale_lims:
            xlims, ylims = None, None
        else:
            # get the birth and death distance limits for the persistence images
            _xlims, _ylims = vectorizations.get_limits(self.tmd)
            if xlims is None or xlims == "None":
                xlims = _xlims
            if ylims is None or ylims == "None":
                ylims = _ylims

        pi_list = self._get_persistence_image_list(norm_factor = 1,
                                                    xlim = xlims,
                                                    ylim = ylims,
                                                    bw_method = bw_method,
                                                    weights = barcode_weight,
                                                    resolution = resolution,
                                                    parallel = parallel
                                                )
        if flatten:
            flatten_method = lambda arr: arr.flatten()
        else:
            flatten_method = lambda arr: arr
        
        images = []
        for pi in pi_list:
            if len(pi) > 0:
                pi = flatten_method(pi)
                norm = norm_methods[norm_method](pi)
                images.append( pi / norm)
            else:
                images.append(np.nan)

        print("pi done! \n")
        return np.array(images)
    


    def betti_curve(self):
        ''' Computes the betti curve of each barcode in self.tmd.

        Parameters
        ----------
        betti_params (dict): the parameters for the betti curve vectorization:
                            -rescale_lims (bool): True: adapt the boundaries of the barcode for each barcode
                                                False: choose the widest boundaries that include all barcodes 
                            -xlims (pair of double): the boundaries
                            -resolution (int): number of sub intervals between boudaries .aka. size of the output vector 
                            -norm_method (str): the method to normalize the vector
                            -parallel (bool): determines if the vectorizations should be computed in parallel or not.

        Returns
        -------
        A numpy array of shape (nb barcodes, resolution) i.e. a vector for each barcode. 
        '''
        betti_params = self.vect_parameters["betti_curve"]

        print("Computing betti curves...")

        betti_curves = self._curve_vectorization(curve_params = betti_params,
                                                curve_method = vectorizations.betti_curve)

        print("bc done! \n")

        return betti_curves


    
    def life_entropy_curve(self):
        ''' Computes the life entropy curve of each barcode in self.tmd.

        Parameters
        ----------
        entropy_params (dict): the parameters for the life entropy curve vectorization:
                            -rescale_lims (bool): True: adapt the boundaries of the barcode for each barcode
                                                False: choose the widest boundaries that include all barcodes 
                            -xlims (pair of double): the boundaries
                            -resolution (int): number of sub intervals between boudaries .aka. size of the output vector 
                            -norm_method (str): the method to normalize the vector
                            -parallel (bool): determines if the vectorizations should be computed in parallel or not.

        Returns
        -------
        A numpy array of shape (nb barcodes, resolution) i.e. a vector for each barcode. 
        '''
        entropy_params = self.vect_parameters["life_entropy_curve"]

        print("Computing life entropy curves...")

        life_entropy_curves = self._curve_vectorization(curve_params = entropy_params,
                                                        curve_method = vectorizations.life_entropy_curve)

        print("lec done! \n")

        return life_entropy_curves



    def lifespan_curve(self):
        ''' Computes the life span curve of each barcode in self.tmd.

        Parameters
        ----------
        lifespan_params (dict): the parameters for the life span curve vectorization:
                            -rescale_lims (bool): True: adapt the boundaries of the barcode for each barcode
                                                False: choose the widest boundaries that include all barcodes 
                            -xlims (pair of double): the boundaries
                            -resolution (int): number of sub intervals between boudaries .aka. size of the output vector 
                            -norm_method (str): the method to normalize the vector
                            -parallel (bool): determines if the vectorizations should be computed in parallel or not.

        Returns
        -------
        A numpy array of shape (nb barcodes, resolution) i.e. a vector for each barcode. 
        '''
        lifespan_params = self.vect_parameters["lifespan_curve"]

        print("Computing lifespan curves...")

        lifespan_cuves = self._curve_vectorization(curve_params = lifespan_params,
                                                    curve_method = self._lifespan_curve)
        print("lsc done! \n")
        return lifespan_cuves



    def stable_ranks(self):
        return

    