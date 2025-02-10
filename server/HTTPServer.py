import socket
from threading import Thread
import json
import xml.etree.ElementTree as ET
import token

carriage_return = '\r'
line_feed = '\n'
crlf = carriage_return+line_feed

class HTTPServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")
            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            client_socket.settimeout(10)
            while True:
                request_data = b""
                while True:
                    chunk = client_socket.recv(1)
                    if not chunk:
                        break
                    request_data += chunk
                    if crlf + crlf in request_data.decode('utf-8'):
                        break  # Fin de los encabezados
                if not request_data:
                    break
                
                request_data = request_data.decode('utf-8')
                request_line = request_data.split(crlf)[0]
                method, path, http_version = request_line.split()

                headers = {}
                header_lines = request_data.split(crlf)[1:]
                for line in header_lines:
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        headers[key] = value

                body = ""
                if "Content-Length" in headers:
                    body = client_socket.recv(int(headers["Content-Length"])).decode()

                connection_header = headers.get('Connection', 'close').lower()
                keep_alive = (http_version == 'HTTP/1.1' and connection_header != 'close') or connection_header == 'keep-alive'

                response = self.process_request(method, path, http_version, headers, body, request_data)

                client_socket.sendall(response.encode('utf-8'))

                if not keep_alive:
                    break

        except socket.timeout:
            print("Conexión cerrada por timeout")
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()
    
    def process_request(self, method, path, http_version, headers, body, request_data):
        try: 
            if path.startswith("/secure"):
                if "Authorization" in headers:
                    auth_token = headers["Authorization"].replace("Bearer ", "").strip()
                    if auth_token != token.TOKEN:
                        response_body = "Invalid or missing authorization token."
                        response_headers = [
                            f"Content-Type: text/plain",
                            f"Content-Length: {len(response_body)}",
                        ]
                        return self.build_response(http_version,401,response_headers,response_body)
                else:
                    response_body = "Authorization header missing."
                    response_headers = [
                        f"Content-Type: text/plain",
                        f"Content-Length: {len(response_body)}",
                    ]
                    return self.build_response(http_version,401,response_headers,response_body)
            if method == 'GET':
                response_body = f'Received GET request from {path}'
                response_headers = [
                    f"Content-Type: text/plain",
                    f"Content-Length: {len(response_body)}",
                ]
                return self.build_response(http_version,200,response_headers,response_body)
            elif method == 'POST':
                content_type = headers.get("Content-Type", "text/plain")
                try:
                    if content_type == "application/json":
                        try:
                            json.loads(body) 
                            response_body = f"{body}"
                            response_headers = [
                                f"Content-Type: {content_type}",
                                f"Content-Length: {len(response_body)}"
                            ]
                            return self.build_response(http_version,201,response_headers,response_body)
                        except json.JSONDecodeError:
                            raise ValueError("Malformed JSON body")
                    elif content_type == "application/xml":
                        try:
                            import xml.etree.ElementTree as ET
                            ET.fromstring(body) 
                            response_body = f"{body}"
                            response_headers = [
                                f"Content-Type: {content_type}",
                                f"Content-Length: {len(response_body)}"
                            ]
                            return self.build_response(http_version,201,response_headers,response_body)
                        except ET.ParseError:
                            raise ValueError("Malformed XML body")
                    else:
                        # Manejar cuerpos de texto o desconocidos
                        response_body = f"{body}"
                        response_headers = [
                            f"Content-Type: {content_type}",
                            f"Content-Length: {len(response_body)}"
                        ]
                        return self.build_response(http_version,201,response_headers,response_body)
                except (IndexError, ValueError) as e:
                    response_headers = [
                        "Content-Type: text/plain",
                        f"Content-Length: {len(str(e))}"
                    ]
                    return self.build_response(http_version,400,response_headers,str(e))
            elif method == 'PUT':
                content_type = headers.get("Content-Type", "text/plain")
                try:
                    if content_type == "application/json":
                        try:
                            json.loads(body) 
                            response_body = f"{body}"
                            response_headers = [
                                f"Content-Type: {content_type}",
                                f"Content-Length: {len(response_body)}"
                            ]
                            return self.build_response(http_version,200,response_headers,response_body)
                        except json.JSONDecodeError:
                            raise ValueError("Malformed JSON body")
                    elif content_type == "application/xml":
                        try:
                            ET.fromstring(body) 
                            response_body = f"{body}"
                            response_headers = [
                                f"Content-Type: {content_type}",
                                f"Content-Length: {len(response_body)}"
                            ]
                            return self.build_response(http_version,200,response_headers,response_body)
                        except ET.ParseError:
                            raise ValueError("Malformed XML body")
                    else:
                        # Manejar cuerpos de texto o desconocidos
                        response_body = f"{body}"
                        response_headers = [
                            f"Content-Type: {content_type}",
                            f"Content-Length: {len(response_body)}"
                        ]
                        return self.build_response(http_version,200,response_headers,response_body)
                except (IndexError, ValueError) as e:
                    response_headers = [
                        "Content-Type: text/plain",
                        f"Content-Length: {len(str(e))}"
                    ]
                    return self.build_response(http_version,400,response_headers,str(e))
            elif method == 'DELETE':
                response_body = f'Resource at {path} deleted successfully'
                response_headers = [
                    f"Content-Type: text/plain",
                    f"Content-Length: {len(response_body)}"
                ]
                return self.build_response(http_version,200,response_headers,response_body)
            elif method == 'OPTIONS':
                response_headers = [
                    "Allow: GET, POST, HEAD, PUT, DELETE, OPTIONS, TRACE, CONNECT",
                    "Content-Length: 0"
                ]
                return self.build_response(http_version,204,response_headers,'')
            elif method == 'HEAD':
                response_headers = [
                    "Content-Type: text/plain",
                    f"Content-Length: {len(body)}"
                ]
                return self.build_response(http_version,200,response_headers,'')
            elif method == 'TRACE':
                response_body = request_data
                response_headers = [
                    "Content-Type: text/plain",
                    f"Content-Length: {len(response_body)}"
                ]
                return self.build_response(http_version,200,response_headers,response_body)
            elif method == 'CONNECT':
                target = path.strip("/")  # Supongamos que el target está en el path
                response_body = f"CONNECT method successful! Tunneling to {target} established."
                response_headers = [
                    "Content-Type: text/plain",
                    f"Content-Length: {len(response_body)}"
                ]
                return self.build_response(http_version,200,response_headers,response_body)
            else:
                response_body = 'Method Not Allowed'
                response_headers = [
                    "Content-Type: text/plain",
                    f"Content-Length: {len(response_body)}"
                ]
                return self.build_response(http_version,400,response_headers,response_body)
        except Exception as e:
            print(f"Error handling request: {e}")
            response_body = 'Internal Server Error'
            response_headers = [
                "Content-Type: text/plain",
                f"Content-Length: {len(response_body)}"
            ]
            return self.build_response(http_version,500,response_headers,response_body)
        
    def build_response(self,http_version,status_code,response_headers,response_body):
        response_line = f'{http_version} {status_code} {self.get_status_phrase(status_code)}' + crlf
        headers = crlf.join(response_headers) + crlf
        response = response_line + headers + crlf + response_body
        return response
    
    def get_status_phrase(self,status_code):
        return {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error',
            501: 'Not Implemented'
        }.get(status_code, 'Unknown Status')
    
if __name__ == '__main__':
    server = HTTPServer()
    server.start()