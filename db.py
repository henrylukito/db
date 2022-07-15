import os, yaml

def load(schemapath):
  global n; n = {}
  global s; s = {}
  with open(schemapath, encoding='utf-8') as schemafile:
    schemadict = yaml.safe_load(schemafile)
  schemadirname = os.path.dirname(schemapath)
  for entry in schemadict:
    entry['path'] = os.path.join(schemadirname, entry['path'])
    eval(entry['loader'])(entry)

def assertid(id, newnodestr):
  if newnodestr == 'all' and id in n:
    raise AssertionError(f"{id} is expected to be new, but already exist")
  elif newnodestr == 'none' and id not in n:
    raise AssertionError(f"{id} is expected to already exist, but not")

def setsfromstr(setstr):
  return [token.strip() for token in setstr.split(",") if token.strip()]

def addidstosets(ids, sets):
  for setid in sets:
    s.setdefault(setid, {}).update(dict.fromkeys(ids))

def idlist(info):
  with open(info['path'], encoding='utf-8') as file:
    ids = [id.strip() for id in file.readlines() if id.strip()]
  newnodestr = info.get('new-node', 'all')
  sets = setsfromstr(info.get('sets', ''))
  for id in ids:
    assertid(id, newnodestr)
    n.setdefault(id)
  addidstosets(ids, sets)