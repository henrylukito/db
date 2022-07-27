import os, yaml
from pathlib import Path

node = {}
nodecol = {}
nodeprop = {}
noderel = {}
nodereltarget = {}
col = {}
prop = {}
rel = {}
reltarget = {}
relprop = {}

def reset_objects():
  node.clear()
  nodecol.clear()
  nodeprop.clear()
  noderel.clear()
  nodereltarget.clear()
  col.clear()
  prop.clear()
  rel.clear()
  reltarget.clear()
  relprop.clear()

def load_schema(schemapath):
  with open(schemapath, encoding='utf-8') as file:
    schemadict = yaml.safe_load(file)
  schemadirname = os.path.dirname(schemapath)
  for entry in schemadict:
    entry['file'] = os.path.join(schemadirname, entry['file'])
    eval(entry['function'])(entry)

def set_node(nodeid):
  node.setdefault(nodeid, {'prop': nodeprop.setdefault(nodeid, {}), 'rel': noderel.setdefault(nodeid, {}), 
  'reltarget': nodereltarget.setdefault(nodeid, {})})

def set_node_collection(nodeid, colid):
  col.setdefault(colid, {}).setdefault(nodeid, node[nodeid])
  nodecol.setdefault(nodeid, {}).setdefault(colid, col[colid])

def set_node_property(nodeid, propid, propvalue):
  prop.setdefault(propid, {})[nodeid] = propvalue
  nodeprop.setdefault(nodeid, {})[propid] = propvalue

def set_node_relationship(sourceid, relid, targetid):
  rel.setdefault(relid, {}).setdefault(sourceid, {}).setdefault(targetid, {})
  reltarget.setdefault(relid, {}).setdefault(targetid, {})[sourceid] = rel[relid][sourceid][targetid]
  noderel.setdefault(sourceid, {}).setdefault(relid, {})[targetid] = rel[relid][sourceid][targetid]
  nodereltarget.setdefault(targetid, {}).setdefault(relid, {})[sourceid] = rel[relid][sourceid][targetid]

def set_node_relationship_property(sourceid, relid, targetid, relpropid, relpropvalue):
  rel.setdefault(relid, {}).setdefault(sourceid, {}).setdefault(targetid, {})[relpropid] = relpropvalue
  relprop.setdefault(relpropid, {}).setdefault(relid, {}).setdefault(sourceid, {})[targetid] = relpropvalue

def assert_node(nodeid, assertion):
  if assertion == 'new':
    assert nodeid not in node, f"node: {nodeid} is expected to be new, but already exist"
  elif assertion == 'old':
    assert nodeid in node, f"node: {nodeid} is expected to already exist, but it's not"

def assert_node_property(nodeid, propid, assertion):
  assert nodeid in nodeprop, f"asserting node: {nodeid} property: {propid}, but node: {nodeid} doesn't exist"
  if assertion == 'new':
    assert propid not in nodeprop[nodeid], f"node: {nodeid} property: {propid} is expected to be new, but already exist"
  elif assertion == 'old':
    assert propid in nodeprop[nodeid], f"node: {nodeid} property: {propid} is expected to already exist, but it's not"

def set_nodes(nodeids, assertion):
  for nodeid in nodeids:
    if assertion:
      assert_node(nodeid, assertion)
    set_node(nodeid)

def set_nodes_collections(nodeids, colstr):
  if not colstr:
    return
  colids = [id.strip() for id in colstr.split(",") if id.strip()]
  for nodeid in nodeids:
    for colid in colids:
      set_node_collection(nodeid, colid)

def nodelist(info):
  nodeids = [id.strip() for id in Path(info['file']).read_text(encoding='utf-8').splitlines() if id.strip()]
  set_nodes(nodeids, info.get('node-assert'))
  set_nodes_collections(nodeids, info.get('collection'))

def nodepropkeyvalue(info):
  filedict = yaml.safe_load(Path(info['file']).read_text(encoding='utf-8'))
  nodeids = list(filedict)
  propid = info['propname']
  set_nodes(nodeids, info.get('node-assert'))
  for nodeid in nodeids:
    if 'prop-assert' in info:
      assert_node_property(nodeid, propid, info['prop-assert'])
    set_node_property(nodeid, propid, filedict[nodeid])
  set_nodes_collections(nodeids, info.get('collection'))

def get_targetdict(obj):
  if isinstance(obj, str):
    obj = {obj: {}}
  if isinstance(obj, list):
    obj = {targetid: {} for targetid in obj}
  return obj

def noderelkeyvalue(info):
  filedict = yaml.safe_load(Path(info['file']).read_text(encoding='utf-8'))
  sourceids = list(filedict)
  relid = info['relname']
  set_nodes(sourceids, info.get('source-assert'))
  set_nodes_collections(sourceids, info.get('source-collection'))
  for sourceid in sourceids:
    targetdict = get_targetdict(filedict[sourceid])
    targetids = list(targetdict)
    set_nodes(targetids, info.get('target-assert'))
    set_nodes_collections(targetids, info.get('target-collection'))
    for targetid in targetids:
      set_node_relationship(sourceid, relid, targetid)