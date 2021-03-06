#!/usr/bin/python
import sys
import datetime
import time
import re
import uuid
import random
import argparse
import libs.Models as Models
import libs.Loggiz as Loggiz
import libs.SerializableDict as SerializableDict
import libs.StorageObjects as StorageObjects
import libs.Comnodestorage
import Commands
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import telegram

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
$ python psybot.py --token <token>
Tracks user and quotes.
"""
# Enable logging


def error(bot, update, error):
    Loggiz.log.write.warn('Update "%s" caused error "%s"' % (update, error))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", dest="debug", action="store_true", default=False)
    parser.add_argument('--token', dest='token', type=str, required=True)
    settings = parser.parse_args(sys.argv[1:])
    if settings.debug is True:
        logging.basicConfig(
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
    else:
        logging.basicConfig(
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.WARN)

    logger = logging.getLogger(__name__)
    libs.Loggiz.log.set(logger)
    logger.info('Starting Bot ...')
    #updater = Updater("207157142:AAFnlgs6nFMYrYhrio9r5ArME8rpE8vUbKg") #bsettings.token)
    updater = Updater(settings.token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("seen", Commands.Seen().run, pass_args=True))
    dp.add_handler(CommandHandler("addquote", Commands.AddQuote().run, pass_args=True))
    dp.add_handler(CommandHandler("quote", Commands.Quote().run, pass_args=True))
    dp.add_handler(CommandHandler("stats", Commands.Stats().run, pass_args=True))
    dp.add_handler(CommandHandler("time", Commands.Time().run, pass_args=True))
    dp.add_handler(CommandHandler("search", Commands.WebSearchDuckDuckGo().run, pass_args=True))
    dp.add_handler(CommandHandler("config", Commands.Configure().run, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], Commands.Counter().run))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
