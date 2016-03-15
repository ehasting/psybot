import json
import libs.Loggiz as Loggiz
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


class SkyShellDict(object):
    class SubDict():
        def __init__(self, datastring="{}"):
            self.load(datastring)

        def load(self, datastring):
            self.data = json.loads(datastring)

        def get(self, key):
            return self.data.get(key, "")

        def set(self, key, value):
            # print "{}: {}".format(key, value)
            self.data[key] = value

        def save(self):
            return json.dumps(self.data)

    def __init__(self, data=dict()):
        if type(data) is dict:
            self.data = data
        else:
            self.data = dict()

    def __str__(self):
        return str(self.data)

    def rawdict(self):
        return self.data.items()

    def get(self, key):
        retd = self.data.get(key, "{}")
        return self.SubDict(retd)

    def set(self, key, value):
        self.data[key] = value

    def remove(self, key):
        del self.data[key]


class SkyShellDictObject(object):
    attributenamestatus = "status"
    status = None
    attributenamename = "name"
    name = ""

    def __init__(self, data=None):
        if isinstance(data, str):
            self.data = SkyShellDict.SubDict(data)
        elif isinstance(data, SkyShellDict.SubDict):
            self.data = data
        else:
            self.data = SkyShellDict.SubDict()
        self.Load()
        # print isinstance(data, SkyShellDict.SubDict)

    def Load(self):
        self.status = self.data.get(self.attributenamestatus)
        self.name = self.data.get(self.attributenamename)

    def Save(self):
        self.data.set(self.attributenamestatus, self.status)
        self.data.set(self.attributenamename, self.name)

    def SaveObject(self):
        self.Save()
        return self.data.save()


class QuoteObject(SkyShellDictObject):
    anusername = "username"
    anfirstname = "firstname"
    anquote = "quote"
    antimestamp = "timestamp"

    def Load(self):
        SkyShellDictObject.Load(self)
        self.counter = self.data.get(self.ancounter)
        self.modified = self.data.get(self.anmodified)
        self.firstname = self.data.get(self.anfirstname)
        self.username = self.data.get(self.anusername)

    def Save(self):
        SkyShellDictObject.Save(self)
        self.data.set(self.ancounter, self.counter)
        self.data.set(self.anmodified, self.modified)
        self.data.set(self.anfirstname, self.firstname)
        self.data.set(self.anusername, self.username)
        return self.data


class UserObject(SkyShellDictObject):
    ancounter = "counter"
    counter = 0

    anmodified = "modified"
    modified = None

    anfirstname = "firstname"
    firstname = None

    anlastname = "lastname"
    lastname = None

    anusername = "username"
    username = None

    anwordcounter = "wordcounter"
    wordcounter = 0


    def __init__(self, data=None):
        SkyShellDictObject.__init__(self, data)

    def Load(self):
        SkyShellDictObject.Load(self)
        self.counter = self.data.get(self.ancounter)
        self.wordcounter = self.data.get(self.anwordcounter)
        self.modified = self.data.get(self.anmodified)
        self.firstname = self.data.get(self.anfirstname)
        self.lastname = self.data.get(self.anlastname)
        self.username = self.data.get(self.anusername)

    def Save(self):
        SkyShellDictObject.Save(self)
        self.data.set(self.ancounter, self.counter)
        self.data.set(self.anwordcounter, self.wordcounter)
        self.data.set(self.anmodified, self.modified)
        self.data.set(self.anfirstname, self.firstname)
        self.data.set(self.anlastname, self.lastname)
        self.data.set(self.anusername, self.username)
        return self.data


if __name__ == '__main__':
    d = SkyShellDictObject()
    d.name = "test"
    # print(d.SaveObject())
