# micropython
# MIT license
# Copyright (c) 2022 Roman Shevchik   goctaprog@gmail.com

import micropython
from sensor_pack import bus_service
from sensor_pack.base_sensor import BaseSensor, Iterator


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
        self.power(False)   # power off before delete

    def _send_cmd(self, command: int):
        """send 1 byte command to device"""
        bo = self._get_byteorder_as_str()[0]    # big, little
        self.adapter.write(self.address, command.to_bytes(1, bo))

    def get_id(self):
        """No ID support in sensor!"""
        return None

    def soft_reset(self):
        """Software reset."""
        self._send_cmd(0b0000_0111)

    def power(self, on_off: bool = True):
        """Sensor powering"""
        if on_off:
            self._send_cmd(0b0000_0001)
        else:
            self._send_cmd(0b0000_0000)

    def set_mode(self, continuously: bool = True, high_resolution: bool = True):
        """Set sensor mode.
        high resolution mode 2 not implemented. I have no desire to do this!"""
        if continuously:
            cmd = 0b0001_0000  # continuously mode
        else:
            cmd = 0b0010_0000  # one shot mode

        if not high_resolution:
            cmd |= 0b11    # L-Resolution Mode

        self._send_cmd(cmd)

    def get_illumination(self) -> int:
        """Return illumination in lux"""
        tmp = self.adapter.read(self.address, 2)
        return self.unpack("H", tmp)[0]     # .unpack(">H", tmp)[0])

    def __next__(self) -> int:
        return self.get_illumination()
