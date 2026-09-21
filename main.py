import asyncio
import logging
import os
import sys

import coloredlogs

try:
    from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
    from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
except ImportError as exc:
    print(f"依赖缺失或版本不匹配：{exc}")
    print(f"当前解释器：{sys.executable}")
    print("本项目需要 requirements.txt 中锁定的 pymobiledevice3 版本。")
    print("请在项目目录下执行 ./run.sh，它会自动创建虚拟环境并用正确的解释器启动。")
    sys.exit(1)

from init import init
from init import tunnel
from init import route

import run

import config


debug = os.environ.get("DEBUG", False)

# set logging level
coloredlogs.install(level=logging.DEBUG if debug else logging.INFO)
for name in ('quic', 'asyncio', 'zeroconf', 'parso.cache', 'parso.cache.pickle',
             'parso.python.diff', 'humanfriendly.prompts',
             'blib2to3.pgen2.driver', 'urllib3.connectionpool'):
    logging.getLogger(name).setLevel(logging.DEBUG if debug else logging.WARNING)


async def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    await init.init()
    logger.info("init done")

    # get route before touching the device, so a bad route file fails fast
    loc = route.get_route()
    logger.info(f"got route from {config.config.routeConfig}")

    logger.info("starting tunnel")
    try:
        async with tunnel.open_tunnel() as rsd:
            logger.info("tunnel started")
            async with DvtProvider(rsd) as dvt:
                async with LocationSimulation(dvt) as sim:
                    try:
                        print(f"已开始模拟跑步，速度大约为 {config.config.v} m/s")
                        print("会无限循环，按 Ctrl+C 退出")
                        print("请勿直接关闭窗口，否则无法还原正常定位")
                        await run.run(sim, loc, config.config.v,
                                      variation=getattr(config.config, 'speedVariation', 0.12))
                    except (KeyboardInterrupt, asyncio.CancelledError):
                        logger.debug("get KeyboardInterrupt")
                    finally:
                        logger.debug("Start to clear location")
                        await sim.clear()
                        logger.info("Location cleared")
    except tunnel.TunnelStartError as exc:
        print(f"隧道建立失败：{exc}")
        print("常见原因：")
        print("  1. 设备未解锁，或没有在设备上点「信任」，请看一眼手机屏幕后重试")
        print("  2. 数据线或接口问题，换一根线/换个口")
        print("  3. 用 DEBUG=1 ./run.sh 重跑可以看到完整错误堆栈")
        sys.exit(1)
    finally:
        print("Bye")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
