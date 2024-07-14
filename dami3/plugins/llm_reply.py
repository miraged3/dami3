import random
from collections import defaultdict
from typing import Dict, List

import nonebot
from nonebot import on_message, logger
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import EventMessage
from nonebot.rule import is_type
from zhipuai import ZhipuAI

config = nonebot.get_driver().config
llm_reply = on_message(rule=is_type(GroupMessageEvent), block=True)
RecentMessages = Dict[int, List[str]]
recent_messages: RecentMessages = defaultdict(list)
client = ZhipuAI(api_key=config.zhipu_api_key)


@llm_reply.handle()
async def handle_function(event: GroupMessageEvent, msg: Message = EventMessage()):
    if 'CQ' not in str(msg):
        recent_messages[event.group_id].append(str(event.sender.nickname) + '：' + str(msg))
    if len(recent_messages[event.group_id]) > int(config.llm_recent_messages):
        recent_messages[event.group_id].pop(0)
    if random_by_percentage(int(config.llm_percentage)):
        logger.info('Requesting LLM: ' + config.zhipu_api_prompt + '\n' + str(recent_messages[event.group_id]))
        response = client.chat.completions.create(
            model='glm-4-0520',
            messages=[
                {'role': 'user',
                 'content': config.zhipu_api_prompt + '\n' + str(recent_messages[event.group_id])}
            ],
            stream=False
        )
        reply_text = response.choices[0].message.content
        if reply_text.startswith('大米：'):
            reply_text = reply_text[3:]
        recent_messages[event.group_id].append('大米：' + reply_text)
        await llm_reply.finish(reply_text)
    else:
        await llm_reply.finish()


def random_by_percentage(percentage: float) -> bool:
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")
    return random.uniform(0, 100) <= percentage
