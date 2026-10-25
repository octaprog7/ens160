# Micropython module for working with ENS160

> **Note:** This English translation was created because of the influx of visitors from [Kazuki's Blog](https://kazukifu.hatenablog.com) in December 2025. The original Russian version is available here: [README_RU.md](README_RU.md).

ENS160 is a digital multi-gas sensor specifically designed for indoor air quality monitoring, providing optimal detection of a wide range of volatile organic compounds (VOCs) and oxidizing gases.

Upload the Micropython firmware to the NANO board (ESP, etc.), the *.py files: main.py, ens160sciosense.py and the service_pack_2 folder.
Then open main.py in your IDE and run it.

## Important rule: the first 24 hours of operation

If you see the "Initial Start-Up" message and are waiting for the sensor to start showing data, read this section.

How the sensor works at first power-on:
1. Inside the chip there is NVM memory that stores information about clean air.
2. At the very first installation, the sensor is empty. It needs to understand what air is around it right now.
3. To do this, it runs for exactly 24 hours without being turned off. During this time it calibrates and remembers the parameters.
4. If you turn off the power before 24 hours have passed, the sensor will forget everything and start calibration from scratch.
5. After a successful 24 hours, the information is stored forever. On subsequent power-ups, the sensor will start up in 3 minutes instead of an hour.

What you need to do:
- Turn on the sensor and leave it running continuously for 24 hours.
- Do not unplug the cable, do not disconnect the power, do not reboot the board.
- You can close the terminal window. The sensor will work on its own.
- After 24 hours it will remember the clean air and will be ready to work immediately after power-on.

Why it is done this way:
This is not a program bug. All gas sensors of this type work exactly this way. They need time to warm up, stabilize internal elements and write baseline values to non-volatile memory.

In short:
- First 24 hours = the sensor is learning. Don't touch it.
- After 24 hours = the sensor has memorized. It will start up quickly.
- If you turn it off before 24 hours = it will start learning again (another 1 hour wait).

# Pictures
## IDE
![alt text](https://github.com/octaprog7/ens160/blob/master/ide_ens160.png)
## Breadboard
![alt text](https://github.com/octaprog7/ens160/blob/master/brd_ens160.png)
## CO2 and TVOC graph
![alt text](https://github.com/octaprog7/ens160/blob/master/co2_graph.png)

## Initial Start-Up time

At the first power-on of the ENS160 sensor (or after storage without power for more than 24 hours) you will see in the output:
```console
[1] Initial Start-Up (~1 hour) | Validity: 2 | NewData: True
[2] Initial Start-Up (~1 hour) | Validity: 2 | NewData: True
```

This is normal behavior, not an error!

### Startup timeline:

| Time from start | Validity Flag | Status           | What happens                                                                                              |
|-----------------|---------------|------------------|-------------------------------------------------------------------------------------------------------------|
| 00:00 - ~60:00  | 2             | Initial Start-Up | Initial calibration of 4 heaters, stabilization of MOX elements, formation of the clean air baseline |
| ~60:00 - ~63:00 | 1             | Warm-Up          | Final warm-up, the TrueVOC algorithm enters operating mode                                                |
| > ~63:00        | 0             | Operating OK     | Stable readings of eCO2 [ppm], TVOC [ppb], AQI                                                            |

### Important:

1. Do not disconnect the power during the first 24 hours of continuous operation.
   After that, the baseline will be saved in the chip's internal NVM memory, and on subsequent power-ups the Initial Start-Up phase will not repeat (only Warm-Up ~3 min).

2. Data in the Validity: 2 phase is invalid -> the driver correctly returns None and does not output zero readings.

3. This is a feature of all MOX sensors (metal-oxide semiconductor), not a driver bug. The physical process of heating and stabilizing the heaters takes time.

### Recommendations:

- In finished devices, do not completely de-energize the ENS160. Use DEEP_SLEEP mode (consumption ~10 uA) instead of disconnecting VDD.
- If power is still removed, inform the user: "Sensor calibration... ~1 hour" instead of showing zeros.
- For tests, you can temporarily ignore validity_flag, but the accuracy of the readings will be low.

### Example output after calibration:

```console
[3601] Warm-Up (~3 min) | Validity: 1 | NewData: True
[3602] Warm-Up (~3 min) | Validity: 1 | NewData: True
...
[3781] Operating OK | eCO2: 485 ppm | TVOC: 62 ppb | AQI: 1
[3782] Operating OK | eCO2: 492 ppm | TVOC: 68 ppb | AQI: 2
```

Just leave the board powered on for ~1.5 hours — and the sensor will start delivering accurate air quality data!

## Air quality and cooking
### Nothing is being cooked in the kitchen
```console
[3962] Operating OK | eCO2: 465 ppm | TVOC: 54 ppb | AQI: 1
[3963] Operating OK | eCO2: 457 ppm | TVOC: 50 ppb | AQI: 1
[3964] Operating OK | eCO2: 494 ppm | TVOC: 69 ppb | AQI: 2
[3965] Operating OK | eCO2: 446 ppm | TVOC: 45 ppb | AQI: 1
[3966] Operating OK | eCO2: 473 ppm | TVOC: 58 ppb | AQI: 1
[3967] Operating OK | eCO2: 493 ppm | TVOC: 69 ppb | AQI: 2
[3968] Operating OK | eCO2: 480 ppm | TVOC: 62 ppb | AQI: 1
[3969] Operating OK | eCO2: 455 ppm | TVOC: 49 ppb | AQI: 1
[3970] Operating OK | eCO2: 489 ppm | TVOC: 66 ppb | AQI: 2
[3971] Operating OK | eCO2: 461 ppm | TVOC: 52 ppb | AQI: 1
[3972] Operating OK | Validity: 0 | NewData: False
[3973] Operating OK | eCO2: 478 ppm | TVOC: 61 ppb | AQI: 1
[3974] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3975] Operating OK | eCO2: 480 ppm | TVOC: 61 ppb | AQI: 1
[3976] Operating OK | eCO2: 488 ppm | TVOC: 66 ppb | AQI: 2
[3977] Operating OK | eCO2: 459 ppm | TVOC: 51 ppb | AQI: 1
[3978] Operating OK | eCO2: 452 ppm | TVOC: 48 ppb | AQI: 1
[3979] Operating OK | eCO2: 462 ppm | TVOC: 52 ppb | AQI: 1
[3980] Operating OK | eCO2: 467 ppm | TVOC: 55 ppb | AQI: 1
[3981] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3982] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3983] Operating OK | eCO2: 451 ppm | TVOC: 47 ppb | AQI: 1
[3984] Operating OK | eCO2: 444 ppm | TVOC: 44 ppb | AQI: 1
[3985] Operating OK | eCO2: 450 ppm | TVOC: 47 ppb | AQI: 1
[3986] Operating OK | eCO2: 467 ppm | TVOC: 55 ppb | AQI: 1
[3987] Operating OK | eCO2: 468 ppm | TVOC: 55 ppb | AQI: 1
[3988] Operating OK | eCO2: 452 ppm | TVOC: 48 ppb | AQI: 1
[3989] Operating OK | eCO2: 444 ppm | TVOC: 44 ppb | AQI: 1
[3990] Operating OK | eCO2: 479 ppm | TVOC: 61 ppb | AQI: 1
[3991] Operating OK | eCO2: 436 ppm | TVOC: 40 ppb | AQI: 1
...
```
### Meat is being fried on a gas stove in the kitchen!!!
```console
[7766] Operating OK | eCO2: 700 ppm | TVOC: 205 ppb | AQI: 2
[7767] Operating OK | eCO2: 694 ppm | TVOC: 201 ppb | AQI: 2
[7768] Operating OK | eCO2: 744 ppm | TVOC: 243 ppb | AQI: 3
[7769] Operating OK | eCO2: 704 ppm | TVOC: 209 ppb | AQI: 2
[7770] Operating OK | eCO2: 678 ppm | TVOC: 188 ppb | AQI: 2
[7771] Operating OK | eCO2: 706 ppm | TVOC: 210 ppb | AQI: 2
[7772] Operating OK | eCO2: 729 ppm | TVOC: 230 ppb | AQI: 3
[7773] Operating OK | eCO2: 707 ppm | TVOC: 212 ppb | AQI: 2
[7774] Operating OK | eCO2: 722 ppm | TVOC: 224 ppb | AQI: 3
[7775] Operating OK | eCO2: 721 ppm | TVOC: 223 ppb | AQI: 3
[7776] Operating OK | eCO2: 736 ppm | TVOC: 236 ppb | AQI: 3
[7777] Operating OK | eCO2: 710 ppm | TVOC: 214 ppb | AQI: 2
[7778] Operating OK | Validity: 0 | NewData: False
[7779] Operating OK | eCO2: 724 ppm | TVOC: 226 ppb | AQI: 3
[7780] Operating OK | eCO2: 708 ppm | TVOC: 212 ppb | AQI: 2
[7781] Operating OK | eCO2: 746 ppm | TVOC: 245 ppb | AQI: 3
[7782] Operating OK | eCO2: 722 ppm | TVOC: 224 ppb | AQI: 3
[7783] Operating OK | eCO2: 727 ppm | TVOC: 229 ppb | AQI: 3
[7784] Operating OK | eCO2: 735 ppm | TVOC: 235 ppb | AQI: 3
[7785] Operating OK | eCO2: 733 ppm | TVOC: 234 ppb | AQI: 3
```
