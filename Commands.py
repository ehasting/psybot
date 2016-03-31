import datetime
import re
import os
import requests
import json
import uuid
import random
import calendar
import time
import libs.SerializableDict as SerializableDict
import libs.StorageObjects as StorageObjects
import libs.Models as Models
import libs.Loggiz as Loggiz
from pytz import timezone
import pytz
import telegram
import logging
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

#         self.db = dbobject
 #       self.uindex = dbobject.Get("userindex")
class GeneralMessageEvent(object):
    def __init__(self):
        self.dbobject = Models.StaticModels()

    def run(self, bot, update, args):
        raise NotImplementedError()

    @classmethod
    def stripusername(self, username):
        if username.startswith("@"):
            # remove @
            return username[1:]
        else:
            return username


class Null(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)

    def run(self, bot, update, args):
        pass


class WebSearchDuckDuckGo(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)

    def _generate_url(self, searchstring):
        searchstring = searchstring.replace(" ", "+")
        print(searchstring)
        return "http://api.duckduckgo.com/?q={}&format=json".format(searchstring)

    def run(self, bot, update, args):
        r = requests.get(self._generate_url(" ".join(args)))
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
            bot.sendMessage(update.message.chat_id, text="{}".format(outputstring), parse_mode="HTML")


class Time(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)

    def run(self, bot, update, args):
        localtime = datetime.datetime.now()
        home = pytz.timezone("Europe/Oslo")
        baltimore = pytz.timezone("US/Eastern")
        denver = pytz.timezone("America/Denver")

        localtime = home.normalize(home.localize(localtime))
        baltimoretime = localtime.astimezone(baltimore)
        denvertime = localtime.astimezone(denver)
        '''
            CLOCK_FACE_ONE_OCLOCK = n(b'\xF0\x9F\x95\x90')
            CLOCK_FACE_TWO_OCLOCK = n(b'\xF0\x9F\x95\x91')
            CLOCK_FACE_THREE_OCLOCK = n(b'\xF0\x9F\x95\x92')
            CLOCK_FACE_FOUR_OCLOCK = n(b'\xF0\x9F\x95\x93')
            CLOCK_FACE_FIVE_OCLOCK = n(b'\xF0\x9F\x95\x94')
            CLOCK_FACE_SIX_OCLOCK = n(b'\xF0\x9F\x95\x95')
            CLOCK_FACE_SEVEN_OCLOCK = n(b'\xF0\x9F\x95\x96')
            CLOCK_FACE_EIGHT_OCLOCK = n(b'\xF0\x9F\x95\x97')
            CLOCK_FACE_NINE_OCLOCK = n(b'\xF0\x9F\x95\x98')
            CLOCK_FACE_TEN_OCLOCK = n(b'\xF0\x9F\x95\x99')
            CLOCK_FACE_ELEVEN_OCLOCK = n(b'\xF0\x9F\x95\x9A')
            CLOCK_FACE_TWELVE_OCLOCK = n(b'\xF0\x9F\x95\x9B')
    '''
        out = "<b>Current Time</b>\n"
        out += "Norway: " + str(localtime.strftime('%X %x %Z')) + "\n"
        out += "Baltimore: " + str(baltimoretime.strftime('%X %x %Z')) + "\n"
        out += "Denver: " + str(denvertime.strftime('%X %x %Z')) + "\n"
        Loggiz.log.write.info(out)
        bot.sendMessage(update.message.chat_id, text="{}".format(out), parse_mode="HTML")


class Stats(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.seen = self.dbobject.Get("seenlog")
        self.uindex = self.dbobject.Get("userindex")

    def run(self, bot, update, args):
        users = self.seen.usercounter.Get()
        data = users.rawdict()
        output_string = "<b>Most Active User Stats (by words):</b>\n\n"
        place = 1
        for key, user in sorted(data, key=self.sort_by_word, reverse=True):
            username = key
            if username == "":
                continue
            usercountobject = SerializableDict.UserObject(user)
            output_string += "[{}] {}: {} (Lines: {})\n".format(place, username, usercountobject.wordcounter, usercountobject.counter)
            place += 1
        Loggiz.log.write.info(output_string)
        bot.sendMessage(update.message.chat_id, text="{}".format(output_string), parse_mode="HTML")

    def sort_by_word(self, userdict):
        usercountobject = SerializableDict.UserObject(userdict[1])
        if not isinstance(usercountobject.wordcounter, int):
            return 1
        Loggiz.log.write.info(usercountobject.wordcounter)
        return usercountobject.wordcounter


class Help(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)

    def run(self, bot, update, args):
        output_string = "<b>Available commands</b>\n"
        output_string += commands
        ybot.sendMessage(update.message.chat_id, text="{}".format(output_string), parse_mode="HTML")

    @classmethod
    def sort_by_word(cls, userdict):
        usercountobject = SerializableDict.UserObject(userdict)
        if usercountobject.wordcounter == "":
            return 0
        return usercountobject.wordcounter

class AudioTips(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.tipdb = self.dbobject.Get("tipdb")




class Counter(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.seen = self.dbobject.Get("seenlog")

    def run(self, bot, update, args):
        user = self.seen.usercounter.Get()
        usercount = user.get(update.message.from_user.username)
        usercountobject = SerializableDict.UserObject(usercount)

        # Line counter
        if usercountobject.counter == "":
            usercountobject.counter = 1
        else:
            usercountobject.counter = usercountobject.counter + 1
        # Word counter
        currentwordcount = re.findall('\w+', update.message.text.lower())
        print("Words: {}".format(len(currentwordcount)))
        if usercountobject.wordcounter == "":
            usercountobject.wordcounter = len(currentwordcount)
        else:
            usercountobject.wordcounter = usercountobject.wordcounter + len(currentwordcount)
        # Last seen
        usercountobject.timestamp = str(datetime.datetime.now().replace(microsecond=0))
        # Metadata
        usercountobject.firstname = update.message.from_user.first_name
        usercountobject.lastname = update.message.from_user.last_name
        usercountobject.username = update.message.from_user.username
        # Store object to dictionary and back to DB
        user.set(update.message.from_user.username, usercountobject.SaveObject())
        self.seen.usercounter.Set(user)


class Seen(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.seendb = self.dbobject.Get("seenlog")

    def run(self, bot, update, args):
        Loggiz.log.write.info("Gettings Stats")
        user = self.seendb.usercounter.Get()

        if len(args) > 0:
            Loggiz.log.write.info("finding user {}".format(args[0]))
            username = self.stripusername(args[0])

            fetchseenuser = user.get(username)
            userseenobject = SerializableDict.UserObject(fetchseenuser)
            Loggiz.log.write.info(userseenobject.timestamp)
            if userseenobject.timestamp != "":
                bot.sendMessage(update.message.chat_id, text="hey! {} was last seen {} (lines/words: {}/{})".format(username, userseenobject.timestamp, userseenobject.counter, userseenobject.wordcounter))
            else:
                Loggiz.log.write.warn("Did not find any user info!")
        else:
            bot.sendMessage(update.message.chat_id, text="{} U ale wlong!! do like this!! command @<username>".format(telegram.Emoji.PILE_OF_POO))


class QuoteBase(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.uindex = self.dbobject.Get("userindex")


class AddQuote(QuoteBase):
    def __init__(self):
        QuoteBase.__init__(self)

    def run(self, bot, update, args):
        new_quote_index = str(uuid.uuid4())

        if len(args) < 2:
            Loggiz.log.write.info("Argument length was {}".format(len(args)))
            bot.sendMessage(update.message.chat_id, text='[USAGE] <username> <quote>')
        else:
            username = self.stripusername(args[0])
            if username not in self.uindex.index.Get():
                tmplist = self.uindex.index.Get()
                tmplist.append(args[1])
                self.uindex.index.Set(tmplist)
                Loggiz.log.write.info("user/nick added to index")
            quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(new_quote_index), "str", desc="", hidden=False)
            quotetext.Set(" ".join(args[1:]))

            quotemetausername = StorageObjects.ComnodeObject("quotemap.{}".format(username), "list", desc="", hidden=False)
            qmun = quotemetausername.Get()
            qmun.append(new_quote_index)
            quotemetausername.Set(qmun)
            bot.sendMessage(update.message.chat_id, text="Quote from {} added with id {}".format(username, new_quote_index))



class Quote(QuoteBase):
    def __init__(self):
        QuoteBase.__init__(self)
        self.taken = list()
        random.seed(calendar.timegm(time.gmtime()))

    def get_quote(self, username):
        quotemetausername = StorageObjects.ComnodeObject("quotemap.{}".format(username), "list", desc="", hidden=False)
        qmun = quotemetausername.Get()
        if len(qmun) > 0:
            random.seed(calendar.timegm(time.gmtime()))
            foundindex = random.randrange(0, len(qmun))
            Loggiz.log.write.info("found: {}, total: {}".format(foundindex, len(qmun)))
            if len(qmun) == foundindex:
                foundindex = foundindex - 1
            if qmun[foundindex] in self.taken:
                return "TAKEN"
            else:
                quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(qmun[foundindex]), "str", desc="", hidden=False)
                self.taken.append(qmun[foundindex])
            return "{}: {}".format(username, quotetext.Get())
        else:
            return None

    def findrandomuser(self):
        userindexlength = len(self.uindex.index.Get())
        if userindexlength == 0:
            return
        luckyuser = random.randrange(0, userindexlength)
        if len(self.uindex.index.Get()) == luckyuser:
            luckyuser = luckyuser - 1
        return self.uindex.index.Get()[luckyuser]

    def run(self, bot, update, args):

        if len(args) == 1:
            quoteoutput = "<b>{} random Quotes</b>\n"
            nums = int(args[0])
            if nums > 10:
                nums = 10
            cnt = 0
            Loggiz.log.write.info("Args {}".format(str(args)))
            while True:
                randomuser = self.findrandomuser()
                currentquote = self.get_quote(randomuser)
                if currentquote == "TAKEN":
                    Loggiz.log.write.info("Quote Taken")
                    cnt -= 1
                    continue
                elif currentquote is None:
                    Loggiz.log.write.info("Quote on {} not found".format(randomuser))
                    continue
                quoteoutput += "{} {}\n".format(telegram.Emoji.CLOCK_FACE_ONE_OCLOCK, currentquote)
                if nums < cnt:
                    break
                cnt += 1
        else:
            quoteoutput = self.get_quote(self.findrandomuser())
        if quoteoutput is not None:
            Loggiz.log.write.info(str(self.taken))
            bot.sendMessage(update.message.chat_id, text=quoteoutput, parse_mode="HTML")


if __name__ == '__main__':
    pass