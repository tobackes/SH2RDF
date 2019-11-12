import sys
import csv
import json
import re

infile  = sys.argv[1];
outfile = sys.argv[2];

_empty = set(['','n','X']);

def clean_rows(rows,index2column):
    for i in xrange(len(rows)):
        for j in xrange(len(rows[i])):
            if rows[i][j] in _empty:
                rows[i][j] = None;
            rows[i][j] = clean(rows[i][j],index2column[j]);

def clean(value,field):
    if value == None:
        return None;
    if field == 'span':
        return tuple(re.findall(r'\d\d\d\d',value));
    if field == 'sofis_id':
        try:
            return int(value);
        except:
            return value;
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
