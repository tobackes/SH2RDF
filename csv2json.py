import sys
import csv
import json
import re
import sqlite3

infile  = sys.argv[1];
outfile = sys.argv[2];

_geo_  = 'resources/allCountries.db';
_con_  = sqlite3.connect(_geo_);
_cur_  = _con_.cursor();
_empty = set(['','n','X']);

def clean_rows(rows,index2column):
    for i in xrange(len(rows)):
        for j in xrange(len(rows[i])):
            if rows[i][j] in _empty:
                rows[i][j] = None;
            rows[i][j] = clean(rows[i][j],index2column[j]);

def is_city(string): #TODO: Could even disambiguate with other information extracted #TODO: Should also normalize string with ascii column from DB
    freq = _cur_.execute("SELECT COUNT(DISTINCT geonameid) FROM alternatives WHERE alternative=?",(string.decode('utf-8'),)).fetchall()[0][0];
    if freq > 0:
        types = set([row[0] for row in _cur_.execute("SELECT feature_class FROM geonames WHERE geonameid IN (SELECT DISTINCT geonameid FROM alternatives WHERE alternative=?)",(string.decode('utf-8'),)).fetchall()]);
        if ('P' in types or 'S' in types):
            print string, 'is a city.';
            return True;
    print string, 'is not a city.';
    return False;

def clean(value,field):
    if value == None:
        return None;
    if field == 'span':
        dates = re.findall(r'\d\d\d\d',value);
        return {'from':dates[0], 'to':dates[-1]} if len(dates)==2 else {'from':dates[0], 'to':None} if len(dates)==1 else {'from':None, 'to':None} if len(dates)==0 else {'from':dates[0], 'to':dates[-1], 'other':dates[1:-2]};
    if field == 'sofis_id':
        try:
            return int(value);
        except:
            return value;
    if field == 'institution_l1':
        match = re.search(r'\(.+\)',value);
        if match and is_city(match.group()[1:-1]):
            span = match.span();
            return {'name':value[:span[0]].strip(), 'city':value[span[0]+1:span[1]-1]};
        else:
            return {'name':value, 'city':None};
    return value;

IN           = open(infile,'r');
rows         = [row for row in csv.reader(IN)];
index2column = rows[0];
index2column = ['name', 'source', 'function', 'activity', 'span', 'activity', 'institution_l2', 'institution_l1', 'sofis_id']; # OVERWRITING ORIGINAL COLUMN NAMES
column2index = {index2column[i]:i for i in xrange(len(index2column))};
rows         = rows[1:];
IN.close();

clean_rows(rows,index2column);

D = dict();
for row in rows:
    if row[0] in D:
        D[row[0]].append({index2column[1:][i]: row[1:][i] for i in xrange(len(row[1:]))});
    else:
        D[row[0]] = [{index2column[1:][i]: row[1:][i] for i in xrange(len(row[1:]))}];

for position in D[D.keys()[0]]:
    print position;

OUT = open(outfile,'w');
json.dump(D,OUT);
OUT.close();
