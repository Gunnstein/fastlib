fastlib
=======


Installation
------------

Either download the repository to your computer and install, e.g. by **pip**

::

   pip install .


or install directly from github.

::

   pip install git+https://www.github.com/gunnstein/fastlib.git@master


Usage
-----

Working with data from FAST binary files 
........................................

The package contains functions to read and work with data from FAST binary
output files. The `ReadFASTBinary` function returns the channel data, names
and units exactly the same as the NREL distributed MATLAB function. Additionally,
the package provides DataSet and DataArray classes to simplify working with 
FAST output data. See code below:


.. code:: python

    import fastlib
    import matplotlib.pyplot as plt

    # Assuming a FAST binary output file "Test18.outb" is located in the folder
    filename = "Test18.outb"

    # Read data, channel names and units from with the ReadFASTBinary function.
    channels, chan_names, chan_units, filefmtid, desc_str = fastlib.ReadFASTBinary(filename)

    # Alternatively, use the DataSet class to work with FAST simulation data.
    dset = fastlib.DataSet()
    dset.load(filename)

    # Show all available DataArrays
    print(dset.names)

    #   ['Time', 'Wind1VelX', 'Wind1VelY', 'Wind1VelZ', 
    #    'OoPDefl1', 'IPDefl1', 'TwstDefl1', 'BldPitch1', 
    #    'Azimuth', ...]

    # DataArrays can be accessed as properties of the DataSet
    t = dset.Time
    y = dset.Azimuth

    # DataArrays are numpy arrays with extra properties. Use them
    # as numpy arrays to plot... or access any of the standard
    # numpy methods (mean, std, ...)

    plt.plot(t, y)
    print("Azimuth mean:", y.mean())
    print("Azimuth std:", y.std())
    print("Azimuth min:", y.min())
    print("Azimuth max:", y.max())


    # Each FAST simulation channel has a name and unit,
    # Access them in the DataArray object as properties
    # `name` and `unit`.
    plt.xlabel(t.name + " " + t.unit)

    #  y.label (= y.name + " " + y.unit) is another useful property 
    plt.ylabel(y.label)

    # It is also possible to set a user defined label
    y.label = "Azimuth with unit (deg)"
    print("User defined label:", y.label)

    # and resetting a user defined label
    y.label = None
    print("Reset label:", y.label)

    plt.show(block=True)
    

The resulting image from the example above is given below, see `example.py`

|example_img|


Support
-------

Please `open an issue <https://github.com/Gunnstein/fastlib/issues/new>`_
for support.


Contributing
------------

Please contribute using `Github Flow
<https://guides.github.com/introduction/flow/>`_.
Create a branch, add commits, and
`open a pull request <https://github.com/Gunnstein/fastlib/compare/>`_.

.. |example_img| image:: https://github.com/Gunnstein/fastlib/blob/master/example_img.png
    :target: https://github.com/gunnstein/fatpack/
