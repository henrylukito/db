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

    with open(schemapath) as file:
        schema = json.load(file)

    fileentries = schema["files"]

    directorypath = (
        Path(schema["directory"]) if "directory" in schema else Path(schemapath).parent
    )

    for filepath in fileentries:

        fullfilepath = directorypath.joinpath(filepath)

        with open(fullfilepath) as file:
            filetext = file.read()

        filedesc = fileentries[filepath]

        def assign_nodes_to_collections(collectiontext, nodeids):
            col_ids = [col_id.strip() for col_id in collectiontext.split(",")]
            for col_id in col_ids:
                collections.setdefault(col_id, {})
                collections[col_id].update(dict.fromkeys(nodeids))

        if filedesc["doctype"] == "id":
            ids = [line.strip() for line in filetext.splitlines() if line.strip()]
            for id in ids:
                nodes.setdefault(id, {})

            if "collections" in filedesc:
                assign_nodes_to_collections(filedesc["collections"], ids)

        elif filedesc["doctype"] == "propvaluelist":
            propname = filedesc["propname"]
            typeconv = str if "datatype" not in filedesc else eval(filedesc["datatype"])
            values = [
                typeconv(line.strip()) for line in filetext.splitlines() if line.strip()
            ]
            properties.setdefault(propname, {})
            for id, value in zip(ids, values):
                nodes[id][propname] = value
                properties[propname][id] = None

        elif filedesc["doctype"] == "propdict":
            propdict = (
                json.loads(filetext)
                if fullfilepath.suffix == ".json"
                else yaml.safe_load(filetext)
            )
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
