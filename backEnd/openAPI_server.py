import sys
import json
from requests import request

def resolve_ref(schema, openapi_spec):
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"]
            schema_name = ref_path.split('/')[-1]
            resolved_schema = openapi_spec.get(schema_name, {})
            return resolve_ref(resolved_schema, openapi_spec)
        else:
            result = {}
            for key, value in schema.items():
                result[key] = resolve_ref(value, openapi_spec)
            return result
    
    elif isinstance(schema, list):
        return [resolve_ref(item, openapi_spec) for item in schema]
    
    else:
        return schema

def openapi_to_functions(openapi_url):
    with open(openapi_url) as my_file:
        openapi_spec = json.loads(my_file.read())
    functions = []
    metadata = {}
    schemas = openapi_spec.get("components",{}).get("schemas",None)
    for path, methods in openapi_spec["paths"].items():
        for method, spec in methods.items():
            function_name = spec.get("operationId", "")
            desc = spec.get("description") or spec.get("summary", "")
            schema = {"type": "object", "properties": {}}
            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                schema["properties"]["requestBody"] = resolve_ref(req_body,schemas)
            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }
            function_name = '_'.join([method,function_name])
            functions.append(
                {
                    "type": "function", 
                    "function": {
                        "name": function_name, 
                        "description": desc, 
                        "parameters": schema
                    }
                }
            )
            metadata[function_name] = {
                "method": method,
                "path": path,
                "base_url": openapi_spec["servers"][0]["url"],  # base_url if base_url is not None else "",
                "params": params 
            }
    return functions, metadata


if __name__ == "__main__":
    tools, metadata_tools = openapi_to_functions(sys.argv[1])
    while True:
        message = json.loads(sys.stdin.readline())
        match message.get("method",""):
            case "tools/list":
                sys.stdout.write(json.dumps(tools) + "\n")
                sys.stdout.flush()
            case "tools/call":
                tool_name = message.get("params", {}).get("name")
                tool_args = message.get("params", {}).get("arguments", {})
                tool = next((t for t in tools if t["function"]["name"] == tool_name), None)
                
                if tool:
                    metadata = metadata_tools[tool["function"]["name"]]  
                    url = ''.join([metadata["base_url"],metadata["path"]])                   
                    params = {}
                    json_url = None

                    if (tool_args.get("requestBody") is not None):
                        json_url = tool_args["requestBody"]

                    path_params = list(filter(lambda x: x["in"]=='path', metadata["params"]))
                    if len(path_params) > 0:
                        for p in path_params:
                            if p["name"] in tool_args["parameters"]:
                                url = url.replace(f"{{{p['name']}}}", tool_args["parameters"][p["name"]])
                    
                    query_params = list(filter(lambda x: x["in"]=='query', metadata["params"]))
                    if len(query_params) > 0:
                        for q in query_params:
                            if q["name"] in tool_args.get("parameters",[]):
                                params[q["name"]] = tool_args["parameters"][q["name"]]
                                        
                    response = request(metadata["method"],url,params=params,json=json_url)
                    result = {
                        "jsonrpc": "2.0",
                        "id": message.get("id",0),
                        "result": {"content": [{"type": "text", "text": response.text}]}
                    }
                    sys.stdout.write(json.dumps(result) + "\n")
                    sys.stdout.flush()
