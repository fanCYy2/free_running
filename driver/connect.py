import sys

from pymobiledevice3.lockdown import create_using_usbmux, LockdownClient
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.exceptions import NoDeviceConnectedError


def _wait_for_enter(prompt: str) -> None:
    """Prompt and wait, but do not blow up when there is no console.

    Without a tty (piped output, launchd, CI) input() raises EOFError, which
    used to surface as a traceback rather than as the actual problem.
    """
    print(prompt)
    try:
        input()
    except EOFError:
        print("没有可用的终端输入，请在交互式终端中运行本程序。")
        sys.exit(1)


async def get_usbmux_lockdownclient() -> LockdownClient:
    while True:
        try:
            await create_using_usbmux()
        except NoDeviceConnectedError:
            _wait_for_enter("请连接设备后按回车...")
        else:
            break
    while True:
        lockdown = await create_using_usbmux()
        if lockdown.all_values.get("PasswordProtected"):
            _wait_for_enter("请解锁设备后按回车...")
        else:
            break
    return await create_using_usbmux()


def get_version(lockdown: LockdownClient) -> str:
    return lockdown.product_version


async def get_developer_mode_status(lockdown: LockdownClient) -> bool:
    return await lockdown.get_developer_mode_status()


async def reveal_developer_mode(lockdown: LockdownClient) -> None:
    await AmfiService(lockdown).reveal_developer_mode_option_in_ui()


def uses_native_tunnel() -> bool:
    """macOS can borrow Apple's own tunnel instead of building one."""
    return sys.platform == "darwin"
