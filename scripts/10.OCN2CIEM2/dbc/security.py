from cryptography.fernet import Fernet
Path = 'XXXXXXXXXXX'


def decrypt(key):
    cipher_suite = Fernet(key)
    with open(f'{Path}\\tipaccess.bin', 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    plain_text_encryptedpassword = bytes(uncipher_text).decode("utf-8")
    return plain_text_encryptedpassword
