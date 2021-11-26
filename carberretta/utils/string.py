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

import typing as t
from string import Formatter

import hikari

ORDINAL_ENDINGS: t.Final = {"1": "st", "2": "nd", "3": "rd"}


class MessageFormatter(Formatter):
    def get_value(
        self, key: int | str, *args: t.Sequence[t.Any], kwargs: dict[str, t.Any]
    ) -> str:
        if isinstance(key, str):
            try:
                return kwargs[key]
            except KeyError:
                return "<BAD_VARIABLE>"
        else:
            return super().get_value(key, args, kwargs)


def safe_format(text: str, *args, **kwargs) -> str:
    formatter = MessageFormatter()
    return formatter.format(text, *args, **kwargs)


def text_is_formattible(text: str) -> t.Union[str, bool]:
    try:
        return safe_format(text)
    except:
        return False


def list_of(items: list, sep: str = "and") -> str:
    if len(items) > 2:
        return f"{', '.join(items[:-1])}, {sep} {items[-1]}"

    return f" {sep} ".join(items)


def ordinal(number: int) -> str:
    if str(number)[-2:] not in ("11", "12", "13"):
        return f"{number:,}{ORDINAL_ENDINGS.get(str(number)[-1], 'th')}"

    return f"{number:,}th"


def possessive(user: hikari.Member | hikari.User) -> str:
    name = getattr(user, "display_name", user.name)
    return f"{name}'{'s' if not name.endswith('s') else ''}"