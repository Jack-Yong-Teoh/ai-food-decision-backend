import ipaddress
from fastapi import Request
from app.models.exceptions.logic_exception import LogicException
from app.utilities.error_message import general_error


def get_ip_address(request: Request) -> str:
    client_host = request.client.host
    forward_for = request.headers.get("x-forwarded-for")
    real_ip = request.headers.get("x-real-ip")
    ip_address = real_ip if real_ip else forward_for if forward_for else client_host
    return ip_address or "127.0.0.1"


def is_public_ip(ip_address: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_address)
        return not (
            ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
        )
    except ValueError as e:
        raise LogicException(general_error("INVALID IP ADDRESS FORMAT")) from e
