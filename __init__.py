import os
from pathlib import Path
import shutil
import asyncio

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, Bot, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from zhenxun.configs.path_config import IMAGE_PATH
from zhenxun.configs.utils import Command, PluginExtraData
from zhenxun.services.log import logger
from zhenxun.services.plugin_init import PluginInit
from zhenxun.utils.message import MessageUtils

__plugin_meta__ = PluginMetadata(
    name="拍他 & 拍死他",
    description="拍他一次 / 拍他五次",
    usage="""
    指令：
      - 拍他 @某人 （戳一下）
      - 拍死他 @某人（戳五次）
    """.strip(),
    extra=PluginExtraData(
        author="阿珏酱", version="1.0", commands=[
            Command(command="拍他"),
            Command(command="拍死他")
        ]
    ).to_dict(),
)

RESOURCE_PATH = IMAGE_PATH / "pat"

pat_cmd = on_command("拍他", priority=5, block=True)
pat_hard_cmd = on_command("拍死他", priority=5, block=True)


async def try_poke(bot: Bot, event: GroupMessageEvent, at_qq: str, times: int = 1):
    try:
        group_id = event.group_id
        for _ in range(times):
            await bot.send_poke(group_id=group_id, user_id=int(at_qq))
            await asyncio.sleep(0.8)
        logger.info(f"已成功戳{times}次，目标QQ: {at_qq}", "拍他")
    except Exception as e:
        logger.error(f"发送戳一戳失败: {e}", "拍他")
        await MessageUtils.build_message(f"戳他失败了: {str(e)}").finish()


@pat_cmd.handle()
async def handle_pat(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    at_qq = None
    for seg in arg:
        if seg.type == "at":
            at_qq = seg.data.get("qq", "")
            break
    if not at_qq:
        await MessageUtils.build_message("请@一个人来拍他").finish()
    await try_poke(bot, event, at_qq, times=1)


@pat_hard_cmd.handle()
async def handle_pat_hard(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    at_qq = None
    for seg in arg:
        if seg.type == "at":
            at_qq = seg.data.get("qq", "")
            break
    if not at_qq:
        await MessageUtils.build_message("请@一个人来拍死他").finish()
    await try_poke(bot, event, at_qq, times=5)


class MyPluginInit(PluginInit):
    async def install(self):
        pass

    async def remove(self):
        if RESOURCE_PATH.exists():
            shutil.rmtree(RESOURCE_PATH)
            logger.info(f"删除 拍他资源文件夹成功 {RESOURCE_PATH}")
