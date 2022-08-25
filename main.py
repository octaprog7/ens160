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
    gas_sens = ens160sciosense.Ens160(adaptor, 0x23, True)

    # если у вас посыпались исключения, чего у меня на макетной плате с али и проводами МГТВ не наблюдается,
    # то проверьте все соединения.
    # Радиотехника - наука о контактах! РТФ-Чемпион!
    gas_sens.power(True)  # Sensor Of Lux
    gas_sens.set_mode(True, True)
    old_lux = curr_max = 1

    for lux in gas_sens:
        if lux != old_lux:
            curr_max = max(lux, curr_max)
            lt = time.localtime()
            print(f"{lt[3:6]}\tIllumination [lux]: {lux}\tmax: {curr_max}\tNormalized [%]: {100 * lux / curr_max}")
        old_lux = lux
        time.sleep_ms(150)