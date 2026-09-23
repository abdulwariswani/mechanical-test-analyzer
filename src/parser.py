import re 
def parsed_log(lines):
    """Yield one record per failed-password line in `lines`."""
    pattern = re.compile(r'''
        ^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})       # Timestamp
        .*?\bFailed\s+password\s+for\s+(?:invalid\s+user\s+)? # Trigger phrase
        (\S+)                                                # Username
        \s+from\s+(\d{1,3}(?:\.\d{1,3}){3})                  # IP address
        (?:\s+port\s+(\d+))?                                 # Optional port
    ''', re.VERBOSE)

    for line in lines:
        for match in pattern.finditer(line):
            yield {
                'timestamp': match.group(1),
                'username': match.group(2),
                'IP_address': match.group(3),
                'port': match.group(4),  # None if port absent
            }