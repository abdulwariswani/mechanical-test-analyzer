def IP_count(records):
    """Aggregate records by source IP: hit count, users targeted, timestamps."""
    result = {}
    for entry in records:
        ip = entry['IP_address']
        if ip not in result:
            result[ip] = {
                'count': 0,
                'users': set(),
                'timestamps': [],
            }
        result[ip]['count'] += 1
        result[ip]['users'].add(entry['username'])
        result[ip]['timestamps'].append(entry['timestamp'])
    return result