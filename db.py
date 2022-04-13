import sys
from pathlib import Path
import json, yaml

nodes = {}
collections = {}
properties = {}


def reset():
    global nodes
    global collections
    global properties
    nodes = {}
    collections = {}
    properties = {}


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

    for filepath, filedesc in fileentries.items():

        fullfilepath = directorypath.joinpath(filepath)

        def strlist_from_filepath(filepath):
            with open(filepath) as file:
                return [line.strip() for line in file.readlines() if line.strip()]

        def assign_nodes_to_collections(collectiontext, nodeids):
            col_ids = [col_id.strip() for col_id in collectiontext.split(",")]
            for col_id in col_ids:
                collections.setdefault(col_id, {})
                collections[col_id].update(dict.fromkeys(nodeids))

        if filedesc["doctype"] == "id":
            ids = strlist_from_filepath(fullfilepath)
            for id in ids:
                nodes.setdefault(id, {})

            if "collections" in filedesc:
                assign_nodes_to_collections(filedesc["collections"], ids)

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
                assign_nodes_to_collections(
                    filedesc["collections"], propkeyvalue.keys()
                )

        elif filedesc["doctype"] == "propdict":
            propdict = dict_from_filepath(fullfilepath)
            for id, obj in propdict.items():
                nodes.setdefault(id, {})
                for propname in obj:
                    properties.setdefault(propname, {})
                    nodes[id][propname] = obj[propname]
                    properties[propname][id] = None

            if "collections" in filedesc:
                assign_nodes_to_collections(filedesc["collections"], propdict.keys())

        else:
            print("error: unsupported file entry")


if __name__ == "__main__":
    load(sys.argv[1])
