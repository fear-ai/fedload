import hashlib

def hash_content(content):
    if not isinstance(content, str):
        raise TypeError("Content must be a string")
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
