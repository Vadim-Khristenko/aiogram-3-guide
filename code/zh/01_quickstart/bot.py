# 导入必要的模块
import asyncio                 # 用于异步编程
import logging                 # 用于记录机器人的日志
from datetime import datetime  # 用于处理日期和时间

# 导入 aiogram 的主要组件
from aiogram import Bot, Dispatcher, types      # 创建机器人的基本类
from aiogram.enums.dice_emoji import DiceEmoji  # 骰子游戏的表情符号
from aiogram.filters.command import Command     # 用于处理命令的过滤器

# 导入配置
from config_reader import config  # 从配置文件加载设置

# 为机器人配置日志
logging.basicConfig(level=logging.INFO)

# 使用配置中的令牌创建机器人实例
bot = Bot(token=config.bot_token.get_secret_value())

# 创建调度程序来处理事件
dp = Dispatcher()

# 将机器人启动时间保存到调度程序上下文中
# 这个值将通过依赖注入在所有处理程序中可用
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


# /start 命令的处理程序
# 装饰器自动将函数注册为处理程序
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """处理 /start 命令 - 向用户问好"""
    await message.answer("你好！")


# /test1 命令的处理程序
# 使用装饰器处理命令的简单示例
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    """处理 /test1 命令 - 发送测试消息"""
    await message.reply("测试 1")


# /test2 命令的处理程序
# 没有装饰器，因为在 main() 函数中手动注册
# 这是注册处理程序的替代方法
async def cmd_test2(message: types.Message):
    """处理 /test2 命令 - 演示手动注册"""
    await message.reply("测试 2")


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    """演示 answer() 方法 - 发送普通回复"""
    await message.answer("这是一个简单的回复")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    """演示 reply() 方法 - 发送带引用的回复"""
    await message.reply('这是带有"回复"的回复')


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    """发送游戏骰子 - 演示特殊类型的消息"""
    await message.answer_dice(emoji=DiceEmoji.DICE)


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    """
    演示依赖注入 - 从调度程序上下文中获取列表
    mylist 在机器人启动时自动传递
    """
    mylist.append(7)
    await message.answer("已添加数字 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    """显示上下文中列表的当前内容"""
    await message.answer(f"您的列表：{mylist}")


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    """
    演示从调度程序上下文中获取数据
    started_at 自动从 dp["started_at"] 传递
    """
    await message.answer(f"机器人启动于 {started_at}")


async def main():
    """主函数用于设置和启动机器人"""

    # 演示手动注册处理程序
    # 使用装饰器的替代方法
    dp.message.register(cmd_test2, Command("test2"))

    # 启动机器人并跳过所有累积的更新。
    # 在重新启动机器人时很有用，以避免处理旧消息。
    # 是的，即使您使用的是长轮询，也可以使用此方法。
    await bot.delete_webhook(drop_pending_updates=True)

    # 在长轮询模式下启动机器人
    # mylist=[1, 2, 3] 传递到调度程序上下文以进行依赖注入
    await dp.start_polling(bot, mylist=[1, 2, 3])


if __name__ == "__main__":
    # 在异步模式下运行主函数
    # 程序的入口点
    asyncio.run(main())
