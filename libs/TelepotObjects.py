import datetime

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
