import libs.Comnodestorage as Comnodestorage
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


class ComnodeObject(object):
    def __init__(self, fullkeyname, valuetype=Comnodestorage.DataTypes.Str, desc="", hidden=False):
        self.hidden = hidden
        if desc == "":
            desc = "no description"
        self.description = desc
        self.storage = Comnodestorage.ConfigDatabase()
        groupname, keyname = fullkeyname.lower().split(".")
        if valuetype in self.storage.supportedtypes:
            self.datamodel = Comnodestorage.DataModel(key=keyname, valuetype=valuetype, collectionname=groupname)
        else:
            print("Wrong type given on key %s - unknown type: %s" % (fullkeyname, valuetype))
            exit(-1)

    def GetDescription(self):
        return self.description

    def GetValueType(self):
        if self.datamodel is None:
            return None
        return self.datamodel.ValueType

    def Set(self, data):
        self.datamodel.Value = data
        self.storage.SetData(self.datamodel)

    def Get(self):
        self.datamodel.Value = None
        return self.storage.GetDataValue(self.datamodel)

    def Del(self):
        return self.storage.DelData(self.datamodel)

    def Name(self):
        return "%s.%s" % (self.datamodel.CollectionName, self.datamodel.Key)

    def GetMeta(self):
        self.datamodel.Value = None
        return self.storage.GetData(self.datamodel)

    def __repr__(self):
        return self.Get()

    def __str__(self):
        return "%s" % (self.Get())

    def IsEmpty(self, verbose=True):
        def Verbose():
            if verbose:
                Loggiz.L.notice("%s is empty" % self.Name())

        d = self.storage.GetData(self.datamodel, default=False)
        if d.Value is None:
            Verbose()
            return True
        elif (d.Value == list()) or (d.Value == dict()):
            Verbose()
            return True
        elif d.Value == "":
            Verbose()
            return True
        else:
            return False


if __name__ == '__main__':
    test = dict()
    test["one"] = "one"
    d = ComnodeObject("services.me", "dict")
    print(d.Set(test))
    print(d.Get())
    print(d.IsEmpty())
