#!/usr/bin/env python3

"""
Thanks to [Packet sniffer in Python](https://www.uv.mx/personal/angelperez/files/2018/10/sniffers_texto.pdf)
https://www.opensourceforu.com/2015/03/a-guide-to-using-raw-sockets/
https://stackoverflow.com/questions/63702118/custom-crc32-calculation-in-python-without-libs
https://reveng.sourceforge.io/crc-catalogue/all.htm#crc.cat.crc-32-cksum
>>> chr(72)
'H'
>>> ord("H")
72
>>> hex(72)
'0x48'
>>> bin(0x48)
'0b1001000'
>>> hex(0b1001000)
'0x48'
>>> int(0b1001000)
72

Extended ASCII Codes
>>> ord(b"\xf2")
242
>>> hex(242)
'0xf2'
>>> b"\xf2".decode("cp437")
'≥'
"""
import socket
import os
import sys
import struct
import binascii
from dataclasses import dataclass

iface = "eth0"


def get_mac_addr(raw_data: bytes) -> str:
    """
    >>> binascii.hexlify(b'\x00\x15]e<\xdd', "-")
    b'00-15-5d-65-3c-dd'
    >>> binascii.hexlify(b'\x00\x15]e<\xdd')
    b'00155d653cdd'
    >>> binascii.unhexlify('00155d653cdd')
    b'\x00\x15]e<\xdd'
    """
    return binascii.hexlify(raw_data, ".").decode().upper()


def get_ip_addr(raw_data: bytes) -> str:
    # ".".join([str(b) for b in b'\xac\x1d\x06\x17']) -> '172.29.6.23'
    return ".".join([str(b) for b in raw_data])


# `if_ether.h`
@dataclass(slots=True)  # python3.10+
class EtherHeader:
    dest_mac: str  # 02.42.D8.32.81.4B
    src_mac: str
    ether_type: int  # 2 bytes

    # >>> format(255, '#04x')
    # '0xff'
    # >>> format(266, '#06x')
    # '0x010a'
    def __str__(self) -> str:
        return "Destination: {}, Source: {}, EtherType: {:#06x}".format(self.dest_mac, self.src_mac, self.ether_type)


# Ethernet (Layer 2) header
def ethernet_parser(raw_data: bytes):
    dest_mac, src_mac, ether_type = struct.unpack("! 6s 6s H", raw_data[:14])

    dest_mac = get_mac_addr(dest_mac)
    src_mac = get_mac_addr(src_mac)

    ether_header = EtherHeader(dest_mac, src_mac, ether_type)
    # crc_checksum = raw_data[-4:]

    data = raw_data[14:-4]

    return ether_header, data


@dataclass(slots=True)
class IPv4Header:
    version: int  # 172.17.0.2
    header_length: int
    type_of_service: int  # 2 bytes
    total_length: int
    time_to_live: int
    protocol: int
    header_checksum: int
    src_ip: str
    dest_ip: str

    # >>> format(255, '#04x')
    # '0xff'
    # >>> format(266, '#06x')
    # '0x010a'
    def __str__(self) -> str:
        return f"Version: {self.version}, Header Length: {self.header_length}, TTL:{self.time_to_live}, Protocol: {self.protocol}, Source: {self.src_ip}, Destination: {self.dest_ip}"


# IP (Layer 3) header
def ipv4_parser(raw_data: bytes):
    version = raw_data[0] >> 4
    header_length = (raw_data[0] & 0b00001111) * 4  # the unit is 4 bytes(32bits)
    type_of_service = raw_data[1]
    (
        total_length,
        time_to_live,
        protocol,
        header_checksum,
        src_ip,
        dest_ip,
    ) = struct.unpack("! H 4x B B H 4s 4s", raw_data[2:20])

    src_ip = get_ip_addr(src_ip)
    dest_ip = get_ip_addr(dest_ip)

    ipv4_header = IPv4Header(
        version=version,
        header_length=header_length,
        type_of_service=type_of_service,
        total_length=total_length,
        time_to_live=time_to_live,
        protocol=protocol,
        header_checksum=header_checksum,
        src_ip=src_ip,
        dest_ip=dest_ip,
    )

    data = raw_data[header_length:]
    return ipv4_header, data


@dataclass(slots=True)
class TCPHeader:
    src_port: int  # 02.42.D8.32.81.4B
    dest_port: int
    seq: int
    ack: int  # 2 bytes
    flag_cwr: int = 0b0
    flag_ece: int = 0b0
    flag_urg: int = 0b0
    flag_ack: int = 0b0
    flag_psh: int = 0b0
    flag_rst: int = 0b0
    flag_syn: int = 0b0
    flag_fin: int = 0b0


# TCP (Layer 4) header
def tcp_parser(raw_data: bytes):
    src_port, dest_port, seq, ack = struct.unpack("! H H L L", raw_data[0:12])
    offset = (raw_data[12] >> 4) * 4
    flag = raw_data[13]
    flag_cwr = (flag & 0x80) >> 7
    flag_ece = (flag & 0x40) >> 6
    flag_urg = (flag & 0x20) >> 5
    flag_ack = (flag & 0x10) >> 4
    flag_psh = (flag & 0x08) >> 3
    flag_rst = (flag & 0x04) >> 2
    flag_syn = (flag & 0x02) >> 1
    flag_fin = flag & 0x01

    tcp_header = TCPHeader(src_port, dest_port, seq, ack)
    tcp_header.flag_cwr = flag_cwr
    tcp_header.flag_ece = flag_ece
    tcp_header.flag_urg = flag_urg
    tcp_header.flag_ack = flag_ack
    tcp_header.flag_psh = flag_psh
    tcp_header.flag_rst = flag_rst
    tcp_header.flag_syn = flag_syn
    tcp_header.flag_fin = flag_fin

    data = raw_data[offset:]
    return tcp_header, data


@dataclass(slots=True)
class ICMPHeader:
    type: int  # 02.42.D8.32.81.4B
    code: int
    checksum: int


# ICMP (Layer 4) header
def icmp_parser(raw_data: bytes):
    type, code, checksum = struct.unpack("! B B H", raw_data[0:4])

    icmp_header = ICMPHeader(type, code, checksum)
    data = raw_data[4:]

    return icmp_header, data


@dataclass(slots=True)
class UDPHeader:
    src_port: int  # 02.42.D8.32.81.4B
    dest_port: int
    length: int
    checksum: int


# UDP (Layer 4) header
def udp_parser(raw_data: bytes):
    src_port, dest_port, length, checksum = struct.unpack("! H H H H", raw_data[0:8])

    udp_header = UDPHeader(src_port, dest_port, length, checksum)
    data = raw_data[8:]

    return udp_header, data


# HTTP (Layer 7) header
def http_parse(raw_data: bytes):
    pass


# create a raw socket and bind it to the public interface
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
s.bind((iface, 0))

while True:
    print(f"{'Raw Packet':*^120}")

    # receive a packet
    raw_data, addr = s.recvfrom(65565)
    ether_header, data = ethernet_parser(raw_data)

    print(f"Ethernet Header:\n\t- {ether_header}")

    """Ether Type
    IPv4: 0x0800 
    ARP:  0X0806
    IPv6: 0x86DD
    """
    if ether_header.ether_type == 0x0800:
        ipv4_header, data = ipv4_parser(data)
        print(f"IPv4 Header:\n\t- {ipv4_header}")

        """IP protocol
        TCP: 6
        ICMP: 1
        UDP: 17
        RDP: 27
        """
        if ipv4_header.protocol == 6:
            tcp_header, data = tcp_parser(data)
            print(f"TCP Header:")
            print("\t - " + "Source Port: {}, Destination Port: {}".format(tcp_header.src_port, tcp_header.dest_port))
            print("\t - " + "Sequence: {}, Acknowledgment: {}".format(tcp_header.seq, tcp_header.ack))
            print("\t - " + "Flags:")
            print(
                "\t\t - " + "URG: {}, ACK: {}, PSH:{}".format(tcp_header.flag_urg, tcp_header.ack, tcp_header.flag_psh)
            )
            print(
                "\t\t - "
                + "RST: {}, SYN: {}, FIN:{}".format(tcp_header.flag_rst, tcp_header.flag_syn, tcp_header.flag_fin)
            )
            print("\t - " + "TCP Data:")
            print("\t\t - " + "{}".format(binascii.hexlify(data, " ")))
            # print("\t\t\t - " + "{}".format(data))

            if len(data) > 0:
                # HTTP
                if tcp_header.src_port == 80 or tcp_header.dest_port == 80:
                    print("\t\t - " + "HTTP Data:")

        elif ipv4_header.protocol == 1:
            icmp_header, data = icmp_parser(data)
            print(f"ICMP Packet:")
            print(
                "\t -"
                + "Type: {}, Code: {}, Checksum:{},".format(icmp_header.type, icmp_header.code, icmp_header.checksum)
            )
            print("\t -" + "ICMP Data:")
            print("\t\t - " + "{}".format(binascii.hexlify(data, " ")))
            # print("\t\t\t - " + "{}".format(data))

        elif ipv4_header.protocol == 17:
            udp_header, data = udp_parser(data)
            print(f"UDP Segment:")
            print(
                "\t -"
                + "Source Port: {}, Destination Port: {}, Length: {}, Checksum: {}".format(
                    udp_header.src_port, udp_header.dest_port, udp_header.length, udp_header.checksum
                )
            )
            print("\t\t - " + "{}".format(binascii.hexlify(data, " ")))

    print(f"{'':*^120}")
    print(f"\n\n")
