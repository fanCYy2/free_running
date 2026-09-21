"""Open a RemoteXPC tunnel and hand back an RSD to talk to the device over."""

import sys
from contextlib import asynccontextmanager

from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService


class TunnelStartError(RuntimeError):
    """The tunnel could not be established."""


@asynccontextmanager
async def open_tunnel():
    """Yield a connected RemoteServiceDiscoveryService.

    On macOS this asks `remotepairingd` -- the daemon Xcode itself uses -- for a
    tunnel. That path needs no root and no tun device of our own, and it is the
    only one iOS 18 accepts: the classic QUIC tunnel gets its TLS handshake
    refused by the device.
    """
    if sys.platform == "darwin":
        from pymobiledevice3.remote.native_tunnel import establish_native_rsd
        try:
            rsd = await establish_native_rsd()
        except Exception as exc:
            raise TunnelStartError(f"无法建立 macOS 原生隧道：{exc}") from exc
        try:
            yield rsd
        finally:
            await rsd.close()
        return

    # Windows and friends: build the tunnel ourselves. Needs Administrator.
    # Untested here -- this project is developed on macOS.
    from pymobiledevice3.remote.tunnel_service import (
        CoreDeviceTunnelProxy, start_tunnel)
    from driver import connect

    lockdown = await connect.get_usbmux_lockdownclient()
    try:
        async with start_tunnel(CoreDeviceTunnelProxy(lockdown)) as tunnel_result:
            rsd = RemoteServiceDiscoveryService(
                (tunnel_result.address, tunnel_result.port))
            await rsd.connect()
            try:
                yield rsd
            finally:
                await rsd.close()
    except TunnelStartError:
        raise
    except Exception as exc:
        raise TunnelStartError(f"无法建立隧道：{exc}") from exc
