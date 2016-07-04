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

class emoji(object):
    def __init__(self):
        self.used = list()
        random.seed(calendar.timegm(time.gmtime()))

    def get_randomanimal(self):
        animals = [ telegram.Emoji.RAT,
                    telegram.Emoji.MOUSE,
                    telegram.Emoji.OX,
                    telegram.Emoji.WATER_BUFFALO,
                    telegram.Emoji.COW,
                    telegram.Emoji.TIGER,
                    telegram.Emoji.LEOPARD,
                    telegram.Emoji.RABBIT,
                    telegram.Emoji.CAT,
                    telegram.Emoji.DRAGON,
                    telegram.Emoji.CROCODILE,
                    telegram.Emoji.WHALE,
                    telegram.Emoji.RAM,
                    telegram.Emoji.GOAT,
                    telegram.Emoji.ROOSTER,
                    telegram.Emoji.DOG,
                    telegram.Emoji.PIG]
        while True:
            foundindex = random.randrange(1, len(animals)) - 1
            if foundindex not in self.used:
                self.used.append(foundindex)
                break
            if len(self.used) == len(animals):
                self.used = list()
        return animals[foundindex]

#         self.db = dbobject
 #       self.uindex = dbobject.Get("userindex")
class GeneralMessageEvent(object):
    def __init__(self):
        self.dbobject = Models.StaticModels()
        self.config = self.dbobject.Get("config")

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
        localtime = home.normalize(home.localize(localtime))
        timezones = self.config.timezones.Get()
        out = "<b>Current Time</b>\n"
        out += "Norway: " + str(localtime.strftime('%X %x %Z')) + "\n"
        for tz in timezones:
            desc = tz[0]
            zonename = tz[1]
            currentzone = pytz.timezone(zonename)
            currentlocaltime = localtime.astimezone(currentzone)
            out += "{}: {}\n".format(desc, str(currentlocaltime.strftime('%X %x %Z')))
        Loggiz.log.write.info(out)
        bot.sendMessage(update.message.chat_id, text="{}".format(out), parse_mode="HTML")


class Configure(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)

    def addignoreword(self, word):
        d = self.config.ignorewords.Get()
        if word not in d:
            d.append(word)
            self.config.ignorewords.Set(d)
            return True
        return False

    def delignoreword(self, word):
        d = self.config.ignorewords.Get()
        if word in d:
            d.remove(word)
            self.config.ignorewords.Set(d)
            return True
        return False

    def addtimezone(self, desc, tzstring):
        d = self.config.timezones.Get()
        for tz in d:
            if tz[0] == desc:
                return False
        d.append([desc, tzstring])
        self.config.timezones.Set(d)
        return True

    def deltimezone(self, desc):
        pass

    def run(self, bot, update, args):
        out = None
        if len(args) == 0:
            return
        if update.message.from_user.username not in self.config.admins.Get() and update.message.from_user.username != "ehasting":
            Loggiz.log.write.error("Non admin ({}) tried to configure the bot".format(update.message.from_user.username))
            bot.sendMessage(update.message.chat_id, text="{}".format("you need backdoor access... no grid for you!!!!"), parse_mode="HTML")
            return
        if args[0] == "help":
            out = "Available configuration: addignoreword, delignoreword, addtimezone"
        elif args[0] == "addignoreword":
            for word in args[1:]:
                out = self.addignoreword(word)
                Loggiz.log.write.info("{} = {}".format(word, out))
        elif args[0] == "delignoreword":
            for word in args[1:]:
                out = self.delignoreword(word)
                Loggiz.log.write.info("{} = {}".format(word, out))
        elif args[0] == "addtimezone":
            out = self.addtimezone(args[1], args[2])
        if out is not None:
            Loggiz.log.write.info(out)
            bot.sendMessage(update.message.chat_id, text="{}".format(out), parse_mode="HTML")


class Stats(GeneralMessageEvent):
    def __init__(self):
        GeneralMessageEvent.__init__(self)
        self.seen = self.dbobject.Get("seenlog")
        self.uindex = self.dbobject.Get("userindex")
        self.wordcounter = self.dbobject.Get("wordcounter")

    def run(self, bot, update, args):
        self.ignorewords = self.config.ignorewords.Get()
        users = self.seen.usercounter.Get()
        data = users.rawdict()
        output_string = "<b>Most Active User Stats (by words):</b>\n"
        place = 1
        placeemoji = emoji()
        for key, user in sorted(data, key=self.sort_by_word, reverse=True):
            username = key
            if username == "":
                continue
            Loggiz.log.write.info(user)
            usercountobject = SerializableDict.UserObject(user)
            useremoji = placeemoji.get_randomanimal()
            output_string += "{} [{}] {}: {} (Lines: {})\n".format(useremoji, place, username, usercountobject.wordcounter, usercountobject.counter)
            if telegram.Emoji.DRAGON == useremoji:
                output_string += "   - Entering the dragon......\n"
            place += 1
        output_string += "\n<b>Most used words:</b>\n"
        words = self.wordcounter.words.Get()
        cnt = 0

        for key, value in sorted(words.rawdict(), key=self.sort_by_wordusage, reverse=True):
            Loggiz.log.write.info(value)
            currentword = SerializableDict.WordStats(value)
            Loggiz.log.write.info(currentword.word)
            if currentword.word in self.ignorewords:
                continue
            output_string += "{}: {} times\n".format(currentword.word, currentword.counter)
            cnt += 1
            if cnt > 4:
                break
        Loggiz.log.write.info(output_string)
        bot.sendMessage(update.message.chat_id, text="{}".format(output_string), parse_mode="HTML")

    def sort_by_wordusage(self, worddict):
        d = SerializableDict.WordStats(worddict[1])
        if not isinstance(d.counter, int):
            return 0
        return d.counter


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
        bot.sendMessage(update.message.chat_id, text="{}".format(output_string), parse_mode="HTML")

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
        self.wordcounter = self.dbobject.Get("wordcounter")

    def run(self, bot, update):
        user = self.seen.usercounter.Get()
        usercount = user.get(update.message.from_user.username)
        usercountobject = SerializableDict.UserObject(usercount)
        words = self.wordcounter.words.Get()

        # Line counter
        if usercountobject.counter == "":
            usercountobject.counter = 1
        else:
            usercountobject.counter = usercountobject.counter + 1
        # Word counter
        currentwordcount = re.findall('\w+', update.message.text.lower())
        ignorecharacterlist = [".", "!", "?", ",", ":", ";", "-", "_", "/"]
        for word in currentwordcount:
            #word = word.translate(None, ''.join(ignorecharacterlist))

            current = words.get(word)
            current = SerializableDict.WordStats(current)
            if current.counter == "":
                current.counter = 0
                current.word = word
            current.counter = int(current.counter) + 1
            Loggiz.log.write.info("{}: {}".format(current.word, current.counter))
            words.set(word, current.SaveObject())
        self.wordcounter.words.Set(words)


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
                tmplist.append(username)
                self.uindex.index.Set(tmplist)
                Loggiz.log.write.info("user/nick added to index")
            thequote = " ".join(args[1:])
            if isinstance(thequote, unicode):
                quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(new_quote_index), "unicode", desc="", hidden=False)
            else:
                quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(new_quote_index), "str", desc="", hidden=False)
            quotetext.Set(thequote)

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
            foundindex = random.randrange(0, len(qmun))
            Loggiz.log.write.info("found: {}, total: {}".format(foundindex, len(qmun)))
            if len(qmun) == foundindex:
                foundindex = foundindex - 1
            if qmun[foundindex] in self.taken:
                Loggiz.log.write.info("{} is taken".format(qmun[foundindex]))
                return "TAKEN"
            else:
                quotetext = StorageObjects.ComnodeObject("quotestext.{}".format(qmun[foundindex]), "str", desc="", hidden=False)
                self.taken.append(qmun[foundindex])
            if quotetext.Get() == "":
                return ""
            return "<i>{}</i>: {}".format(username, quotetext.Get())
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
        emojiz = emoji()
        iterationcount = 0
        if len(args) == 1:
            nums = int(args[0])
            if nums > 10:
                nums = 10
            quoteoutput = "<b>{} random Quotes</b>\n".format(nums)
            Loggiz.log.write.info("Args {} converted to {}".format(str(args), nums))
            while True:
                if iterationcount > (nums * 8):
                    Loggiz.log.write.warn("Retry exhausted")
                    break
                randomuser = self.findrandomuser()
                currentquote = self.get_quote(randomuser)
                if currentquote == "TAKEN":
                    Loggiz.log.write.info("Quote Taken")
                    iterationcount += 1
                    continue
                elif currentquote is None:
                    Loggiz.log.write.info("Quote on {} not found".format(randomuser))
                    break
                elif currentquote == "":
                    Loggiz.log.write.info("Quote is blank")
                    iterationcount += 1
                    continue
                quoteoutput += "{} {}\n".format(emojiz.get_randomanimal(), currentquote)
                if len(self.taken) >= nums:
                    break
                

        else:
            quoteoutput = self.get_quote(self.findrandomuser())
        if quoteoutput is not None:
            Loggiz.log.write.info(str(self.taken))
            bot.sendMessage(update.message.chat_id, text=quoteoutput, parse_mode="HTML")
            self.taken = list()


if __name__ == '__main__':
    pass