#!/usr/bin/python3
import sys
import asyncio
import telepot
import datetime
import time
import re
import uuid
import random
import argparse
from telepot.async.delegate import per_from_id, create_open, per_chat_id
import libs.Models as Models
import libs.Loggiz as Loggiz
import libs.SerializableDict as SerializableDict
import libs.StorageObjects as StorageObjects
import libs.TelepotObjects as TelepotObjects
import Commands
'''
Copyright (c) 2016, Egil Hasting
All rights reserved.
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
'''
__author__ = "Egil Hasting"
__copyright__ = "Copyright 2016"
__credits__ = ["Egil Hasting"]
__license__ = "BSD"
__version__ = "1.0.0"
__maintainer__ = "Egil Hasting"
__email__ = "egil.hasting@higen.org"
__status__ = "Production"

"""
$ python3.4 psybot.py --token <token>
Tracks user and quotes.
"""


class UserTracker(telepot.async.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout, dbobject):
        super(UserTracker, self).__init__(seed_tuple, timeout)
        self.db = dbobject
        self.uindex = dbobject.Get("userindex")

    @asyncio.coroutine
    def on_chat_message(self, msg):
        Loggiz.L.info("Incomming message: {}".format(str(msg)))
        if msg.get("text"):
            currentmessage = TelepotObjects.MessageObject.CreateFromMessage(msg)
            cnt = yield from Commands.Counter("NoCommand", self.sender, self.db, currentmessage).run()
            Loggiz.L.Print(currentmessage.text)
            if currentmessage.text.startswith("!seen"):
                a = yield from Commands.Seen("!seen", self.sender, self.db, currentmessage).run()
            elif currentmessage.text.startswith("!addquote"):
                a = yield from Commands.AddQuote("!addquote", self.sender, self.db, currentmessage).run()
            elif currentmessage.text.startswith("!quote"):
                a = yield from Commands.Quote("!quote", self.sender, self.db, currentmessage).run()
            elif currentmessage.text.startswith("!search"):
                a = yield from Commands.WebSearchDuckDuckGo("!search", self.sender, self.db, currentmessage).run()
            elif currentmessage.text.startswith("!stats"):
                a = yield from Commands.Stats("!stats", self.sender, self.db, currentmessage).run()
        flavor = telepot.flavor(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", dest="debug", action="store_true", default=False)
    #parser.add_argument('--token', dest='token', type=str, required=True)
    settings = parser.parse_args(sys.argv[1:])
    if settings.debug is True:
        Loggiz.L.setlevel(7)
    else:
        Loggiz.L.setlevel(3)  # 3

    T = "214276085:AAG5fqcTWnAIMbC3co5THYoj1icSA95T2bo"

    dbobject = Models.StaticModels()
    bot = telepot.async.DelegatorBot(T, [
    #bot = telepot.async.DelegatorBot(settings.token, [
        (per_chat_id(), create_open(UserTracker, timeout=30, dbobject=dbobject)),
    ])
    loop = asyncio.get_event_loop()

    loop.create_task(bot.messageLoop())
    Loggiz.L.Print('Starting Bot ...')
    # Loggiz.L.Print(bot.getMe())

    loop.run_forever()
