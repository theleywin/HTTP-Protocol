import json
import socket
import argparse
from CharacterUtils import CharacterUtils
from HttpHelper import HttpHelper
from HTTPRequest import HTTPRequest 
from HTTPResponse import HTTPResponse 

class HTTPClient :
    def __init__(self, url):
        host, port, path = HttpHelper.parse_url(url)
        self.host = host
        self.port = port
        self.url = url
        self.path = path
    
    def send_request(self, method: str, header: str, data: str):
        req_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        req_socket.connect((self.host, self.port))        
        request = HTTPRequest.build_http_request(method=method, uri=self.path,  headers=header, body=data)
        req_socket.send(request.encode())
        response = self.receive_response(req_socket)
        req_socket.close()
        return response
        
        
    def receive_response(self, req_socket: socket.socket):
        # Leer headers eficientemente
        buffer = b""
        while True:
            data = req_socket.recv(4096)
            if not data:
                break
            buffer += data
            if b"\r\n\r\n" in buffer:
                header_part, body_buffer = buffer.split(b"\r\n\r\n", 1)
                break

        # Parsear línea de estado y headers
        head_info = HTTPResponse.parse_response_head(header_part.decode())
        status_code = head_info["status_code"]
        headers = {k.lower(): v for k, v in head_info["headers"].items()}  # Headers en minúsculas

        # Determinar si hay cuerpo
        body = b""
        if not (self.method == "HEAD" or 100 <= status_code < 200 or status_code in (204, 304)):
            # Manejar Transfer-Encoding: chunked
            if "transfer-encoding" in headers and "chunked" in headers["transfer-encoding"].lower():
                while True:
                    # Leer tamaño del chunk
                    chunk_line, body_buffer = self._read_until_crlf(body_buffer, req_socket)
                    chunk_size = int(chunk_line.split(b";", 1)[0].strip(), 16)
                    if chunk_size == 0:
                        break
                    # Leer datos del chunk
                    chunk_data, body_buffer = self._read_exact(chunk_size, body_buffer, req_socket)
                    body += chunk_data
                    # Ignorar CRLF final del chunk
                    _, body_buffer = self._read_exact(2, body_buffer, req_socket)
            
            # Manejar Content-Length
            elif "content-length" in headers:
                content_length = int(headers["content-length"])
                remaining = content_length - len(body_buffer)
                body = body_buffer
                while remaining > 0:
                    data = req_socket.recv(remaining)
                    if not data:
                        break
                    body += data
                    remaining -= len(data)
            
            # Leer hasta fin de conexión (HTTP/1.0)
            else:
                body = body_buffer
                while True:
                    data = req_socket.recv(4096)
                    if not data:
                        break
                    body += data

        # Descomprimir cuerpo si es necesario
        if "content-encoding" in headers:
            body = self._decode_body(headers["content-encoding"], body)

        # Decodificar cuerpo según charset
        charset = self._get_charset_from_headers(headers)
        try:
            body_str = body.decode(charset)
        except UnicodeDecodeError:
            body_str = body  # Mantener como bytes si hay error

        return {
            "version": head_info.get("version", "HTTP/1.1"),
            "status": status_code,
            "reason": head_info.get("reason", ""),
            "headers": headers,
            "body": body_str
        }


    def _read_until_crlf(self, buffer: bytes, sock: socket.socket) -> tuple:
        while b"\r\n" not in buffer:
            data = sock.recv(4096)
            if not data:
                return buffer, b""
            buffer += data
        line, _, buffer = buffer.partition(b"\r\n")
        return line, buffer

    def _read_exact(self, n: int, buffer: bytes, sock: socket.socket) -> tuple:
        while len(buffer) < n:
            data = sock.recv(n - len(buffer))
            if not data:
                break
            buffer += data
        result = buffer[:n]
        remaining = buffer[n:]
        return result, remaining

    def _decode_body(self, encoding: str, body: bytes) -> bytes:
        encoding = encoding.lower()
        if encoding == "gzip":
            import gzip
            return gzip.decompress(body)
        elif encoding == "deflate":
            import zlib
            return zlib.decompress(body)
        return body

    def _get_charset_from_headers(self, headers: dict) -> str:
        content_type = headers.get("content-type", "")
        if "charset=" in content_type:
            return content_type.split("charset=")[-1].split(";")[0].strip()
        return "utf-8"  # Valor por defecto




def parse():
    """Parses command-line arguments for making an HTTP request."""
    parser = argparse.ArgumentParser(description="Send an HTTP request.")
    
    parser.add_argument(
        "-m", "--method", type=str, required=True,
        help="HTTP method of the request (e.g., GET, POST, PUT, DELETE)"
    )
    parser.add_argument(
        "-u", "--url", type=str, required=True,
        help="Target resource URL"
    )
    parser.add_argument(
        "-H", "--headers", type=str, default="{}",
        help="Headers for the request in JSON format (e.g., '{\"Content-Type\": \"application/json\"}')"
    )
    parser.add_argument(
        "-d", "--data", type=str, default="",
        help="Body of the request (useful for POST/PUT requests)"
    )
    
    args = parser.parse_args()
    

    return {
        "method": args.method.upper(),
        "url": args.url,
        "headers": args.headers,
        "data": args.data,
    }
    
    
def main():
    args = parse()
    
    client = HTTPClient(args["url"])
    response = client.send_request(method=args["method"], header=args["headers"], data=args["data"])
    print(json.dumps(response, indent=4))
    
if __name__=="__main__":
    main()