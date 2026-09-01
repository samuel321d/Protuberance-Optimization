import numpy as np
import matplotlib.pyplot as plt

# Generate example
x = np.arange(0, 2*np.pi, 0.1)
sinx = np.sin(x)

plt.figure(figsize = (10, 5))
plt.plot(x, sinx)
plt.grid()
plt.show()