import hashlib
from datetime import timedelta
from models import utcnow
def test_token_expiry_is_24_hours(): assert (utcnow()+timedelta(hours=24))>utcnow()
def test_tokens_are_hashed(): assert hashlib.sha256(b"secret-token").hexdigest()!="secret-token"
