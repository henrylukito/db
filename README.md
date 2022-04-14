# db
Local graph database from files

## Overview

Given multiple files with different data structures (list, key-value, dictionary) and a schema file, this Python module/script will build several `dict` objects that serve as a graph database.

## Usage

Create a schema file (YAML or JSON), then load it with db.py:

Import as module in a script:

```python
import db
db.load('schema.json')
```

Or with Python interactive mode in a shell:

```shell
python -i db.py schema.json
```

Then access `dict` objects like `node`, `collection`, `property` and `relationship` (prefix with `db.` if imported as module)

Use various methods in Python like list comprehension or dictionary comprehension to perform queries on these `dict` objects.
