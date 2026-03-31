import hashlib
import os
from mygit_core.repository import get_mygit_path

def hash_file(filepath):
    """Hash a file's content and return the SHA1 hex string. Does not store."""
    with open(filepath, "rb") as f:
        content = f.read()
    return hashlib.sha1(content).hexdigest()

def store_object(filepath):
    """Hash the file, store its content in objects/, return the hash."""
    with open(filepath, "rb") as f:
        content = f.read()

    file_hash = hashlib.sha1(content).hexdigest()
    object_path = get_mygit_path("objects", file_hash)

    if not os.path.exists(object_path):
        with open(object_path, "wb") as f:
            f.write(content)

    return file_hash

def restore_object(file_hash, destination):
    """Read a stored blob from objects/ and write it back to destination."""
    object_path = get_mygit_path("objects", file_hash)
    with open(object_path, "rb") as f:
        content = f.read()
    with open(destination, "wb") as f:
        f.write(content)

