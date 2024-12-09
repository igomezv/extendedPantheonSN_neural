# -*- coding: utf-8 -*-
"""Pantheon matern lbfgs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zlZMY8VQucnvRtOCScMCe_rbt2F7KiXz
"""

!pip install gpytorch

import torch
import gpytorch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("/content/drive/MyDrive/Astrofinal/lcparam_full_long.txt", sep=" ", header=0)
redshift = torch.tensor(data['zcmb'].values, dtype=torch.float)
mag = torch.tensor(data['mb'].values, dtype=torch.float)
mag_err = torch.tensor(data['dmb'].values, dtype=torch.float)

# Definir el modelo de regresión gaussiana
class GaussianProcess(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood):
        super(GaussianProcess, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.MaternKernel(nu=1.5, lengthscale=1))

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

# Definir la función de likelihood
likelihood = gpytorch.likelihoods.GaussianLikelihood()

# Inicializar el modelo
model = GaussianProcess(redshift, mag, likelihood)

# Entrenar el modelo
model.train()
likelihood.train()

# Definir el optimizador L-BFGS
optimizer = torch.optim.LBFGS(model.parameters(), lr=0.1)
mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

# Definir la función de entrenamiento
def closure():
    optimizer.zero_grad()
    output = model(redshift)
    loss = -mll(output, mag)
    loss.backward()
    return loss

# Entrenar el modelo con L-BFGS durante 100 iteraciones
for i in range(100):
    optimizer.step(closure)

# Evaluar el modelo en un rango de valores de redshift
test_x = torch.linspace(redshift.min(), redshift.max(), 1000)
model.eval()
likelihood.eval()
with torch.no_grad():
    # Obtener la media y la varianza de la distribución gaussiana
    observed_pred = likelihood(model(test_x))
    mean = observed_pred.mean
    lower, upper = observed_pred.confidence_region()

# Graficar los resultados
plt.figure(figsize=(24, 14))
plt.errorbar(redshift.numpy(), mag.numpy(), yerr=mag_err.numpy(), fmt='o', markersize=3, alpha=0.5, label='Datos de supernovas')
plt.plot(test_x.numpy(), mean.numpy(), 'r', label='Predicción media')
plt.fill_between(test_x.numpy(), lower.numpy(), upper.numpy(), alpha=0.2, color='gray', label='Intervalo de confianza')
plt.xlabel('Redshift')
plt.ylabel('Magnitud aparente')
plt.legend()
plt.show()