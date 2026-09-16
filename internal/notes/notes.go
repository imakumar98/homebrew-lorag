package notes

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

const ExportJXA = `
const Notes = Application("Notes");
const exported = [];
let skipped = 0;

for (const note of Notes.notes()) {
    try {
        exported.push({
            id: String(note.id()),
            title: String(note.name() || ""),
            body: String(note.plaintext() || "")
        });
    } catch (error) {
        skipped += 1;
    }
}

JSON.stringify({notes: exported, skipped});
`

type AppleNote struct {
	ID    string
	Title string
	Body  string
}

type ExportError struct {
	Msg string
}

func (e *ExportError) Error() string {
	return e.Msg
}

type FetchFunc func() ([]AppleNote, int, error)
type RebuildFunc func(docsDir, dbDir string) error
type runFunc func(name string, args []string) (stdout, stderr string, err error)

var (
	writeFile   = os.WriteFile
	renamePath  = os.Rename
	writeExport = WriteExport
)

func NoteFilename(noteID string) string {
	sum := sha256.Sum256([]byte(noteID))
	return hex.EncodeToString(sum[:])[:20] + ".txt"
}

func ParseExportPayload(payload string) ([]AppleNote, int, error) {
	invalid := &ExportError{Msg: "Notes returned invalid export data."}

	var root map[string]json.RawMessage
	if err := json.Unmarshal([]byte(payload), &root); err != nil {
		return nil, 0, invalid
	}

	rawNotes, ok := root["notes"]
	if !ok {
		return nil, 0, invalid
	}
	rawSkipped, ok := root["skipped"]
	if !ok {
		return nil, 0, invalid
	}

	skipped, err := parseSkipped(rawSkipped)
	if err != nil {
		return nil, 0, invalid
	}

	var items []json.RawMessage
	if err := json.Unmarshal(rawNotes, &items); err != nil {
		return nil, 0, invalid
	}

	notes := make([]AppleNote, 0, len(items))
	seen := make(map[string]struct{})
	for _, item := range items {
		var fields map[string]json.RawMessage
		if err := json.Unmarshal(item, &fields); err != nil {
			return nil, 0, invalid
		}
		if len(fields) != 3 {
			return nil, 0, invalid
		}
		id, err := parseJSONString(fields["id"])
		if err != nil {
			return nil, 0, invalid
		}
		title, err := parseJSONString(fields["title"])
		if err != nil {
			return nil, 0, invalid
		}
		body, err := parseJSONString(fields["body"])
		if err != nil {
			return nil, 0, invalid
		}
		if id == "" {
			return nil, 0, invalid
		}
		if _, dup := seen[id]; dup {
			return nil, 0, invalid
		}
		seen[id] = struct{}{}
		notes = append(notes, AppleNote{ID: id, Title: title, Body: body})
	}
	return notes, skipped, nil
}

func parseJSONString(raw json.RawMessage) (string, error) {
	if len(raw) == 0 || strings.TrimSpace(string(raw)) == "null" {
		return "", errors.New("missing")
	}
	var value string
	if err := json.Unmarshal(raw, &value); err != nil {
		return "", err
	}
	return value, nil
}

func parseSkipped(raw json.RawMessage) (int, error) {
	trimmed := strings.TrimSpace(string(raw))
	if trimmed == "true" || trimmed == "false" {
		return 0, errors.New("bool")
	}
	var skipped int
	if err := json.Unmarshal(raw, &skipped); err != nil {
		return 0, err
	}
	if skipped < 0 {
		return 0, errors.New("negative")
	}
	return skipped, nil
}

func FetchNotes(platform string, run runFunc) ([]AppleNote, int, error) {
	if platform != "darwin" {
		return nil, 0, &ExportError{Msg: "Apple Notes sync is macOS-only."}
	}

	stdout, stderr, err := run("osascript", []string{"-l", "JavaScript", "-e", strings.TrimSpace(ExportJXA)})
	if err != nil {
		if errors.Is(err, exec.ErrNotFound) {
			return nil, 0, &ExportError{Msg: "Apple Notes sync failed because osascript is unavailable."}
		}
		lower := strings.ToLower(stderr)
		for _, signal := range []string{"-1743", "not authorized", "not permitted"} {
			if strings.Contains(lower, signal) {
				return nil, 0, &ExportError{Msg: "Apple Notes sync needs macOS Automation permission. Allow access under System Settings > Privacy & Security > Automation."}
			}
		}
		return nil, 0, &ExportError{Msg: "Apple Notes automation failed."}
	}
	return ParseExportPayload(stdout)
}

func WriteExport(notes []AppleNote, exportDir string) error {
	parent := filepath.Dir(exportDir)
	if err := os.MkdirAll(parent, 0o755); err != nil {
		return err
	}
	staging, err := os.MkdirTemp(parent, ".apple-notes-")
	if err != nil {
		return err
	}

	backup := ""
	cleanupStaging := true
	defer func() {
		if cleanupStaging {
			os.RemoveAll(staging)
		}
	}()

	for _, note := range notes {
		content := "Title: " + strings.TrimSpace(note.Title) + "\n\n" + strings.TrimSpace(note.Body) + "\n"
		if err := writeFile(filepath.Join(staging, NoteFilename(note.ID)), []byte(content), 0o644); err != nil {
			return err
		}
	}

	if exists(exportDir) {
		backup, err = unusedHiddenPath(parent, ".apple-notes-backup-")
		if err != nil {
			return err
		}
		if err := renamePath(exportDir, backup); err != nil {
			return err
		}
	}

	if err := renamePath(staging, exportDir); err != nil {
		if backup != "" {
			_ = renamePath(backup, exportDir)
		}
		return err
	}
	cleanupStaging = false
	if backup != "" {
		os.RemoveAll(backup)
	}
	return nil
}

func Sync(exportDir, dbDir string, fetch FetchFunc, rebuild RebuildFunc) (int, int, error) {
	notes, skipped, err := fetch()
	if err != nil {
		return 0, 0, err
	}

	if err := writeExport(notes, exportDir); err != nil {
		var exportErr *ExportError
		if errors.As(err, &exportErr) {
			return 0, 0, err
		}
		return 0, 0, &ExportError{Msg: "Apple Notes export failed."}
	}

	if err := refreshIndex(filepath.Dir(exportDir), dbDir, rebuild); err != nil {
		return 0, 0, &ExportError{Msg: "Notes were exported, but the index rebuild failed."}
	}
	return len(notes), skipped, nil
}

func refreshIndex(docsDir, dbDir string, rebuild RebuildFunc) error {
	staging, err := unusedHiddenPath(filepath.Dir(dbDir), "."+filepath.Base(dbDir)+"-staging-")
	if err != nil {
		return err
	}

	backup := ""
	defer func() {
		os.RemoveAll(staging)
		if backup != "" && exists(backup) && !exists(dbDir) {
			_ = renamePath(backup, dbDir)
		}
		if backup != "" {
			removePath(backup)
		}
	}()

	if err := rebuild(docsDir, staging); err != nil {
		return err
	}
	if !exists(staging) {
		return errors.New("Index rebuild did not create a database.")
	}

	if exists(dbDir) {
		backup, err = unusedHiddenPath(filepath.Dir(dbDir), "."+filepath.Base(dbDir)+"-backup-")
		if err != nil {
			return err
		}
		if err := renamePath(dbDir, backup); err != nil {
			return err
		}
	}

	if err := renamePath(staging, dbDir); err != nil {
		if backup != "" {
			_ = renamePath(backup, dbDir)
		}
		return err
	}
	if backup != "" {
		removePath(backup)
		backup = ""
	}
	staging = ""
	return nil
}

func unusedHiddenPath(parent, prefix string) (string, error) {
	if err := os.MkdirAll(parent, 0o755); err != nil {
		return "", err
	}
	path, err := os.MkdirTemp(parent, prefix)
	if err != nil {
		return "", err
	}
	if err := os.Remove(path); err != nil {
		return "", err
	}
	return path, nil
}

func exists(path string) bool {
	_, err := os.Lstat(path)
	return err == nil
}

func removePath(path string) {
	info, err := os.Lstat(path)
	if err != nil {
		return
	}
	if info.IsDir() && info.Mode()&os.ModeSymlink == 0 {
		os.RemoveAll(path)
		return
	}
	os.Remove(path)
}
