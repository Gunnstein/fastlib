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


Parametrizing FAST input files 
..............................

The package contains template formatters to help parametrize FAST simulations.
The `TemplateString` class takes in a template string and substitute template 
keys (${}) with instance properties, see below.


.. code:: python

    import fastlib
    
    template_str = """------- FAST v8.16.* INPUT FILE ------------------------------------------------
   ${description}
   ---------------------- SIMULATION CONTROL --------------------------------------
   ${Echo}         Echo            - Echo input data to <RootName>.ech (flag)
   "FATAL"       AbortLevel      - Error level when simulation should abort (string) {"WARNING", "SEVERE", "FATAL"}
   ${TMax}   TMax            - Total run time (s)
         0.005   DT              - Recommended module time step (s)
            2   InterpOrder     - Interpolation order for input/output time history (-) {1=linear, 2=quadratic}
            0   NumCrctn        - Number of correction iterations (-) {0=explicit calculation, i.e., no corrections}
         99999   DT_UJac         - Time between calls to get Jacobians (s)
         1E+06   UJacSclFact     - Scaling factor used in Jacobians (-)
    """

    fmter = fastlib.TemplateStringFormatter(template_str)
    fmter.description = "This is a demonstration of the TemplateStringFormatter class"
    fmter.Echo = False
    fmter.TMax = 90

    print(fmter.substitute())
   

which yields the following output::

      ------- FAST v8.16.* INPUT FILE ------------------------------------------------
      This is a demonstration of the TemplateStringFormatter class
      ---------------------- SIMULATION CONTROL --------------------------------------
      False         Echo            - Echo input data to <RootName>.ech (flag)
      "FATAL"       AbortLevel      - Error level when simulation should abort (string) {"WARNING", "SEVERE", "FATAL"}
               90   TMax            - Total run time (s)
            0.005   DT              - Recommended module time step (s)
                2   InterpOrder     - Interpolation order for input/output time history (-) {1=linear, 2=quadratic}
                0   NumCrctn        - Number of correction iterations (-) {0=explicit calculation, i.e., no corrections}
            99999   DT_UJac         - Time between calls to get Jacobians (s)
            1E+06   UJacSclFact     - Scaling factor used in Jacobians (-)


Note that the `TemplateStringFormatter.write(fname)` can write the substituted string directly to a file `fname`. There 
also exists a `TemplateFileFormatter` class that can read in a template string from a separate file rather than
a template string defined within the code.


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
