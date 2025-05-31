# micropython
# MIT license


# Please read this before use!: https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/
from machine import I2C, Pin
import ens160sciosense
from sensor_pack_2.bus_service import I2cAdapter
import time

if __name__ == '__main__':
    # пожалуйста установите выводы scl и sda в конструкторе для вашей платы, иначе ничего не заработает!
    # please set scl and sda pins for your board, otherwise nothing will work!
    # https://docs.micropython.org/en/latest/library/machine.I2C.html#machine-i2c
    # i2c = I2C(id=1, scl=Pin(27), sda=Pin(26), freq=400_000)  # on Arduino Nano RP2040 Connect and Pico W tested!
    # i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)  # create I2C peripheral at frequency of 400kHz
    i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)
    adaptor = I2cAdapter(i2c)
    # ps - pressure sensor
    sensor = ens160sciosense.Ens160(adaptor)

    # если у вас посыпались исключения, то проверьте все соединения.
    sensor.start_measurement(start=False)
    print(f"Sensor ID: {sensor.get_id():X}")
        
    fw = sensor.get_firmware_version()
    print(f"Firmware version: {fw}")
    st = sensor.get_data_status(raw=True)
    print(f"Status: {st:X}")
    st = sensor.get_data_status(raw=False)
    print(f"Status: {st}")
    #
    cfg_raw = sensor.get_config(raw=True)
    cfg = sensor.get_config(raw=False)
    print(f"raw config: {cfg_raw:X}")
    print(f"config: {cfg}")

    wt = sensor.get_conversion_cycle_time()
    sensor.start_measurement(start=True)
    time.sleep_ms(wt)
    #
    for air_params in sensor:
        if not air_params is None:
            print(f"{air_params}")
        else:
            print("no data!")
        time.sleep_ms(wt)
