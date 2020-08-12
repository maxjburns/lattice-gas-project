import numpy as np


a_3d_array = np.array([
    [[1], [2], [3]], 
    [[4], [5], [6]], 
    [[7], [8], [9]]])

print(a_3d_array)

print(np.sum(a_3d_array[0:2][0:2]))
print(a_3d_array)
print('\n\n\n')
print(a_3d_array[0:3][1:2])
print('\n\n\n')
print(a_3d_array[1:3][1:2])
print('\n\n\n')
print(a_3d_array[0:2][1:2])
print('\n\n\n')
print(a_3d_array[0:2, 1:3])
