from qiskit import *
import numpy as np
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_aer.noise import NoiseModel, depolarizing_error
import matplotlib.pyplot as plt

#creation of simple quantum circuit
phi = np.array([0, np.pi/4, np.pi/2])
theta = np.array([0, np.pi/4, np.pi/2])

qc = QuantumCircuit(3,3)

for i in range(len(phi)):
    qc.ry(theta[i], i)
    qc.rz(phi[i], i)

qc.cx(0, 1)
qc.cx(1, 2)

qc.measure(0,0)
qc.measure(1,1)
qc.measure(2,2)

#measurements without depolarizing error
shots_number = 100000
backend = AerSimulator(method='statevector', shots=shots_number)
result = backend.run(qc).result()
shots_result = result.get_counts()

p_without_error = shots_result["100"] / shots_number
print(p_without_error)

#measurements with error with several error rates
error_rates = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
shots_number = 100000
p = []

for error_rate in error_rates:
    noise_model = NoiseModel()
    error = depolarizing_error(error_rate, 1)
    noise_model.add_all_qubit_quantum_error(error, ['rz', 'ry', 'h'])

    backend = AerSimulator(method='density_matrix', shots=shots_number, noise_model=noise_model)
    result = backend.run(qc).result()
    shots_result = result.get_counts()

    p.append(shots_result["100"] / shots_number)

print(p)

#interpolation of the dependence of result on error rate
degree = 1
poly_coefficients = np.polyfit(error_rates, p, degree)
poly_model = np.poly1d(poly_coefficients)

x = np.linspace(0, 0.08, 10)
y = poly_model(x)

plt.scatter(error_rates, p)
plt.plot(x, y)

plt.show()

#obtaining of approximated result of observable without error and its comparison to exact result
p_approx = poly_model(0)
print(p_approx)

relative_error = (np.abs(p_approx - p_without_error) / p_without_error) * 100
print('Relative error:', relative_error, '%')
