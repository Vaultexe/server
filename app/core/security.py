import hashlib


def sha256_hash(data: bytes) -> str:
    """Get a sha256 hash of a string."""
    return hashlib.sha256(data).hexdigest()
