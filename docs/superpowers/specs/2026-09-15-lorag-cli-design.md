# Lorag CLI Design

## Goal

This repo is the source of an installable macOS CLI named `lorag` and the Homebrew tap that ships it (`imakumar98/homebrew-lorag`). After `brew install imakumar98/lorag/lorag`, the clone is not required at runtime. Documents live in `~/lorag/docs`. The tool can be run from any working directory.

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
| Homebrew `lorag` | Command installed by the tap. Does not depend on this clone after install. |

Repo `docs/superpowers/` is developer documentation only. It is not indexed. User documents and the vector index never live in the clone.

## Config

```toml
chat_model = "llama3.2:3b"
embed_model = "nomic-embed-text"
```

Defaults if the file is missing: `llama3.2:3b` and `nomic-embed-text`. `lorag init` writes these defaults only when `config.toml` does not exist. It does not overwrite a chat model the user already set.

The embedding model is not swapped by a command. Changing it would require a new index; that is out of scope.

## Distribution

This GitHub repo is named `homebrew-lorag` so Homebrew’s tap naming works. Other people install with:

```bash
brew install imakumar98/lorag/lorag
```

That taps `imakumar98/homebrew-lorag` and installs `Formula/lorag.rb`. The formula depends on Homebrew Python and `ollama`, installs this package into a prefix virtualenv, and does not pull models or run `lorag init`. After install, caveats tell the user to:

1. `brew services start ollama`
2. `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`
3. `lorag init`

`brew upgrade lorag` upgrades the command. Homebrew itself is not installed automatically.

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
- `Formula/lorag.rb` is the Homebrew tap formula. It installs the package and depends on `ollama`.
- `lorag.cli` owns subcommand parsing (`lorag` and `python -m lorag`).
- `lorag.paths` is the only place that resolves `~/lorag/docs`, `~/lorag/database`, and `~/.lorag/config.toml`.
- `lorag.notes` owns JXA fetch, validation, filenames, and staged directory replace. Sync passes `~/lorag/docs/apple-notes/` as the export directory.
- `lorag.rag` loads documents, splits, builds Chroma, and answers one question. Paths and model names come from config, never from the clone.
- Notes file format, skipped locked notes, and “no attachments” are unchanged from the Apple Notes sync design.

## Data flow

1. `brew install imakumar98/lorag/lorag`, then the caveat steps, then `lorag init`.
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
- `brew install` may stop halfway. Re-running `brew install imakumar98/lorag/lorag` continues the formula install. Model pulls and `lorag init` are separate.
- Note bodies and retrieved chunk text are never printed as debug output.

## Testing

- Unit tests use a fake home (temp dirs). They never touch `~/lorag`, `~/.lorag`, real Notes, or this machine’s Ollama.
- Cover: `init` creates directories and default config without overwriting an existing chat model; `sync` replaces only `apple-notes` and rebuilds the index through mocks; `q` refuses to run with no db; `model` / `model use` read and write config and do not save the name if pull fails.
- Existing Notes tests remain: payload parsing, stable filenames, staged export replace. Automation and indexing stay mocked.
- The Homebrew formula is not run in unit tests. Manual check: `brew install imakumar98/lorag/lorag`, then `lorag q "..."` from a directory that is not the clone.

## Out of scope

- Linux and Windows
- Publishing to PyPI
- A command to change the embedding model
- Copying the clone’s `docs/` into `~/lorag/docs`
- Interactive REPL as a `lorag` command
- Automatic Homebrew installation
