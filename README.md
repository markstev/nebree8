Wiring / component information
==============================

Overview
-----------------------------
A Raspberry Pi is used for the CPU.

Fluid levels are monitored using a load cell; the output from the load cell is
a voltage difference that is amplified (INA129), digitized (ADS1115), and read
through i2c. See monitor_load_cell.py.

A stepper motor is used to move the chuck along the track. See toggle_pin.py.

Valves are actuated using io_bank.py.

ADS1x15: 4-channel 16-bit ADC
------------------------------
http://www.adafruit.com/products/1085
VDD: 3.3v
GND: GND
SCL: rPI SCL
SDA: rPI SDA
ADDR: GND
A0: INA129 Vo
A1: INA129 Ref / GND


INA129: Instrumentation amplifier
---------------------------------
http://www.ti.com/product/ina129

p1-p8: 100 ohm resistor -- configures 500x gain
p2: Vin- load cell white
p3: Vin+ load cell blue
p4: V-, ground
p5: Ref, GND (and ch0 on the ADS1115)
p6: Vo - ch1 on the ADS1115
p7: 3.3v to ensure Vo is clamped 0-3.3v


Load Cell
---------------------------------
http://www.amazon.com/gp/product/B005GIXJKY/ref=wms_ohs_product?ie=UTF8&psc=1

Black: GND
Red: +10v
White: Vo-
Blue: Vo+

Output is ~1mV/V, or 10mV at the full 1kg load with an activation voltage of
10V.
