import sys
from pathlib import Path
import json, yaml

nodes = {}
collections = {}
properties = {}
relationships = {}


def reset():
    global nodes
    global collections
    global properties
    global relationships
    nodes = {}
    collections = {}
    properties = {}
    relationships = {}


def load(schemapath):

    reset()

    def dict_from_filepath(filepath):
        with open(filepath) as file:
            return (
                json.load(file)
                if Path(filepath).suffix == ".json"
                else yaml.safe_load(file)
            )

    def strlist_from_filepath(filepath):
        with open(filepath) as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    def strlist_from_str(text):
        return [token.strip() for token in text.split(",")]

    def ensure_dict(obj):
        if isinstance(obj, dict):
            return obj
        elif isinstance(obj, list):
            return dict.fromkeys(obj)
        else:
            return dict.fromkeys([obj])

    def setcollections(nodeids, collectionids):
        for collectionid in collectionids:
            collections.setdefault(collectionid, {}).update(dict.fromkeys(nodeids))

    def setproperty(nodeid, propname, propvalue):
        nodes.setdefault(nodeid, {})[propname] = propvalue
        properties.setdefault(propname, {})[nodeid] = nodes[nodeid][propname]

    def setrelationship(nodeid, relname, reltargetdict):
        nodes.setdefault(nodeid, {}).setdefault(relname, {}).update(reltargetdict)
        relationships.setdefault(relname, {})[nodeid] = nodes[nodeid][relname]

    schema = dict_from_filepath(schemapath)

    fileentries = schema["files"]

    directorypath = (
        Path(schema["directory"]) if "directory" in schema else Path(schemapath).parent
    )

    for filedesc in fileentries:

        fullfilepath = directorypath.joinpath(filedesc["path"])

        if filedesc["doctype"] == "id":
            nodeids = strlist_from_filepath(fullfilepath)
            for nodeid in nodeids:
                nodes.setdefault(nodeid, {})

            if "collections" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collections"]))

        elif filedesc["doctype"] == "propvaluelist":
            propname = filedesc["propname"]
            typeconv = str if "datatype" not in filedesc else eval(filedesc["datatype"])
            propvalues = [typeconv(item) for item in strlist_from_filepath(fullfilepath)]
            for nodeid, propvalue in zip(nodeids, propvalues):
                setproperty(nodeid, propname, propvalue)

        elif filedesc["doctype"] == "propkeyvalue":
            propname = filedesc["propname"]
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()
            for nodeid, propvalue in filedict.items():
                setproperty(nodeid, propname, propvalue)

            if "collections" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collections"]))

        elif filedesc["doctype"] == "propdict":
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()
            for nodeid, propdict in filedict.items():
                for propname, propval in propdict.items():
                    setproperty(nodeid, propname, propval)

            if "collections" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collections"]))
                

        elif filedesc["doctype"] == "relkeyvalue":
            relname = filedesc["relname"]
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()

            inverserelname = (
                filedesc["inverserelname"] if "inverserelname" in filedesc else None
            )

            if "sourcecollections" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["sourcecollections"]))

            targetcollectionids = (
                strlist_from_str(filedesc["targetcollections"])
                if "targetcollections" in filedesc
                else None
            )

            for nodeid, reltargetdict in filedict.items():
                reltargetdict = ensure_dict(reltargetdict)
                targetids = reltargetdict.keys()

                setrelationship(nodeid, relname, reltargetdict)

                if inverserelname:
                    for targetid in targetids:
                        relpropvalue = nodes[nodeid][relname][targetid]
                        setrelationship(targetid, inverserelname, {nodeid: relpropvalue})

                if targetcollectionids:
                    setcollections(targetids, targetcollectionids)

        else:
            print("error: unsupported file entry")


if __name__ == "__main__":
    load(sys.argv[1])
