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

class ComnodeModel(object):
    def __init__(self):
        pass

    def GetMemberList(self):
        members = [attr for attr in dir(self)
                   if not callable(attr) and not
                   attr.startswith("__") and not
                   (attr == "s") and not
                   attr.startswith("GetMemberList") and not
                   attr.startswith("GetMemberDict")]
        return members


    def GetMemberDict(self):
        members = [attr for attr in dir(self)
                   if not callable(attr)
                   and not attr.startswith("__")
                   and not (attr == "s")
                   and not attr.startswith("GetMemberList")
                   and not attr.startswith("GetMemberDict")
                   and not attr == "hidden"]
        ret = dict()
        for d in members:
            ret[d] = True
        return ret

    @classmethod
    def s(cls, name):
        return "%s.%s" % (cls.__name__, name)


class seenlog(ComnodeModel):
     def __init__(self):
         ComnodeModel.__init__(self)
         self.usercounter = StorageObjects.ComnodeObject(self.s("usercounter"), "SkyShellDict", desc="", hidden=False)

class tipdb(ComnodeModel):
     def __init__(self):
         ComnodeModel.__init__(self)
         self.tips = StorageObjects.ComnodeObject(self.s("tips"), "SkyShellDict", desc="", hidden=False)

class userindex(ComnodeModel):
     def __init__(self):
         ComnodeModel.__init__(self)
         self.index = StorageObjects.ComnodeObject(self.s("index"), "list", desc="", hidden=False)

class wordcounter(ComnodeModel):
     def __init__(self):
         ComnodeModel.__init__(self)
         self.words = StorageObjects.ComnodeObject(self.s("words"), "SkyShellDict", desc="", hidden=False)

class StaticModels(object):
    models = {}
    models["seenlog"] = seenlog()
    models["userindex"] = userindex()
    models["tipdb"] = tipdb()
    models["wordcounter"] = wordcounter()

    @staticmethod
    def Get(modelname):
        if modelname == "":
            return StaticModels.models
        return StaticModels.models[modelname]

if __name__ == '__main__':
    c = mssql()
    print(c.port)
