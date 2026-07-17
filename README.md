# Forge

Forge is a self-hosted developer toolbox that combines a password/secrets
vault, a notes board, code/crypto utilities, and a document-to-Markdown
converter into one application you run on your own hardware.

## Features

- **Vault** — encrypted secret storage with folders, tags, favorites, and version history
- **Notes** — drag-and-resize sticky note board with Markdown support and full-text search
- **Generators** — passwords, UUIDs, NanoIDs, random bytes, API keys, JWT secrets
- **Crypto** — Base64, hashing, AES-256-GCM, JWT decode/verify/build, RSA, ECDSA
- **Converters** — JSON formatter, regex tester, URL/Unicode tools, cron parser, diff viewer, timestamp converter
- **Utilities** — QR code generator, checksum/file hashing, color picker, timezone converter
- **Ingest** — convert PDFs, Office documents, HTML, images, and audio into clean Markdown
- **Dashboard & search** — recent activity overview and a command palette (Ctrl+K) across the whole app

## Requirements

- Docker
- Docker Compose

## Installation

1. Clone the repository and enter it:
   ```bash
   git clone <repo-url> FORGE
   cd FORGE
   ```

2. Create your environment file:
   ```bash
   cp .env.example .env
   ```

3. Open `.env` and set `FORGE_MASTER_KEY` to a random value:
   ```bash
   openssl rand -base64 32
   ```

4. Build and start the app:
   ```bash
   docker compose up --build
   ```

5. Open `http://localhost:8585` in your browser and follow the setup screen to create your master password.

## Documentation

Full documentation is available in the [docs](docs) folder, including architecture, development setup, deployment, security, and API reference.

## License

MIT
