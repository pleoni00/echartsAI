import json
import requests
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import select

class Server(HTTPServer):
    processes = []
    tools = []
    id = 0
    dict_tools_server = []

    def __init__(self, server_address, RequestHandlerClass, command=None):
        if command != None:
            self.mcp_client = self.initialize_mcp_server(command)
        super().__init__(server_address, RequestHandlerClass)
    
    def initialize_mcp_server(self, commands):
        processes = []
        for command in commands:
            print(command)
            processes.append(subprocess.Popen(
                command.get("cmd"),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=command.get("cwd","."),
                text=True,
                bufsize=1,
            ))

            request = {
                'jsonrpc': '2.0',
                # 'id': self.get_id(),
                'method': 'tools/list'
            }
            time.sleep(3)
            while True:
                ready, _, _ = select.select([processes[-1].stdout], [], [], 1)
                if ready:
                    line = processes[-1].stdout.readline()
                    print(line)
                else:
                    break

            processes[-1].stdin.write(json.dumps(request) + '\n')
            processes[-1].stdin.flush()
            
            # Leggi risposta
            mcp_response = json.loads(processes[-1].stdout.readline())
            if isinstance(mcp_response, dict) and mcp_response.get('result',"-") is not None:
                mcp_response = self.refine_tools(json.loads(mcp_response)['result']['tools'])
            self.tools.extend(mcp_response)
            self.dict_tools_server.append([t.get('function').get('name') for t in mcp_response])
        print(f"Tools MCP disponibili: {json.dumps(self.tools)}")
        return processes
    
    def refine_tools(self, tools):
        return [
            {'type': 'function', 'function': {'name': t['name'], 'description': t['description'], 'parameters': t['inputSchema']}}
            for t in tools
        ]

    def __del__(self):
        for process in self.mcp_client:
            process.terminate()
            process.wait()



class HTTPRequestHandler(BaseHTTPRequestHandler):
    llm_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    mcp_url = ""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8083')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            user_messages = data.get("messages", [])
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        try:
            # Inizia con i messaggi dell'utente
            conversation = user_messages.copy() if isinstance(user_messages, list) else [user_messages]
            
            # Loop per gestire multiple tool calls
            llm_response = self.redirect_llm(conversation)

            while llm_response.get("choices", [])[0].get("finish_reason") == "tool_calls":
                message = llm_response.get("choices", [])[0].get("message")
                
                conversation.append({
                    'role': 'assistant',
                    'content': message.get('content'),
                    'tool_calls': message.get('tool_calls'),
                    "tool_choice": "auto"
                })

                inner_conversation = []
                for tool_call in message.get("tool_calls", []):
                    list_idx_server = [i for i, sottolista in enumerate(self.server.dict_tools_server) if tool_call["function"]["name"] in sottolista]
                    if len(list_idx_server)==0:
                        inner_conversation = [{
                            'role': 'system',
                            'content': f"tool named {tool_call["function"]["name"]} doesn't exist"
                        }]
                        break
                    mcp_request = {
                        'jsonrpc': '2.0',
                        'id': tool_call["id"],
                        'method': 'tools/call',
                        'params': {
                            'name': tool_call["function"]["name"],
                            'arguments': json.loads(tool_call["function"]["arguments"])
                        }
                    }
                    idx_server = [i for i, sottolista in enumerate(self.server.dict_tools_server) if tool_call["function"]["name"] in sottolista][0]
                    self.server.mcp_client[idx_server].stdin.write(json.dumps(mcp_request) + '\n')
                    self.server.mcp_client[idx_server].stdin.flush()
                    
                    response_line = self.server.mcp_client[idx_server].stdout.readline().strip()
                    
                    inner_conversation.append({
                        'tool_call_id': tool_call["id"],
                        'role': 'tool',
                        'name': tool_call["function"]["name"],
                        'content': response_line
                    })
                conversation.extend(inner_conversation)
                llm_response = self.redirect_llm(conversation)
            
            final_message = llm_response.get("choices", [])[0].get("message")
            conversation.append(final_message)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers() 
            print(conversation)
            self.wfile.write(json.dumps({
                'messages': conversation,
                # 'response': final_message.get('content')
            }).encode("utf-8"))
            
        except Exception as e:
            import traceback
            self.send_error(500, f"LLM Error: {str(e)}\n{traceback.format_exc()}")

    def redirect_llm(self, request):
        response = requests.post(
        self.llm_url, 
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GEMINI_API_KEY}"
        },
        json={
                "model": "gemini-2.0-flash",
                "messages": request,
                "tools": self.server.tools
            }
        )        

        response.raise_for_status()
        print(f"\n\n{response.json()}\n\n")

        return response.json()

if __name__ == "__main__":
    command = []
    # command.append({"cmd": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]})
    command.append({"cmd": ["python3", "openAPI_server.py", "openAPI.json"]})
    # command.append({"cmd": ['node', 'src/dataset.js'], "cwd": "/home/paolo/Documents/echarts-mcp"})

    server = Server(("0.0.0.0", 8000), HTTPRequestHandler, command)
    server.serve_forever()

