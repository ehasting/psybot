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


class ChatObject(object):
    def __init__(self, title, cid, ctype):
        self.title = title
        self.id = cid
        self.type = ctype


class UserObject(object):
    def __init__(self, last_name, first_name, username, uid):
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.id = uid


class PrivateObject(UserObject):
    def __init__(self, last_name, first_name, username, uid):
        UserObject.__init__(self, last_name, first_name, username, uid)
        self.mtype = "private"


class MessageObject(object):
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.message_id = -1
        self.mfrom = None
        self.chat = None
        self.text = None

    def __str__(self):
        return "{} {} {}".format(self.timestamp, self.message_id, self.text)

    @staticmethod
    def CreateFromMessage(msg):
        d = MessageObject()
        d.timestamp = msg["date"]
        d.message_id = msg["message_id"]
        d.mfrom = UserObject(msg["from"]["last_name"], msg["from"]["first_name"], msg["from"].get("username", ""), msg["from"]["id"])
        if msg["chat"]["type"] == "private":
            d.chat = PrivateObject(msg["from"]["last_name"], msg["from"]["first_name"], msg["from"].get("username", ""), msg["chat"]["id"])
        elif msg["chat"]["type"] == "group":
            d.chat = ChatObject(msg["chat"]["title"], msg["chat"]["id"], msg["chat"]["type"])
        d.text = msg["text"]
        return d


class UserTracker(telepot.async.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout, dbobject):
        super(UserTracker, self).__init__(seed_tuple, timeout)
        self.db = dbobject
        self.uindex = dbobject.Get("userindex")

    def get_quote(self, username):
        quotemetausername = StorageObjects.ComnodeObject("quotemap.{}".format(username), "list", desc="", hidden=False)
        qmun = quotemetausername.Get()
        if len(qmun) > 0:
            foundindex = random.randrange(0, len(qmun))
            if len(qmun) == foundindex:
                foundindex = foundindex - 1
            quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(qmun[foundindex]), "str", desc="", hidden=False)
            return "{}: {}".format(username, quotetext.Get())
        else:
            return None

    @asyncio.coroutine
    def on_chat_message(self, msg):
        Loggiz.L.info("Incomming message: {}".format(str(msg)))
        if msg.get("text"):
            d = MessageObject.CreateFromMessage(msg)
            seen = dbobject.Get("seenlog")
            user = seen.usercounter.Get()
            usercount = user.get(d.mfrom.username)
            usercountobject = SerializableDict.UserObject(usercount)

            if usercountobject.counter == "":
                usercountobject.counter = 1
                usercountobject.modified = str(datetime.datetime.now())
            else:
                usercountobject.counter = usercountobject.counter + 1
                usercountobject.modified = str(datetime.datetime.now())

            user.set(d.mfrom.username, usercountobject.SaveObject())
            seen.usercounter.Set(user)
            if d.text.startswith("!seen"):
                found = None
                m = re.search('^(!seen)\s(.*)[$\s.]+$', d.text)
                if m is not None:
                    found = m.groups()
                else:
                    m = re.search('^(!seen)\s(.*)$', d.text)
                    if m is not None:
                        found = m.groups()
                if found is not None:
                    fetchseenuser = user.get(found[1])
                    userseenobject = SerializableDict.UserObject(fetchseenuser)
                    if userseenobject.modified != "":
                        yield from self.sender.sendMessage("hey! {} was last seen {} (message count: {})".format(found[1], userseenobject.modified, userseenobject.counter))
            elif d.text.startswith("!addquote"):

                new_quote_index = str(uuid.uuid4())

                m = re.search('^(!addquote)\s+(.*): (.*)$', d.text)
                if m is not None:
                    found = m.groups()
                    if len(found) != 3:
                        yield from self.sender.sendMessage('[USAGE] !addquote <username>: <quote>')
                    if found[1] not in self.uindex.index.Get():
                        tmplist = self.uindex.index.Get()
                        tmplist.append(found[1])
                        self.uindex.index.Set(tmplist)
                        Loggiz.L.info("user/nick added to index")
                    quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(new_quote_index), "str", desc="", hidden=False)
                    quotetext.Set(found[2])
                    
                    quotemetausername = StorageObjects.ComnodeObject("quotemap.{}".format(found[1]), "list", desc="", hidden=False)
                    qmun = quotemetausername.Get()
                    qmun.append(new_quote_index)
                    quotemetausername.Set(qmun)
                    yield from self.sender.sendMessage("Quote from {} added with id {}".format(found[1], new_quote_index))
                else:
                    yield from self.sender.sendMessage('[USAGE] !addquote <username>: <quote>')
            elif d.text.startswith("!quote"):
                quoteoutput = None
                found = None
                qsentence = re.search('^.*(!quote)\s(.*)[$\s.]+$', d.text)
                qdirect = re.search('.*(!quote)\s(.*)$', d.text)
                qsingle = re.search('^(!quote)$', d.text)
                if qsentence is not None:
                    found = qsentence.groups()
                    Loggiz.L.info("quote found in sentence")
                    quoteoutput = self.get_quote(found[1])
                elif qdirect is not None:
                    found = qdirect.groups()
                    Loggiz.L.info("quote found direct")
                    quoteoutput = self.get_quote(found[1])
                elif qsingle is not None:
                    found = qsingle.groups()
                    Loggiz.L.info("quote found single")
                    userindexlength = len(self.uindex.index.Get())
                    if userindexlength == 0:
                        return
                    luckyuser = random.randrange(0, userindexlength)
                    if len(self.uindex.index.Get()) == luckyuser:
                        luckyuser = luckyuser - 1
                    quoteoutput = self.get_quote(self.uindex.index.Get()[luckyuser])
                if found is not None:
                    if quoteoutput is not None:
                        yield from self.sender.sendMessage(quoteoutput)
        flavor = telepot.flavor(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", dest="debug", action="store_true", default=False)
    parser.add_argument('--token', dest='token', type=str, required=True)
    settings = parser.parse_args(sys.argv[1:])
    if settings.debug is True:
        Loggiz.L.setlevel(7)
    else:
        Loggiz.L.setlevel(3)


    dbobject = Models.StaticModels()

    bot = telepot.async.DelegatorBot(settings.token, [
        (per_chat_id(), create_open(UserTracker, timeout=30, dbobject=dbobject)),
    ])
    loop = asyncio.get_event_loop()

    loop.create_task(bot.messageLoop())
    Loggiz.L.Print('Starting Bot ...')
    # Loggiz.L.Print(bot.getMe())

    loop.run_forever()
