import sys
import ctypes

from driver import connect


async def init():
    # Privilege check. macOS uses Apple's native tunnel via remotepairingd, so
    # it needs no root at all; other platforms still build their own tun device.
    if sys.platform == "win32":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("请以管理员权限运行")
            sys.exit(1)
    elif sys.platform != "darwin":
        print("仅支持 macOS 和 Windows")
        sys.exit(1)

    # get lockdown client
    lockdown = await connect.get_usbmux_lockdownclient()

    # check version
    version = connect.get_version(lockdown)
    print(f"Your system version is {version}")
    # Compare as a number: "9" < "17" is False as a string comparison, which
    # would let an unsupported device through.
    try:
        major = int(str(version).split(".")[0])
    except (TypeError, ValueError):
        major = 0
    if major < 17:
        print("仅支持 17 及以上版本")
        sys.exit(1)

    # check developer mode status
    if not await connect.get_developer_mode_status(lockdown):
        await connect.reveal_developer_mode(lockdown)
        print("您未开启开发者模式，请打开设备的 设置-隐私与安全性-开发者模式 来开启，"
              "开启后需要重启并输入密码，完成后再次运行此程序")
        sys.exit(1)
