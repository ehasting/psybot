import datetime
import asyncio
import re
import uuid
import random
import libs.TelepotObjects as TelepotObjects
import libs.SerializableDict as SerializableDict
import libs.StorageObjects as StorageObjects
import libs.Loggiz as Loggiz
import libs.Models as Models
import telepot.helper
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

class GeneralMessageEvent(object):
    def __init__(self, bot, dbobject, messageobject):
        self.dbobject = dbobject
        self.messageobject = messageobject
        self.bot = bot
        self.isvalid = True
        self._validate()

    def _validate(self):
        if not isinstance(self.messageobject, TelepotObjects.MessageObject):
            self.isvalid = False
        if not isinstance(self.dbobject, Models.StaticModels):
            self.isvalid = False
        if not isinstance(self.bot, telepot.telepot.helper.Sender):
            self.isvalid = False
        if not self.isvalid:
            Loggiz.L.err("GeneralMessageEvent() - Object did not validate")

    @asyncio.coroutine
    def run(self):
        raise NotImplementedError()


class Counter(GeneralMessageEvent):
    def __init__(self, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, bot, dbobject, messageobject)
        self.seen = self.dbobject.Get("seenlog")

    @asyncio.coroutine
    def run(self):
        user = self.seen.usercounter.Get()
        usercount = user.get(self.messageobject.mfrom.username)
        usercountobject = SerializableDict.UserObject(usercount)
        if usercountobject.counter == "":
            usercountobject.counter = 1
            usercountobject.modified = str(datetime.datetime.now())
        else:
            usercountobject.counter = usercountobject.counter + 1
            usercountobject.modified = str(datetime.datetime.now())
        user.set(self.messageobject.mfrom.username, usercountobject.SaveObject())
        self.seen.usercounter.Set(user)


class Seen(GeneralMessageEvent):
    def __init__(self, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, bot, dbobject, messageobject)
        self.seendb = self.dbobject.Get("seenlog")

    @asyncio.coroutine
    def run(self):
        Loggiz.L.Print(self.messageobject.text)
        user = self.seendb.usercounter.Get()
        found = None
        m = re.search('^(!seen)\s(.*)[$\s.]+$', self.messageobject.text)
        if m is not None:
            found = m.groups()
        else:
            m = re.search('^(!seen)\s(.*)$', self.messageobject.text)
            if m is not None:
                found = m.groups()
        if found is not None:
            fetchseenuser = user.get(found[1])
            userseenobject = SerializableDict.UserObject(fetchseenuser)
            if userseenobject.modified != "":
                yield from self.bot.sendMessage("hey! {} was last seen {} (message count: {})".format(found[1], userseenobject.modified, userseenobject.counter))
            else:
                Loggiz.L.Print("Did not find any user!")


class QuoteBase(GeneralMessageEvent):
    def __init__(self, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, bot, dbobject, messageobject)
        self.uindex = self.dbobject.Get("userindex")


class AddQuote(QuoteBase):
    def __init__(self, bot, dbobject, messageobject):
        QuoteBase.__init__(self, bot, dbobject, messageobject)

    @asyncio.coroutine
    def run(self):
        new_quote_index = str(uuid.uuid4())

        m = re.search('^(!addquote)\s+(.*): (.*)$', self.messageobject.text)
        if m is not None:
            found = m.groups()
            if len(found) != 3:
                yield from self.bot.sendMessage('[USAGE] !addquote <username>: <quote>')
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
            yield from self.bot.sendMessage("Quote from {} added with id {}".format(found[1], new_quote_index))
        else:
            yield from self.bot.sendMessage('[USAGE] !addquote <username>: <quote>')


class Quote(QuoteBase):
    def __init__(self, bot, dbobject, messageobject):
        QuoteBase.__init__(self, bot, dbobject, messageobject)

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
    def run(self):
        quoteoutput = None
        found = None
        qsentence = re.search('^.*(!quote)\s(.*)[$\s.]+$', self.messageobject.text)
        qdirect = re.search('.*(!quote)\s(.*)$', self.messageobject.text)
        qsingle = re.search('^(!quote)$', self.messageobject.text)
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
                yield from self.bot.sendMessage(quoteoutput)
