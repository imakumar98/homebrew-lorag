# Sift CLI Design

## Goal

Turn this repo into a macOS CLI named `sift` that other people can clone and install. Documents live in a shared home-directory location. The tool can be run from any working directory.

This replaces `python main.py` and `python notes_cli.py sync` as the user-facing interface. Notes export still uses the existing Apple Notes automation design; only the paths and the command name change.

## Audience

macOS only. Apple Notes sync and the Homebrew bootstrap do not target Linux or Windows.

## Layout

| Path | Role |
|------|------|
| `~/sift/docs` | User document root. Drop `.txt`, `.md`, and `.pdf` files here. |
| `~/sift/docs/apple-notes/` | Managed Apple Notes export. Replaced on each successful notes export. Other files under `~/sift/docs` are left alone. |
| `~/.sift/db` | Chroma vector index. |
| `~/.sift/config.toml` | Chat model name. Created on first `sift init` if missing. |
| `~/.local/bin/sift` | Wrapper written at install time. Points at this clone’s `venv`. |

Repo `docs/` and `db/` are not used at runtime after this change. Existing files in the clone are not copied into `~/sift/docs`.

## Config

```toml
chat_model = "llama3.2:3b"
embed_model = "nomic-embed-text"
```

Defaults if the file is missing: `llama3.2:3b` and `nomic-embed-text`. `sift init` writes these defaults only when `config.toml` does not exist. It does not overwrite a chat model the user already set.

The embedding model is not swapped by a command. Changing it would require a new index; that is out of scope.

## Distribution

Other people clone this repo and run `./install-helper` once from the clone. That script is idempotent.

1. If not macOS, exit with a short error.
2. If Homebrew is missing, print the official Homebrew install command and exit. Do not install Homebrew automatically.
3. `brew install python ollama` when those formulae are missing.
4. If the Ollama daemon is not responding, start it with `brew services start ollama` and wait until `ollama list` succeeds.
5. `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`.
6. Create `venv` in the clone if needed and `pip install -r requirements.txt`.
7. Write `~/.local/bin/sift` so it `exec`s `<clone>/venv/bin/python -m sift "$@"`. Create `~/.local/bin` if needed.
8. If `~/.local/bin` is not on `PATH`, print how to add it.
9. Run `sift init`.

If the clone is moved, the user re-runs `./install-helper`. The wrapper always records the clone path from the install that wrote it.

`sift` itself does not install Python, Ollama, or Homebrew. Those belong to `./install-helper`.

## Commands

| Command | Behavior |
|---------|----------|
| `sift init` | Create `~/sift/docs` and `~/.sift/`. Write default `config.toml` if missing. Then run the same work as `sift sync`. |
| `sift sync` | Export unlocked, text-readable Apple Notes into `~/sift/docs/apple-notes/` using the existing staged-replace export. Leave other files under `~/sift/docs` in place. Delete `~/.sift/db` and rebuild it from all supported files under `~/sift/docs`. |
| `sift question ...` | One-shot RAG answer against `~/.sift/db`. Everything after `question` is the query (quotes optional). Empty query is an error. Print the answer and unique source paths. Exit. Do not start a REPL. Do not build the index if it is missing. |
| `sift model` | Print the current chat model from config (or the default). |
| `sift model use <name>` | `ollama pull <name>`. On success, write `chat_model` in `config.toml`. On pull failure, leave config unchanged. Do not rebuild the index. |

## Architecture

- `requirements.txt` at the repo root lists Python dependencies. `./install-helper` installs from that file.
- `install-helper` (bash at repo root) owns machine bootstrap and the PATH wrapper.
- `python -m sift` owns subcommand parsing.
- A paths/config module is the only place that resolves `~/sift/docs`, `~/.sift/db`, and `~/.sift/config.toml`.
- Existing Notes export in `notes_cli.py` stays responsible for JXA fetch, validation, filenames, and staged directory replace. Sync passes `~/sift/docs/apple-notes/` as the export directory.
- Existing RAG code in `main.py` (load documents, split, Chroma, agent) takes `docs_dir` and `db_dir` instead of `./docs` and `./db`. Chat and embed model names come from config. `sift question` calls this path once and exits.
- Notes file format, skipped locked notes, and “no attachments” are unchanged from the Apple Notes sync design.

## Data flow

1. `./install-helper` → `sift init`.
2. `sift init` → directories + default config → `sift sync`.
3. `sift sync` → Notes export → rebuild `~/.sift/db`.
4. `sift question` reads `~/.sift/db` and the configured chat model.
5. Adding files later: drop them in `~/sift/docs`, then `sift sync`.
6. `sift model use` updates config and pulls the chat model only.

## Error handling

- Not macOS, `osascript` missing, or Notes automation denied: `sift sync` / `sift init` fail with a short message. Existing `~/sift/docs` files and `~/.sift/db` stay as they were.
- Notes export fails before replace: previous `apple-notes` folder and the index stay as they were.
- Index rebuild fails after a successful Notes export: exported notes remain. Rerun `sift sync` to retry the rebuild.
- `sift question` with no `~/.sift/db`: tell the user to run `sift init` or `sift sync`. Do not index implicitly.
- Ollama not running, or the configured chat model missing during `question`: fail with a short message (`start Ollama` / `sift model use <name>`). Do not install or pull during `question`.
- `sift model use` pull failure: config is not updated.
- `./install-helper` may stop halfway. Rerunning it continues from whatever is still missing.
- Note bodies and retrieved chunk text are never printed as debug output.

## Testing

- Unit tests use a fake home (temp dirs). They never touch `~/sift`, `~/.sift`, real Notes, or this machine’s Ollama.
- Cover: `init` creates directories and default config without overwriting an existing chat model; `sync` replaces only `apple-notes` and rebuilds the index through mocks; `question` refuses to run with no db; `model` / `model use` read and write config and do not save the name if pull fails.
- Existing Notes tests remain: payload parsing, stable filenames, staged export replace. Automation and indexing stay mocked.
- `./install-helper` is not run in unit tests. Manual check: clone, run the script, then `sift question "..."` from a directory that is not the clone.

## Out of scope

- Linux and Windows
- Publishing to PyPI / pipx
- A command to change the embedding model
- Copying the clone’s `docs/` into `~/sift/docs`
- Interactive REPL as a `sift` command
- Automatic Homebrew installation
