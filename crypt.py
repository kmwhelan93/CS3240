__author__ = 'justin'
#from http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
from Crypto.Cipher import AES
from Crypto import Random
import hashlib

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

class AESCipher:
    def __init__( self, password ):
        """
        Requires hex encoded param as a key
        """
        m = hashlib.md5()
        m.update(password)
        self.key = m.hexdigest()


    def encrypt( self, raw ):
        """
        Returns hex encoded encrypted value!
        """
        raw = pad(raw)
        iv = Random.new().read(AES.block_size);
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return ( iv + cipher.encrypt( raw ) ).encode("hex")

    def decrypt( self, enc ):
        """
        Requires hex encoded param to decrypt
        """
        enc = enc.decode("hex")
        iv = enc[:16]
        enc= enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc))

if __name__== "__main__":
    password = "password"
    text = "hello my name is venkat";
    encrypt_decrypt = AESCipher(password)
    encrypted_text = encrypt_decrypt.encrypt(text)
    decrypted_text = encrypt_decrypt.decrypt(encrypted_text)
    print "%s" % decrypted_text