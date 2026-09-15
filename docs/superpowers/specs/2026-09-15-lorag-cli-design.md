# Lorag CLI Design

## Goal

This repo is the source of an installable macOS CLI named `lorag`. After `pipx install`, the clone is not required at runtime. Documents live in `~/lorag/docs`. The tool can be run from any working directory.

This replaces `python main.py` and `python notes_cli.py sync` as the user-facing interface. Notes export still uses the existing Apple Notes automation design; only the paths and the command name change.

## Audience

macOS only. Apple Notes sync and the Homebrew bootstrap do not target Linux or Windows.

## Layout

| Path | Role |
|------|------|
| `~/lorag/docs` | User document root. Drop `.txt`, `.md`, and `.pdf` files here. |
| `~/lorag/docs/apple-notes/` | Managed Apple Notes export. Replaced on each successful notes export. Other files under `~/lorag/docs` are left alone. |
| `~/lorag/database` | Chroma vector index. |
| `~/.lorag/config.toml` | Chat model name. Created on first `lorag init` if missing. |
| `~/.local/bin/lorag` | Command installed by pipx. Does not depend on this clone after install. |

Repo `docs/superpowers/` is developer documentation only. It is not indexed. User documents and the vector index never live in the clone.

## Config

```toml
chat_model = "llama3.2:3b"
embed_model = "nomic-embed-text"
```

Defaults if the file is missing: `llama3.2:3b` and `nomic-embed-text`. `lorag init` writes these defaults only when `config.toml` does not exist. It does not overwrite a chat model the user already set.

The embedding model is not swapped by a command. Changing it would require a new index; that is out of scope.

## Distribution

Other people clone this repo once and run `./install-lorag`. That script is idempotent. After it finishes, `lorag` is a pipx-installed command; the clone can be deleted.

1. If not macOS, exit with a short error.
2. If Homebrew is missing, print the official Homebrew install command and exit. Do not install Homebrew automatically.
3. `brew install python ollama pipx` when those formulae are missing.
4. If the Ollama daemon is not responding, start it with `brew services start ollama` and wait until `ollama list` succeeds.
5. `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`.
6. `pipx install <clone> --force`, which copies the package into pipx’s environment and puts `lorag` on `~/.local/bin`.
7. If `~/.local/bin` is not on `PATH`, print how to add it.
8. Run `lorag init`.

Re-running `./install-lorag` from a clone upgrades the installed command. `lorag` itself does not install Python, Ollama, Homebrew, or pipx.

## Commands

| Command | Behavior |
|---------|----------|
| `lorag init` | Create `~/lorag/docs` and `~/.lorag/`. Write default `config.toml` if missing. Then run the same work as `lorag sync`. |
| `lorag sync` | Export unlocked, text-readable Apple Notes into `~/lorag/docs/apple-notes/` using the existing staged-replace export. Leave other files under `~/lorag/docs` in place. Delete `~/lorag/database` and rebuild it from all supported files under `~/lorag/docs`. |
| `lorag q ...` | One-shot RAG answer against `~/lorag/database`. Everything after `q` is the query (quotes optional). Empty query is an error. Print the answer and unique source paths. Exit. Do not start a REPL. Do not build the index if it is missing. |
| `lorag model` | Print the current chat model from config (or the default). |
| `lorag model use <name>` | `ollama pull <name>`. On success, write `chat_model` in `config.toml`. On pull failure, leave config unchanged. Do not rebuild the index. |

## Architecture

- `pyproject.toml` declares the `lorag` package, dependencies, and the `lorag` console script.
- `./install-lorag` installs Homebrew Python, Ollama, pipx, pulls models, then `pipx install`s this package.
- `lorag.cli` owns subcommand parsing (`lorag` and `python -m lorag`).
- `lorag.paths` is the only place that resolves `~/lorag/docs`, `~/lorag/database`, and `~/.lorag/config.toml`.
- `lorag.notes` owns JXA fetch, validation, filenames, and staged directory replace. Sync passes `~/lorag/docs/apple-notes/` as the export directory.
- `lorag.rag` loads documents, splits, builds Chroma, and answers one question. Paths and model names come from config, never from the clone.
- Notes file format, skipped locked notes, and “no attachments” are unchanged from the Apple Notes sync design.

## Data flow

1. `./install-lorag` → `lorag init`.
2. `lorag init` → directories + default config → `lorag sync`.
3. `lorag sync` → Notes export → rebuild `~/lorag/database`.
4. `lorag q` reads `~/lorag/database` and the configured chat model.
5. Adding files later: drop them in `~/lorag/docs`, then `lorag sync`.
6. `lorag model use` updates config and pulls the chat model only.

## Error handling

- Not macOS, `osascript` missing, or Notes automation denied: `lorag sync` / `lorag init` fail with a short message. Existing `~/lorag/docs` files and `~/lorag/database` stay as they were.
- Notes export fails before replace: previous `apple-notes` folder and the index stay as they were.
- Index rebuild fails after a successful Notes export: exported notes remain. Rerun `lorag sync` to retry the rebuild.
- `lorag q` with no `~/lorag/database`: tell the user to run `lorag init` or `lorag sync`. Do not index implicitly.
- Ollama not running, or the configured chat model missing during `q`: fail with a short message (`start Ollama` / `lorag model use <name>`). Do not install or pull during `q`.
- `lorag model use` pull failure: config is not updated.
- `./install-lorag` may stop halfway. Rerunning it continues from whatever is still missing.
- Note bodies and retrieved chunk text are never printed as debug output.

## Testing

- Unit tests use a fake home (temp dirs). They never touch `~/lorag`, `~/.lorag`, real Notes, or this machine’s Ollama.
- Cover: `init` creates directories and default config without overwriting an existing chat model; `sync` replaces only `apple-notes` and rebuilds the index through mocks; `q` refuses to run with no db; `model` / `model use` read and write config and do not save the name if pull fails.
- Existing Notes tests remain: payload parsing, stable filenames, staged export replace. Automation and indexing stay mocked.
- `./install-lorag` is not run in unit tests. Manual check: clone, run the script, then `lorag q "..."` from a directory that is not the clone.

## Out of scope

- Linux and Windows
- Publishing to PyPI
- A command to change the embedding model
- Copying the clone’s `docs/` into `~/lorag/docs`
- Interactive REPL as a `lorag` command
- Automatic Homebrew installation
