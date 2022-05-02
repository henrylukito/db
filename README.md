# db
Local graph database from files

## Overview

Given multiple files with different data structures (list, key-value, dictionary) and a schema file, this Python module will build several dict objects that contain data like a graph database.

## Usage

Create a schema (yaml or json) that points to files and describe how to use the data from those files, then db.load.

Afterwards, use Python programming such as list comprehension to analyze db objects such as `node`, `relationship` etc.

## Objects

### node

dict where key is node id and value is dictionary for the node's properties and relationships, and the collections where they're in.

### collection

dict where key is collection id and value is the set of node ids of all the nodes inside that collection.

### property

dict where key is property id and value is subdict. subdict's key is node id and value is property value.

### relationship

dict where key is relationship id and value is subdict. subdict's key is node id of relationship source and value is subsubdict. subsubdict's key is node id of relationship target and value is relationship value.

## Schema

`files` should contain a list of files that will be read. For each file entry, `path` and `doctype` attributes are required. Additional attributes may be required depending on the doctype.

## Doctypes

### id

The file contains a list of node ids. `collection` is optional and can be used to assign nodes to collections.

### propvaluelist

The file contains a list of values for a property of nodes that were referenced in last opened file. `propname` is required to specify property name. `datatype` is optional to specify value type (otherwise it will be string).

### propkeyvalue

The file contains a dict where key is node id and value is the value of a property of that node. `propname` is required to specify property name. `collection` is optional and can be used to assign nodes to collections.

### propdict

The file contains a dict where key is node id and value is subdict. subdict's key is property name and value is property value. `propmap` is optional and can be used to select a subset of properties and rename them. `collection` is optional and can be used to assign nodes to collections.

### relkeyvalue

The file contains a dict where key is node id of relationship source and value is subdict. subdict's key is node id of relationship target and value is relationship value. `relname` is required to specify relationship name. `inverserelname` is optional and can be used to automatically define inverse relationship. `sourcecollections` is optional and can be used to assign source nodes to collections. `targetcollections` is optional and can be used to assign target nodes to collections.

### reldict

The file contains a dict where key is node id of relationship source and value is subdict. subdict's key is relationship name and value is subsubdict. subsubdict's key is node id of relationship target and value is relationship value. `relmap` is optional and can be used to select a subset of relationships and rename them. `inverserelmap` is optional and can be used to automatically define inverse relationship for each relationship. `sourcecollection` is optional and can be used to assign source nodes to collection. `targetcollectionmap` is optional and can be used to assign target nodes for each relationship to collections.

## Query Techniques

`len` function to count number of objects.

`list` constructor to list only ids (dictionary keys) and not values.

list comprehension

dict comprehension

## Possible Future Updates

- change map such as `propmap` to `propselect` and `proprename`
- support for files with table data structure (csv)
- instead of relationship just having a value, it should have properties or even relationships (relprop and relrel)
- a dict object where key is property id and value is property type
- id remapping feature for when file's node ids are not the same
- `expects` in schema to validate database after it is loaded
- `builds` in schema to automatically output certain files after database is loaded
