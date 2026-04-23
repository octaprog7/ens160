# Please read this before use!: https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/
import time
import ens160sciosense
from machine import I2C, Pin
from micropython import const
from sensor_pack_2.bus_service import I2cAdapter

ID_I2C = const(1)
SDA_PIN_N = const(6)
SCL_PIN_N = const(7)
FREQ_I2C = const(400_000)
#
REPEAT_COUNT = const(9999)

# Расшифровка флага валидности согласно Table 10 датшита
VALIDITY_DESCRIPTION = {
    0: "Operating OK",
    1: "Warm-Up (~3 min)",
    2: "Initial Start-Up (~1 hour)",
    3: "Invalid Output"
}

if __name__ == '__main__':
    # please set scl and sda pins for your board, otherwise nothing will work!
    i2c = I2C(id=ID_I2C, scl=Pin(SCL_PIN_N), sda=Pin(SDA_PIN_N), freq=FREQ_I2C)
    adaptor = I2cAdapter(i2c)
    sensor = ens160sciosense.Ens160(adaptor)

    try:
        # Идентификация датчика
        print("Sensor ID: 0x{:04X}".format(sensor.get_id()))
        fw = sensor.get_firmware_version()
        print("Firmware: major={}, minor={}, release={}".format(fw.major, fw.minor, fw.release))

        # Запуск измерений
        sensor.start_measurement(start=True)
        wt = sensor.get_conversion_cycle_time()
        print("Measurements started. Cycle time: {} ms".format(wt))
        print("Waiting for valid data...")

        loop_counter = 0
        while True:
            if loop_counter >= REPEAT_COUNT:
                break
            loop_counter += 1
            status = sensor.get_data_status(raw=False)
            desc = VALIDITY_DESCRIPTION.get(status.validity_flag, "Unknown")

            # Данные валидны И флаг новых данных установлен
            if status.validity_flag == 0 and status.new_data:
                air = sensor.get_measurement_value(None)
                if air is not None:
                    print(f"[{loop_counter}] {desc} | eCO2: {air.eco2} ppm | TVOC: {air.tvoc} ppb | AQI: {air.aqi}")
            else:
                # Период прогрева или инициализации
                print(f"[{loop_counter}] {desc} | Validity: {status.validity_flag} | NewData: {status.new_data}")

            time.sleep_ms(wt)

    except KeyboardInterrupt:
        print("\nStopped by user.")