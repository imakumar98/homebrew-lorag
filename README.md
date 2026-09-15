# lorag

Ask questions about files on your Mac and your Apple Notes. Answers stay local: Ollama runs the models, Chroma stores the index, and nothing is sent to a cloud API.

Drop `.txt`, `.md`, and `.pdf` files into `~/lorag/docs`, sync Notes, then ask:

```text
lorag q What did I write about the Q3 plan?
```

macOS only. Install with Homebrew; you do not need a clone on PATH.

## How it works

1. `lorag sync` exports unlocked, text-readable Apple Notes into `~/lorag/docs/apple-notes/` and rebuilds a vector index from everything under `~/lorag/docs`.
2. `lorag q …` retrieves matching chunks from that index and answers with the configured Ollama chat model.
3. Files you add yourself under `~/lorag/docs` are kept; only the managed `apple-notes/` folder is replaced on each successful Notes export.

Locked notes, notes Notes cannot read, and attachments are skipped. Only the plaintext Notes exposes is indexed.

## Requirements

- macOS on Apple Silicon
- [Homebrew](https://brew.sh)
- [Ollama](https://ollama.com) (installed as a Homebrew dependency)

## Install

```bash
brew install imakumar98/lorag/lorag
brew services start ollama
ollama pull llama3.2:3b
ollama pull nomic-embed-text
lorag init
```

`lorag init` creates `~/lorag/docs`, writes default config if missing, exports Apple Notes, and builds the index.

Upgrade later with:

```bash
brew update
brew upgrade lorag
```

macOS may ask for permission the first time Notes is exported. Allow access for Notes automation, then run `lorag sync` again.

## Usage

```bash
lorag init                          # create ~/lorag/docs, default config, then sync
lorag sync                          # export Notes and rebuild the index
lorag q What is the ACATS fee?      # one-shot question (quotes optional)
lorag model                         # print the current chat model
lorag model use qwen3.5:4b          # pull a chat model and switch to it
```

`lorag q` does not build the index. If there is no database yet, run `lorag init` or `lorag sync` first.

Add your own files later:

```bash
cp notes.md ~/lorag/docs/
lorag sync
lorag q Summarize notes.md
```

## Layout

| Path | Role |
|------|------|
| `~/lorag/docs` | Your documents (`.txt`, `.md`, `.pdf`) |
| `~/lorag/docs/apple-notes/` | Exported Apple Notes (replaced on each successful sync) |
| `~/lorag/database` | Chroma vector index |
| `~/.lorag/config.toml` | Chat and embedding model names |

Default config:

```toml
chat_model = "llama3.2:3b"
embed_model = "nomic-embed-text"
```

`lorag init` writes this file only if it does not already exist. Changing the embedding model is not supported from the CLI; that would require a new index.

## Troubleshooting

| Problem | What to do |
|---------|------------|
| Not macOS | lorag does not support Linux or Windows. |
| Homebrew missing | Install from https://brew.sh, then `brew install imakumar98/lorag/lorag`. |
| `lorag: command not found` | Open a new terminal so Homebrew’s prefix is on `PATH`. |
| Ollama is not running | Start Ollama (or `brew services start ollama`) and try again. |
| Chat model missing | `lorag model use llama3.2:3b` (or another pulled model). |
| Notes sync denied | Grant Notes automation permission in System Settings, then `lorag sync`. |
| No index found | Run `lorag init` or `lorag sync` before `lorag q`. |

If Notes export fails, existing files under `~/lorag/docs` and the current index are left as they were. If export succeeds but the index rebuild fails, the exported notes stay; re-run `lorag sync` to retry.

## Uninstall

```bash
brew uninstall lorag
rm -rf ~/lorag ~/.lorag
```
