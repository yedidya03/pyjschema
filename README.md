# jschema

This package is handling json schema validation and parsing. It is capable of 
validating jsons according to schemas, but also it is capable of parsing a json
into a python object with pythonic types according to the schema.

## Features
* Json schema validation
* Json parsing according to a json schema

## Installation
```commandline
$ pip install jschema
```

## Examples
```python
>>> from pyjschema import loads
>>> json = '{"uuid": "9449771f-56ca-44c7-b9f6-d20315a2c6e0"}'
>>> # Setting up a property "uuid" to be of format "uuid"
>>> schema = {
... 'type': 'object', 
... 'properties': {'uuid': {'type': 'string', 'format': 'uuid'}}
... }
>>> loads(json, schema)
{'uuid': UUID('3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a')}
```