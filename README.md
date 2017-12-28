flaskbuckle
-------------

Generate swagger documentation from your API implemented in Flask, and expose a
Swagger UI for this API. Tries to do as much as possible automatically, and when
automatically is not possible it tries to be as non-intrusive as possible.
Becomes much better if you bother to use type annotations in your application!

### Quickstart

1. `pip install flaskbuckle` 
2. Add to application configuration:
```python
from flaskbuckle import swagger
...
swagger.enable_swagger(app)
```
3. Access swagger ui at `http://flask-app-url/api/docs`
4. If necessary, access swaggerfile at
   `http://flask-app-url/api/docs/swagger.json`
To use this library, simply add `swagger.enable_swagger(app)` to your where you
configure your application object. This call will do nothing more but add some
routes to your application.

This library is best used with type annotations and docstrings in this manner:


```python
@app.route("/example/<int:parameter>")
def hello_world(parameter: int):
    """A small description of this view"""
    ...
```


### API

##### `swagger.enable_swagger(application: Flask, title="", version="", route="/api/docs")`
Enables swagger for this flask application. By default, the swaggerfile will be
exposed at `http://flask-app-url/api/docs/swagger.json` and Swagger UI will be
exposed at `http://flask-app-url/api/docs` .

Parameters:
- `application: Flask` - an instance of your flask application
- `title: str` - The title of your flask application
- `version: str` - The version string for your application, ex: `"1.0.0"`
- `route: str` - The path to expose swagger documentation on.

##### `@swagger.header(name: str, header_type=str)`
Decorator to mark that this endpoint takes a header parameter.

Parameters:
- `name: str` - The name of the header, ex: `"X-Custom-Header"`
- `header_type` - A type variable declaring what the type of the header is, ex:
  `str`, `Optional[int]`, `bool`

##### `@swagger.query_param(name: str, param_type=str)`
Decorator to mark that this endpoint takes a query string parameter.

Parameters:
- `name: str` - The name of the query string parameter, ex: `include`, `fields`
- `param_type` - A type variable declaring what the type of the header is, ex:
  `str`, `Optional[bool]`, `List[int]`

##### `@swagger.post_model(model: SwaggerModel)`
Decorator to mark that this endpoint has a post model. The post model shall be a
dict of `SwaggerModel`-type, and shall have the format explained in its section.
Post models double as both schemas and examples for the endpoint.
RESTRICTION: You may only have one post model per endpoint. This is a restriction
imposed by the Swagger 2.0-standard.

Parameters:
- `model: SwaggerModel` - A dict of `SwaggerModel`-type.

##### `@swagger.return_model(model: SwaggerModel, status_code: int, mimetype: str)`
Decorator to mark that this endpoint has a return model. The return model shall
be a dict of `SwaggerModel`-type, and shall have the format
explained in its section. Return models double as both schemas and examples for
the endpoint.

Parameters:
- `model: SwaggerModel` - A dict of `SwaggerModel`-type.
- `status_code: int` - The status code that will return the declared model. ex:
  `200`
- `mimetype: str` - The mimetype of the declared model. ex: `"application/json"`

##### `type SwaggerModel`
A dict describing a Swagger Model. The type definition is: `Dict[Any, Tuple[type, Any]]` where the
key is the field name, the first tuple item is the type of the field and the second tuple item is
an example value for this field. If the type is set to `dict`, the example field must be set to
another `SwaggerModel`, to allow for arbitrary model definitions. An example:

```python
EXAMPLE_MODEL = {
    "hello": (str, "world")
}

NESTED_EXAMPLE_MODEL = {
    "foo": (int, 1),
    "bar": (dict, EXAMPLE_MODEL)
}
```

Would generate the following schemas:
```json
{
    "type": "object",
    "properties": {
        "hello": {
            "type": "string"
        }
    }
},
{
    "type": "object",
    "properties": {
        "foo": {
            "type": "integer",
            "format": "int64"
        },
        "bar": {
            "type": "object",
            "properties": {
                "hello": {
                    "type": "string"
                }
            }
        }
    }
}
```

And the following examples:
```json
{
    "hello": "world"
},
{
    "foo": 1,
    "bar": {
        "hello": "world"
    }
}
```


##### `class SwaggerException`
If at any time you've done something wrong (or gods forbid the implementation of
this library is incorrect), flaskbuckle wont hesitate to raise a
`SwaggerException`, hopefully with some information about why this occured.

##### `swagger.generate_swagger(application: Flask, title="", version="", path="/api/docs") -> dict`
If you need to get the swaggerfile as a dict programmatically for some reason,
flaskbuckle provides a function for this. Note that it *must* be called after
you've added your views to the application: calling it before wont do anything
good at all.

Parameters:
- `application: Flask` - an instance of your flask application
- `title: str` - The title of your flask application
- `version: str` - The version string for your application, ex: `"1.0.0"`
- `route: str` - If you've previously enabled swagger on a custom path you need
  to specify it here, else flaskbuckles own paths will be listed in the returned
  swagger spec.

### Notable swagger extensions
- flaskbuckle will generate a `"x-nullable"`-key and set it to `true` for
  anything declared with the type `Optional[T]`. As this is non-standard it will
  not have any effect on SwaggerUI, but you may find that other tooling can
  utilize this field (perhaps most notable for python developers is `flex`).
- flaskbuckle will encode UUID-annotations as being of type string and additionally
  will set "format" to be "uuid" for these types. This is supported (and suggested)
  by the Swagger 2.0-spec, but not required nor defined by the spec.

### TODO
Things that need to be done in this library, in order of priority.

- Add referenced models to `definitions` and reference them via `$ref` instead
  of the naive approach currently used
- Add testing
- Refactor code to not be just a mess in one file
- Implement missing swagger features (I'm sure there are at least a few)


### Thanks to
Swashbuckle, which inspired this library (and its name, once I figured out my
working title was already used).

