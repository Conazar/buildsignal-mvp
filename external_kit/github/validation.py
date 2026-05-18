from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import jwt
import requests
from dotenv import load_dotenv


# =========================================================
# Exception Hierarchy
# =========================================================

class EnvironmentErrorBase(Exception):
    """Base class for all environment-related errors."""


class EnvFileNotFoundError(EnvironmentErrorBase):
    """Raised when .env file is missing."""


class DuplicateEnvironmentVariableError(EnvironmentErrorBase):
    """Raised when duplicate environment variables exist."""


class MissingEnvironmentVariableError(EnvironmentErrorBase):
    """Raised when required environment variable is missing."""


class EmptyEnvironmentVariableError(EnvironmentErrorBase):
    """Raised when environment variable is empty."""


class PrivateKeyFileError(EnvironmentErrorBase):
    """Raised when private key file is invalid."""


class GitHubAuthenticationError(EnvironmentErrorBase):
    """Raised when GitHub authentication fails."""


class GitHubRepositoryAccessError(EnvironmentErrorBase):
    """Raised when repository access validation fails."""


# =========================================================
# Config Model
# =========================================================

@dataclass(frozen=True)
class GitHubConfig:
    app_id: str
    private_key_path: str
    repository: str


# =========================================================
# Required Variables
# =========================================================

REQUIRED_ENV_VARS = [
    "GITHUB_APP_ID",
    "GITHUB_PRIVATE_KEY_PATH",
    "GITHUB_REPOSITORY",
]


# =========================================================
# Environment Validation
# =========================================================

def check_env_file_exists(env_path: Path) -> None:
    """
    Ensure .env file exists.
    """

    if not env_path.exists():
        raise EnvFileNotFoundError(
            ".env file not found."
        )


def check_duplicate_keys(env_path: Path) -> None:
    """
    Detect duplicate keys inside .env
    """

    seen = set()

    with env_path.open("r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key = line.split("=", 1)[0].strip()

            if key in seen:
                raise DuplicateEnvironmentVariableError(
                    f"Duplicate environment variable detected: {key}"
                )

            seen.add(key)


def load_and_validate_env(
    env_path: Path,
) -> GitHubConfig:
    """
    Load and validate environment variables.
    """

    load_dotenv(dotenv_path=env_path)

    env_values = {}

    for env_var in REQUIRED_ENV_VARS:

        value = os.getenv(env_var)

        if value is None:

            raise MissingEnvironmentVariableError(
                f"Missing required environment variable: "
                f"{env_var}"
            )

        if not value.strip():

            raise EmptyEnvironmentVariableError(
                f"Environment variable '{env_var}' is empty."
            )

        env_values[env_var] = value

    return GitHubConfig(
        app_id=env_values["GITHUB_APP_ID"],
        private_key_path=env_values[
            "GITHUB_PRIVATE_KEY_PATH"
        ],
        repository=env_values[
            "GITHUB_REPOSITORY"
        ],
    )


# =========================================================
# Private Key Validation
# =========================================================

def load_private_key(
    private_key_path: str,
) -> str:
    """
    Load private key from PEM file.
    """

    path = Path(private_key_path)

    if not path.exists():

        raise PrivateKeyFileError(
            f"Private key file not found: "
            f"{private_key_path}"
        )

    try:

        with path.open("r") as file:

            private_key = file.read()

    except Exception as e:

        raise PrivateKeyFileError(
            f"Failed to read private key file: {e}"
        )

    if not private_key.strip():

        raise PrivateKeyFileError(
            "Private key file is empty."
        )

    return private_key


# =========================================================
# GitHub Semantic Validation
# =========================================================

def generate_github_jwt(
    app_id: str,
    private_key: str,
) -> str:
    """
    Generate GitHub JWT token.
    """

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": app_id,
    }

    try:

        encoded_jwt = jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
        )

        return encoded_jwt

    except Exception as e:

        raise GitHubAuthenticationError(
            f"Failed to generate GitHub JWT: {e}"
        )


def validate_github_app(
    jwt_token: str,
) -> None:
    """
    Validate GitHub App authentication.
    """

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    try:

        response = requests.get(
            "https://api.github.com/app",
            headers=headers,
            timeout=10,
        )

    except requests.RequestException as e:

        raise GitHubAuthenticationError(
            f"GitHub API request failed: {e}"
        )

    if response.status_code != 200:

        raise GitHubAuthenticationError(
            "GitHub rejected APP_ID or PRIVATE_KEY."
        )


def validate_repository_access(
    repository: str,
) -> None:
    """
    Validate repository existence.
    """

    try:

        response = requests.get(
            f"https://api.github.com/repos/{repository}",
            timeout=10,
        )

    except requests.RequestException as e:

        raise GitHubRepositoryAccessError(
            f"Failed to validate repository: {e}"
        )

    if response.status_code != 200:

        raise GitHubRepositoryAccessError(
            f"Repository '{repository}' "
            f"does not exist."
        )


def validate_github_credentials(
    config: GitHubConfig,
) -> None:
    """
    Perform semantic validation against GitHub.
    """

    private_key = load_private_key(
        config.private_key_path
    )

    jwt_token = generate_github_jwt(
        app_id=config.app_id,
        private_key=private_key,
    )

    validate_github_app(jwt_token)

    validate_repository_access(
        repository=config.repository,
    )


# =========================================================
# Main Validation Pipeline
# =========================================================

def validate_environment() -> GitHubConfig:
    """
    Full environment validation pipeline.
    """

    env_path = Path(".env")

    # Step 1
    check_env_file_exists(env_path)

    # Step 2
    check_duplicate_keys(env_path)

    # Step 3
    config = load_and_validate_env(env_path)

    # Step 4
    validate_github_credentials(config)

    return config


# =========================================================
# Example Usage
# =========================================================

if __name__ == "__main__":

    try:

        config = validate_environment()

        print("✅ Environment validation successful.")

        print({
            "GITHUB_APP_ID": config.app_id,
            "GITHUB_PRIVATE_KEY_PATH":
                config.private_key_path,
            "GITHUB_REPOSITORY":
                config.repository,
        })

    except EnvironmentErrorBase as e:

        print(
            f"❌ Environment Validation Error: {e}"
        )

        raise