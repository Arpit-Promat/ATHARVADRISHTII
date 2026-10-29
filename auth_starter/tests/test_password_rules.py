from auth import validate_password, normalize_email
def test_password_minimum_length():
    assert validate_password("correct horse battery")
    assert not validate_password("short")
def test_password_no_outer_spaces():
    assert not validate_password("  a long enough password  ")
def test_email_normalization():
    assert normalize_email(" Test@Example.COM ") == "test@example.com"
