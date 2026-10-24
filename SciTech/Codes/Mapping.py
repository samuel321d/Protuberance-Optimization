import matplotlib.pyplot as plt
import numpy as np

# f(x) parameters
a = 0.05067808
b = -0.55044524
c = 2.18505828
d = -4.08722944
e = 3.35193831
f = 2.95

# g(x) parameters
m = 0.37
B = 0.85

# Functions
def h(x):
    return a*x**5 + b*x**4 + c*x**3 + d*x**2 + e*x + f

def g(x):
    return m*x + B

L = 3.6

# Mapping coordinates
u = np.linspace(0, 1, 100)
v = np.linspace(0, 1, 100)

U, V = np.meshgrid(u, v)

X = U * L
Y = g(X) + V * (h(X)-g(X))

x = np.linspace(0, L, 100)

plt.figure(figsize = (10, 6))
plt.plot(x, h(x), label = 'h(x)')
plt.scatter(X, Y, c = 'red', s = 1)
plt.plot(x, g(x), label = 'g(x)')
plt.xlim(0, 4)
plt.legend()
plt.show()