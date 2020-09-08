import json
import hashlib as hl


# __all__ = ['hash_str_256', 'hash_block']
def hash_str_256(string):
    """
    Create a SHA256 hash for a given input string.
    :param string:
    :return: string: The string which should be hashed.
    """
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """
    Hashes a block and return a string representations of it.
    :param block: the block that should be hashed.
    :return: The block that should be hashed.
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_str_256(json.dumps(hashable_block, sort_keys=True).encode())
