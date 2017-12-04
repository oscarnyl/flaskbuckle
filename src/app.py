from typing import Tuple, List, Dict, Optional, TypeVar, Union

from flask import Flask, jsonify, Response

import swagger

app = Flask(__name__)

StringReturn = Tuple[str, int]
ListReturn = Tuple[List[int], int]
DictReturn = Tuple[Dict, int]
MultiDimensionalListReturn = Tuple[List[List[List[int]]], int]


T = TypeVar("T")

FlaskReturn = Union[T, Tuple[T, int], Tuple[T, int, dict], Response]


class ExampleModel(swagger.SwaggerModel):
    """An example model"""
    _MIMETYPE = "application/json"
    hello: str = "world"


class ExampleRecursiveModel(swagger.SwaggerModel):
    """A recursive example model"""
    _MIMETYPE = "application/json"
    dict_field: ExampleModel = ExampleModel


@app.route("/")
@swagger.return_model(ExampleModel, 200)
def hello() -> FlaskReturn[dict]:
    """A simple Hello World endpoint"""
    return jsonify({"hello": "world"}), 200


@app.route("/routes/<int:one>/<two>")
@swagger.return_model(ExampleRecursiveModel, 200)
@swagger.header("X-CustomHeader")
def route_with_two_parameters(one: int, two: bool) -> FlaskReturn[dict]:
    """Route that has two parameters in path and one in header"""
    return jsonify({"dict_field": {"hello": "world"}}), 200


@app.route("/routes/<param>")
@swagger.header("X-CorrelationId", header_type=str)
def route_with_parameter(param: str) -> StringReturn:
    """Route with one parameter in path and one in header"""
    return param, 200


@app.route("/routes/something")
@swagger.header("X-Optional-Header", header_type=Optional[str])
@swagger.query_param("foo", param_type=int)
def some_route() -> MultiDimensionalListReturn:
    """Route with lots of different types of parameters"""
    return jsonify([[[100]]]), 200


@app.route("/manual_swagger_endpoint")
def manual_swagger_endpoint():
    return str(swagger.get_swagger(app, "foo", "0.0.1"))


swagger.enable_swagger(app, title="Swagger test API", version="0.0.2")

