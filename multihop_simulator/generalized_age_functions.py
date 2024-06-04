import numpy as np

# generalized age functions for the age-debt based scheduler
# Usage: comment out the age functions which are not used for a particular experiment

# def g(age, A = np.array([[0.5, 0.1], [0.6, 0.8]]), noise_var = 0.1):
#     noise_std = np.square(noise_var)
#     Sigma = np.array([[noise_std, 0], [0, noise_std]])

#     g_delta = 0
#     for p in range(age):
#         g_delta = g_delta + np.trace(np.linalg.matrix_power(A.T, p) @ np.linalg.matrix_power(A, p) @ Sigma)
#     return g_delta

def g(age):
    return age
