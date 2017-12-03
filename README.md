flask-swagger
-------------

Generate swagger documentation from your API implemented in Flask, and expose a
Swagger UI for this API. Tries to do as much as possible automatically, and when
automatically is not possible it tries to be as non-intrusive as possible.
Becomes much better if you bother to use type annotations in your application!


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


##### `swagger.enable_swagger(application: Flask, title="", version="", route="/api/docs")`
Enables swagger for this flask application. By default, the swaggerfile will be
exposed at http://flask-app-url/api/docs/swagger.json and Swagger UI will be
exposed at http://flask-app-url/api/docs .

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

##### `@swagger.return_model(model: SwaggerModel, status_code: int)`
Decorator to mark that this endpoint has a return model. The return model shall
be a class inheriting from `swagger.SwaggerModel`, and shall have the format
explained in its section. Return models double as both schemas and examples for
the endpoint.

Parameters:
- `model: SwaggerModel` - A class extending from `swagger.SwaggerModel`. Note
  that you should not pass an instance of a class; you should reference the
  class directly.
- `status_code: int` - The status code that will return the declared model. ex:
  `200`

##### `class SwaggerModel`
A class describing a return model. Classes inheriting from this class describes
both schemas and examples for endpoints. An example:

```python
from flask_swagger import SwaggerModel

class ExampleModel(SwaggerModel):
    hello: str = "world"
```

Would generate the following schema:
```json
{
    "type": "object",
    "properties": {
        "hello": {
            "type": "string"
        }
    }
}
```

And the following example:
```json
{
    "hello": "world"
}
```
`SwaggerModel`s may define properties that in turn are SwaggerModels - these
will be treated as objects.

