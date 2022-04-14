# db
Local graph database made from different files

## Overview

Given multiple files with different data structures (lists, key-values, dictionaries) and a schema file that describes how to interpret them, this Python module/script will generate several `dict` objects that combined the data from those files to form a graph database.

## Loading Database

As a module:

```python
import db
db.load('schema.json')
```

Python interactive mode in a shell:

```shell
python -i db.py schema.json
```

## Using Database

After loading, the following `dict` objects are available: `nodes`, `collections`, `properties` and `relationships`.

Use various programming techniques in Python (type conversion, list comprehension, dictionary comprehension etc) to make queries on these `dict` objects.
