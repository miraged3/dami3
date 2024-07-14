import datetime
import json
import random

import nonebot
from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.internal.rule import Rule
from nonebot.rule import is_type


async def is_enable() -> bool:
    # 获取当前日期和时间
    current_date = datetime.datetime.now()

    # 判断当前是否是周四（周四的weekday()返回值为3）
    return current_date.weekday() == 3


config = nonebot.get_driver().config
kfc = on_message(rule=Rule(is_enable, is_type(GroupMessageEvent)), block=True)


def get_kfc_data():
    # 读取JSON文件内容
    with open('kfc_data.json', 'r') as file:
        data = json.load(file)

    # 从列表中随机选择一个值
    return random.choice(data)


@kfc.handle()
async def handle_function():
    if random_by_percentage(int(config.kfc_percentage)):
        await kfc.finish(get_kfc_data())
    else:
        await kfc.finish()


def random_by_percentage(percentage: float) -> bool:
    if not 0 <= percentage <= 1000:
        raise ValueError("Percentage must be between 0 and 1000.")
    return random.uniform(0, 1000) <= percentage
