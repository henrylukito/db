import os, yaml

def load(schemapath):
  global n; n = {}
  global s; s = {}
  global p; p = {}
  with open(schemapath, encoding='utf-8') as schemafile:
    schemadict = yaml.safe_load(schemafile)
  schemadirname = os.path.dirname(schemapath)
  for entry in schemadict:
    entry['path'] = os.path.join(schemadirname, entry['path'])
    eval(entry['loader'])(entry)

def assertid(id, newnodestr):
  if newnodestr == 'all' and id in n:
    raise AssertionError(f"{id} expected new, but already exist")
  elif newnodestr == 'none' and id not in n:
    raise AssertionError(f"{id} expected already exist, but new")

def handleids(ids, newnodestr, setstr):
  if len(ids) == 0: return
  sets = [token.strip() for token in setstr.split(",") if token.strip()]
  for id in ids: assertid(id, newnodestr); n.setdefault(id)
  for setid in sets: s.setdefault(setid, {}).update(dict.fromkeys(ids))

def idlist(info):
  with open(info['path'], encoding='utf-8') as file:
    ids = [id.strip() for id in file.readlines() if id.strip()]
  handleids(ids, info.get('new-node', 'all'), info.get('sets', ''))

def propkeyvalue(info):
  with open(info['path'], encoding='utf-8') as file:
    filedict = yaml.safe_load(file)
  handleids(list(filedict), info.get('new-node', 'none'), info.get('sets', ''))
  p.setdefault(info['propname'], {}).update(filedict)