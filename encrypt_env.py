# encrypt_env.py
from cryptography.fernet import Fernet

# ── Step A: Generate & save master key (run once) ──────────────────
def generate_key():
    key = Fernet.generate_key()
    with open(".secrets.key", "wb") as f:
        f.write(key)
    print("✅ Key saved to .secrets.key — DO NOT commit this file!")
    return key

# ── Step B: Load the master key ────────────────────────────────────
def load_key() -> bytes:
    with open(".secrets.key", "rb") as f:
        return f.read()

# ── Step C: Encrypt a single value ─────────────────────────────────
def encrypt_value(plain_text: str, key: bytes) -> str:
    return Fernet(key).encrypt(plain_text.encode()).decode()

# ── Step D: Encrypt all your secrets → write to .env ───────────────
def encrypt_all_secrets():
    key = load_key()

    secrets = {
        "API_KEY":            "your_actual_api_key_here",
        "SNOWFLAKE_USER":     "your_snowflake_user_id",
        "SNOWFLAKE_PASSWORD": "your_snowflake_password",
        "SNOWFLAKE_ACCOUNT":  "your_account_identifier",
    }

    with open(".env", "w") as f:
        for var_name, plain_value in secrets.items():
            encrypted = encrypt_value(plain_value, key)
            f.write(f"{var_name}={encrypted}\n")

    print("✅ Secrets encrypted and saved to .env")

if __name__ == "__main__":
    generate_key()        # Comment this out after first run
    encrypt_all_secrets()