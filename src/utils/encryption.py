from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct

# Global key for demonstration - in production, this should be securely managed
ENCRYPTION_KEY = b'ThisIsA32ByteKeyForTestingOnly!!'  # 32-byte static key for testing

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypt data using AES-256 in CBC mode.
    """
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    # Prepend IV length and IV to ciphertext
    iv_len = len(cipher.iv)
    return struct.pack('>H', iv_len) + cipher.iv + ct_bytes

def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    Decrypt data using AES-256 in CBC mode.
    """
    try:
        if len(encrypted_data) < 2:
            return b""
            
        # Extract IV length and IV
        iv_len = struct.unpack('>H', encrypted_data[:2])[0]
        if len(encrypted_data) < 2 + iv_len:
            return b""
            
        iv = encrypted_data[2:2+iv_len]
        ct = encrypted_data[2+iv_len:]
        
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt
    except Exception as e:
        print(f"Decryption error: {e}")
        return b"" 