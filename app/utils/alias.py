import re

MIN_ALIAS_LENGTH = 3
MAX_ALIAS_LENGTH = 30

ALIAS_PATTERN = rf"^[a-zA-Z0-9_-]{{{MIN_ALIAS_LENGTH},{MAX_ALIAS_LENGTH}}}$"

RESERVED_ALIASES = {
    "admin",
    "Login",
    "login",
    "signup",
    "api",
    "docs",
    "swagger",
    "redoc",
    "favicon.ico",
    "robots.txt",
    "sitemap.xml"
}

def validate_alias(alias: str) -> str:
    normalised_alias = alias.strip().lower()
    if normalised_alias in RESERVED_ALIASES:
        raise ValueError(f"The alias '{normalised_alias}' is reserved and cannot be used.")
    
    if not re.match(ALIAS_PATTERN, normalised_alias):
        raise ValueError("Alias may only contain letters, numbers, hyphens and underscores.")           
    
    return normalised_alias