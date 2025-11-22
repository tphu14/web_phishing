"""
Feature extraction và normalization
"""

import re
from matplotlib.pylab import log2
import tldextract
from urllib.parse import urlparse, parse_qs
from .constants import *
from .utils import calculate_entropy, max_consecutive_chars, check_ssl_certificate, check_dns

# Normalization functions
def normalize_length(value, short_thresh, long_thresh):
    """Chuẩn hóa độ dài"""
    if value < short_thresh:
        return 1
    elif value < long_thresh:
        return 0
    else:
        return -1

def normalize_count(value, low_thresh, high_thresh):
    """Chuẩn hóa số lượng"""
    if value <= low_thresh:
        return 1
    elif value <= high_thresh:
        return 0
    else:
        return -1

def normalize_ratio(ratio):
    """Chuẩn hóa ratio [0-1]"""
    if ratio < 0.3:
        return 1
    elif ratio < 0.6:
        return 0
    else:
        return -1

def normalize_entropy(entropy):
    """Chuẩn hóa entropy"""
    if entropy < 3.5:
        return 1
    elif entropy < 4.5:
        return 0
    else:
        return -1

def extract_features(url):
    """
    Trích xuất 80+ features và normalize về {-1, 0, 1}
    
    Parameters:
    url: str - URL cần phân tích
    
    Returns:
    dict - Features đã normalized
    """
    features = {}
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        scheme = parsed.scheme
        query = parsed.query
        fragment = parsed.fragment
        
        ext = tldextract.extract(url)
        subdomain = ext.subdomain
        domain_name = ext.domain
        tld = ext.suffix
        
        if not domain:
            domain = url.split('/')[0] if '/' in url else url
        
        url_lower = url.lower()
        
        # ========== URL-BASED FEATURES (30) ==========
        
        # Lengths
        features['URL_Length'] = normalize_length(len(url), 54, 75)
        features['Domain_Length'] = normalize_length(len(domain), 20, 30)
        features['Path_Length'] = normalize_length(len(path), 30, 60)
        
        # Protocol
        features['Has_HTTPS'] = 1 if scheme == 'https' else (-1 if scheme == 'http' else 0)
        features['Has_Protocol'] = 1 if scheme in ['http', 'https'] else -1
        
        # Special characters
        features['Num_Dots'] = normalize_count(url.count('.'), 3, 5)
        features['Num_Hyphens'] = normalize_count(url.count('-'), 0, 2)
        features['Num_Underscores'] = normalize_count(url.count('_'), 0, 1)
        features['Num_Slashes'] = normalize_count(url.count('/'), 3, 5)
        features['Num_At'] = 1 if url.count('@') == 0 else -1
        features['Num_Ampersand'] = normalize_count(url.count('&'), 0, 3)
        features['Num_Percent'] = normalize_count(url.count('%'), 0, 2)
        
        # Subdomain
        subdomain_count = len(subdomain.split('.')) if subdomain else 0
        features['Num_Subdomains'] = normalize_count(subdomain_count, 1, 2)
        features['Subdomain_Length'] = normalize_length(len(subdomain), 10, 20)
        features['Has_WWW'] = 1 if subdomain.startswith('www') else -1
        
        # Query & Fragment
        features['Query_Length'] = normalize_length(len(query), 20, 50)
        features['Fragment_Length'] = normalize_length(len(fragment), 10, 30)
        features['Num_Query_Params'] = normalize_count(len(parse_qs(query)), 0, 3)
        
        # Path
        dir_depth = len([p for p in path.split('/') if p])
        features['Directory_Depth'] = normalize_count(dir_depth, 2, 4)
        ext_len = len(path.split('.')[-1]) if '.' in path else 0
        features['File_Extension_Length'] = normalize_count(ext_len, 0, 4)
        features['Has_Index_Page'] = 1 if 'index' in path.lower() else -1
        
        # IP & Port
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        features['Has_IP'] = -1 if re.search(ip_pattern, domain) else 1
        features['Has_Port'] = -1 if parsed.port and parsed.port not in [80, 443] else 1
        features['Is_IP_Only'] = -1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', domain) else 1
        
        # Suspicious patterns
        features['Has_Double_Slash'] = -1 if '//' in path else 1
        features['Has_At_Symbol'] = -1 if '@' in url else 1
        features['Has_Tilde'] = -1 if '~' in url else 1
        
        # Encoding
        percent_count = len(re.findall(r'%[0-9A-Fa-f]{2}', url))
        unicode_count = sum(1 for c in url if ord(c) > 127)
        features['Percent_Encoding_Count'] = normalize_count(percent_count, 0, 3)
        features['Unicode_Char_Count'] = normalize_count(unicode_count, 0, 2)
        features['Has_Hex_Encoding'] = -1 if re.search(r'\\x[0-9A-Fa-f]{2}', url) else 1
        
        # ========== DOMAIN-BASED FEATURES (15) ==========
        
        # TLD
        features['TLD_Length'] = normalize_length(len(tld), 3, 5)
        if f'.{tld}' in TRUSTED_TLDS:
            features['TLD_Type'] = 1
        elif f'.{tld}' in SUSPICIOUS_TLDS:
            features['TLD_Type'] = -1
        else:
            features['TLD_Type'] = 0
        features['Is_Common_TLD'] = 1 if tld in ['com', 'org', 'net'] else -1
        
        # Reputation
        is_trusted = any(t in domain.lower() for t in TRUSTED_DOMAINS)
        features['Is_Trusted_Domain'] = 1 if is_trusted else -1
        features['Is_Shortening_Service'] = -1 if any(s in domain.lower() for s in URL_SHORTENERS) else 1
        features['Domain_Age'] = 1 if is_trusted else 0  # Simplified
        
        # Brand
        has_brand = any(b in domain_name.lower() for b in BRAND_NAMES)
        features['Has_Brand_Name'] = 1 if has_brand and is_trusted else (-1 if has_brand else 0)
        features['Has_Typosquatting'] = -1 if (has_brand and not is_trusted) else 1
        features['Brand_Distance'] = 0
        
        # Structure
        token_count = len(re.split(r'[.-]', domain_name))
        features['Domain_Token_Count'] = normalize_count(token_count, 1, 3)
        longest_token = max([len(w) for w in re.split(r'[.-]', domain_name)] or [0])
        features['Longest_Domain_Token'] = normalize_length(longest_token, 10, 15)
        shortest_token = min([len(w) for w in re.split(r'[.-]', domain_name) if w] or [999])
        features['Shortest_Domain_Token'] = 1 if shortest_token >= 3 else -1
        
        # Patterns
        features['Has_Prefix_Suffix'] = -1 if re.search(r'-.*\.', domain) else 1
        digit_ratio = sum(c.isdigit() for c in domain_name) / max(len(domain_name), 1)
        features['Digit_Domain_Ratio'] = normalize_ratio(digit_ratio)
        consonants = max([len(m.group()) for m in re.finditer(r'[bcdfghjklmnpqrstvwxyz]+', domain_name.lower())] or [0])
        features['Consecutive_Consonants'] = normalize_count(consonants, 4, 6)
        
        # ========== SSL/SECURITY FEATURES (10) ==========
        
        ssl_info = check_ssl_certificate(domain)
        features['Has_Valid_SSL'] = ssl_info['has_ssl']
        days = ssl_info['days_to_expire']
        features['SSL_Validity_Period'] = 1 if days > 180 else (0 if days > 30 else -1)
        features['Has_Trusted_CA'] = 1 if ssl_info['is_trusted'] else -1
        features['SSL_Days_To_Expire'] = features['SSL_Validity_Period']
        features['Forces_HTTPS'] = 1 if scheme == 'https' else -1
        
        # Simplified features
        for feat in ['Has_HSTS', 'Has_Security_Headers', 'Certificate_Transparency', 
                     'Has_Mixed_Content', 'SSL_Version']:
            features[feat] = 0
        
        # ========== DNS/NETWORK FEATURES (5) ==========
        
        dns_info = check_dns(domain)
        features['Has_DNS_Record'] = dns_info['has_dns']
        features['Is_Suspicious_IP_Range'] = -1 if dns_info['is_private'] else 1
        features['DNS_Resolve_Time'] = 0
        features['Has_DNSSEC'] = 0
        features['Num_Nameservers'] = 0
        
        # ========== CONTENT FEATURES (10) - Simplified ==========
        
        for feat in ['Has_Forms', 'Has_Password_Field', 'External_Links_Ratio',
                     'Has_IFrame', 'Has_Popup', 'Content_Length',
                     'Favicon_From_Domain', 'Has_Copyright', 'Has_Social_Links', 'Page_Rank']:
            features[feat] = 0
        
        # ========== LEXICAL FEATURES (10) ==========
        
        digit_ratio = sum(c.isdigit() for c in url) / max(len(url), 1)
        features['Digit_Ratio'] = normalize_ratio(digit_ratio)
        
        letter_ratio = sum(c.isalpha() for c in url) / max(len(url), 1)
        features['Letter_Ratio'] = 1 if letter_ratio > 0.7 else 0
        
        special_ratio = sum(not c.isalnum() for c in url) / max(len(url), 1)
        features['Special_Char_Ratio'] = normalize_ratio(special_ratio)
        
        upper_ratio = sum(c.isupper() for c in url) / max(len(url), 1)
        features['Uppercase_Ratio'] = normalize_count(int(upper_ratio * 10), 0, 3)
        
        features['Lowercase_Ratio'] = 1 if letter_ratio > 0.7 else 0
        features['Mixed_Case'] = -1 if (upper_ratio > 0 and letter_ratio > 0) else 1
        
        vowel_ratio = sum(c.lower() in 'aeiou' for c in url) / max(len(url), 1)
        features['Vowel_Ratio'] = 1 if vowel_ratio > 0.3 else 0
        
        features['Consonant_Ratio'] = 1 if vowel_ratio < 0.5 else 0
        
        max_consec = max_consecutive_chars(domain)
        features['Max_Consecutive_Chars'] = normalize_count(max_consec, 2, 3)
        
        char_diversity = len(set(url)) / max(len(url), 1)
        features['Char_Repetition_Rate'] = 1 if char_diversity > 0.6 else 0
        
        # ========== HEURISTIC FEATURES (10) ==========
        
        features['URL_Entropy'] = normalize_entropy(calculate_entropy(url))
        features['Domain_Entropy'] = normalize_entropy(calculate_entropy(domain))
        features['Path_Entropy'] = normalize_entropy(calculate_entropy(path))
        
        keyword_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
        features['Suspicious_Keyword_Count'] = normalize_count(keyword_count, 0, 1)
        
        features['Has_Urgent_Words'] = -1 if any(w in url_lower for w in ['urgent', 'immediate', 'now', 'alert']) else 1
        features['Has_Financial_Words'] = -1 if any(w in url_lower for w in ['bank', 'paypal', 'payment', 'credit']) else 1
        
        random_score = calculate_entropy(domain_name) / max(log2(len(domain_name)), 1) if len(domain_name) > 0 else 0
        features['Random_String_Score'] = normalize_ratio(random_score)
        
        features['Has_Dictionary_Words'] = 0
        
        obfusc_score = (percent_count + unicode_count) / max(len(url), 1)
        features['Obfuscation_Score'] = normalize_ratio(obfusc_score)
        
        complexity = (subdomain_count + dir_depth + len(parse_qs(query))) / 3
        features['URL_Complexity_Score'] = normalize_count(int(complexity), 1, 3)
        
    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        # Return default (all 0)
        features = {f'Feature_{i}': 0 for i in range(90)}
    
    return features
