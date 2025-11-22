"""
Utility functions
"""

import re
import socket
import ssl
from math import log2
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

def calculate_entropy(text):
    """Tính Shannon entropy"""
    if not text or len(text) == 0:
        return 0
    counter = Counter(text)
    length = len(text)
    entropy = -sum((count/length) * log2(count/length) for count in counter.values())
    return entropy

def max_consecutive_chars(text):
    """Đếm ký tự lặp liên tiếp tối đa"""
    if len(text) == 0:
        return 0
    max_count = 1
    current_count = 1
    for i in range(1, len(text)):
        if text[i] == text[i-1]:
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_count = 1
    return max_count

def check_ssl_certificate(domain, timeout=2):
    """Kiểm tra SSL certificate"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_to_expire = (not_after - datetime.now()).days
                
                issuer = dict(x[0] for x in cert['issuer'])
                is_trusted = any(t in str(issuer).lower() 
                               for t in ['verisign', 'digicert', 'comodo', 'godaddy', 'letsencrypt'])
                
                return {
                    'has_ssl': 1,
                    'days_to_expire': days_to_expire,
                    'is_trusted': is_trusted
                }
    except:
        return {
            'has_ssl': -1,
            'days_to_expire': -1,
            'is_trusted': False
        }

def check_dns(domain, timeout=2):
    """Kiểm tra DNS records"""
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(domain)
        is_private = ip.startswith(('10.', '192.168.', '172.'))
        return {'has_dns': 1, 'is_private': is_private, 'ip': ip}
    except:
        return {'has_dns': -1, 'is_private': False, 'ip': None}