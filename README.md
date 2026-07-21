# Eintracht Team Performance

A private, German-language coaching dashboard focused on simple workflows for squad status, player evaluations, training planning, match tracking, calendar overview and printable reports.

## Current source package

The reviewed Django source is stored in the `.bootstrap/` archive parts while the initial GitHub Actions publishing job is prepared. It can be expanded at any time with:

```bash
chmod +x bootstrap-source.sh
./bootstrap-source.sh
```

The script validates and extracts the complete application source into the repository root. No password, production environment file or local database is included in the archive.

After extraction, start the production stack with:

```bash
docker compose up -d --build
```

The application creates its first trainer account interactively at `/setup/`; no shared default password is shipped.
