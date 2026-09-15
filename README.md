# lorag

Ask questions about files on your Mac and your Apple Notes. Answers stay local: Ollama runs the models, Chroma stores the index, and nothing is sent to a cloud API.

Drop `.txt`, `.md`, and `.pdf` files into `~/lorag/docs`, then:

```text
lorag q What did I write about the Q3 plan?
```

macOS only.

## Install

```bash
brew install imakumar98/lorag/lorag
brew services start ollama
ollama pull llama3.2:3b
ollama pull nomic-embed-text
lorag sync
```

`lorag sync` creates `~/lorag/docs`, exports Apple Notes, and builds the index. macOS may ask for Notes permission; allow it, then run `lorag sync` again.

```bash
brew upgrade lorag
```

## Usage

```bash
lorag sync                          # export Notes and rebuild the index
lorag q What is the ACATS fee?      # one-shot question (quotes optional)
```

Add your own files later:

```bash
cp notes.md ~/lorag/docs/
lorag sync
lorag q Summarize notes.md
```

`lorag q` needs an index. Run `lorag sync` first.

## Where files live

| Path | Role |
|------|------|
| `~/lorag/docs` | Your documents (`.txt`, `.md`, `.pdf`) |
| `~/lorag/docs/apple-notes/` | Exported Apple Notes |
| `~/lorag/database` | Vector index |

Your own files under `~/lorag/docs` are kept. The `apple-notes/` folder is replaced on each successful Notes export. Locked notes and attachments are skipped.

## Uninstall

```bash
brew uninstall lorag
rm -rf ~/lorag ~/.lorag
```
