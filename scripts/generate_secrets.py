#!/usr/bin/env python3
"""
Generate secrets for FastAPI application
Creates a SECRET_KEY for the .env file using cryptographically secure random generation.
"""
import secrets


def generate_secret_key():
    """Generate a cryptographically secure SECRET_KEY for FastAPI"""
    return secrets.token_urlsafe(32)


def main():
    """Main function to generate and display the SECRET_KEY"""
    print("🔐 Generating SECRET_KEY for FastAPI application...")
    print()

    secret_key = generate_secret_key()

    print("📋 Add this line to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print()
    print("⚠️  SECURITY IMPORTANT:")
    print("   - Never commit .env files to version control")
    print("   - Add .env to your .gitignore file")
    print("   - Keep your SECRET_KEY secure and private")
    print("   - Use different SECRET_KEYs for different environments")
    print()
    print("✅ Generated 32-byte URL-safe secret key")


if __name__ == "__main__":
    main()
