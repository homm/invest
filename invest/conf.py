CONF_PROLOGUE = (
    "Put this code to the `conf.py` file:\n"
    "# ------------- conf.py ------------"
)

try:
    from conf import enc_token_nonce, enc_token
except ImportError:
    enc_token_nonce = enc_token = None
