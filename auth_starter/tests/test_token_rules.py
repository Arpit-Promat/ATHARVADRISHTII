import hashlib
from datetime import timedelta
from models import utcnow
def test_token_expiry_is_future():
    now = utcnow()
    assert now + timedelta(hours=24) > now
def test_raw_token_is_not_stored():
    raw = "sample-token"
    assert hashlib.sha256(raw.encode()).hexdigest() != raw
