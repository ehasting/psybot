import datetime
import textwrap
import subprocess
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


class TERMINAL:
    @staticmethod
    def checkterminalsize():
        try:
            p = subprocess.Popen("/usr/bin/stty size", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for output in p.stdout.readlines():
                rows, currentterminalwidth = output.split()
                L.setterminalwidth(currentterminalwidth)
        except:
            L.notice("Can't read terminal size")

class COLORS:

    # FX
    BLINK = 5
    ZERO = 0
    UNDERLINE = 4
    BOLD = 1

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37
    DEFAULT = 39
    GRAY = 90

    ESC = '\033['

    # ALIAS
    WARN = YELLOW
    ERROR = RED
    OK = GREEN
    HEADER = BLUE


    @staticmethod
    def text(text, color=39, fx=0):
        assert isinstance(color, int), "Color is not a number"
        assert isinstance(fx, int), "FX is not a number"
        if fx == 0:
            return "{esc}{color}m{text}{esc}{end}m".format(esc=COLORS.ESC, color=color, text=text, end=COLORS.ZERO)
        return "{esc}{color};{fx}m{text}{esc}{end}m".format(esc=COLORS.ESC, color=color, text=text, end=COLORS.ZERO, fx=fx)

    @staticmethod
    def test():
        L.Print(COLORS.text("TEST", COLORS.WHITE))
        L.Print(COLORS.text("TEST", COLORS.PURPLE))
        L.Print(COLORS.text("TEST", COLORS.GREEN))
        L.Print(COLORS.text("TEST", COLORS.BLUE))
        L.Print(COLORS.text("TEST", COLORS.RED))
        L.Print(COLORS.text("TEST", COLORS.CYAN))

    @staticmethod
    def disable():
        COLORS.ROSA = ''
        COLORS.BLUE = ''
        COLORS.GREEN = ''
        COLORS.YELLOW = ''
        COLORS.RED = ''
        COLORS.ENDC = ''
        COLORS.BOLD = ''

class LEVELS:
    levellist = {"emerg": 0, "alert": 1, "crit": 2, "err": 3, "warn": 4, "notice": 5, "info": 6, "debug": 7}

    @staticmethod
    def getvaluebylable(lable):
        llable = lable.lower()
        return LEVELS.levellist[llable]

    @staticmethod
    def getlablebyvalue(invalue):
        for key, value in LEVELS.levellist.items():
            if value == invalue:
                return key
        return None

class PREFIX:
    # Type of prefix based on syslog level
    prefixlist = {0: '!', 1: '!', 2: '!', 3: '!', 4: '*', 5: '^', 6: '', 7: 'D', -1: None}
    # intending based on syslog level
    prefixlenght = {0:   3, 1:   2, 2:   2, 3:   1, 4:   1, 5:   1, 6:  0, 7:   0, -1: 0}
    prefixmaxlenght = 0

class L:
    lastmsg = ""
    loglevel = LEVELS.getvaluebylable("err")
    terminalwidth = 80

    @classmethod
    def setterminalwidth(self, width):
        if int(width) != L.getterminalwidth():
            L.notice("Change terminal width from {0} to {1}".format(L.getterminalwidth(), width))
            self.terminalwidth = int(width)

    @classmethod
    def getterminalwidth(self):
        return self.terminalwidth

    @classmethod
    def setlevel(self, level=7):
        L.notice("Change loglevel from {0} to {1}".format(LEVELS.getlablebyvalue(L.getlevel()), LEVELS.getlablebyvalue(level)))
        self.loglevel = level

    @classmethod
    def getlevel(self):
        return self.loglevel

    @staticmethod
    def notice(text):
        L.Print(text, 5, COLORS.WHITE,  COLORS.BOLD)

    @staticmethod
    def warn(text):
        L.Print(text, 4, COLORS.YELLOW)

    @staticmethod
    def err(text):
        L.Print(text, 3, COLORS.RED)

    @staticmethod
    def info(text):
        L.Print(text, 6, COLORS.WHITE)


    @staticmethod
    def debug(text):
        L.Print(text, 7, COLORS.GREEN)
# %-*s: %s" % (maxlen, a, getattr(self.data, a)

    @staticmethod
    def Print(text, level=-1, *tagcolor):
        cnt = 0
        color = 0
        fx = 0
        if tagcolor is None:
            color = COLORS.WHITE
            fx = COLORS.ZERO
        else:
            for c in tagcolor:
                if cnt == 0:
                    color = c
                elif cnt == 1:
                    fx = c
                else:
                    pass
                cnt += 1

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if level == -1:
            out = text
        else:
            out = "{:<9}[{}] {:>2}".format(timestamp,
                                               COLORS.text(LEVELS.getlablebyvalue(level), color, fx),
                                               text)
        if L._sameaslastline("{}{}".format(out, level)) is False:
            if L.getlevel() >= level:
                wrappedtext = textwrap.wrap(out, L.terminalwidth, subsequent_indent=">> ")
                for line in wrappedtext:
                    print (line)

    @staticmethod
    def shellprint(text):
        L.debug("shellprint is depricated, use Print() with default behaviour instead")
        L.Print(text, -1)

    @staticmethod
    def _sameaslastline(input):
        prev = L.lastmsg
        L.lastmsg = input
        if prev == input:
            return True
        return False

if __name__ == '__main__':
    L.setlevel(7)
    L.Print("Test1")
    L.err("Test2")
    L.notice("Test3")
    L.warn("Test4")
