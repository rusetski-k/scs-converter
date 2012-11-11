# -*- coding: utf-8 -*-
from articles.components.scs.parser import *;

import codecs
import sys
import os

ctr = 0
nodes = set()
triples = []
arc_types = {"=>" : "sc-arc-common", "<=" : "sc-arc-common", "->": "sc-arc-main", "<-": "sc-arc-main", "=": "sc-edge" }
pair_idtfs = {}

def mk_arc_id():
    global ctr
    ctr += 1
    return "pair%d" % ctr

def mk_arc(connector):
    global ctr
    ctr += 1
    return "pair%d/%s" % (ctr, arc_types[connector])

def sgroup(item):
    if isinstance(item.subject, SimpleIdentifierGroup):
        if isinstance(item.object, ParseResults):
            s = str(item.subject)
            p = str(item.predicate)
            for i in item.object:
                a_id = mk_arc_id()
                a = "%s/%s" %(a_id, arc_types[p])
                triples.append((s,a,i.idtf))
                
                if isinstance(i.internal, InternalListGroup):
                    isentencelist(i.idtf, i.internal)
                    
                if item.attrs is not None:
                    for attr in item.attrs:
                        triples.append((attr, mk_arc("->") ,a_id))
                    
    pass

def iwigroup(item):
    i = item.idtf
    if isinstance(i, TripleGroup):
        pred = str(i.predicate)
        pair = str(i)
        
        if pair_idtfs.has_key(pair):
            arc_id = pair_idtfs[pair]
            arc = "%s/%s" % (arc_id, arc_types[pred])
        else:
            arc_id = mk_arc_id()
            arc = "pair%d/%s" %(arc_id, arc_types[pred])
            pair_idtfs[str(i)] = arc_id
            triples.append((str(id.subject), arc, str(id.object)))                
        return arc_id

def presults(fields):
    for f in fields:
        processors[f.__class__](f)
        
def isentencelist(subj, sentList):
    for s in sentList.sentences:
        pred = str(s.predicate)
        for obj in s.object:
            print obj.__class__
            if not isinstance(obj, IdtfWithIntGroup):
                continue
            
            a_id = mk_arc_id()
            arc = "%s/%s" %(a_id, arc_types[pred])
            
            if isinstance(obj.internal, InternalListGroup):
                isentencelist(obj.idtf, obj.internal)
            
            
            triples.append((str(subj), arc, str(obj.idtf)))
            for attr in s.attrs:
                triples.append((attr, mk_arc("->"), a_id))
                
def skip(item):
    pass
           
processors = {SentenceGroup: sgroup,
              IdtfWithIntGroup: iwigroup,
              ParseResults: presults,
              KeywordGroup: skip}

#os.chdir("../sc-git-repo/scs")

fl = [os.path.join(path, f)
 for (path,dir,files) in os.walk(os.getcwd())
 for f in files if f.endswith(".scs")]

for f in fl:
    presults(parse(f))

    
