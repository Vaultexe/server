from typing import Annotated

from fastapi import Depends, Request
from pydantic import IPvAnyAddress


def get_ip(req: Request) -> IPvAnyAddress:
    """Returns the IP address of the client making the request"""
    if ip := req.headers.get("X-Forwarded-For"):
        return ip.split(",", 1)[0]  # type: ignore
    return req.client.host  # type: ignore


reqIpDep = Annotated[IPvAnyAddress, Depends(get_ip)]
