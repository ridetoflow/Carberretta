# Copyright (c) 2020-2021, Carberra Tutorials
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime as dt
import typing as t

import hikari
from lightbulb import plugins

if t.TYPE_CHECKING:
    from lightbulb.app import BotApp

from carberretta import Config

TIMEOUT = 600

plugin = plugins.Plugin("Gateway")


async def schedule_action(member: hikari.Member, secs: int = TIMEOUT) -> None:
    async def _take_action(member: hikari.Member) -> None:
        if member.is_pending:
            return await member.kick(
                reason=(
                    "Member failed to accept the server rules before "
                    "being timed out."
                )
            )

        for role in [Config.ANNOUNCEMENTS_ROLE_ID, Config.VIDEOS_ROLE_ID]:
            await plugin.bot.rest.add_role_to_member(
                Config.GUILD_ID,
                member,
                role,
                reason="Member accepted the server rules.",
            )

    plugin.bot.d.scheduler.add_job(
        _take_action,
        id=f"{member.id}",
        next_run_time=dt.datetime.utcnow() + dt.timedelta(seconds=secs),
        args=[member],
    )


@plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    now = dt.datetime.now().astimezone()
    
    async for m in plugin.bot.rest.fetch_members(Config.GUILD_ID):
        if (secs := (now - m.joined_at).seconds) <= TIMEOUT:
            await schedule_action(m, secs=TIMEOUT - secs)
        elif m.is_pending:
            await m.kick(
                reason=(
                    "Member failed to accept the server rules before "
                    "being timed out."
                )
            )


@plugin.listener(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    if event.member.guild_id != Config.GUILD_ID:
        return
    
    await schedule_action(event.member)


@plugin.listener(hikari.MemberDeleteEvent)
async def on_member_leave(event: hikari.MemberDeleteEvent) -> None:
    member = event.old_member

    if not member:
        return

    if member.guild_id != Config.GUILD_ID:
        return

    try:
        plugin.bot.d.scheduler.get_job(f"{member.id}").remove()
        return
    except AttributeError:
        if member.is_pending:
            return

        await plugin.bot.rest.create_message(
            Config.GATEWAY_CHANNEL_ID,
            f"{member.display_name} is no longer in the server. " f"(ID: {member.id})",
        )


@plugin.listener(hikari.MemberUpdateEvent)
async def on_member_update(event: hikari.MemberUpdateEvent) -> None:
    if event.member.guild_id != Config.GUILD_ID:
        return

    if not event.old_member or not event.member:
        return

    if event.old_member.is_pending != event.member.is_pending:
        humans = len(
            [
                m
                async for m in plugin.bot.rest.fetch_members(Config.GUILD_ID)
                if not m.is_bot
            ]
        )
        await plugin.bot.rest.create_message(
            Config.GATEWAY_CHANNEL_ID,
            f"Welcome {event.member.mention}! You are member nº {humans:,} of "
            "Carberra Tutorials (excluding bots). Make yourself at home "
            "in <#626608699942764548>, and look at <#739572184745377813> "
            "to find out how to get support.",
        )


def load(bot: "BotApp") -> None:
    bot.add_plugin(plugin)


def unload(bot: "BotApp") -> None:
    bot.remove_plugin(plugin)
