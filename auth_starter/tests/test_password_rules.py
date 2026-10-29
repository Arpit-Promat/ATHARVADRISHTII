from auth import validate_password,normalize_email
def test_password_minimum(): assert validate_password("correct horse battery")
def test_short_password(): assert not validate_password("short")
def test_no_outer_spaces(): assert not validate_password("  a long enough password  ")
def test_email_normalization(): assert normalize_email(" Test@Example.COM ")=="test@example.com"
