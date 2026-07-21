# Eintracht Team Performance

A private, German-language coaching dashboard focused on simple workflows for squad status, player evaluations, training planning, match tracking, calendar overview and printable reports.

## Current source package

The reviewed, privacy-safe Django source is stored in the `.source-v2/` archive parts until the initial publishing workflow expands it. It can also be expanded manually with:

```bash
chmod +x bootstrap-source.sh
./bootstrap-source.sh
```

The extraction script validates the archive against its fixed SHA-256 checksum before writing any source files. The package contains only fictional demo players and a fictional opponent; no password, production environment file or local database is included.

After extraction, start the production stack with:

```bash
docker compose up -d --build
```

The application creates its first trainer account interactively at `/setup/`; no shared default password is shipped.

## Deployment

The `Publish and deploy application` GitHub Actions workflow validates the Django project, publishes the readable source to `main`, and deploys it to `eintracht.smarbiz.sbs` through the configured `HOST` and `PASS` repository secrets.
