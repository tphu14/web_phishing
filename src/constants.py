"""
Constants cho feature extraction
"""

SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'account', 'update', 'verify', 'secure', 'banking',
    'confirm', 'suspend', 'locked', 'alert', 'warning', 'urgent', 'expire',
    'password', 'credential', 'validate', 'authenticate', 'wallet', 'payment',
    'billing', 'invoice', 'refund', 'prize', 'winner', 'claim', 'free',
    'gift', 'bonus', 'rewards', 'click', 'now', 'limited', 'offer'
]

URL_SHORTENERS = [
    'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd',
    'buff.ly', 'adf.ly', 'bit.do', 'short.io', 'tiny.cc', 'rebrand.ly',
    'cutt.ly', 'bl.ink', 'shorte.st', 'clk.sh'
]

TRUSTED_DOMAINS = [
    'google.com', 'youtube.com', 'facebook.com', 'wikipedia.org',
    'amazon.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'microsoft.com', 'apple.com', 'netflix.com', 'reddit.com',
    'yahoo.com', 'ebay.com', 'github.com', 'stackoverflow.com',
    'wordpress.com', 'adobe.com', 'paypal.com', 'live.com'
]

SUSPICIOUS_TLDS = [
    '.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.cc', '.xyz', '.top',
    '.work', '.click', '.link', '.download', '.racing', '.review'
]

TRUSTED_TLDS = ['.com', '.org', '.net', '.edu', '.gov', '.mil']

BRAND_NAMES = [
    'google', 'facebook', 'amazon', 'microsoft', 'apple', 'paypal',
    'netflix', 'ebay', 'twitter', 'instagram', 'linkedin', 'yahoo',
    'alibaba', 'samsung', 'oracle', 'walmart', 'visa', 'mastercard',
    'wells', 'chase', 'bank', 'citibank', 'hsbc', 'barclays'
]