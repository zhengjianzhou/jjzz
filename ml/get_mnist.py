def get_mnist(img, label, n):
    images, path = [], r'C:\Users\ZKFCWPH\Downloads\mnist\\'
    f, l = open(path+img, "rb"), open(path+label, "rb")
    f.read(16), l.read(8)
    images = tuple(tuple((ord(l.read(1)), tuple(ord(k) for k in f.read(28*28)))) for i in range(n))
    f.close(), l.close()
    return images

# max = len([i for i in f.read()]) # => 60007
x = get_mnist("train-images-idx3-ubyte", "train-labels-idx1-ubyte", 3)

import numpy
X, Y = numpy.reshape(x[0][1],[28,28]), x[0][0]
print X,Y
Xf = numpy.fft.fft2(X)
print Xf

import matplotlib.pyplot as plt
# plt.imshow(X)
plt.imshow(X, interpolation='nearest')
plt.show()
# imgplot = plt.imshow(Xf)
