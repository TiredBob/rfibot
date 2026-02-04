Both `.env` and `.envdiscord` files are used.

1.  `load_dotenv()` is called first, which loads variables from the default `.env` file.
2.  `load_dotenv('.envdiscord')` is called second, loading variables from `.envdiscord`.

By default, `python-dotenv`'s `load_dotenv` function does NOT override existing environment variables. This means if a variable (e.g., `DISCORD_TOKEN`) is present in both `.env` and `.envdiscord`, the value from the `.env` file (loaded first) will be used.

Therefore, the `.env` file takes precedence for any conflicting variables.
