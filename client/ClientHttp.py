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
    
    def send_request(self, method: str, header: str, data: str, redirect_count=0, max_redirects=5):
    
        headers_dict = json.loads(header)
        headers_dict = {}

        
        headers_dict['Host'] = self.host

        request = HTTPRequest.build_http_request(
            method=method,
            uri=self.path,
            headers=headers_dict,
            body=data
        )

        req_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        req_socket.connect((self.host, self.port))
        req_socket.send(request.encode())
        response = self.receive_response(req_socket)
        req_socket.close()

        # Handle redirects
        if str(response['status']) in ['301', '302', '303', '307', '308'] and redirect_count < max_redirects:
            location = response['headers'].get('Location')
            if not location:
                return response

            new_method = method
            new_data = data
            if response['status'] == '303':
                new_method = 'GET'
                new_data = ''

            new_headers = headers_dict.copy()
            if not new_data:
                new_headers.pop('Content-Length', None)
                new_headers.pop('Content-Type', None)

            new_client = HTTPClient(location)
            return new_client.send_request(
                method=new_method,
                header=json.dumps(new_headers),
                data=new_data,
                redirect_count=redirect_count + 1,
                max_redirects=max_redirects
            )

        return response
        
        
    def receive_response(self, req_socket: socket.socket):
        head = ""
        while True:
            data = req_socket.recv(1)
            if not data:
                break
            head += data.decode()
            if head.endswith(CharacterUtils.crlf * 2):
                break
        header_contents = HTTPResponse.parse_response_head(head)
        
        if "Transfer-Encoding" in header_contents["headers_fields"] and header_contents["headers_fields"]["Transfer-Encoding"] == "chunked":
                body = self.chunked_body(req_socket)
                
        elif "Content-Length" in header_contents["headers_fields"]:
            body = req_socket.recv(int(header_contents["headers_fields"]["Content-Length"])).decode()
            
            
        status_line = (
        f"{header_contents['http_version']} "
        f"{header_contents['status_code']} "
        f"{header_contents['reason_phrase']}"
    )
        return {
            "status_line": status_line,
            "http_version": header_contents['http_version'],
            "status":header_contents['status_code'],
            "reason":header_contents['reason_phrase'],
            "headers": header_contents["headers_fields"],
            "body": body
        }


    def chunked_body(self, req_socket: socket.socket):
        body = ""
        while True:
            chunk = ""
            while True:
                    data = req_socket.recv(1)
                    chunk += data.decode()
                    if chunk.endswith(CharacterUtils.crlf):
                        break
               
            
            chunk_size = int(chunk.strip(), 16)
            if chunk_size == 0:
                break
            chunk_data = req_socket.recv(chunk_size).decode()
            body += chunk_data
            req_socket.recv(2)
            
        return body

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