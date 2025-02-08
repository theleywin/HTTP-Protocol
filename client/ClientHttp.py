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
        head = ""
        while True:
            data = req_socket.recv(1)
            if not data:
                break
            head += data.decode()
            if head.endswith(CharacterUtils.crlf * 2):
                break
        head_info = HTTPResponse.parse_response_head(head)
        if "Content-Length" in head_info["headers_fields"]:
            body = req_socket.recv(int(head_info["headers_fields"]["Content-Length"])).decode()
            
            
        status_line = (
        f"{head_info['http_version']} "
        f"{head_info['status_code']} "
        f"{head_info['reason_phrase']}"
    )
        return {
            "status": status_line,
            "headers": head_info["headers_fields"],
            "body": body
        }




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