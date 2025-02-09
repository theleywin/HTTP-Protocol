import socket
from threading import Thread
import json
import xml.etree.ElementTree as ET

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
            request_data = client_socket.recv(4096).decode('utf-8')
            if not request_data:
                response = "HTTP/1.1 400 Bad Request"+crlf+"Content-Type: text/plain"+crlf+crlf+"Empty request received. Please send a valid HTTP request."
                client_socket.sendall(response.encode())
                client_socket.close()
                return

            request_line = request_data.split(crlf)[0]
            method, path, http_version = request_line.split()

            headers = {}
            header_lines = request_data.split(crlf+crlf)[0].split(crlf)[1:]
            for line in header_lines:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key] = value

            body = ''
            if crlf+crlf in request_data:
                body = request_data.split(crlf+crlf)[1]

            if method == 'GET':
                response_body = f'Received GET request from {path}'

            elif method == 'POST':
                content_type = headers.get("Content-Type", "text/plain")
                try:
                    if content_type == "application/json":
                        try:
                            json.loads(body) 
                            response_body = f"POST request successful! JSON body received: {body}."
                        except json.JSONDecodeError:
                            raise ValueError("Malformed JSON body")
                    elif content_type == "application/xml":
                        try:
                            import xml.etree.ElementTree as ET
                            ET.fromstring(body) 
                            response_body = f"POST request successful! XML body received: {body}."
                        except ET.ParseError:
                            raise ValueError("Malformed XML body")
                    else:
                        # Manejar cuerpos de texto o desconocidos
                        response_body = f"POST request successful! Plain text body received: {body}."
                except (IndexError, ValueError) as e:
                    response_headers = [
                        "HTTP/1.1 400 Bad Request",
                        "Content-Type: text/plain",
                        f"Content-Length: {len(str(e))}"
                    ]
                    response = crlf.join(response_headers) +crlf+crlf + str(e)
                    client_socket.sendall(response.encode('utf-8'))
                    client_socket.close()
                    return
                
            elif method == 'PUT':
                content_type = headers.get("Content-Type", "text/plain")
                try:
                    if content_type == "application/json":
                        try:
                            json.loads(body) 
                            response_body = f"PUT request successful! JSON body received: {body}."
                        except json.JSONDecodeError:
                            raise ValueError("Malformed JSON body")
                    elif content_type == "application/xml":
                        try:
                            ET.fromstring(body) 
                            response_body = f"PUT request successful! XML body received: {body}."
                        except ET.ParseError:
                            raise ValueError("Malformed XML body")
                    else:
                        # Manejar cuerpos de texto o desconocidos
                        response_body = f"PUT request successful! Plain text body received: {body}."
                except (IndexError, ValueError) as e:
                    response_headers = [
                        "HTTP/1.1 400 Bad Request",
                        "Content-Type: text/plain",
                        f"Content-Length: {len(str(e))}"
                    ]
                    response = crlf.join(response_headers) +crlf+crlf + str(e)
                    client_socket.sendall(response.encode('utf-8'))
                    client_socket.close()
                    return
            elif method == 'DELETE':
                response_body = f'Resource at {path} deleted successfully'
            elif method == 'OPTIONS':
                response_headers = [
                    "HTTP/1.1 204 No Content",
                    "Allow: GET, POST, HEAD, PUT, DELETE, OPTIONS, TRACE, CONNECT",
                    "Content-Length: 0"
                ]
                response = crlf.join(response_headers) + crlf+crlf
                client_socket.sendall(response.encode())
                client_socket.close()
                return
            elif method == 'HEAD':
                response_body = ''
            elif method == 'TRACE':
                response_body = request_data
            elif method == 'CONNECT':
                target = path.strip("/")  # Supongamos que el target está en el path
                response_body = f"CONNECT method successful! Tunneling to {target} established."
            else:
                response_body = 'Method Not Allowed'

            status_code = 200

            status_phrase = {
                200: 'OK',
                201: 'Created',
                204: 'No Content',
                400: 'Bad Request',
                404: 'Not Found',
                405: 'Method Not Allowed',
                500: 'Internal Server Error',
                501: 'Not Implemented'
            }.get(status_code, 'Unknown Status')

            content_type = headers.get("Content-Type", "text/plain")

            response_line = f'{http_version} {status_code} {status_phrase}'+crlf
            headers = f'Content-Type: {content_type}'+crlf
            content_length = f'Content-Length: {len(response_body)}'+crlf
            response = response_line + headers + content_length + crlf + response_body
            client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling request: {e}")
            body = 'Internal Server Error'
            status_code = 500
            status_phrase = "OK"
            response_line = f'HTTP/1.1 {status_code} {status_phrase}'+crlf
            headers = 'Content-Type: text/plain'+crlf
            content_length = f'Content-Length: {len(body)}'+crlf
            response = response_line + headers + content_length + crlf + body
            client_socket.sendall(response.encode('utf-8'))
        finally:
            client_socket.close()

    
    
if __name__ == '__main__':
    server = HTTPServer()
    server.start()