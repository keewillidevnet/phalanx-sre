from typing import Literal

Protocol = Literal["tcp", "udp"]

def five_tuple_bpf(src_ip: str, src_port: int, dst_ip: str, dst_port: int, proto: Protocol = "tcp") -> str:
    p = proto.lower()
    return f'{p} and (host {src_ip} and port {src_port}) and (host {dst_ip} and port {dst_port})'

def service_bpf(host_a: str, host_b: str, port: int, proto: Protocol="tcp") -> str:
    p = proto.lower()
    return f'{p} and host {host_a} and host {host_b} and port {port}'
