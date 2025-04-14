## Component Connection Table

| Component | Connection | ESP32 Pin |
|-----------|-----------|-----------|
| DHT11 | VCC | 3.3V |
| DHT11 | GND | GND |
| DHT11 | Data | GPIO4 |
| MQ-135 | VCC | VIN |
| MQ-135 | GND | GND |
| MQ-135 | AO | GPIO15 |
| GP2Y1010AU0F | VCC | VIN |
| GP2Y1010AU0F | GND (Black) | GND |
| GP2Y1010AU0F | GND (Yellow) | GND |
| GP2Y1010AU0F | LED CONTROL (Green) | GPIO25 |
| GP2Y1010AU0F | LED ANODE (White) | 150 Ohm Resistor -> VIN |
| GP2Y1010AU0F | Analog Output (Black) | GPIO34 |
| Capacitor (220uF) | + (Long) | GPIO34 (Analog Output) |
| Capacitor (220uF) | - (Short) | GND |
| 150 Ohm Resistor | One end | White Wire (LED ANODE) |
| 150 Ohm Resistor | Other end | VIN |

## Wiring Diagram Notes

1. The GP2Y1010AU0F dust sensor requires a 150Ω resistor between the LED ANODE pin and VIN
2. The 220μF capacitor is connected between the Analog Output and GND
3. Be careful with the polarity of the capacitor - the longer leg is positive
