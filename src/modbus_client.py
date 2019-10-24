
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import BinaryPayloadDecoder


class ModbusClient(object):

    def __init__(self, ip='158.38.140.73'):
        self.ip = ip
        self.client = ModbusTcpClient(self.ip)
        self.connection = self.client.connect()

    def is_connected(self):

        return self.connection

    def write_int(self, value, address):

        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        builder.add_16bit_int(value)
        payload = builder.build()
        result = self.client.write_registers(address, payload, skip_encode=True, unit=1)
        return result

    def write_float(self, value, address):

        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        builder.add_32bit_float(value)
        payload = builder.build()
        result = self.client.write_register(address, payload, skip_encode=True, unit=1)
        return result

    def read_int(self, address=12288, size=1):

        response = self.client.read_holding_registers(address, size, unit=1)
        return response.registers

    def read_float(self, address=12290, size=2):

        response = self.client.read_holding_registers(address, size, unit=1)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        value = decoder.decode_32bit_float()
        return value

    def close(self):

        self.client.close()


if __name__ == '__main__':
    client = ModbusClient()

    client.write_int(value=69, address=12288)
    while client.is_connected():
        print(client.read_int(address=12288))
