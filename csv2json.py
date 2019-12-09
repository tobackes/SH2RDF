import sys
import csv
import json
import re
import sqlite3
from copy import deepcopy as copy
import collections

infile  = sys.argv[1];
outfile = sys.argv[2];

_geo_  = 'resources/allCountries.db';
_con_  = sqlite3.connect(_geo_);
_cur_  = _con_.cursor();
_empty = set([None,'','n','X']);

_context = json.load(open('context.json'));
_initial = json.load(open('initial.json'));

_fields = ['rowid','name','source','function','activity','span','activity','instiution_l2','institution_l1','sofis_id'];

_targets = [ 
            {'smart_harvesting':{'':{'occupations':{'':{'@id'           :None                                    }}}}},
            {'smart_harvesting':{'':{'name':None,'@id':None                                                        }}},
            {'smart_harvesting':{'':{'occupations':{'':{'source'        :None                                    }}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'function'      :None                                    }}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'activity'      :None                                    }}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'start_date'    :None,'end_date':None                    }}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'activity'      :None                                    }}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'institution_l2':{'@id':None,'location':None,'name':None}}}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'institution_l1':{'@id':None,'location':None,'name':None}}}}}},
            {'smart_harvesting':{'':{'occupations':{'':{'sofis_id'      :None                                    }}}}},
          ];

def merge(d, u):
    for k, v in u.iteritems():
        #TODO: consider adding integers and floats up and giving a warning if strings and then replace with new string
        #if k in d and d[k]!=None and v != None and type(d[k]) != type(v):
        #    print 'WARNING:', d[k], 'and', v, 'have different types! Skipping...';
        #    continue;
        if isinstance(v, collections.Mapping) and v != dict():
            d[k] = merge(d.get(k,{}),v);
        elif isinstance(v,set) or isinstance(v,list):
            d[k] = d[k] + v;
        elif v != None and v != dict():
            d[k] = v;
    return d;

def parse_rows(rows):
    D = dict();
    for i in xrange(len(rows)):
        d = copy(_initial);
        for j in xrange(len(rows[i])):
            print d; print '----------------------------------'; print parse(rows[i][j],j); print '----------------------------------';
            merge(d,parse(rows[i][j],j));
            print d; print '----------------------------------';
        print '###############################################';
        person_id, occupa_id                                = d['smart_harvesting']['']['@id'], d['smart_harvesting']['']['occupations']['']['@id'];
        d['smart_harvesting']['']['occupations'][occupa_id] = d['smart_harvesting']['']['occupations'].pop('');
        d['smart_harvesting'][person_id]                    = d['smart_harvesting'].pop('');
        merge(D,d);
    return D;

def parse(value,colnum):
    field  = _fields[colnum];
    target = copy(_targets[colnum]);
    if value in _empty:
        if field == 'rowid':
            target['smart_harvesting']['']['occupations']['']['@id'] = ""; print 'WARNING: ID-relevant field',field,'has empty value',value,'!';
        elif field == 'name':
            target['smart_harvesting']['']['@id'] = ""; print 'WARNING: ID-relevant field',field,'has empty value',value,'!';
        else:
            return target;
    if field == 'rowid':
        target['smart_harvesting']['']['occupations']['']['@id'] = value;
    elif field == 'name':
        target['smart_harvesting']['']['name'] = value;
        target['smart_harvesting']['']['@id']  = value.replace(' ','_');
    elif field == 'source':
        target['smart_harvesting']['']['occupations']['']['source'] = value;
    elif field == 'function':
        target['smart_harvesting']['']['occupations']['']['function'] = value;
    elif field == 'activity':
        target['smart_harvesting']['']['occupations']['']['activity'] = value;
    elif field == 'span':
        dates = re.findall(r'\d\d\d\d',value);
        if len(dates)>=2:
            target['smart_harvesting']['']['occupations']['']['start_date'] = dates[0];
            target['smart_harvesting']['']['occupations']['']['end_date']   = dates[1];
        elif len(dates)==1:
            target['smart_harvesting']['']['occupations']['']['start_date'] = dates[0];
    elif field == 'institution_l1':
        match = re.search(r'\(.+\)',value);
        if match and is_city(match.group()[1:-1]):
            span = match.span();
            target['smart_harvesting']['']['occupations']['']['institution_l1']['@id']      = value[:span[0]].strip().replace(' ','_');
            target['smart_harvesting']['']['occupations']['']['institution_l1']['location'] = value[span[0]+1:span[1]-1];
            target['smart_harvesting']['']['occupations']['']['institution_l1']['name']     = value[:span[0]].strip();
        else:
            target['smart_harvesting']['']['occupations']['']['institution_l1']['@id']      = value.replace(' ','_');
            target['smart_harvesting']['']['occupations']['']['institution_l1']['name']     = value;
    elif field == 'institution_l2':
        match = re.search(r'\(.+\)',value);
        if match and is_city(match.group()[1:-1]):
            span = match.span();
            target['smart_harvesting']['']['occupations']['']['institution_l2']['@id']      = value[:span[0]].strip().replace(' ','_');
            target['smart_harvesting']['']['occupations']['']['institution_l2']['location'] = value[span[0]+1:span[1]-1];
            target['smart_harvesting']['']['occupations']['']['institution_l2']['name']     = value[:span[0]].strip();
        else:
            target['smart_harvesting']['']['occupations']['']['institution_l2']['@id']      = value.replace(' ','_');
            target['smart_harvesting']['']['occupations']['']['institution_l2']['name']     = value;
    return target;

def is_city(string): #TODO: Could even disambiguate with other information extracted #TODO: Should also normalize string with ascii column from DB
    freq = _cur_.execute("SELECT COUNT(DISTINCT geonameid) FROM alternatives WHERE alternative=?",(string.decode('utf-8'),)).fetchall()[0][0];
    if freq > 0:
        types = set([row[0] for row in _cur_.execute("SELECT feature_class FROM geonames WHERE geonameid IN (SELECT DISTINCT geonameid FROM alternatives WHERE alternative=?)",(string.decode('utf-8'),)).fetchall()]);
        if ('P' in types or 'S' in types):
            print string, 'is a city.';
            return True;
    print string, 'is not a city.';
    return False;


IN           = open(infile,'r');
rows         = [row for row in csv.reader(IN)];
index2column = rows[0];
column2index = {index2column[i]:i for i in xrange(len(index2column))};
rows         = [[i]+rows[1:][i] for i in xrange(len(rows[1:]))];#adding rowids
IN.close();

D = parse_rows(rows);
merge(D,_context);

OUT = open(outfile,'w');
json.dump(D,OUT,indent=1);
OUT.close();
