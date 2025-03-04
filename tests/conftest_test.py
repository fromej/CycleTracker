def test_settings_override():
    print("Starting test")  # Debug print
    from app.core.config import get_settings
    settings = get_settings()
    print(f"Got settings: database_url={settings.database_url}, secret_key={settings.secret_key}")  # Debug print
    assert settings.secret_key == "test_secret_key"
    assert settings.database_url == "sqlite:///:memory:"
