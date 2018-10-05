# Copyright (c) 2018, Jay Kubo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from os import sep
import re
import requests
from bs4 import BeautifulSoup

class ConnectionException(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message

class ArgumentException(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message

name = "pyelection"

class PyElection(object):
    """
        Example to instantiate the 2016 election

        >>> from pyelection import PyElection
        >>> pye = PyElection(2016)
    """
    def __init__(self, year=None):
        self.base_url = 'http://www.presidency.ucsb.edu'
        self.headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'PyElection'
        }
        try:
            res = requests.get(url=sep.join([self.base_url, 'elections.php']), headers=self.headers)
            tables = BeautifulSoup(res.content, features='lxml').find_all('table')
            self.years = list(filter(None, map(lambda x: x.text, tables[10].find_all('a'))))
            self.year = str(year)
        except:
            raise ConnectionException('Failed to connect')
        if self.year not in self.years:
            raise ArgumentException('Provided year is not found: %s' % str(self.years))
        try:
            res = requests.get(url=sep.join([self.base_url, 'showelection.php']), headers=self.headers, params={
                'year': self.year
            })
            self.__tables = BeautifulSoup(res.content, features='lxml').find_all('table')
        except:
            raise

    def get_state_summary(self, table_index=11):
        """
        Example truncated output (json library):
        
        >>> state = pye.get_state_summary()
        >>> import json
        >>> json.dumps(state, indent=4, sort_keys=True)
        [
            {
                "STATE": "Alabama",
                "STATS": [
                    {
                        "%": "34.4",
                        "Candidate": "HILLARY CLINTON",
                        "EV": "",
                        "Party": "Democratic",
                        "Votes": "729547"
                    },
                    {
                        "%": "62.1",
                        "Candidate": "DONALD TRUMP",
                        "EV": "9",
                        "Party": "Republican",
                        "Votes": "1318255"
                    },
                    {
                        "%": "2.1",
                        "Candidate": "GARY JOHNSON",
                        "EV": "",
                        "Party": "Libertarian",
                        "Votes": "44467"
                    }
                ],
                "TOTAL VOTES": "2123372"
            },
            *omitted*
            {
                "STATE": "Wyoming",
                "STATS": [
                    {
                        "%": "21.9",
                        "Candidate": "HILLARY CLINTON",
                        "EV": "",
                        "Party": "Democratic",
                        "Votes": "55973"
                    },
                    {
                        "%": "68.2",
                        "Candidate": "DONALD TRUMP",
                        "EV": "3",
                        "Party": "Republican",
                        "Votes": "174419"
                    },
                    {
                        "%": "5.2",
                        "Candidate": "GARY JOHNSON",
                        "EV": "",
                        "Party": "Libertarian",
                        "Votes": "13287"
                    }
                ],
                "TOTAL VOTES": "255849"
            }
        ]
        """
        data = map(lambda x: x.find_all('td'), self.__tables[table_index].find_all('tr'))
        rows = [list(map(lambda x: x.text.strip(), c)) for c in data]
        reg = re.compile('(,|%)')
        start = 'STATE'
        end = 'Totals'
        scope = []
        rec = False
        for row in rows:
            if row[0] == start:
                rec = True
                head = row
                # hacky but needed for scraping inconsistent format
                if head[1] != 'TOTAL VOTES':
                    head.insert(1, 'TOTAL VOTES')
                continue
            if row[0] == end:
                break
            if rec:
                scope.append(list(map(lambda c: reg.sub('', c), row)))
            else:
                party = list(filter(None, list(map(lambda x: tuple(x.splitlines()), row))))
        # relying on secondary method to obtain parties list as initial method is not always reliable
        parties = self.get_candidate_summary()
        ret = []
        init = False
        for s in scope:
            if len(s) == 1:
                init = True
                continue
            if init:
                col = list(zip(head, s))
                d = dict(col[:2])
                dim = int(len(col[2:]) / len(party))
                index = dim * len(party)
                d['STATS'] = list(map(dict, list(zip(*[iter(col[-index:])]*dim))))
                for i in range(min(len(party), len(parties))):
                    d['STATS'][i]['Candidate'] = parties[i]['President']
                    d['STATS'][i]['Party'] = parties[i]['Party']
                ret.append(d)
        
        return ret

    def get_candidate_summary(self, table_index=12):
        """
        Example output (using pandas `DataFrame`):

        >>> candidates = pye.get_candidate_summary()
        >>> import pandas as pd
        >>> pd.DataFrame(candidates)
            EV  EV %        Party        President Vice President     Votes Votes %
        0  227  42.2   Democratic  Hillary Clinton      Tim Kaine  65853516    48.2
        1  304  56.5   Republican     Donald Trump     Mike Pence  62984824    46.1
        2    0    --  Libertarian     Gary Johnson   William Weld   4489221     3.3
        3    0    --        Green       Jill Stein   Ajamu Baraka   1449542     1.1
        """
        data = map(lambda x: x.find_all('td'), self.__tables[table_index].find_all('tr'))
        rows = [list(map(lambda x: x.text.strip(), c)) for c in data]
        reg = re.compile('(,|%)')
        start = 'Party'
        end = 'STATE'
        scope = []
        rec = False
        for row in rows:
            if row[0] == start:
                rec = True
                continue
            if row[0] == end:
                list(map(lambda x: list(filter(None, x)), scope))
                break
            if rec:
                scope.append(list(map(lambda c: reg.sub('', c), row)))
        ret = []
        init = False
        rstart = 'Presidential'
        for r in list(map(lambda x: list(filter(None, x)), scope)):
            if len(r) and r[0] == rstart:
                init = True
                continue
            if len(r) == 0:
                break
            if init and len(r) == 7:
                ret.append({
                    'Party': r[0],
                    'President': r[1],
                    'Vice President': r[2],
                    'EV': r[3],
                    'EV %': r[4],
                    'Votes': r[5],
                    'Votes %': r[6],
                })
        return ret
