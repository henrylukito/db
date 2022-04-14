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

    schema = dict_from_filepath(schemapath)

    fileentries = schema["files"]

    directorypath = (
        Path(schema["directory"]) if "directory" in schema else Path(schemapath).parent
    )

    for filedesc in fileentries:

        fullfilepath = directorypath.joinpath(filedesc["path"])

        def strlist_from_filepath(filepath):
            with open(filepath) as file:
                return [line.strip() for line in file.readlines() if line.strip()]

        def strlist_from_str(text):
            return [token.strip() for token in text.split(",")]

        def assign_nodes_to_collections(col_ids, nodeids):
            for col_id in col_ids:
                collections.setdefault(col_id, {})
                collections[col_id].update(dict.fromkeys(nodeids))

        if filedesc["doctype"] == "id":
            ids = strlist_from_filepath(fullfilepath)
            for id in ids:
                nodes.setdefault(id, {})

            if "collections" in filedesc:
                col_ids = strlist_from_str(filedesc["collections"])
                assign_nodes_to_collections(col_ids, ids)

        elif filedesc["doctype"] == "propvaluelist":
            propname = filedesc["propname"]
            typeconv = str if "datatype" not in filedesc else eval(filedesc["datatype"])
            values = [typeconv(item) for item in strlist_from_filepath(fullfilepath)]
            properties.setdefault(propname, {})
            for id, value in zip(ids, values):
                nodes[id][propname] = value
                properties[propname][id] = None

        elif filedesc["doctype"] == "propkeyvalue":
            propname = filedesc["propname"]
            propkeyvalue = dict_from_filepath(fullfilepath)
            properties.setdefault(propname, {})
            for id, value in propkeyvalue.items():
                nodes.setdefault(id, {})
                nodes[id][propname] = value
                properties[propname][id] = None

            if "collections" in filedesc:
                col_ids = strlist_from_str(filedesc["collections"])
                assign_nodes_to_collections(col_ids, propkeyvalue.keys())

        elif filedesc["doctype"] == "propdict":
            propdict = dict_from_filepath(fullfilepath)
            for id, obj in propdict.items():
                nodes.setdefault(id, {})
                for propname in obj:
                    properties.setdefault(propname, {})
                    nodes[id][propname] = obj[propname]
                    properties[propname][id] = None

            if "collections" in filedesc:
                col_ids = strlist_from_str(filedesc["collections"])
                assign_nodes_to_collections(col_ids, propdict.keys())

        elif filedesc["doctype"] == "relkeyvalue":
            relname = filedesc["relname"]
            filedict = dict_from_filepath(fullfilepath)

            relationships.setdefault(relname, {})

            inverserelname = (
                filedesc["inverserelname"] if "inverserelname" in filedesc else None
            )
            if inverserelname:
                relationships.setdefault(inverserelname, {})

            if "sourcecollections" in filedesc:
                sourcecollections = strlist_from_str(filedesc["sourcecollections"])
                assign_nodes_to_collections(sourcecollections, filedict.keys())

            targetcollections = (
                strlist_from_str(filedesc["targetcollections"])
                if "targetcollections" in filedesc
                else None
            )

            for id, relvaluedict in filedict.items():
                nodes.setdefault(id, {})

                # massage relvalue to be dict
                if isinstance(relvaluedict, dict):
                    pass
                elif isinstance(relvaluedict, list):
                    relvaluedict = dict.fromkeys(relvaluedict)
                else:
                    relvaluedict = dict.fromkeys([relvaluedict])

                nodes[id][relname] = relvaluedict
                relationships[relname][id] = relvaluedict

                for targetid in relvaluedict:
                    nodes.setdefault(targetid, {})

                    if inverserelname:
                        relpropvalue = nodes[id][relname][targetid]
                        nodes[targetid].setdefault(inverserelname, {})
                        nodes[targetid][inverserelname][id] = relpropvalue
                        relationships[inverserelname].setdefault(targetid, {})
                        relationships[inverserelname][targetid][id] = relpropvalue

                if targetcollections:
                    assign_nodes_to_collections(targetcollections, relvaluedict.keys())

        else:
            print("error: unsupported file entry")


if __name__ == "__main__":
    load(sys.argv[1])
