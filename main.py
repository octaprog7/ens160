# micropython
# mail: goctaprog@gmail.com
# MIT license


# Please read this before use!: https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/
from machine import I2C
import ens160sciosense
from sensor_pack.bus_service import I2cAdapter
import time

if __name__ == '__main__':
    # пожалуйста установите выводы scl и sda в конструкторе для вашей платы, иначе ничего не заработает!
    # please set scl and sda pins for your board, otherwise nothing will work!
    # https://docs.micropython.org/en/latest/library/machine.I2C.html#machine-i2c
    # i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400_000) № для примера
    # bus =  I2C(scl=Pin(4), sda=Pin(5), freq=100000)   # на esp8266    !
    i2c = I2C(0, freq=400_000)  # on Arduino Nano RP2040 Connect tested
    adaptor = I2cAdapter(i2c)
    # ps - pressure sensor
    gas_sens = ens160sciosense.Ens160(adaptor)

    # если у вас посыпались исключения, чего у меня на макетной плате с али и проводами МГТВ не наблюдается,
    # то проверьте все соединения.
    # Радиотехника - наука о контактах! РТФ-Чемпион!
    gas_sens.set_mode(0x02)
    gs_id = gas_sens.get_id()
    print(f"Sensor ID: {hex(gs_id)}")

    while True:
        co2, tvoc = gas_sens.get_eco2(), gas_sens.get_tvoc()
        aqi = gas_sens.get_air_quality_index()
        print(f"CO2: {co2}\tTVOC: {tvoc}\tAQI: {aqi}")
        time.sleep_ms(1000)


