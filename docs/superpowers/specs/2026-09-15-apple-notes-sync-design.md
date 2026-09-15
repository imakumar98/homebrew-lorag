# Apple Notes Sync CLI Design

## Goal

Add a macOS-only command, `python notes_cli.py sync`, that exports all accessible Apple Notes into the RAG document directory and rebuilds the Chroma index.

## Architecture

- `notes_cli.py` owns argument parsing and sync orchestration.
- Apple Notes is accessed through `osascript`, using the supported Notes automation interface instead of its private SQLite database.
- Exported notes are managed under `docs/apple-notes/`.
- Each note is stored as UTF-8 text with its title and body. A stable digest of the Apple Note ID is used as the filename.
- Export output is assembled in a temporary directory and replaces the managed export directory only after a complete successful export.
- After export succeeds, the existing `db/` directory is removed and `main.get_vectorstore()` rebuilds it from all files under `docs/`.

## Behavior

- `python notes_cli.py sync` exports every unlocked, text-readable note and rebuilds the index automatically.
- Existing files elsewhere under `docs/` are preserved.
- Notes deleted from Apple Notes disappear from the managed export directory on the next successful sync.
- Locked or inaccessible notes are skipped by Notes automation.
- Attachments are not extracted; text exposed by Notes is indexed.

## Error Handling

- The command fails clearly when run outside macOS, when `osascript` is unavailable, or when Notes automation permission is denied.
- Existing exports and the vector database remain untouched if note retrieval or export preparation fails.
- If index rebuilding fails after export, the exported notes remain available and rerunning the command retries the rebuild.
- Note content is never printed to the terminal.

## Testing

- Unit tests cover note parsing, deterministic filenames, export replacement, and sync orchestration.
- Tests mock the automation subprocess and index rebuild, so they never request Notes permission or access real note content.
