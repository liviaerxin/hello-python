#!/usr/bin/env python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64

def encrypt(plaintext, key):
    print(f"encrypt")
    # Pad the plaintext to ensure it's a multiple of the block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    print(f"before padding: {len(plaintext)}, after padding: {len(padded_data)}")

    # Create an AES cipher object with the provided key and a random IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\0' * 16), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the padded data
    ciphertext = encryptor.update(padded_data)

    # Return the base64-encoded ciphertext
    return base64.b64encode(ciphertext)

def decrypt(ciphertext, key):
    print(f"decrypt")
    # Decode the base64-encoded ciphertext
    ciphertext = base64.b64decode(ciphertext)

    # Create an AES cipher object with the provided key and a random IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(b'\0' * 16), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    decrypted_data = decryptor.update(ciphertext)
    print(decrypted_data)
    print(f"padding size: {decrypted_data[-1]}")

    # Unpad the decrypted data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()
    
    print(f"before unpadding: {len(decrypted_data)}, after unpadding: {len(plaintext)}")

    return plaintext

# Example usage
key = b'this_is_a_16_key'
plaintext = b'Hello, symmetric encryption with AES-128!'

# Encrypt the plaintext
encrypted_text = encrypt(plaintext, key)
print("Encrypted:", encrypted_text)

# Decrypt the ciphertext
decrypted_text = decrypt(encrypted_text, key)
print("Decrypted:", decrypted_text.decode('utf-8'))


def test_smon_decrypt():
    key = b"Gr4S2eiNl7zq5MrU"
    with open("data.b64", "r") as fp:
        data = fp.read()
    
    cipher_data = base64.b64decode(data)
    cipher = Cipher(algorithms.AES(key), modes.CBC(b'\0' * 16), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(cipher_data)
    print(f"padding size: {decrypted_data[-1]}")
    
    # Unpad the decrypted data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    plain_data = unpadder.update(decrypted_data) + unpadder.finalize()
    
    import zlib
    import binascii
    import json
    plain_data = zlib.decompress(plain_data)
    print(plain_data.decode())
    print(json.loads(plain_data))
    print(len(plain_data))
    print(len(plain_data.decode()))
    print(len(json.dumps(json.loads(plain_data.decode()))))
    print(len(json.dumps(json.loads(plain_data)).encode()))

    with open("data.json", "w") as f:
        f.write(json.dumps(json.loads(plain_data.decode())))
test_smon_decrypt()