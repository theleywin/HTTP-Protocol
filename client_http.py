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