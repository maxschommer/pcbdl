# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numbers
from typing import Union, Optional
from .base import *

# Ways to define an indicator
# Value Choices:
# Color, Frequency
# Brightness, luninescenscense, current

# Part choice optimizer
# Specific part choices:
# Package preference
# Size preference
# SMD vs TH
# Cost preference
# In stock preference
# Supplier preference


colors_to_frequencies = {
    "red": 650e-9,
    "orange": 610e-9,
    "yellow": 580e-9,
    "green": 530e-9,
    "blue": 470e-9,
    "indigo": 435e-9,
    "violet": 400e-9
}


def quadratic_wavelength_to_forward_voltage(frequency: float):
    """Convert a wavelength to an LED forward voltage using a quadratic
    model which was fit using the Digikey Discrete LED section and IR
    LED section as data points.

    Args:
        wavelength (float): The wavelength of the LED

    Returns:
        float: The estimated forward voltage of the LED
    """
    res = 6.24e12 * frequency ** 2 - 12.04e6 * frequency + 7.22
    return res


class Indicator():
    def __init__(self, input_voltage: float, *args, **kwargs):
        self.input_voltage = input_voltage
        led_wavelength = None
        led_current = None
        led_forward_voltage = None

        # If one argument, assume color is being set
        if len(args) == 1:
            led_wavelength = args[0]
        # Assume color and brightness are being set.
        elif len(args) == 2:
            led_wavelength = args[0]
            led_current = args[1]

        if kwargs:
            for kwarg in kwargs:
                value = kwargs[kwarg]
                if kwarg in ("led_color", "led_wavelength"):
                    led_wavelength = value
                elif kwarg == "led_current":
                    led_current = value
                elif kwarg == "led_forward_voltage":
                    led_forward_voltage = value
                else:
                    raise ValueError(
                        f"Keyword Argument {kwarg} not recognized.")

        if led_current is None:
            led_current = 5e-3
        if led_wavelength is None:
            led_wavelength = "blue"  # Best LED color objectively

        self.led_forward_voltage = led_forward_voltage
        self.led_current = led_current
        self.led_wavelength = led_wavelength

    def generate_subcircuit(self):
        input = NET("VIN")
        output = NET("VOUT")
        diode = LED(f"LAM_{self.led_wavelength}",
                    to=R(f"{self.resistor_value}R", to=output))

    @property
    def led_wavelength(self):
        """The wavelength of the LED in the indicator

        Returns:
            float: The wavelength in meters
        """
        return self._led_wavelength

    @led_wavelength.setter
    def led_wavelength(self, value: Union[numbers.Number, str]):
        if isinstance(value, numbers.Number):
            self._led_wavelength = value
        elif isinstance(value, str):
            assert value in colors_to_frequencies, f"Color {value}" +\
                f"not understood. Options are {colors_to_frequencies.keys()}"
            self._led_wavelength = colors_to_frequencies[value]
        else:
            raise ValueError(f"{value} is not convertible to a wavelength.")

    @property
    def led_current(self) -> float:
        """The current of the LED resistor pair. This sets the brightness of the
        LED.

        Returns:
            float: The current in amps.
        """
        return self._led_current

    @led_current.setter
    def led_current(self, value: numbers.Number):
        assert isinstance(
            value, numbers.Number), "led_current must be a number."
        self._led_current = value

    @property
    def led_forward_voltage(self) -> float:
        """If the led forward voltage isn't specified, then a general model
        for the forward voltage is used.

        Returns:
            float: The forward voltage of the LED
        """
        if self._led_forward_voltage is None:
            return quadratic_wavelength_to_forward_voltage(self.led_wavelength)
        return self._led_forward_voltage

    @led_forward_voltage.setter
    def led_forward_voltage(self, value: Optional[numbers.Number]):
        self._led_forward_voltage = value

    @property
    def resistor_value(self):
        led_v = self.led_forward_voltage
        input_voltage = self.input_voltage
        assert input_voltage > led_v, f"Input voltage {input_voltage}V must" +\
            f" be greater than LED forward voltage {led_v}V."
        r_val = (input_voltage - led_v) / self.led_current
        return r_val

    def __str__(self):
        res = "Indicator with:\n" +\
            f"  VIN: {self.input_voltage}V\n" + \
            f"  I: {self.led_current}A\n" + \
            f"  λ: {self.led_wavelength * 1e9}nm"
        return res


def test():
    ind = Indicator(3, led_color="green")
    print(ind)
    print(ind.resistor_value)


if __name__ == "__main__":
    test()
