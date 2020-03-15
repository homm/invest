from getpass import getpass

from Crypto.Cipher import Salsa20
from Crypto.Hash import SHA256

try:
    from conf import enc_token_nonce, enc_token
except ImportError:
    enc_token_nonce = enc_token = None


def get_cipher(password, nonce=enc_token_nonce):
    key = SHA256.new(password.encode('utf-8')).digest()
    return Salsa20.new(key=key, nonce=nonce)


def prompt_cipher():
    password = getpass('Password: ')
    return get_cipher(password)


def decode_token(cipher, enc_token):
    token = cipher.decrypt(enc_token)
    assert token.startswith(b't.'), "Likely incorrect password"
    return token.decode('utf-8')


def is_password_weak(password, min_length=12):
    if len(password) < min_length:
        return True, "password is too short"
    if not password.isprintable():
        return True, "not all chars are printable"
    if not password.isascii():
        return True, "not ascii chars"
    if password.islower():
        return True, "all chars are lower"
    if password.isupper():
        return True, "all chars are upper"
    if password.isdigit():
        return True, "all chars are digits"
    return False, None


def prompt_new_password():
    while True:
        while True:
            password = getpass('New password: ')
            weak, reason = is_password_weak(password)
            if not weak:
                break
            print(f'Password is too weak: {reason}')

        if password == getpass('Repeat password: '):
            break
        print("Passwords don't match.")
    return password


def limit_str_repr(var, line_width=79):
    end = 0
    while end <= len(var):
        if len(repr(var[:end + 1])) > line_width:
            yield repr(var[:end])
            var = var[end:]
            end = 0
        end += 1
    if var:
        yield repr(var)


def output_conf(password, token):
    new_cipher = get_cipher(password, nonce=None)
    new_enc_token = new_cipher.encrypt(token.encode('utf-8'))

    line = "\n    "
    print(f"""
Put this code to the `conf.py` file:
# ------------- conf.py ------------
enc_token_nonce = {repr(new_cipher.nonce)}
enc_token = (
    {line.join(limit_str_repr(new_enc_token, 79 - 4))}
)
""")


def command_set_token():
    password = prompt_new_password()

    print("Now please paste the token once.")
    print("Do not store it anywhere else.")
    token = getpass('Paste token: ')

    output_conf(password, token)


def command_change_password():
    old_cipher = prompt_cipher()
    token = decode_token(old_cipher, enc_token)

    password = prompt_new_password()

    output_conf(password, token)
