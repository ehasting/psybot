import datetime
import asyncio
import re
import requests
import json
import uuid
import random
import calendar
import time
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
    def __init__(self, keyword, bot, dbobject, messageobject):
        self.keyword = keyword
        self.dbobject = dbobject
        self.messageobject = messageobject
        self.bot = bot
        self.isvalid = True
        self._validate()

    def _validate(self):
        if self.keyword is None:
            self.isvalid = False
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


class WebSearchDuckDuckGo(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)

    def _generate_url(self, searchstring):
        searchstring = searchstring.replace(" ", "+")
        print(searchstring)
        return "http://api.duckduckgo.com/?q={}&format=json".format(searchstring)

    @asyncio.coroutine
    def run(self):
        found = None
        m = re.search('^({})\s(.*)[$\s.]+$'.format(self.keyword), self.messageobject.text)
        if m is not None:
            found = m.groups()
        else:
            m = re.search('^({})\s(.*)$'.format(self.keyword), self.messageobject.text)
            if m is not None:
                found = m.groups()
        if found is not None:
            r = requests.get(self._generate_url(found[1]))
            if r.status_code == 200:
                searchresult = r.json()
                resultcount = len(searchresult["RelatedTopics"])
                outputstring = "{} (found: {})\n".format(searchresult["Heading"], resultcount)
                limitcounter = 0
                for article in searchresult["RelatedTopics"]:
                    outputstring += article.get("Result", "") + "\n"
                    d = article.get("Result", "")
                    if d == "":
                        print(article)
                    limitcounter += 1
                    if limitcounter == 3:
                        break
                yield from self.bot.sendMessage("{}".format(outputstring), parse_mode="HTML")
        else:
            Loggiz.L.err("Missing search term")


class Time(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)

    @asyncio.coroutine
    def run(self):
        out = "<b>Current Time</b>\n"
        os.environ['TZ'] = 'US/Eastern'
        time.tzset()
        time.tzname
        out += str(time.strftime('%X %x %Z')) + "\n"
        os.environ['TZ'] = 'Oslo'
        time.tzset()
        time.tzname
        out += str(time.strftime('%X %x %Z'))
        Loggiz.L.info(out)
        yield from self.bot.sendMessage("{}".format(out), parse_mode="HTML")


class Stats(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)
        self.seen = self.dbobject.Get("seenlog")
        self.uindex = self.dbobject.Get("userindex")

    @asyncio.coroutine
    def run(self):
        users = self.seen.usercounter.Get()
        output_string = "<b>Most Active User Stats (by words):</b>\n\n"
        place = 1
        for key, user in sorted(users.rawdict(), key=self.sort_by_word):
            username = key
            if username == "":
                continue
            usercountobject = SerializableDict.UserObject(user)
            output_string += "[{}] {}: {} (Lines: {})\n".format(place, username, usercountobject.wordcounter, usercountobject.counter)
            place += 1
        Loggiz.L.info(output_string)
        yield from self.bot.sendMessage("{}".format(output_string), parse_mode="HTML")

    @classmethod
    def sort_by_word(cls, userdict):
        usercountobject = SerializableDict.UserObject(userdict)
        if not isinstance(usercountobject.wordcounter, int):
            return 1
        return usercountobject.wordcounter

class Help(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)

    @asyncio.coroutine
    def run(self, commands):
        output_string = "<b>Available commands</b>\n"
        output_string += commands
        yield from self.bot.sendMessage("{}".format(output_string), parse_mode="HTML")

    @classmethod
    def sort_by_word(cls, userdict):
        usercountobject = SerializableDict.UserObject(userdict)
        if usercountobject.wordcounter == "":
            return 0
        return usercountobject.wordcounter

class Counter(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)
        self.seen = self.dbobject.Get("seenlog")

    @asyncio.coroutine
    def run(self):
        user = self.seen.usercounter.Get()
        usercount = user.get(self.messageobject.mfrom.username)
        usercountobject = SerializableDict.UserObject(usercount)

        # Line counter
        if usercountobject.counter == "":
            usercountobject.counter = 1
        else:
            usercountobject.counter = usercountobject.counter + 1
        # Word counter
        currentwordcount = re.findall('\w+', self.messageobject.text.lower())
        print("Words: {}".format(len(currentwordcount)))
        if usercountobject.wordcounter == "":
            usercountobject.wordcounter = len(currentwordcount)
        else:
            usercountobject.wordcounter = usercountobject.wordcounter + len(currentwordcount)
        # Last seen
        usercountobject.modified = str(datetime.datetime.now().replace(microsecond=0))
        # Metadata
        usercountobject.firstname = self.messageobject.mfrom.first_name
        usercountobject.lastname = self.messageobject.mfrom.last_name
        usercountobject.username = self.messageobject.mfrom.username
        # Store object to dictionary and back to DB
        user.set(self.messageobject.mfrom.username, usercountobject.SaveObject())
        self.seen.usercounter.Set(user)


class Seen(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)
        self.seendb = self.dbobject.Get("seenlog")

    @asyncio.coroutine
    def run(self):
        Loggiz.L.info("Gettings Stats")
        Loggiz.L.Print(self.messageobject.text)
        user = self.seendb.usercounter.Get()
        found = None
        m = re.search('^({})\s(.*)[$\s.]+$'.format(self.keyword), self.messageobject.text)
        if m is not None:
            found = m.groups()
        else:
            m = re.search('^({})\s(.*)$'.format(self.keyword), self.messageobject.text)
            if m is not None:
                found = m.groups()
        if found is not None:
            username = found[1]
            if username.startswith("@"):
                # remove @
                username = username[1:]

            fetchseenuser = user.get(username)
            userseenobject = SerializableDict.UserObject(fetchseenuser)
            if userseenobject.modified != "":
                yield from self.bot.sendMessage("hey! {} was last seen {} (lines/words: {}/{})".format(username, userseenobject.modified, userseenobject.counter, userseenobject.wordcounter))
            else:
                Loggiz.L.Print("Did not find any user!")


class QuoteBase(GeneralMessageEvent):
    def __init__(self, keyword, bot, dbobject, messageobject):
        GeneralMessageEvent.__init__(self, keyword, bot, dbobject, messageobject)
        self.uindex = self.dbobject.Get("userindex")


class AddQuote(QuoteBase):
    def __init__(self, keyword, bot, dbobject, messageobject):
        QuoteBase.__init__(self, keyword, bot, dbobject, messageobject)

    @asyncio.coroutine
    def run(self):
        new_quote_index = str(uuid.uuid4())

        m = re.search('^({})\s+(.*): (.*)$'.format(self.keyword), self.messageobject.text)
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
    def __init__(self, keyword, bot, dbobject, messageobject):
        QuoteBase.__init__(self, keyword, bot, dbobject, messageobject)

    def get_quote(self, username):
        quotemetausername = StorageObjects.ComnodeObject("quotemap.{}".format(username), "list", desc="", hidden=False)
        qmun = quotemetausername.Get()
        if len(qmun) > 0:
            random.seed(calendar.timegm(time.gmtime()))
            foundindex = random.randrange(0, len(qmun))
            Loggiz.L.info("found: {}, total: {}".format(foundindex, len(qmun)))
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
        qsentence = re.search('^.*({})\s(.*)[$\s.]+$'.format(self.keyword), self.messageobject.text)
        qdirect = re.search('.*({})\s(.*)$'.format(self.keyword), self.messageobject.text)
        qsingle = re.search('^({})$'.format(self.keyword), self.messageobject.text)
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
            random.seed(calendar.timegm(time.gmtime()))
            luckyuser = random.randrange(0, userindexlength)
            if len(self.uindex.index.Get()) == luckyuser:
                luckyuser = luckyuser - 1
            quoteoutput = self.get_quote(self.uindex.index.Get()[luckyuser])
        if found is not None:
            if quoteoutput is not None:
                yield from self.bot.sendMessage(quoteoutput)


if __name__ == '__main__':
    pass