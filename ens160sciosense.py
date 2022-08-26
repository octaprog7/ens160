# micropython
# MIT license
# Copyright (c) 2022 Roman Shevchik   goctaprog@gmail.com

import micropython
from sensor_pack import bus_service
from sensor_pack.base_sensor import BaseSensor, Iterator


@micropython.native
def _check_value(value: int, valid_range, error_msg: str) -> int:
    if value not in valid_range:
        raise ValueError(error_msg)
    return value


class Ens160(BaseSensor, Iterator):
    """Class for work with Digital Metal-Oxide Multi-Gas Sensor ENS160.
    https://www.sciosense.com/products/environmental-sensors/digital-multi-gas-sensor/"""

    def __init__(self, adapter: bus_service.I2cAdapter, address: int = 0x52):
        """  """
        super().__init__(adapter, address, False)

    def _read_register(self, reg_addr, bytes_count=2) -> bytes:
        """считывает из регистра датчика значение.
        bytes_count - размер значения в байтах"""
        return self.adapter.read_register(self.address, reg_addr, bytes_count)

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
        Operating mode:
                7:0     Field Name
                0x00:   DEEP SLEEP mode (low-power standby)
                0x01:   IDLE mode (low power)
                0x02:   STANDARD Gas Sensing Mode
                0xF0:   RESET"""
        self._write_register(0x10, new_mode, 1)

    def get_mode(self) -> int:
        """Return current operation mode of sensor"""
        reg_val = self._read_register(0x10, 1)
        return self.unpack("B", reg_val)[0]

    def get_config(self) -> int:
        reg_val = self._read_register(0x11, 1)
        return self.unpack("b", reg_val)[0]

    def set_config(self, new_config: int) -> int:
        return self._write_register(0x11, new_config, 1)

    def _exec_cmd(self, cmd: int) -> bytes:
        _check_value(cmd, (0x00, 0x0E, 0xCC), f"Invalid command code: {cmd}")
        self._write_register(0x12, cmd, 1)
        # read General Purpose WRITE Registers at address 0x40-47
        return self._read_register(0x40, 8)

    def set_ambient_temp(self, value: float):
        """write ambient temperature data to ENS160 for compensation. value in Celsius"""
        t = int(64*(273.15+value))
        self._write_register(0x13, t, 2)

    def set_humidity(self, value: float):
        """write relative humidity data to ENS160 for compensation. value in percent"""
        h = int(512*value)
        self._write_register(0x15, h, 2)

    def get_status(self) -> int:
        """indicates the current status of the ENS160"""
        reg_val = self._read_register(0x20, 1)
        return self.unpack("b", reg_val)[0]

    def get_air_quality_index(self) -> int:
        """reports the calculated Air Quality Index according to the UBA"""
        reg_val = self._read_register(0x21, 1)
        return self.unpack("b", reg_val)[0] & 0x07

    def get_tvoc(self) -> int:
        """reports the calculated TVOC concentration in ppb"""
        reg_val = self._read_register(0x22, 2)
        return self.unpack("H", reg_val)[0]

    def get_eco2(self) -> int:
        """reports the calculated equivalent CO 2 -concentration in ppm, based on the detected VOCs and hydrogen."""
        reg_val = self._read_register(0x24, 2)
        return self.unpack("H", reg_val)[0]

    def get_last_checksum(self) -> int:
        """reports the calculated checksum of the previous DATA_* read transaction (of n-
        bytes). It can be read as a separate transaction, if required, to check the validity of the previous
        transaction. The value should be compared with the number calculated by the Host system on the incoming Data."""
        reg_val = self._read_register(0x38, 1)
        return self.unpack("b", reg_val)[0]


    def get_illumination(self) -> int:
        """Return illumination in lux"""
        tmp = self.adapter.read(self.address, 2)
        return self.unpack("H", tmp)[0]     # .unpack(">H", tmp)[0])

    def __next__(self) -> int:
        return self.get_illumination()
