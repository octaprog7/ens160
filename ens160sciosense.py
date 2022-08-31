# micropython
# MIT license
# Copyright (c) 2022 Roman Shevchik   goctaprog@gmail.com

from sensor_pack import bus_service
from sensor_pack.base_sensor import BaseSensor, Iterator, check_value


class Ens160(BaseSensor, Iterator):
    """Class for work with Digital Metal-Oxide Multi-Gas Sensor ENS160
    Класс для работы с цифровым металлооксидным мультигазовым датчиком ENS160.
    https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/"""
    _CRC_POLY = 0x1D

    @staticmethod
    def _crc8(sequence, polynomial: int, init_value: int):
        """какое-то особое CRC8 от sciosense!
        Мало того, кто-то "очень" умный придумал читать CRC из датчика, вместо того,
        чтобы передать его вместе с результатами одним пакетом!"""
        crc = init_value & 0xFF
        for item in sequence:
            tmp = 0xFF & ((crc << 1) ^ item)
            if 0 == crc & 0x80:
                crc = tmp
            else:
                crc = tmp ^ polynomial
        return crc

    def __init__(self, adapter: bus_service.I2cAdapter, address: int = 0x52, check_crc: bool = True):
        """Адаптер шины, адрес на шине, проверять CRC или нет.
        Bus adapter, bus address, check CRC or not"""
        super().__init__(adapter, address, False)
        self.check_crc = check_crc

    def _read_register(self, reg_addr, bytes_count=2) -> bytes:
        """считывает из регистра датчика значение.
        bytes_count - число считываемых байт, начиная с адреса reg_addr"""
        before = 0
        if self.check_crc: 
            before = self._get_last_checksum()   # read crc from sensor
        b = self.adapter.read_register(self.address, reg_addr, bytes_count)
        if self.check_crc:
            if 0 <= reg_addr < 0x38:
                crc = Ens160._crc8(b, Ens160._CRC_POLY, before)  # calculate crc from readed data
                after = self._get_last_checksum()   # read crc from sensor
                if crc != after:  # compare calculated crc and readed from sensor
                    raise IOError(f"Input data broken! Bad CRC! Calculated crc8: {hex(crc)} != {hex(after)}")
                
        return b

    def _write_register(self, reg_addr, value: int, bytes_count=2) -> int:
        """записывает данные value в датчик, по адресу reg_addr.
        bytes_count - кол-во записываемых байт, начиная с адреса reg_addr"""
        byte_order = self._get_byteorder_as_str()[0]
        return self.adapter.write_register(self.address, reg_addr, value, bytes_count, byte_order)

    def __del__(self):
        self.set_mode(0x00)     # go to deep sleep

    def get_id(self) -> int:
        """Return part number of the ENS160.
        Возвращает какое-то число (the part number) из датчика"""
        reg_val = self._read_register(0x00, 2)
        return self.unpack("H", reg_val)[0]

    def soft_reset(self):
        """Software reset.
        Програмный сброс датчика"""
        self.set_mode(0xF0)

    def set_mode(self, new_mode: int):
        """Set sensor mode.
        Устанавливает режим работы датчика.
        Pls see 16.2.2 OPMODE (Address 0x10) in official documentation
        Operating mode:
                7:0     Description
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
        return self.unpack("B", reg_val)[0]

    def set_config(self, new_config: int) -> int:
        """Set current config sensor.
        Pls see Table 19: Register CONFIG in official documentation!
         Настраивает датчик. Смотри таблицу 19 в официальной документации"""
        return self._write_register(0x11, new_config, 1)

    def _exec_cmd(self, cmd: int) -> bytes:
        """Для внутреннего использования!
        For internal use!"""
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
        Возвращает текущий статус ENS160 в виде байта
        Pls read Table 26: Register DEVICE_STATUS from official documentation!"""
        reg_val = self._read_register(0x20, 1)
        return self.unpack("B", reg_val)[0]

    def get_air_quality_index(self) -> int:
        """reports the calculated Air Quality Index according to the UBA.
        Возвращает расчетный индекс качества воздуха в соответствии с UBA. 1(прекрасно)..5(кошмар))
        See section “AQI-UBA – UBA Air Quality Index” for further information. From official documentation!"""
        reg_val = self._read_register(0x21, 1)
        return self.unpack("B", reg_val)[0] & 0x07

    def get_tvoc(self) -> int:
        """reports the calculated TVOC concentration in ppb.
        Возвращает расчетную концентрацию Летучих Органических Соединений (ЛОС) в частях на миллион (ppm)
        See section “TVOC – Total Volatile Organic Compounds” for further information. From official documentation!"""
        reg_val = self._read_register(0x22, 2)
        return self.unpack("H", reg_val)[0]

    def get_eco2(self) -> int:
        """reports the calculated equivalent CO 2 -concentration in ppm, based on the detected VOCs and hydrogen.
        Возвращает расчетную эквивалентную концентрацию CO2 в частях на миллион [ppm] на
        основе обнаруженных летучих органических соединений (ЛОС) и водорода.
        See section “eCO2 – Equivalent CO2” for further information. From official documentation!"""
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
        # читаю 1 байт crc из датчика
        return self.adapter.read_register(self.address, 0x38, 1)[0]

    def get_firmware_version(self) -> tuple:
        """Return the firmware version of the ENS160 as tuple (Major, Minor, Release).
        Возвращает версию прошивки ENS160 в виде кортежа (Major, Minor, Release)"""
        b = self._exec_cmd(0x0E)
        return b[4], b[5], b[6]

    def __next__(self) -> tuple:
        """Механизм итератора.
        Возвращает кортеж: CO2 [ppm], ЛОС[ppm], Индекс Качества Воздуха. 1(прекрасно)..5(кошмар)
        Iterator mechanism.
        Returns a tuple: CO2 [ppm], VOC[ppm], Air Quality Index. 1(great)..5(nightmare)"""
        return self.get_eco2(), self.get_tvoc(), self.get_air_quality_index()
