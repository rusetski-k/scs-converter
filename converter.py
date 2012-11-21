# -*- coding: utf-8 -*-
from articles.components.scs.parser import *;
import os
import codecs
from glob import glob

# тип третьего компонента тройки
URL = 0     # sc-ссылка на содержимое
CONTENT = 1 # собственно содержимое

content_ctr = 0
ctr = 0
triples = []
arc_types = {"=>" : "sc-arc-common",
             "<=" : "sc-arc-common",
             "->": "sc-arc-main",
             "<-": "sc-arc-main",
             "<=>": "sc-edge",
             "=": ""}

reverse_arcs = ("<=", "<-")

pair_idtfs = {}

def append_triple(c1,c2,c3,pred):
    if pred in reverse_arcs:
        triples.append((c3,c2,c1))
    else:
        triples.append((c1,c2,c3))
    

def mk_arc_id():
    global ctr
    ctr += 1
    return "pair%d" % ctr

def mk_arc(connector):
    global ctr
    ctr += 1
    return "pair%d/%s" % (ctr, arc_types[connector])

def content(c):
    global content_ctr
    content_ctr += 1
    if not os.path.exists("./data"):
        os.mkdir("./data")
    with codecs.open("./data/content%d" % content_ctr, "w", "utf-8") as f:
        f.write(c.value)
    return (URL, "\"file://data/content%d\"" % content_ctr)

def url(u):
    return (URL, "\"file://" + u.value + "\"")

def sgroup(item):
    if isinstance(item.subject, SimpleIdentifierGroup):
        if isinstance(item.object, ParseResults):
            s = str(item.subject)
            p = str(item.predicate)
            for i in item.object:
                if isinstance(i.idtf, SetGroup):
                    for it in i.idtf.items:
                        o = iwigroup(it[1])
                        a_id = mk_arc_id()
                        a = "%s/%s" %(a_id, arc_types[p])
                        append_triple(s,a,o,p)

                        if isinstance(i.internal, InternalListGroup):
                            isentencelist(i.idtf, i.internal)

                        if item.attrs is not None:
                            for attr in item.attrs:
                                triples.append((attr, mk_arc("->") ,a_id))
                    continue
                elif isinstance(i.idtf, UrlGroup):
                    o = url(i.idtf)
                elif isinstance(i.idtf, ContentGroup):
                    o = content(i.idtf)
                else:
                    o = i.idtf

                a_id = mk_arc_id()
                a = "%s/%s" %(a_id, arc_types[p])
                append_triple(s,a,o,p)
                if isinstance(i.internal, InternalListGroup):
                    isentencelist(i.idtf, i.internal)

                if item.attrs is not None:
                    for attr in item.attrs:
                        triples.append((attr, mk_arc("->") ,a_id))

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
            append_triple(str(id.object), arc, str(id.subject),pred)
        return arc_id
    elif isinstance(i, SimpleIdentifierGroup):
        return str(i)
    elif isinstance(i, ContentGroup):
        return content(i)

def presults(fields):
    for f in fields:
        processors[f.__class__](f)

def isentencelist(subj, sentList):
    for s in sentList.sentences:
        pred = str(s.predicate)
        for obj in s.object:
            if not isinstance(obj, IdtfWithIntGroup):
                continue

            a_id = mk_arc_id()
            arc = "%s/%s" %(a_id, arc_types[pred])

            if isinstance(obj.internal, InternalListGroup):
                isentencelist(obj.idtf, obj.internal)

            if isinstance(subj, ContentGroup):
                append_triple(str(obj.idtf), arc, subj.value, pred)
            else:
                append_triple(str(subj), arc, str(obj.idtf), pred)
            for attr in s.attrs:
                triples.append((attr, mk_arc("->"), a_id))

def skip(item):
    pass

processors = {SentenceGroup: sgroup,
              IdtfWithIntGroup: iwigroup,
              ParseResults: presults,
              KeywordGroup: skip}

os.chdir("./test")

# process all sc.s files from the current directory and below
# and write output
    
for root, subFolders, files in os.walk(os.getcwd()):
    for f in files:
        fn = os.path.join(root,f)
        if fn.endswith(".scs"):
            presults(parse(fn))

with codecs.open("out.scs1", "w", "utf-8") as output:
    for t in triples:
        s, a, o = t;
        if isinstance(o, tuple): o = o[1] 
        output.write("%s|%s|%s;;\n" % (s,a,o))
