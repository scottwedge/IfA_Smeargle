"""
The purpose of this line is for the storage of configuration elements that are used on all 
other lines. The configuration of the entire Smeargle module is read, written, and used from
here.

Though technically a meta-line, as it is a full line in itself, it is not considered to fit 
in the meta functionality.
"""

import copy
import pickle

from IfA_Smeargle import meta

from IfA_Smeargle.yankee import configuration_classes as conclass

# Pulling deeper functions into the light.
from IfA_Smeargle.yankee.configuration_classes.BaseConfig_file \
    import read_config_file, write_config_file

class SmeargleConfig(conclass.BaseConfig):
    """ Configuration class of the entire Smeargle pipeline and other properties.
    
    Each different array configuration must have its own reduction method. The purpose of this
    class is to be an organized collection of ALL configuration options possible. That is, 
    this class is read by the main pipeline and all other functions are created.

    Within each argument exists another configuration class specific to each of the Smeargle
    lines. They are defined in their appropriate files. 

    Arguments
    ---------
    EchoConfig : Configuration class
        The configuration class for the ECHO line.
    HotelConfig : Configuration class
        The configuration class for the HOTEL line.
    YankeeConfig : Configuration class
        The configuration class for the YANKEE line.

    BaseConfig : Configuration class
        The base configuration class, should generally not be used. 
    """


    BravoConfig = conclass.BravoConfig()
    EchoConfig = conclass.EchoConfig()
    HotelConfig = conclass.HotelConfig()
    YankeeConfig = conclass.YankeeConfig()




