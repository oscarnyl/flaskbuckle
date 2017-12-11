import inspect
import os
import re
import json
from typing import (
    Tuple,
    Callable,
    GenericMeta,
    List,
    Dict,
    _Union
)
from enum import Enum

from flask import Flask, render_template_string, send_file


PATH_REGEX = re.compile(r"{.*:")
SWAGGER_FILE_LOCATION = "/swagger.json"
SWAGGER_UI_CSS = "/swagger-ui.css"
SWAGGER_UI_CSS_MAP = SWAGGER_UI_CSS + ".map"
SWAGGER_UI_JS_BUNDLE = "/swagger-ui-bundle.js"
SWAGGER_UI_JS_BUNDLE_MAP = SWAGGER_UI_JS_BUNDLE + ".map"
SWAGGER_UI_STANDALONE_PRESET_JS = "/swagger-ui-standalone-preset.js"
SWAGGER_UI_STANDALONE_PRESET_JS_MAP = SWAGGER_UI_STANDALONE_PRESET_JS + ".map"


SWAGGER_UI_PATH = "/swagger-ui"


class SwaggerException(Exception):
    pass


def enable_swagger(
    application: Flask,
    title="",
    version="",
    route="/api/docs"
) -> None:
    current_path = os.path.dirname(os.path.realpath(__file__))

    @application.route(route + SWAGGER_FILE_LOCATION)
    def generate_swagger() -> Tuple[dict, int, dict]:
        swagger = _generate_swagger(application, title, version, route)
        return json.dumps(swagger, separators=(",", ":")), 200

    @application.route(route, strict_slashes=False)
    def swagger_ui():
        with open(current_path + "/swagger-ui/index.html", "r") as f:
            template_string = "".join(f.readlines())
            return render_template_string(
                template_string,
                swagger_url=route + SWAGGER_FILE_LOCATION,
                base_url=route
            )

    @application.route(route + SWAGGER_UI_JS_BUNDLE)
    def swagger_ui_js_bundle():
        return send_file(
            current_path + SWAGGER_UI_PATH + SWAGGER_UI_JS_BUNDLE,
            mimetype="application/javascript"
        )

    @application.route(route + SWAGGER_UI_JS_BUNDLE_MAP)
    def swagger_ui_js_bundle_map():
        return send_file(
            current_path + SWAGGER_UI_PATH + SWAGGER_UI_JS_BUNDLE_MAP,
            mimetype="application/json"
        )

    @application.route(route + SWAGGER_UI_STANDALONE_PRESET_JS)
    def swagger_ui_standalone_js():
        return send_file(
            current_path + SWAGGER_UI_PATH + SWAGGER_UI_STANDALONE_PRESET_JS,
            mimetype="application/javascript"
        )

    @application.route(route + SWAGGER_UI_STANDALONE_PRESET_JS_MAP)
    def swagger_ui_standalone_js_map():
        return send_file(
            current_path +
            SWAGGER_UI_PATH +
            SWAGGER_UI_STANDALONE_PRESET_JS_MAP,
            mimetype="application/javascript"
        )

    @application.route(route + SWAGGER_UI_CSS)
    def swagger_ui_css():
        return send_file(
            current_path + SWAGGER_UI_PATH + SWAGGER_UI_CSS,
            mimetype="text/css"
        )

    @application.route(route + SWAGGER_UI_CSS_MAP)
    def swagger_ui_css_map():
        return send_file(
            current_path + SWAGGER_UI_PATH + SWAGGER_UI_CSS_MAP,
            mimetype="text/css"
        )


def get_swagger(
    application: Flask,
    title: str,
    version: str,
    route: str="/api/docs"
) -> dict:
    return _generate_swagger(application, title, version, route)


def header(name: str, header_type=str) -> Callable:
    def header_decorator(f: Callable) -> Callable:
        header_metadata = {}
        if hasattr(f, "__SWAGGER_HEADERS"):
            if name in f.__SWAGGER_HEADERS:
                return f
            header_metadata.update(f.__SWAGGER_HEADERS)
        header_metadata[name] = header_type
        f.__SWAGGER_HEADERS = header_metadata
        return f
    return header_decorator


def query_param(name: str, param_type=str) -> Callable:
    def query_param_decorator(f: Callable) -> Callable:
        query_param_metadata = {}
        if hasattr(f, "__SWAGGER_QUERY_PARAMS"):
            if name in f.__SWAGGER_QUERY_PARAMS:
                return f
            query_param_metadata.update(f.__SWAGGER_QUERY_PARAMS)
        query_param_metadata[name] = param_type
        f.__SWAGGER_QUERY_PARAMS = query_param_metadata
        return f
    return query_param_decorator


class SwaggerModel:
    def _example(self):
        properties = [item for item in dir(self) if not item.startswith("_")]
        return {key: getattr(self.__class__, key) for key in properties}

    def _schema(self):
        return {
            k: v for k, v in self.__annotations__.items()
            if not k.startswith("_")
        }


def return_model(model: SwaggerModel, status_code: int) -> Callable:
    def return_model_decorator(f: Callable) -> Callable:
        return_model_metadata = {}
        if hasattr(f, "__SWAGGER_RETURN_MODELS"):
            if status_code in f.__SWAGGER_RETURN_MODELS:
                return f
            return_model_metadata.update(f.__SWAGGER_RETURN_MODELS)
        return_model_metadata[status_code] = model
        f.__SWAGGER_RETURN_MODELS = return_model_metadata
        return f
    return return_model_decorator


def _generate_model_description(
    model: SwaggerModel,
    status_code: int,
    f: Callable
) -> str:
    description = inspect.getdoc(model)
    if not description:
        description = f"{f.__name__}: {status_code}"
    model_inst = model()
    return {
        "description": description,
        "examples": {
            model._MIMETYPE: _generate_model_example(model_inst)
        },
        "schema": _generate_swagger_schema(
            _generate_model_schema(model_inst)
        )
    }


def _generate_model_schema(model_instance: SwaggerModel) -> dict:
    generated_schema = model_instance._schema()
    replacements = {}
    for key, value in generated_schema.items():
        if issubclass(value, SwaggerModel):
            replacements[key] = _generate_model_schema(
                getattr(model_instance, key)()
            )
    generated_schema.update(replacements)
    return generated_schema


def _generate_swagger_schema(model_mapping: dict) -> dict:
    return {
        "type": "object",
        "properties": {
            key: _generate_swagger_type(value)
            for key, value in model_mapping.items()
        }
    }


def _generate_model_example(model_instance: SwaggerModel) -> dict:
    generated_example = model_instance._example()
    replacements = {}
    for key, value in generated_example.items():
        if isinstance(value, type):
            if not issubclass(value, SwaggerModel):
                raise SwaggerException(
                    f"Invalid swagger model definition: {key}"
                )
            replacements[key] = _generate_model_example(value())
    if replacements:
        generated_example.update(replacements)
    return generated_example


def _gorg(t):
    if hasattr(t, "_gorg"):
        return t._gorg
    return t.__origin__


SWAGGER_TYPE_MAP = {
    str: {"type": "string"},
    int: {"type": "integer", "format": "int64"},
    bool: {"type": "boolean"},
    float: {"type": "number"}
}


def _generate_swagger_type(t) -> dict:
    if isinstance(t, dict):
        return {
            "type": "object",
            "properties": {
                key: _generate_swagger_type(value)
                for key, value in t.items()
            }
        }
    if t in SWAGGER_TYPE_MAP:
        return SWAGGER_TYPE_MAP[t].copy()
    if isinstance(t, GenericMeta):
        if _gorg(t) is List:
            inner_type = _generate_swagger_type(t.__args__[0])
            return {
                "type": "array",
                "items": inner_type
            }
        if _gorg(t) is Tuple:
            return _generate_swagger_type(t.__args__[0])
        if _gorg(t) is Dict:
            return {"type": "object"}
    if isinstance(t, _Union) \
    and len(t.__args__) == 2 \
    and t.__args__[1] is type(None):  # noqa: E721
        inner_type = _generate_swagger_type(t.__args__[0])
        inner_type.update({"x-nullable": True})
        return inner_type
    raise SwaggerException(f"Cannot understand type: {t}")


class ParameterLocation(Enum):
    PATH = "path"
    HEADER = "header"
    QUERY = "query"


def _generate_parameter_description(
    name: str,
    location: ParameterLocation,
    required: bool
) -> dict:
    return {
        "name": name,
        "in": location.value,
        "required": required
    }


def _generate_path_parameter_description(
    parameter,
    rule_function: Callable
) -> dict:
    parameter_description = _generate_parameter_description(
        parameter, ParameterLocation.PATH, True
    )
    annotation = inspect.signature(
        rule_function
    ).parameters[parameter].annotation
    if annotation != inspect.Parameter.empty:
        parameter_description.update(_generate_swagger_type(annotation))
    return parameter_description


def _generate_header_parameter_description(header, header_type) -> dict:
    description = _generate_parameter_description(
        header,
        ParameterLocation.HEADER,
        True
    )
    description.update(_generate_swagger_type(header_type))
    if description.get("x-nullable"):
        description["required"] = False
        del description["x-nullable"]
    return description


def _generate_query_parameter_description(query_name, query_type) -> dict:
    description = _generate_parameter_description(
        query_name,
        ParameterLocation.QUERY,
        True
    )
    description.update(_generate_swagger_type(query_type))
    if description.get("x-nullable"):
        description["required"] = False
        del description["x-nullable"]
    return description


def _generate_method(application: Flask, rule, method) -> dict:
    if method in ["HEAD", "OPTIONS"]:
        return None
    rule_function = application.view_functions[rule.endpoint]
    description = inspect.getdoc(rule_function)
    if not description:
        description = rule.endpoint
    entry = {"description": description}
    if rule.arguments:
        parameters = []
        for path_param in rule.arguments:
            param_desc = _generate_path_parameter_description(
                path_param,
                rule_function
            )
            parameters.append(param_desc)
        entry["parameters"] = parameters
    else:
        entry["parameters"] = []
    if hasattr(rule_function, "__SWAGGER_HEADERS"):
        for header, header_type in rule_function.__SWAGGER_HEADERS.items():
            entry["parameters"].append(
                _generate_header_parameter_description(
                    header,
                    header_type
                )
            )
    if hasattr(rule_function, "__SWAGGER_QUERY_PARAMS"):
        for query_param, t in rule_function.__SWAGGER_QUERY_PARAMS.items():
            entry["parameters"].append(
                _generate_query_parameter_description(query_param, t)
            )
    entry["responses"] = {}
    if hasattr(rule_function, "__SWAGGER_RETURN_MODELS"):
        for code, model in rule_function.__SWAGGER_RETURN_MODELS.items():
            entry["responses"][code] = _generate_model_description(
                model,
                code,
                rule_function
            )

    if not entry["responses"]:
        entry["responses"]["default"] = {
            "description": f"{rule.endpoint}: default response"
        }
    return entry


def _generate_methods(application: Flask, rule) -> dict:
    methods = {}
    for method in rule.methods:
        method_definition = _generate_method(application, rule, method)
        if not method_definition:
            continue
        methods[method.lower()] = method_definition
    return methods


def _generate_swagger(
    application: Flask,
    title: str,
    version: str,
    route: str
) -> dict:
    paths = {}
    for rule in application.url_map.iter_rules():
        rulestring = rule.rule.replace("<", "{").replace(">", "}")
        methods = _generate_methods(application, rule)
        cleaned_rulestring = PATH_REGEX.sub("{", rulestring)
        paths[cleaned_rulestring] = methods

    keylist = list(paths.keys())
    for k in keylist:
        if (route and k.startswith(route)) or k.startswith("/static"):
            paths.pop(k)
    return {
        "swagger": "2.0",
        "paths": paths,
        "info": {
            "title": title,
            "version": version
        }
    }