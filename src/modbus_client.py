#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Establish a connection with the PLC using
Modbus TCP. Sends and receives data.

@AUTHOR: Arvin Khodabandeh
@DATE: 2019-10-24
"""

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder

class ModbusClient(object):

    def __init__(self, ip='158.38.140.73'):
        """
        Establishes a TCP connection with the PLC.
        Can read and write to all the available I/O.
        :param the IP address of the Modbus Server.
        """
        self.ip = ip
        self.client = ModbusTcpClient(self.ip)
        self.connection = self.client.connect()

    def is_connected(self):
        """
        Returns true if the TCP connection is active,
        false if not.
        """
        return self.connection

    def write_int(self, value, address):
        """
        Writes a 16-bit integer value to the given address on the PLC.
        :param value: The integer value to send
        :param address: The I/O address on the PLC to write the value to
        :return: True if successful, false if not
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        builder.add_16bit_int(value)
        payload = builder.build()
        result = self.client.write_registers(address, payload, skip_encode=True, unit=1)
        return result

    def write_float(self, value, address):
        """
        Writes a 32-bit float value to the given address on the PLC.
        :param value: The float value to send
        :param address: The I/O address on the PLC to write the value to
        :return: True if successful, false if not
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        builder.add_32bit_float(value)
        payload = builder.build()
        result = self.client.write_registers(address, payload, skip_encode=True, unit=1)
        return result

    def read_int(self, address=12288, size=1):
        """
        Read an integer value on a specified address on the PLC.
        :param address: Address to read the value from
        :param size:
        :return: the read value
        """
        response = self.client.read_holding_registers(address, size, unit=1)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        value = decoder.decode_16bit_int()
        return value

    def read_float(self, address=12290, size=2):
        """
        Read a float value on a specified address on the PLC.
        :param address: Address to read the value from
        :param size:
        :return: the read value
        """
        response = self.client.read_holding_registers(address, size, unit=1)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        value = decoder.decode_32bit_float()
        return value

    def close(self):
        """
        Close the connection with the PLC.
        :return: True if the connection is closed
        """
        self.client.close()


# Simple example to show the functionality of this class
if __name__ == '__main__':
    client = ModbusClient()
    client.write_int(value=1000, address=12288)
    client.write_int(value=69, address=12289)
    client.write_int(value=12312, address=12290)
    while client.is_connected():
        print(client.read_int(address=12288))
        print(client.read_int(address=12289))
        print(client.read_int(address=12290))

