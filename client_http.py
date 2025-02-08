import json


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