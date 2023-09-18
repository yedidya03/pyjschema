# pyjschema

Unlike other packages that handle the Json-Schema format, this package is 
pretending to give a solution for getting common pythonic types (like datetime, 
UUID, etc) from json data according to the Json-Schema format.

Alongside that, the package has validation capabilities like several other 
packages.

## Features
* Json schema validation
* Json parsing according to a json schema
* Extending Json-Schema by adding custom formats

## Installation
```commandline
$ pip install jschema
```

## Examples
### Basic Use
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

### Custom Formats
The package allows also to extend the default Json-Schema formats and define 
more formats that will be structured in the json data. An example for that could 
be adding a "bytes" format that will be structured in the json as base64 phrase.
An optional implementation for that with pyjschema would be:
```python
from base64 import b64encode, b64decode
from pyjschema import Formatter, JsonSchemaParser

class BytesFormatter(Formatter):
    symbol = 'bytes'
    
    def decode(self, raw: str) -> bytes:
        return b64decode(raw)
    
    def encode(self, data: bytes) -> str:
        return b64encode(data).decode()


if __name__ == '__main__':
    schema = {'type': 'string', 'format': 'bytes'}
    parser = JsonSchemaParser(schema, extended_formats=[BytesFormatter])

    data = parser.loads('"SGVsbG8gV29ybGQh"')

    print(type(data), data)
    # output: <class 'bytes'> b'Hello World!'
```

## References

* [GitHub repo](https://github.com/yedidya03/pyjschema)
* [pypi project](https://pypi.org/project/pyjschema)