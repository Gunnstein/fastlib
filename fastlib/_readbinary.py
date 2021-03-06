#-*- coding: utf-8 -*-
import numpy as np
import re


__all__ = ["ReadFASTBinary", "DataArray", "DataSet"]


LenName = 10  # number of characters per channel name
LenUnit = 10  # number of characters per unit name

FileFmtID = {"WithTime": 1, "WithoutTime": 2}               # File identifiers used in FAST


def fread(file, n, dtype):
    "Reads bytes from a outb file and converts to n number of objects of type dtype"
    o = np.fromfile(file, count=n, dtype=dtype)
    if n == 1:
        ret = o[0]
    else:
        ret = o
    return ret


def ReadFASTBinary(FileName, print_desc_str=False):
    """Read metadata and data from binary FAST files (.outb)

    This implementation is a translated copy of the MATLAB function 
    `ReadFASTbinary` found in the file `ReadFASTBinary.m` distributed
    with FASTv8.16.00a-bjj windows distribution. 
    
    The original function in MATLAB was:
        Authored by Bonnie Jonkman, National Renewable Energy Laboratory  
        (c) 2012, 2013 National Renewable Energy Laboratory.

    Arguments
    ---------
    FileName : str
        Name of the binary FAST output file.
    print_desc_str : Optional[bool]
        Print the description string after reading the metadata and before
        attempting to read the time and channel data.
    
    Returns
    -------
    Channels : 2darray
        First column is time, all other columns are data channels.
    ChanName : list[str]
        Channel names of the columns in the 2darray `Channels`
    ChanUnit : list[str]
        Channel units of the oclumns in the 2darray `Channels`
    FileID : int
        A constant defining whether the time is stored in the output 
        file or generated from a startup time and an increment. 
        If time is stored in the output file this may indicate 
        non-constant time step. {1: WithTime, 2:WithoutTime}.
    DescStr : str
        Description string from the output file.
    """
    with open(FileName, 'rb') as fid:

        FileID = fread(fid, 1, np.int16)                    # FAST output file format, INT(2)

        NumOutChans = fread(fid, 1, np.int32)               # The number of output channels, INT(4)
        NT = fread(fid, 1, np.int32)                        # The number of time steps, INT(4)

        if FileID == FileFmtID["WithTime"]:                 
            TimeScl = fread(fid, 1, np.float64)             # The time slopes for scaling, REAL(8)
            TimeOff = fread(fid, 1, np.float64)             # The time offsets for scaling, REAL(8)
        else:
            TimeOut1 = fread(fid, 1, np.float64)            # The first time in the time series, REAL(8)
            TimeIncr = fread(fid, 1, np.float64)            # The time increment, REAL(8)

        ColScl = fread(fid, NumOutChans, np.float32)        # The channel slopes for scaling, REAL(4)
        ColOff = fread(fid, NumOutChans, np.float32)        # The channel offsets for scaling, REAL(4)

        LenDesc = fread(fid, 1, np.int32)                   # The number of characters in the description string, INT(4)
        DescStrASCII = fread(fid, LenDesc, np.uint8)        # DescStr converted to ASCII

        DescStr = "".join(map(chr, DescStrASCII))


        ChanName = []                                       # initialize the ChanName array
        for __ in range(NumOutChans+1):
            ChanNameASCII = fread(fid, LenName, np.uint8)   # ChanName converted to numeric ASCII
            ChanName.append("".join(map(chr, ChanNameASCII)).strip())

        ChanUnit = []                                       # initialize the ChanUnit array
        for __ in range(NumOutChans+1):
            ChanUnitASCII = fread(fid, LenUnit, np.uint8)   # ChanUnit converted to numeric ASCII
            ChanUnit.append("".join(map(chr, ChanUnitASCII)).strip())

        if print_desc_str:
            print("Reading from the file ", FileName, "with heading: ")
            print('    "', DescStr, '".')

        #----------------------------
        # get the channel time series
        #----------------------------

        nPts = NT * NumOutChans                             # number of data points in the file            
        Channels = np.zeros((NT, NumOutChans+1), dtype=np.float32) # output channels (including time in column 1)

        if FileID == FileFmtID["WithTime"]:
            PackedTime = fread(fid, NT, np.int32)           # read the time data
            
        PackedData = fread(fid, nPts, np.int16)             # read the channel data

    #-------------------------------------
    # Scale the packed binary to real data
    #-------------------------------------
    Channels[:, 1:] = (PackedData.reshape((NT, NumOutChans)) - ColOff) / ColScl

    if FileID == FileFmtID["WithTime"]:
        Channels[:, 0] = (PackedTime - TimeOff) / TimeScl
    else:
        Channels[:, 0] = TimeOut1 + TimeIncr * np.arange(0, NT, 1, dtype=np.float32)

    return Channels, ChanName, ChanUnit, FileID, DescStr


class DataArray(np.ndarray):
    """DataArray is a numpy.ndarray with metadata for FAST channels.

    FAST data channels has a channel name and unit. The DataArray
    object has `name` and `unit` properties to ease data processing.

    Note that a DataArray created from another DataArray will loose 
    metadata, for instance
        >>> azimuth_deg = DataArray(data, name="Azimuth", unit="(deg)")
        >>> print(azimuth_deg.name, azimuth_deg.unit)
            "Azimuth" "(deg)"
        >>> azimuth_rad = azimuth_deg / 180 * np.pi
        >>> print(azimuth_rad.name, azimuth_rad.unit)
            None None
    
    The metadata can be set manually
        >>> azimuth_rad.name = "Azimuth"
        >>> azimuth_rad.unit = "(rad)"
        >>> print(azimuth_rad.name, azimuth_rad.unit)
            "Azimuth" "(rad)"
    
    or copied by the copy_metadata method.
        >>> azimuth_rad.copy_metadata(azimuth_deg)
        >>> print(azimuth_rad.name, azimuth_rad.unit)
            "Azimuth" "(deg)"
        >>> azimuth_rad.unit = "(rad)"
        >>> print(azimuth_rad.name, azimuth_rad.unit)
            "Azimuth" "(rad)"

        

    Properties
    ----------
    name : str
        Name or identifier of the data array.
    unit : str
        Unit of data points in data array.
    """
    def __new__(cls, data, name=None, unit=None):
        obj = np.asarray(data).view(cls)
        obj.name = name
        obj.unit = unit
        obj._label = None
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.name = None
        self.unit = None
        self._label = None

    def copy_metadata(self, obj):
        """
        
        """
        self.name = getattr(obj, 'name', None)
        self.unit = getattr(obj, 'unit', None)
        self._label = getattr(obj, '_label', None)

    @property
    def label(self):
        if (self._label is None):
            try:
                return self.name + " " + self.unit
            except TypeError:
                return None
        else:
            return self._label

    @label.setter
    def label(self, val):
        self._label = val


class DataSet(object):
    """DataSet organizes data from FAST simulations.

    Access data channels as a property of the DataSet object, 
    e.g. DataSet.Time refers directly to the DataArray with channel 
    name Time. Any channelname with an illegal property name character, 
    e.g. "-ReactFXss" contains the python operator "-", will be changed 
    by removing the illegal character.

    Use `load` method to load binary .outb files from FAST 
    simulations.
    """
    def __init__(self, dataarrays=None, description=None):
        self.dataarrays = dataarrays
        for da in dataarrays:
            self.__dict__[da.name] = da
        self.verbose_description = description
        self.description = description

    def load(self, filename):
        """Load data from FAST binary file.

        Arguments
        ---------
        filename : str
            Name of binary output file from FAST simulations.
        """
        arrays, names, units, _, full_desc = ReadFASTBinary(filename)

        regex = "Description from the FAST input file: (.*$)"
        self.description = re.findall(regex, full_desc)[0]
        self.verbose_description = full_desc
        self.dataarrays = []
        for i in range(len(names)):
            dataarr = DataArray(arrays[:, i], name=names[i], unit=units[i])
            dname = self._clean_dname(names[i])
            self.__dict__[dname] = dataarr
            self.dataarrays.append(dataarr)

    @staticmethod
    def _clean_dname(dname):
        name = dname
        for illegal_char in ["-", "+", "*", "/"]:
                name = name.replace(illegal_char, "")
        return name
    @property
    def names(self):
        return [self._clean_dname(da.name) for da in self.dataarrays if da.name is not None]