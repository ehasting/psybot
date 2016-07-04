import sqlite3
import json
import ast
import os
import sys
import libs.Loggiz as Loggiz
import libs.SerializableDict as SerializableDict
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



pathaccessfailed = False
currentcheckpath = os.path.join(".")
created = False
dbname = "localdatabase.db"
dbset = False
defaultcollection = "default"


class DataTypes(object):
    Int = "int"
    Str = "str"
    Unicode = "unicode"
    Bool = "bool"
    Float = "float"
    List = "list"
    Dict = "dict"
    SkyShellDict = "SkyShellDict"


class DataModel(object):
    def __init__(self, key="", value="", collectionname="default", valuetype=DataTypes.Str):
        self.CollectionName = collectionname
        self.Key = key
        self.Value = value
        self.ValueType = valuetype
        self.Created = ""

    def __str__(self):
        return "{}, {}, {}, {} - {}".format(self.CollectionName, self.Key, self.Value, self.ValueType, self.Created)

    def ReturnDefault(self):
        if self.ValueType == DataTypes.Str:
            self.Value = str()
        elif self.ValueType == DataTypes.Int:
            self.Value = int()
        elif self.ValueType == DataTypes.Float:
            self.Value = float()
        elif self.ValueType == DataTypes.List:
            self.Value = list()
        elif self.ValueType == DataTypes.Dict:
            self.Value = dict()
        elif self.ValueType == DataTypes.Bool:
            self.Value = bool()
        elif self.ValueType == DataTypes.SkyShellDict:
            self.Value = SerializableDict.SkyShellDict()
        else:
            self.Value = str()

    def DecodeData(self):
        if self.ValueType == DataTypes.List:
            json_string = json.dumps(self.Value, separators=(',', ':'))
            self.Value = json_string
        elif self.ValueType == DataTypes.Dict:
            json_string = json.dumps(self.Value, separators=(',', ':'))
            self.Value = json_string
        elif self.ValueType == DataTypes.SkyShellDict:
            json_string = json.dumps(self.Value.data, separators=(',', ':'))
            self.Value = json_string

    def EncodeData(self):
        if self.ValueType == DataTypes.Str:
            self.Value = self.Value
        elif self.ValueType == DataTypes.Int:
            self.Value = int(self.Value)
        elif self.ValueType == DataTypes.Float:
            self.Value = float(self.Value)
        elif self.ValueType == DataTypes.List:
            self.Value = json.loads(self.Value)
        elif self.ValueType == DataTypes.Dict:
            self.Value = json.loads(self.Value)
        elif self.ValueType == DataTypes.SkyShellDict:
            if self.Value == "":
                self.Value = "{}"
            self.Value = SerializableDict.SkyShellDict(data=json.loads(self.Value))
        elif self.ValueType == DataTypes.Bool:
            if type(self.Value).__name__ == "int":
                self.Value = bool(self.Value)
            self.Value = self.Value.lower() in ("yes", "true", "t", "1")
        else:
            self.Value = self.Value


class DbObject(object):
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    def __enter__(self):
        self.connection = self.conn.cursor()
        return self.connection

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()


class ConfigDatabase(object):
    def __init__(self):
        global pathaccessfailed
        global currentcheckpath
        global created
        global dbname
        global dbset
        if not dbset:
            if os.access(os.path.dirname(dbname), os.W_OK) is False:
                if pathaccessfailed is False:
                    Loggiz.log.write.debug("DB can't write to original path, storing in local path!")
                    pathaccessfailed = True
                Loggiz.log.write.info("Searching in path %s" % currentcheckpath)
                dbname = os.path.join(currentcheckpath, dbname)
            dbset = True

        self.dbname = dbname
        self.tablename = "comnodeconfig"
        self.supportedtypes = [DataTypes.Str,
                               DataTypes.Unicode,
                               DataTypes.Int,
                               DataTypes.Bool,
                               DataTypes.Float,
                               DataTypes.List,
                               DataTypes.Dict,
                               DataTypes.SkyShellDict]
        if not created:
            with DbObject(self.dbname) as c:
                #  Create table
                c.execute('''CREATE TABLE IF NOT EXISTS %s (
                    [CollectionName] [VARCHAR(255)],
                    [Key] [VARCHAR(255)],
                    [Value] BLOB,
                    [ValueType] [VARCHAR(255)],
                    [LastValue] BLOB DEFAULT '',
                    [LastValueType] [VARCHAR(255)] DEFAULT '',
                    [Flag] BOOLEAN DEFAULT (0),
                    [Created] DATETIME DEFAULT (datetime('now', 'localtime'))
                    );
                    ''' % (self.tablename))
                c.execute("CREATE INDEX IF NOT EXISTS [Searchable] ON [%s] ([CollectionName] COLLATE BINARY ASC, [Key] COLLATE BINARY ASC);" % (self.tablename))
                created = True

    def previouspath(self, currentpath):
        return os.path.join("..", currentpath)

    def GetData(self, datamodel, default=True):
        with DbObject(self.dbname) as c:
            c.execute("SELECT CollectionName, Key, Value, ValueType, Created FROM [%s] "
                      "WHERE CollectionName=\'%s\' "
                      "AND Key=\'%s\'" % (self.tablename, datamodel.CollectionName, datamodel.Key))
            d = c.fetchall()
            if len(d) > 1:
                Loggiz.log.write.err("There are duplicates of %s.%s in your configuration!" % (datamodel.CollectionName, datamodel.Key))
            if default:
                datamodel.ReturnDefault()
            else:
                datamodel.Value = None
            for item in d:
                datamodel.CollectionName = item[0]
                datamodel.Key = item[1]
                datamodel.Value = item[2]
                datamodel.ValueType = item[3]
                datamodel.Created = item[4]
                datamodel.EncodeData()
            return datamodel

    def GetDataValue(self, datamodel):
        d = self.GetData(datamodel)
        return d.Value

    def IsKeyExisting(self, datamodel):
        # keyname, collectionname
        with DbObject(self.dbname) as c:
            c.execute("SELECT CollectionName, Key FROM [%s] WHERE CollectionName=\'%s\' AND Key=\'%s\'" % (self.tablename, datamodel.CollectionName, datamodel.Key))
            d = c.fetchall()
            if len(d) == 0:
                return False
            else:
                return True

    def SetData(self, datamodel):
        typename = datamodel.Value.__class__.__name__
        # hack to tell the system that unicode is also string.
        if typename == DataTypes.Unicode:
            typename = DataTypes.Str
        try:
            if datamodel.ValueType == DataTypes.Int:
                if typename != DataTypes.Int:
                    datamodel.Value = int(datamodel.Value)
            elif datamodel.ValueType == DataTypes.Str:
                if typename != DataTypes.Str:
                    datamodel.Value = str(datamodel.Value)
            elif datamodel.ValueType == DataTypes.Bool:
                if typename != DataTypes.Bool:
                    datamodel.Value = datamodel.Value.lower() in ("yes", "true", "t", "1")
            elif datamodel.ValueType == DataTypes.Float:
                if typename != DataTypes.Float:
                    datamodel.Value = float(datamodel.Value)
            elif datamodel.ValueType == DataTypes.List:
                if typename != DataTypes.List:
                    datamodel.Value = ast.literal_eval(datamodel.Value)
            elif datamodel.ValueType == DataTypes.Dict:
                if typename != DataTypes.Dict:
                    datamodel.Value = ast.literal_eval(datamodel.Value)
            elif datamodel.ValueType == DataTypes.SkyShellDict:
                if typename == DataTypes.Str:
                    try:
                        datamodel.Value = SerializableDict.SkyShellDict(data=ast.literal_eval(datamodel.Value))
                    except:
                        print(str(sys.exc_info()[0]))

        except:
            Loggiz.log.write.warn("Problem parsing, trying default unicode: %s %s" % (datamodel.Value, datamodel.ValueType))
        if datamodel.Value.__class__.__name__ != datamodel.ValueType:
            Loggiz.log.write.warn("The value you are trying to set is not correct type, Value is %s attribute requires %s"
                        % (datamodel.Value.__class__.__name__, datamodel.ValueType))
            return False
        datamodel.DecodeData()
        with DbObject(self.dbname) as c:
            if self.IsKeyExisting(datamodel):
                return c.execute("UPDATE [%s] SET Created=datetime('now', 'localtime'), Value=\'%s\', ValueType=\'%s\' WHERE CollectionName=\'%s\' AND Key=\'%s\' " % (self.tablename, datamodel.Value, datamodel.ValueType, datamodel.CollectionName, datamodel.Key))
            else:
                return c.execute("INSERT INTO [%s] (CollectionName, Key, Value, ValueType, Created) VALUES (\'%s\',\'%s\',\'%s\',\'%s\', datetime('now', 'localtime'))" % (self.tablename, datamodel.CollectionName, datamodel.Key, datamodel.Value, datamodel.ValueType))

    def DelData(self, datamodel):
        print("DELETE FROM [%s] WHERE CollectionName=\'%s\' AND Key=\'%s\' " % (self.tablename, datamodel.CollectionName, datamodel.Key))
        if self.IsKeyExisting(datamodel):
            with DbObject(self.dbname) as c:
                return c.execute("DELETE FROM [%s] WHERE CollectionName=\'%s\' AND Key=\'%s\' " % (self.tablename, datamodel.CollectionName, datamodel.Key))
        else:
            return False

if __name__ == '__main__':
    Loggiz.log.set(None)
    Loggiz.log.write.info("no example made, exiting..")
