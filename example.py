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