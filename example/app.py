import sys
from os import path
from typing import Tuple, List, Dict, Optional, TypeVar, Union

from flask import Flask, jsonify, Response, request

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
from flaskbuckle import swagger  # noqa: E402

app = Flask(__name__)

StringReturn = Tuple[str, int]
ListReturn = Tuple[List[int], int]
DictReturn = Tuple[Dict, int]
MultiDimensionalListReturn = Tuple[List[List[List[int]]], int]


T = TypeVar("T")

FlaskReturn = Union[T, Tuple[T, int], Tuple[T, int, dict], Response]

EXAMPLE_MODEL = {
    "hello": (str, "world")
}

EXAMPLE_RECURSIVE_MODEL = {
    "dict_field": (dict, EXAMPLE_MODEL)
}


EXAMPLE_GENERIC_MODEL = {
    "list_field": (List[dict], [
        EXAMPLE_MODEL
    ])
}


@app.route("/")
@swagger.return_model(EXAMPLE_MODEL, 200, "application/json")
def hello() -> FlaskReturn[dict]:
    """A simple Hello World endpoint"""
    return jsonify({"hello": "world"}), 200


@app.route("/routes/<int:one>/<two>")
@swagger.return_model(EXAMPLE_RECURSIVE_MODEL, 200, "application/json")
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


@app.route("/post_something", methods=["POST"])
@swagger.post_model(EXAMPLE_MODEL)
@swagger.return_model(EXAMPLE_MODEL, 200, "application/json")
def post_something():
    """echo, but in post format!"""
    return request.data, 200


@app.route("/manual_swagger_endpoint")
def manual_swagger_endpoint():
    return str(swagger.get_swagger(app, "foo", "0.0.1"))


@app.route("/some/route/with/<untyped_parameter>")
@swagger.return_model(EXAMPLE_GENERIC_MODEL, 200, "application/json")
def route_with_untyped_parameter(untyped_parameter):
    return untyped_parameter


swagger.enable_swagger(app, title="Swagger test API", version="0.0.2")
