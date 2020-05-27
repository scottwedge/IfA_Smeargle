"""
This contains the functions required for making effective subframes; usually
by extracting and subtracting subsets of frames and normalizing over some 
time.
"""

import copy
import os


import numpy as np
import numpy.ma as np_ma

import IfA_Smeargle.core as core


def subframe_by_endpoints(data_array, start_chunk, end_chunk, 
                          average_method='median', frame_exposure_time=None):
    """ This function reads a fits file and computes its end section values.

    This function reads in a fits file of 3 dimensions, averaging some 
    top chunk and bottom chunk of their "temporal" axis.

    If there is no temporal axis, this program raises an error.
    
    Parameters
    ----------
    data_array : ndarray
        The data array that the average will be taken from.
    start_chunk : array-like
        The exact range of frames from the beginning that will be averaged as
        per the averaging method.
    end_chunk : array-like
        The exact range of frames from the end that will be averaged as
        per the averaging method.
    average_method : string (optional)
        The current available methods for determining the file size that is
        proper. Defaults to median.

            * 'mean' : This takes the mean along the frames of each chunk
            * 'median' : This takes the median along the frames of each chunk.
                         Even sets use the mean of the middle most two values.
    frame_exposure_time : float
        The duration, per frame (in seconds), of each exposure. This is 
        really not used in this function, but, it is added for uniformity with
        the other functions.

    Returns
    -------
    final_data : ndarray
        The final data array of the median-ed frames as desired.
    """

    # Evaluate the averaging based on the median or mean. The divisor is 
    # normally meant for the time.
    if (average_method == 'mean'):
        final_data = _primary_mean_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=1)
    elif (average_method == 'median'):
        final_data = _primary_median_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=1)
    return final_data

def subframe_by_endpoints_per_second(data_array, start_chunk, end_chunk,frame_exposure_time, 
                                     average_method='median'):
    """ This function reads a fits file and computes its end section values,
    normalizing per second.

    This function reads in a fits file of 3 dimensions, averaging some 
    top chunk and bottom chunk of their "temporal" axis, normalizing
    and dividing over a timespan. The time is measured in seconds.

    If there is no temporal axis, this program raises an error.
    
    Parameters
    ----------
    data_array : ndarray
        The data array that the average will be taken from.
    start_chunk : array-like
        The exact range of frames from the beginning that will be averaged as
        per the averaging method.
    end_chunk : array-like
        The exact range of frames from the end that will be averaged as
        per the averaging method.
    frame_exposure_time : float
        The duration, per frame (in seconds), of each exposure. This is 
        really not used in this function, but, it is added for uniformity with
        the other functions.
    average_method : string (optional)
        The current available methods for determining the file size that is
        proper. Defaults to median.

            * 'mean' : This takes the mean along the frames of each chunk
            * 'median' : This takes the median along the frames of each chunk.
                         Even sets use the mean of the middle most two values.
    """
    # Calculating the divisor: the integration time.
    integration_time = (frame_exposure_time 
                        * (np.median(end_chunk) - np.median(start_chunk)))

    # Evaluate the averaging based on the median or mean.
    if (average_method == 'mean'):
        final_data = _primary_mean_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=integration_time)
    elif (average_method == 'median'):
        final_data = _primary_median_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=integration_time)
    return final_data

def subframe_by_endpoints_per_kilosecond(data_array, start_chunk, end_chunk, 
                          frame_exposure_time, average_method='median'):
    """ This function reads a fits file and computes its end section values,
    normalizing per second.

    This function reads in a fits file of 3 dimensions, averaging some 
    top chunk and bottom chunk of their "temporal" axis, normalizing
    and dividing over a timespan. The time is measured in seconds.This
    is basically a wrapper function around the per second version.

    If there is no temporal axis, this program raises an error.
    
    Parameters
    ----------
    data_array : ndarray
        The data array that the average will be taken from.
    start_chunk : array-like
        The exact range of frames from the beginning that will be averaged as
        per the averaging method.
    end_chunk : array-like
        The exact range of frames from the end that will be averaged as
        per the averaging method.
    frame_exposure_time : float
        The duration, per frame (in seconds), of each exposure. This is 
        really not used in this function, but, it is added for uniformity with
        the other functions.
    average_method : string (optional)
        The current available methods for determining the file size that is
        proper. Defaults to median.

            * 'mean' : This takes the mean along the frames of each chunk
            * 'median' : This takes the median along the frames of each chunk.
                         Even sets use the mean of the middle most two values.
    """
    # Calculating the divisor: the integration time in seconds.
    integration_time = (frame_exposure_time 
                        * (np.median(end_chunk) - np.median(start_chunk)))
    # However, this function desires kiloseconds, therefore, integration time 
    # should be factored down.
    integration_time_kilosecond = integration_time / 1000.0

    # Evaluate the averaging based on the median or mean.
    if (average_method == 'mean'):
        final_data = _primary_mean_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=integration_time_kilosecond)
    elif (average_method == 'median'):
        final_data = _primary_median_function(data_array=data_array,
                                              start_chunk=start_chunk, end_chunk=end_chunk,
                                              divisor=integration_time_kilosecond)
    return final_data


def _primary_mean_function(*args, **kwargs):
    """ For means. """
    return _primary_combination_function(combining_function=core.math.ifas_masked_mean, 
                                         *args, **kwargs)

def _primary_median_function(*args, **kwargs):
    """ For medians. """
    return _primary_combination_function(combining_function=core.math.ifas_masked_median, 
                                         *args, **kwargs)

def _primary_combination_function(data_array, start_chunk, end_chunk, 
                                  divisor, combining_function):
    """ This function takes a 3D array and computes its end section values.

    This function reads in an array of 3 dimensions, averaging some 
    top chunk and bottom chunk of their "temporal" axis.

    If there is no temporal axis, this program raises an error.
    
    Parameters
    ----------
    data_array : ndarray
        This is the data array that will be modified, or at least have its
        values calculated from.
    start_chunk : array-like
        The exact range of frames from the beginning that will be median-ed.
    end_chunk : array-like
        The exact range of frames from the bottom that will be median-ed.
    divisor : float
        An value by which the data frame will be divided by to either act as 
        a normalization or a per-unit factor.
    combining_function : function
        The function that would be used to combine the arrays.

    Returns
    -------
    final_data : ndarray
        The final data array of the median-ed frames as desired.
    """

    # Check and adapt for a masked array.
    if (np_ma.isMaskedArray(data_array)):
        raw_data = np_ma.getdata(data_array)
        data_mask = np_ma.getmask(data_array)
    else:
        raw_data = np.array(data_array)
        data_mask = None

    # Check for too many or too little dimensions; it is important as the 
    # array shape of data is assumed.
    if (raw_data.ndim == 0):
        raise core.error.InputError("There is no data to analyze as the array is zero "
                                    "dimensional.")
    elif (raw_data.ndim <= 2):
        raise core.error.InputError("The data of the input fits file does not have any "
                                    "wavelength or temporal axis; to collapse spatially would "
                                    "be incorrect.")
    elif (raw_data.ndim > 3):
        core.error.ifas_warning(core.error.InputWarning,
                                ("The number of dimensions in the data array is greater "
                                 "than 3, it is assumed that the 0th axis is the temporal "
                                 "axis."))

    # Allow for swapped, but valid ranges.
    start_chunk = np.sort(start_chunk)
    end_chunk = np.sort(end_chunk)
    # Check if the chunks overlap, if they do, this is a problem.
    if (start_chunk[1] >= end_chunk[0]):
        core.error.ifas_error(core.error.ConfigurationError,
                              ("The end of the start_chunk is after the start of the "
                              "end_chunk. The overlap is improper and should be fixed."))
    # It is unnatural, but not forbidden, to have differing top and bottom 
    # chunk range values.
    if (start_chunk.ptp() != end_chunk.ptp()):
        core.error.ifas_warning(core.error.ReductionWarning,
                                ("The size of the start chunk and end chunk are "
                                 "different sizes, this is unusual but acceptable."))


    # Calculate the combinations. The custom combinations functions are needed 
    # to handle both nans and masked arrays. Keywords are strictly used as
    # a weak double check that the proper function is used.
    start_combinations = combining_function(array=raw_data[start_chunk[0]:start_chunk[-1]],axis=0)
    end_combinations = combining_function(array=raw_data[end_chunk[0]:end_chunk[-1]],axis=0)

    # Subtracting and normalizing over the time span, starting and ending
    # at respective midpoints; integer multiplication/division is required  
    # because of the discrete nature of frames.
    final_raw_data = (end_combinations - start_combinations) / divisor

    # Reapply the mask if there was a mask.
    if (data_mask is not None):
        final_data = np_ma.array(data=final_raw_data, mask=data_mask)
    else:
        final_data = np.array(final_raw_data)

    return final_data


def _format_subframe_config(config):
    """ The scripting version of `all subframe`. This function
    applies the inner function to either the entire directory or a single 
    file.
    
    Parameters
    ----------
    config : ConfigObj
        The configuration object that is to be used for this function.

    Returns
    -------
    data_directory : string
        The data directory.
    start_chunks : ndarray
        The starting chunks to process.
    end_chunks : ndarray
        The ending chunks to process.
    average_method : string
        The method that will be used to average.
    frame_exposure_time : float
        The number of seconds that it takes for a frame to be taken.
    """

    # Extract the configuration parameters.
    data_directory = core.config.extract_configuration(config_object=config, 
                                                       keys=['data_directory'])
    start_chunks = core.config.extract_configuration(config_object=config, 
                                                     keys=['subframe','start_chunks'])
    end_chunks = core.config.extract_configuration(config_object=config, 
                                                   keys=['subframe','end_chunks'])
    average_method = core.config.extract_configuration(config_object=config,
                                                       keys=['subframe','average_method'])
    frame_exposure_time = core.config.extract_configuration(
        config_object=config, keys=['subframe','frame_exposure_time'])

    # Force both the chunks to be in array format for processing.
    start_chunks = np.array(start_chunks)
    end_chunks = np.array(end_chunks)

    # If both are one dimensional, assume matching pairs, else, populate 
    # unless they are the same dimension size or raise for non-equal sizes.
    if (start_chunks.ndim == end_chunks.ndim):
        # Assume valid procedure and that these arrays are parallel. But
        # basic checks are nice.
        if (start_chunks.shape != end_chunks.shape):
            raise core.error.ConfigurationError("Both the start chunk and the end chunk are of "
                                                "same dimension but different shape.")
        if (start_chunks.size != end_chunks.size):
            raise core.error.ConfigurationError("Both the start chunk and the end chunk are of "
                                                "same dimension but different size.")
        # They also need to be 2D.
        if ((start_chunks.ndim == 1) and (end_chunks.ndim == 1)):
            start_chunks = np.array([start_chunks])
            end_chunks = np.array([end_chunks])
        else:
            # it is assumed that they are fine.
            pass
    elif (start_chunks.ndim == 1) and (1 <= end_chunks.ndim):
        # The start chunks are the minor here and should duplicate where
        # needed to match.
        start_chunks = np.tile(start_chunks, (end_chunks.shape[0],1))
    elif (end_chunks.ndim == 1) and (1 <= start_chunks.ndim):
        # The end chunks are the minor here and should duplicate where
        # needed to match.
        end_chunks = np.tile(end_chunks, (start_chunks.shape[0],1))
    else:
        raise core.error.ConfigurationError("The start and end chunks are not in a format that "
                                            "can be understood. The simple validation checking "
                                            "is not sufficient to prevent this. Use a "
                                            "multi-dimensional array for multiple subarrays.")

    # Return the configurations.
    return data_directory, start_chunks, end_chunks, average_method, frame_exposure_time

# The scripts of the subframe calculations.

def script_subframe_endpoints(config):
    """ The scripting version of `subframe_by_endpoints`. This function applies the
    rename to the entire directory. It also adds the tags to the header file
    of each fits.
    
    Parameters
    ----------
    config : ConfigObj
        The configuration object that is to be used for this function.

    Returns
    -------
    None
    """

    # Obtain the configuration parameters.
    data_directory, start_chunks, end_chunks, average_method, frame_exposure_time = \
        _format_subframe_config(config=config)

    # If the directory is really one file.
    if (os.path.isfile(data_directory)):
        # Force into list for convience.
        data_files = list([data_directory])
    else:
        # Assume it is a valid data directory.
        data_files = core.io.get_fits_filenames(data_directory=data_directory, recursive=False)

    # Loop over all files present and apply the procedure...
    core.error.ifas_info("Subframes are being created by subtracting the {method} of two sets of "
                         "frames, {start_set} and {end_set}, from the fits files in {data_dir}. "
                         "The frame exposure is {frame_time}; there is no normalization by time."
                         .format(method=average_method, start_set=start_chunks, end_set=end_chunks,
                                 data_dir=data_directory, frame_time=frame_exposure_time))
    for filedex in data_files:
        # Also, loop over all desired subframes that should be made.
        for substartdex, subenddex in zip(start_chunks, end_chunks):
            # Load the fits file.
            hdul_file, hdu_header, hdu_data = core.io.read_fits_file(file_name=filedex, 
                                                                     extension=0, silent=False)
            # Process a copy of the data based on the current subframes.
            subframe_data = subframe_by_endpoints(data_array=copy.deepcopy(hdu_data), 
                                                  start_chunk=substartdex, end_chunk=subenddex,
                                                  frame_exposure_time=frame_exposure_time,
                                                  average_method=average_method)
            # Create and write the file out with added terms.
            dir, file, ext = core.strformat.split_pathname(pathname=filedex)
            new_file = ''.join([file, 
                                core.strformat.format_slice_appending_name(
                                    reference_frame=substartdex, averaging_frame=subenddex), 
                                ext])
            new_path = os.path.join(dir, new_file)

            # Write the file to disk.
            core.io.write_fits_file(file_name=new_path, hdu_header=hdu_header, 
                                    hdu_data=subframe_data, hdu_object=None,
                                    save_file=True, overwrite=False, silent=False)
            # Add the subframe data to the header file of the new file. This
            # may add IO overhead, but it ensures that headers don't get 
            # messed up by odd references.
            headers = {'SUBFRM_F':'subframe_endpoints',
                       'FRAVGMTH':average_method,
                       'STRTFRMS':str(substartdex),
                       'ENDFRMS':str(subenddex),
                       'FRM_EXPO':frame_exposure_time}
            comments = {'SUBFRM_F':'The subframing method used to make this.',
                       'FRAVGMTH':'The method used to average chunks.',
                       'STRTFRMS':'The frame range of the start chunk.',
                       'ENDFRMS':'The frame range of the end chunk.',
                       'FRM_EXPO':'The frame exposure, in seconds.'}
            core.io.append_astropy_header_card(file_name=new_path, 
                                            header_cards=headers,
                                            comment_cards=comments)

    # Finished, hopefully.
    return None

def script_subframe_endpoints_per_second(config):
    """ The scripting version of `subframe_by_endpoints_per_second`. This function applies the
    rename to the entire directory. It also adds the tags to the header file
    of each fits.
    
    Parameters
    ----------
    config : ConfigObj
        The configuration object that is to be used for this function.

    Returns
    -------
    None
    """

    # Obtain the configuration parameters.
    data_directory, start_chunks, end_chunks, average_method, frame_exposure_time = \
        _format_subframe_config(config=config)

    # If the directory is really one file.
    if (os.path.isfile(data_directory)):
        # Force into list for convience.
        data_files = list([data_directory])
    else:
        # Assume it is a valid data directory.
        data_files = core.io.get_fits_filenames(data_directory=data_directory, recursive=False)

    # Loop over all files present and apply the procedure...
    core.error.ifas_info("Subframes are being created by subtracting the {method} of two sets of "
                         "frames, {start_set} and {end_set}, from the fits files in {data_dir}. "
                         "The frame exposure is {frame_time}; the normalization is per second."
                         .format(method=average_method, start_set=start_chunks, end_set=end_chunks,
                                 data_dir=data_directory, frame_time=frame_exposure_time))
    for filedex in data_files:
        # Also, loop over all desired subframes that should be made.
        for substartdex, subenddex in zip(start_chunks, end_chunks):
            # Load the fits file.
            hdul_file, hdu_header, hdu_data = core.io.read_fits_file(file_name=filedex, 
                                                                     extension=0, silent=False)
            # Process a copy of the data based on the current subframes.
            subframe_data = subframe_by_endpoints_per_second(
                data_array=copy.deepcopy(hdu_data),
                start_chunk=substartdex, end_chunk=subenddex,
                frame_exposure_time=frame_exposure_time,
                average_method=average_method)
            # Create and write the file out with added terms.
            dir, file, ext = core.strformat.split_pathname(pathname=filedex)
            new_file = ''.join([file, 
                                core.strformat.format_slice_appending_name(
                                    reference_frame=substartdex, averaging_frame=subenddex), 
                                ext])
            new_path = os.path.join(dir, new_file)

            # Write the file to disk.
            core.io.write_fits_file(file_name=new_path, hdu_header=hdu_header, 
                                    hdu_data=subframe_data, hdu_object=None,
                                    save_file=True, overwrite=False, silent=False)
            # Add the subframe data to the header file of the new file. This
            # may add IO overhead, but it ensures that headers don't get 
            # messed up by odd refrences.
            core.io.append_astropy_header_card(file_name=new_path, 
                                            header_cards={'SUBFRM_F':'subframe_endpoints',
                                                          'FRAVGMTH':average_method,
                                                          'STRTFRMS':str(substartdex),
                                                          'ENDFRMS':str(subenddex),
                                                          'FRM_EXPO':frame_exposure_time})

    # Finished, hopefully.
    return None

def script_subframe_endpoints_per_kilosecond(config):
    """ The scripting version of `subframe_by_endpoints_per_kilosecond`. This function applies the
    rename to the entire directory. It also adds the tags to the header file
    of each fits.
    
    Parameters
    ----------
    config : ConfigObj
        The configuration object that is to be used for this function.

    Returns
    -------
    None
    """

    # Obtain the configuration parameters.
    data_directory, start_chunks, end_chunks, average_method, frame_exposure_time = \
        _format_subframe_config(config=config)

    # If the directory is really one file.
    if (os.path.isfile(data_directory)):
        # Force into list for convience.
        data_files = list([data_directory])
    else:
        # Assume it is a valid data directory.
        data_files = core.io.get_fits_filenames(data_directory=data_directory, recursive=False)

    # Loop over all files present and apply the procedure...
    core.error.ifas_info("Subframes are being created by subtracting the {method} of two sets of "
                         "frames, {start_set} and {end_set}, from the fits files in {data_dir}. "
                         "The frame exposure is {frame_time}; the normalization is per kilosecond."
                         .format(method=average_method, start_set=start_chunks, end_set=end_chunks,
                                 data_dir=data_directory, frame_time=frame_exposure_time))
    for filedex in data_files:
        # Also, loop over all desired subframes that should be made.
        for substartdex, subenddex in zip(start_chunks, end_chunks):
            # Load the fits file.
            hdul_file, hdu_header, hdu_data = core.io.read_fits_file(file_name=filedex, 
                                                                     extension=0, silent=False)
            # Process a copy of the data based on the current subframes.
            subframe_data = subframe_by_endpoints_per_kilosecond(
                data_array=copy.deepcopy(hdu_data),
                start_chunk=substartdex, end_chunk=subenddex,
                frame_exposure_time=frame_exposure_time,
                average_method=average_method)
            # Create and write the file out with added terms.
            dir, file, ext = core.strformat.split_pathname(pathname=filedex)
            new_file = ''.join([file, 
                                core.strformat.format_slice_appending_name(
                                    reference_frame=substartdex, averaging_frame=subenddex), 
                                ext])
            new_path = os.path.join(dir, new_file)

            # Write the file to disk.
            core.io.write_fits_file(file_name=new_path, hdu_header=hdu_header, 
                                    hdu_data=subframe_data, hdu_object=None,
                                    save_file=True, overwrite=False, silent=False)
            # Add the subframe data to the header file of the new file. This
            # may add IO overhead, but it ensures that headers don't get 
            # messed up by odd refrences.
            core.io.append_astropy_header_card(file_name=new_path, 
                                            header_cards={'SUBFRM_F':'subframe_endpoints',
                                                          'FRAVGMTH':average_method,
                                                          'STRTFRMS':str(substartdex),
                                                          'ENDFRMS':str(subenddex),
                                                          'FRM_EXPO':frame_exposure_time})

    # Finished, hopefully.
    return None