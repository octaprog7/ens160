# micropython
# MIT license
# Copyright (c) 2022 Roman Shevchik   goctaprog@gmail.com

from sensor_pack import bus_service
from sensor_pack.base_sensor import BaseSensor, Iterator, check_value


class Ens160(BaseSensor, Iterator):
    """Class for work with Digital Metal-Oxide Multi-Gas Sensor ENS160.
    https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/"""
    _CRC_POLY = 0x1D

    @staticmethod
    def _crc8(sequence, polynomial: int, init_value: int):
        """какое-то особое CRC8 от sciosense!"""
        crc = init_value & 0xFF
        for item in sequence:
            tmp = 0xFF & ((crc << 1) ^ item)
            if 0 == crc & 0x80:
                crc = tmp
            else:
                crc = tmp ^ polynomial
        return crc

    def __init__(self, adapter: bus_service.I2cAdapter, address: int = 0x52, check_crc: bool = True):
        """  """
        super().__init__(adapter, address, False)
        self.check_crc = check_crc
        self.misr = 0
        # misr sinchronization!
        self._get_last_checksum()

    def _read_register(self, reg_addr, bytes_count=2) -> bytes:
        """считывает из регистра датчика значение.
        bytes_count - размер значения в байтах"""
        b = self.adapter.read_register(self.address, reg_addr, bytes_count)
        if self.check_crc:
            if 0x38 == reg_addr:
                self.misr = b[0]    # update misr
                return b
            # calc crc buf
            crc = Ens160._crc8(b, Ens160._CRC_POLY, self.misr)
            print(f"crc, misr: {hex(crc)}, {hex(self.misr)}")
            # compare calculated crc and misr
        return b

    def _write_register(self, reg_addr, value: int, bytes_count=2) -> int:
        """записывает данные value в датчик, по адресу reg_addr.
        bytes_count - кол-во записываемых данных"""
        byte_order = self._get_byteorder_as_str()[0]
        return self.adapter.write_register(self.address, reg_addr, value, bytes_count, byte_order)

    def __del__(self):
        self.set_mode(0x00)     # go to deep sleep

    def get_id(self) -> int:
        """Return part number of the ENS160"""
        reg_val = self._read_register(0x00, 2)
        return self.unpack("H", reg_val)[0]

    def soft_reset(self):
        """Software reset."""
        self.set_mode(0xF0)

    def set_mode(self, new_mode: int):
        """Set sensor mode.
        Устанавливает режим работы датчика.
        Operating mode:
                7:0     Field Name
                --------------------------------------------
                0x00:   DEEP SLEEP mode (low-power standby) (режим ожидания)
                0x01:   IDLE mode (low power)   (экономный режим работы, для батарейной техники)
                0x02:   STANDARD Gas Sensing Mode (нормальный режим)
                0xF0:   RESET"""
        nm = check_value(new_mode, (0, 1, 2, 0xF0), f"Invalid mode value: {new_mode}")
        self._write_register(0x10, nm, 1)

    def get_mode(self) -> int:
        """Return current operation mode of sensor
        Возвращает текущий режим работы датчика"""
        reg_val = self._read_register(0x10, 1)
        return self.unpack("B", reg_val)[0]

    def get_config(self) -> int:
        """Return current config from sensor.
        Pls see Table 19: Register CONFIG in official documentation!
        Возвращает текущие настройки датчика. Смотри таблицу 19 в официальной документации"""
        reg_val = self._read_register(0x11, 1)
        return self.unpack("b", reg_val)[0]

    def set_config(self, new_config: int) -> int:
        """Set current config sensor.
        Pls see Table 19: Register CONFIG in official documentation!
         Настраивает датчик. Смотри таблицу 19 в официальной документации"""
        return self._write_register(0x11, new_config, 1)

    def _exec_cmd(self, cmd: int) -> bytes:
        """Для внутреннего использования!"""
        check_value(cmd, (0x00, 0x0E, 0xCC), f"Invalid command code: {cmd}")
        self._write_register(0x12, cmd, 1)
        return self._read_register(0x48, 8)

    def set_ambient_temp(self, value_in_celsius: float):
        """write ambient temperature data to ENS160 for compensation. value in Celsius.
        This value must be read from the temperature sensor! It must be correct!
        Записывает в ENS160 датчик температуру окружающей среды, для компенсации!
        Значение в градусах Цельсия! Это значение должно быть считано с датчика температуры!
        Оно должно быть правильным и в допустимом диапазоне!
        """
        t = int(64*(273.15+value_in_celsius))
        self._write_register(0x13, t, 2)

    def set_humidity(self, rel_hum: int):
        """write relative humidity data to ENS160 for compensation. value in percent.
        Записывает в ENS160 датчик относительную влажность, для компенсации! значение в процентах!"""
        check_value(rel_hum, range(101), f"Invalid humidity value: {rel_hum}")
        self._write_register(0x15, rel_hum << 9, 2)

    def get_status(self) -> int:
        """indicates the current status of the ENS160.
        Возвращает текущий статус ENS160 в виде байта"""
        reg_val = self._read_register(0x20, 1)
        return self.unpack("b", reg_val)[0]

    def get_air_quality_index(self) -> int:
        """reports the calculated Air Quality Index according to the UBA.
        Возвращает расчетный индекс качества воздуха в соответствии с UBA. 1(прекрасно)..5(кошмар))"""
        reg_val = self._read_register(0x21, 1)
        return self.unpack("b", reg_val)[0] & 0x07

    def get_tvoc(self) -> int:
        """reports the calculated TVOC concentration in ppb.
        Возвращает расчетную концентрацию Летучих Органических Соединений (ЛОС) в частях на миллион (ppm)"""
        reg_val = self._read_register(0x22, 2)
        return self.unpack("H", reg_val)[0]

    def get_eco2(self) -> int:
        """reports the calculated equivalent CO 2 -concentration in ppm, based on the detected VOCs and hydrogen.
        Возвращает расчетную эквивалентную концентрацию CO2 в частях на миллион [ppm] на
        основе обнаруженных летучих органических соединений (ЛОС) и водорода."""
        reg_val = self._read_register(0x24, 2)
        return self.unpack("H", reg_val)[0]

    def _get_last_checksum(self) -> int:
        """Reports the calculated checksum of the previous DATA_* read transaction (of n-bytes).
        It can be read as a separate transaction, if required, to check the validity of the previous
        transaction. The value should be compared with the number calculated by the Host system on the incoming Data.

        Возвращает рассчитанную контрольную сумму предыдущей транзакции чтения n-байт.
        При необходимости её можно прочитать как отдельную транзакцию, чтобы проверить правильность предыдущей
        операции чтения. Значение следует сравнить с числом, рассчитанным хост-системой для входящих данных!
        """
        reg_val = self._read_register(0x38, 1)
        return self.unpack("B", reg_val)[0]

    def get_firmware_version(self) -> tuple:
        """Return the firmware version of the ENS160 as tuple (Major, Minor, Release).
        Возвращает версию прошивки ENS160 в виде кортежа (Major, Minor, Release)"""
        b = self._exec_cmd(0x0E)
        return b[4], b[5], b[6]

    def __next__(self) -> tuple:
        """Механизм итератора.
        Возвращает кортеж: CO2 [ppm], ЛОС[ppm], Индекс Качества Воздуха. 1(прекрасно)..5(кошмар)"""
        return self.get_eco2(), self.get_tvoc(), self.get_air_quality_index()
