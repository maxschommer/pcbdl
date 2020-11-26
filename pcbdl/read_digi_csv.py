import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


led = pd.read_csv("/home/max/Downloads/led_indication___discrete.csv")

led['Wavelength - Peak'] = led['Wavelength - Peak'].str.extract(
    '(\d+)', expand=False).astype(float)
led['Voltage - Forward (Vf) (Typ)'] = led['Voltage - Forward (Vf) (Typ)'].str.extract(
    '(\d+.\d+)', expand=False).astype(float)

led = led.dropna(subset=['Wavelength - Peak', 'Voltage - Forward (Vf) (Typ)'])

lam = led['Wavelength - Peak'] * 1e-9
v = led['Voltage - Forward (Vf) (Typ)']

p, m, b = np.polyfit(lam, v, 2)
x = np.linspace(np.min(lam), np.max(lam))
y = p * x**2 + m * x + b

print(p, m, b)
plt.scatter(lam, v)
plt.plot(x, y)
plt.show()
