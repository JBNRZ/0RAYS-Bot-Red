import nonebot
from nonebot.adapters.red import Adapter as RedAdapter


nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(RedAdapter)

nonebot.load_builtin_plugin("echo")
nonebot.load_plugins("nonebot2/plugins")


if __name__ == "__main__":
    nonebot.run()
