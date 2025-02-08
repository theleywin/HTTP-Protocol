import json
import re
import socket
import argparse


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
        if "Content-Length" in head_info["headers"]:
            body = req_socket.recv(int(head_info["headers"]["Content-Length"])).decode()
        return {
            "status": head_info["status_code"],
            "body": body
        }



class CharacterUtils:
    def __init__(self):
        # Special characters used for validation
        self.carriage_return = '\r'
        self.line_feed = '\n'
        self.space = ' '
        self.horizontal_tab = '\t'
        self.crlf = self.carriage_return + self.line_feed
        self.separators = '()<>@,;:\\\"/[]?={} ' + self.horizontal_tab

    def is_ascii(self, c: str) -> bool:
        """Checks if the character is within the ASCII range (0-127)."""
        return 0 <= ord(c) <= 127

    def is_uppercase(self, c: str) -> bool:
        """Checks if the character is an uppercase letter (A-Z)."""
        return c.isupper()

    def is_lowercase(self, c: str) -> bool:
        """Checks if the character is a lowercase letter (a-z)."""
        return c.islower()

    def is_letter(self, c: str) -> bool:
        """Checks if the character is a letter (uppercase or lowercase)."""
        return c.isalpha()

    def is_numeric(self, c: str) -> bool:
        """Checks if the character is a digit (0-9)."""
        return c.isdigit()

    def is_control_char(self, c: str) -> bool:
        """Checks if the character is a control character (0-31 or 127)."""
        return ord(c) in range(0, 32) or ord(c) == 127

    def is_carriage_return(self, c: str) -> bool:
        """Checks if the character is a carriage return ('\r')."""
        return c == self.carriage_return

    def is_line_feed(self, c: str) -> bool:
        """Checks if the character is a line feed ('\n')."""
        return c == self.line_feed

    def is_space(self, c: str) -> bool:
        """Checks if the character is a space (' ')."""
        return c == self.space

    def is_tab(self, c: str) -> bool:
        """Checks if the character is a horizontal tab ('\t')."""
        return c == self.horizontal_tab

    def is_printable(self, c: str) -> bool:
        """Checks if the character is printable (not a control character)."""
        return self.is_ascii(c) and not self.is_control_char(c)

    def is_hexadecimal(self, c: str) -> bool:
        """Checks if the character is a hexadecimal digit (0-9, A-F, a-f)."""
        return c in "0123456789ABCDEFabcdef"

    def is_separator(self, c: str) -> bool:
        """Checks if the character is a separator."""
        return c in self.separators
    
    
class HTTPRequest:
    @staticmethod
    def is_supported_method(method: str) -> bool:
        """Checks if the given method is a valid HTTP method."""
        return method in ["OPTIONS", "GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT"]

    @staticmethod
    def create_request_line(method: str, uri: str, http_version: str) -> str:
        """Constructs the request line using the HTTP method, URI, and version."""
        separator = CharacterUtils.space
        line_break = CharacterUtils.crlf
        return method + separator + uri + separator + http_version + line_break

    @staticmethod
    def format_headers(headers_json: str) -> str:
        """Formats HTTP headers from a JSON string representation."""
        if not headers_json:
            return ""
        headers_dict = json.loads(headers_json)
        headers = ""
        for key, value in headers_dict.items():
            headers += key + ": " + value + CharacterUtils.crlf
        return headers

    @staticmethod
    def build_http_request(method: str, uri: str, headers: str = None, body: str = None) -> str:
        """Builds the complete HTTP request by assembling the request line, headers, and body."""
        request_line = HTTPRequest.create_request_line(method, uri, HttpHelper.format_http_version(1, 1))
        headers_section = HTTPRequest.format_headers(headers)
        return request_line + headers_section + CharacterUtils.crlf + (body if body else "")





class HttpHelper:
    @staticmethod
    def format_http_version(major: int, minor: int) -> str:
        return f"HTTP/{major}.{minor}"

    @staticmethod
    def parse_url(url: str):
        if url.startswith("http://"):
            url = url[7:] 
            default_port = 8080
        elif url.startswith("https://"):
            url = url[8:] 
            default_port = 443
        else:
            default_port = 8080

        # Split the host and path
        split_index = url.find("/")
        if split_index == -1:
            domain_part = url
            path = "/"
        else:
            domain_part = url[:split_index]
            path = url[split_index:]

        # Extract port if specified
        port_index = domain_part.find(":")
        if port_index == -1:
            host = domain_part
            port = default_port
        else:
            host = domain_part[:port_index]
            port = int(domain_part[port_index + 1:])

        return host, port, path
    
class HTTPResponse:
    @staticmethod
    def parse_response_head(head: str) -> dict:
        """Parses the response head to extract the HTTP version, status code, reason phrase, and headers."""
        status_line, headers_section = head.split(CharacterUtils.crlf, 1)
        headers_list = headers_section.split(CharacterUtils.crlf)
        
        header_fields = {}
        for header in headers_list:
            if not header:
                continue
            key, value = re.split(r":\s+", header, 1)
            header_fields[key] = value

        http_version, status_code, reason_phrase = status_line.split(CharacterUtils.space, 2)

        return {
            "http_version": http_version,
            "status_code": int(status_code),
            "reason_phrase": reason_phrase,
            "headers": header_fields
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
    
    try:
        headers = json.loads(args.headers)  # Convert headers from string to dictionary
    except json.JSONDecodeError:
        raise ValueError("Invalid headers format. Provide a valid JSON string.")

    return {
        "method": args.method.upper(),
        "url": args.url,
        "headers": headers,
        "data": args.data,
    }
    
    
def main():
    args = parse()
    
    client = HTTPClient(args["url"])
    response = client.send_request(method=args["method"], header=args["headers"], data=args["data"])
    print(json.dumps(response, indent=4))
    
if __name__=="__main__":
    main()