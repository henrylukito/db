#! python -i

import sys
from pathlib import Path
import json, yaml


def reset():
    global node
    global collection
    global property
    global relationship

    node = {}
    collection = {}
    property = {}
    relationship = {}


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

    def touch_node(nodeid):
        if nodeid not in node or not node[nodeid]:
            node[nodeid] = {"collection": None, "property": None, "relationship": None}
        return node[nodeid]

    def touch_node_collection(nodeid):
        if not touch_node(nodeid)["collection"]:
            node[nodeid]["collection"] = {}
        return node[nodeid]["collection"]

    def touch_node_property(nodeid):
        if not touch_node(nodeid)["property"]:
            node[nodeid]["property"] = {}
        return node[nodeid]["property"]

    def touch_node_relationship(nodeid):
        if not touch_node(nodeid)["relationship"]:
            node[nodeid]["relationship"] = {}
        return node[nodeid]["relationship"]

    def setnodes(nodeids):
        for nodeid in nodeids:
            node.setdefault(nodeid)

    def setcollections(nodeids, collectionids):
        for nodeid in nodeids:
            touch_node_collection(nodeid)
            for collectionid in collectionids:
                node[nodeid]["collection"].setdefault(collectionid)
        for collectionid in collectionids:
            collection.setdefault(collectionid, {})
            for nodeid in nodeids:
                collection[collectionid].setdefault(nodeid, node[nodeid])

    def setproperty(nodeid, propname, propvalue):
        touch_node_property(nodeid).setdefault(propname, propvalue)
        property.setdefault(propname, {})[nodeid] = node[nodeid]["property"][propname]

    def setrelationship(nodeid, relname, reltargetdict):
        touch_node_relationship(nodeid).setdefault(relname, {}).update(reltargetdict)
        relationship.setdefault(relname, {})[nodeid] = node[nodeid]["relationship"][
            relname
        ]

    schema = dict_from_filepath(schemapath)

    fileentries = schema["files"]

    directorypath = (
        Path(schema["directory"]) if "directory" in schema else Path(schemapath).parent
    )

    for filedesc in fileentries:

        fullfilepath = directorypath.joinpath(filedesc["path"])

        if filedesc["doctype"] == "id":
            nodeids = strlist_from_filepath(fullfilepath)
            setnodes(nodeids)

            if "collection" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collection"]))

        elif filedesc["doctype"] == "propvaluelist":
            propname = filedesc["propname"]
            typeconv = (
                lambda x: x
                if "datatype" not in filedesc
                else eval(filedesc["datatype"])
            )
            propvalues = [
                typeconv(item) for item in strlist_from_filepath(fullfilepath)
            ]
            for nodeid, propvalue in zip(nodeids, propvalues):
                setproperty(nodeid, propname, propvalue)

        elif filedesc["doctype"] == "propkeyvalue":
            propname = filedesc["propname"]
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()
            for nodeid, propvalue in filedict.items():
                setproperty(nodeid, propname, propvalue)

            if "collection" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collection"]))

        elif filedesc["doctype"] == "propdict":
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()
            propmap = filedesc["propmap"] if "propmap" in filedesc else None
            for nodeid, propdict in filedict.items():
                if propmap:
                    propdict = {
                        (propmap[propname] if propmap[propname] else propname): propval
                        for propname, propval in propdict.items()
                        if propname in propmap
                    }
                for propname, propval in propdict.items():
                    setproperty(nodeid, propname, propval)

            if "collection" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["collection"]))

        elif filedesc["doctype"] == "relkeyvalue":
            relname = filedesc["relname"]
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()

            inverserelname = (
                filedesc["inverserelname"] if "inverserelname" in filedesc else None
            )

            if "sourcecollection" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["sourcecollection"]))

            targetcollectionids = (
                strlist_from_str(filedesc["targetcollection"])
                if "targetcollection" in filedesc
                else None
            )

            for nodeid, reltargetdict in filedict.items():
                reltargetdict = ensure_dict(reltargetdict)
                targetids = reltargetdict.keys()

                setnodes(targetids)

                setrelationship(nodeid, relname, reltargetdict)

                if inverserelname:
                    for targetid in targetids:
                        relpropvalue = node[nodeid]["relationship"][relname][targetid]
                        setrelationship(
                            targetid, inverserelname, {nodeid: relpropvalue}
                        )

                if targetcollectionids:
                    setcollections(targetids, targetcollectionids)

        elif filedesc["doctype"] == "reldict":
            filedict = dict_from_filepath(fullfilepath)
            nodeids = filedict.keys()

            relmap = filedesc["relmap"] if "relmap" in filedesc else None

            inverserelmap = (
                filedesc["inverserelmap"] if "inverserelmap" in filedesc else None
            )

            if "sourcecollection" in filedesc:
                setcollections(nodeids, strlist_from_str(filedesc["sourcecollection"]))

            targetcollectionmap = (
                filedesc["targetcollectionmap"]
                if "targetcollectionmap" in filedesc
                else None
            )

            for nodeid, reldict in filedict.items():
                if relmap:
                    reldict = {
                        (relmap[relname] if relmap[relname] else relname): reltargetdict
                        for relname, reltargetdict in reldict.items()
                        if relname in relmap
                    }
                for relname, reltargetdict in reldict.items():
                    reltargetdict = ensure_dict(reltargetdict)
                    targetids = reltargetdict.keys()

                    setnodes(targetids)

                    setrelationship(nodeid, relname, reltargetdict)

                    if targetcollectionmap and relname in targetcollectionmap:
                        targetcollectionids = strlist_from_str(
                            targetcollectionmap[relname]
                        )
                        setcollections(targetids, targetcollectionids)

                    if inverserelmap and relname in inverserelmap:
                        inverserelname = inverserelmap[relname]
                        for targetid in targetids:
                            relpropvalue = node[nodeid]["relationship"][relname][
                                targetid
                            ]
                            setrelationship(
                                targetid, inverserelname, {nodeid: relpropvalue}
                            )

        else:
            print("error: unsupported file entry")


if __name__ == "__main__":
    load(sys.argv[1])
