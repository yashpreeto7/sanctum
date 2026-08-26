# Execution Scripts

Deterministic Python scripts that handle the actual work.

## Principles
- **Reliable**: Scripts should produce the same output for the same input.
- **Testable**: Each script should be runnable independently for verification.
- **Fast**: Minimize unnecessary work; batch where possible.
- **Well-commented**: Every script should explain *why*, not just *what*.

## Conventions
- Load secrets from `.env` using `python-dotenv` or `os.environ`.
- Accept inputs via CLI arguments or stdin.
- Print structured output (JSON preferred) to stdout.
- Log progress/errors to stderr.
- Exit with non-zero codes on failure.

## File Naming
Use descriptive, snake_case filenames:
- `scrape_single_site.py`
- `upload_to_sheets.py`
- `generate_slides.py`
