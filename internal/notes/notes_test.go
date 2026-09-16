package notes

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestFetchNotesRunsJXAAndReturnsExport(t *testing.T) {
	payload, _ := json.Marshal(map[string]any{
		"notes": []map[string]string{
			{"id": "note/1", "title": "Ideas", "body": "Build it"},
		},
		"skipped": 3,
	})
	var gotArgs []string
	run := func(name string, args []string) (string, string, error) {
		gotArgs = append([]string{name}, args...)
		return string(payload), "", nil
	}

	notes, skipped, err := FetchNotes("darwin", run)
	if err != nil {
		t.Fatal(err)
	}
	if len(notes) != 1 || notes[0] != (AppleNote{ID: "note/1", Title: "Ideas", Body: "Build it"}) {
		t.Fatalf("notes = %#v", notes)
	}
	if skipped != 3 {
		t.Fatalf("skipped = %d", skipped)
	}
	if len(gotArgs) != 5 || gotArgs[0] != "osascript" || gotArgs[1] != "-l" || gotArgs[2] != "JavaScript" || gotArgs[3] != "-e" {
		t.Fatalf("args = %#v", gotArgs)
	}
	script := gotArgs[4]
	if !strings.Contains(script, "Notes.notes()") {
		t.Fatal("missing Notes.notes()")
	}
	if strings.Contains(script, "passwordProtected") {
		t.Fatal("should not mention passwordProtected")
	}
	for _, want := range []string{
		"String(note.id())",
		`String(note.name() || "")`,
		`String(note.plaintext() || "")`,
		"catch (error)",
		"skipped += 1",
		"JSON.stringify({notes: exported, skipped})",
	} {
		if !strings.Contains(script, want) {
			t.Fatalf("script missing %q", want)
		}
	}
}

func TestFetchNotesRejectsNonMacOSWithoutSubprocess(t *testing.T) {
	run := func(string, []string) (string, string, error) {
		t.Fatal("run should not be called")
		return "", "", nil
	}
	_, _, err := FetchNotes("linux", run)
	if err == nil || !strings.Contains(err.Error(), "macOS-only") {
		t.Fatalf("error = %v", err)
	}
}

func TestFetchNotesReportsMissingOsascript(t *testing.T) {
	run := func(string, []string) (string, string, error) {
		return "", "", exec.ErrNotFound
	}
	_, _, err := FetchNotes("darwin", run)
	if err == nil || !strings.Contains(err.Error(), "osascript is unavailable") {
		t.Fatalf("error = %v", err)
	}
}

func TestFetchNotesReportsAutomationPermissionFailure(t *testing.T) {
	stderrs := []string{
		"execution error: Not authorized to send Apple events. (-1743)",
		"Notes is not authorized for automation",
		"Operation not permitted: private note content",
	}
	for _, stderr := range stderrs {
		t.Run(stderr, func(t *testing.T) {
			run := func(string, []string) (string, string, error) {
				return "", stderr, errors.New("exit 1")
			}
			_, _, err := FetchNotes("darwin", run)
			if err == nil {
				t.Fatal("expected error")
			}
			msg := err.Error()
			if !strings.Contains(msg, "System Settings > Privacy & Security > Automation") {
				t.Fatalf("message = %q", msg)
			}
			if strings.Contains(msg, stderr) {
				t.Fatalf("leaked stderr: %q", msg)
			}
		})
	}
}

func TestFetchNotesReportsSafeGenericAutomationFailure(t *testing.T) {
	stderr := "Notes failed while reading private note content"
	run := func(string, []string) (string, string, error) {
		return "", stderr, errors.New("exit 1")
	}
	_, _, err := FetchNotes("darwin", run)
	if err == nil {
		t.Fatal("expected error")
	}
	if err.Error() != "Apple Notes automation failed." {
		t.Fatalf("error = %q", err.Error())
	}
	if strings.Contains(err.Error(), stderr) || strings.Contains(err.Error(), "System Settings") {
		t.Fatalf("unsafe error: %q", err.Error())
	}
}

func TestFetchNotesRejectsInvalidStdout(t *testing.T) {
	run := func(string, []string) (string, string, error) {
		return "not json", "", nil
	}
	_, _, err := FetchNotes("darwin", run)
	if err == nil || err.Error() != "Notes returned invalid export data." {
		t.Fatalf("error = %v", err)
	}
}

func TestParseExportPayloadReturnsNotesAndSkippedCount(t *testing.T) {
	payload, _ := json.Marshal(map[string]any{
		"notes": []map[string]string{
			{"id": "note/1", "title": "Ideas", "body": "Build it"},
			{"id": "note/2", "title": "", "body": ""},
		},
		"skipped": 2,
	})
	notes, skipped, err := ParseExportPayload(string(payload))
	if err != nil {
		t.Fatal(err)
	}
	want := []AppleNote{
		{ID: "note/1", Title: "Ideas", Body: "Build it"},
		{ID: "note/2"},
	}
	if fmt.Sprintf("%v", notes) != fmt.Sprintf("%v", want) || skipped != 2 {
		t.Fatalf("got %#v skipped=%d", notes, skipped)
	}
}

func TestParseExportPayloadRejectsInvalidOutput(t *testing.T) {
	invalid := []string{
		"{not json",
		"[]",
		"{}",
		`{"notes": "invalid", "skipped": 0}`,
		`{"notes": [], "skipped": "0"}`,
		`{"notes": [], "skipped": true}`,
		`{"notes": [{}], "skipped": 0}`,
		`{"notes": [{"id": 1, "title": "Title", "body": "Body"}], "skipped": 0}`,
		`{"notes": [{"id": "1", "title": null, "body": "Body"}], "skipped": 0}`,
		`{"notes": [{"id": "1", "title": "Title", "body": false}], "skipped": 0}`,
	}
	for _, payload := range invalid {
		t.Run(payload, func(t *testing.T) {
			_, _, err := ParseExportPayload(payload)
			if err == nil || err.Error() != "Notes returned invalid export data." {
				t.Fatalf("payload %s: error = %v", payload, err)
			}
		})
	}
}

func TestParseExportPayloadRejectsExtraNoteFields(t *testing.T) {
	payload := `{"notes":[{"id":"1","title":"Title","body":"Body","account":"Private"}],"skipped":0}`
	_, _, err := ParseExportPayload(payload)
	if err == nil || err.Error() != "Notes returned invalid export data." {
		t.Fatalf("error = %v", err)
	}
}

func TestParseExportPayloadRejectsNegativeSkippedCount(t *testing.T) {
	_, _, err := ParseExportPayload(`{"notes":[],"skipped":-1}`)
	if err == nil {
		t.Fatal("expected error")
	}
}

func TestParseExportPayloadRejectsEmptyAndDuplicateNoteIDs(t *testing.T) {
	payloads := []string{
		`{"notes":[{"id":"","title":"Title","body":"Body"}],"skipped":0}`,
		`{"notes":[{"id":"duplicate","title":"First","body":"Body"},{"id":"duplicate","title":"Second","body":"Body"}],"skipped":0}`,
	}
	for _, payload := range payloads {
		_, _, err := ParseExportPayload(payload)
		if err == nil {
			t.Fatalf("accepted %s", payload)
		}
	}
}

func TestNoteFilenameIsStableAndHidesNoteID(t *testing.T) {
	noteID := "x-coredata://private-id"
	filename := NoteFilename(noteID)
	sum := sha256.Sum256([]byte(noteID))
	want := hex.EncodeToString(sum[:])[:20] + ".txt"
	if filename != want || filename != NoteFilename(noteID) {
		t.Fatalf("filename = %q want %q", filename, want)
	}
	if strings.Contains(filename, "private-id") {
		t.Fatal("filename leaked note id")
	}
}

func TestWriteExportReplacesStaleFilesAndPreservesSiblingDocs(t *testing.T) {
	root := t.TempDir()
	exportDir := filepath.Join(root, "docs", "apple-notes")
	if err := os.MkdirAll(exportDir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(exportDir, "stale.txt"), []byte("stale"), 0o644); err != nil {
		t.Fatal(err)
	}
	sibling := filepath.Join(root, "docs", "keep.txt")
	if err := os.WriteFile(sibling, []byte("keep"), 0o644); err != nil {
		t.Fatal(err)
	}

	if err := WriteExport([]AppleNote{{ID: "1", Title: "  Ideas  ", Body: "  Build it  "}}, exportDir); err != nil {
		t.Fatal(err)
	}

	entries, err := filepath.Glob(filepath.Join(exportDir, "*.txt"))
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 1 {
		t.Fatalf("entries = %v", entries)
	}
	if _, err := os.Stat(filepath.Join(exportDir, "stale.txt")); !os.IsNotExist(err) {
		t.Fatal("stale file still present")
	}
	got, _ := os.ReadFile(sibling)
	if string(got) != "keep" {
		t.Fatalf("sibling = %q", got)
	}
	content, _ := os.ReadFile(entries[0])
	if string(content) != "Title: Ideas\n\nBuild it\n" {
		t.Fatalf("content = %q", content)
	}
}

func TestWriteExportPreservesOldExportWhenStagingWriteFails(t *testing.T) {
	root := t.TempDir()
	exportDir := filepath.Join(root, "docs", "apple-notes")
	if err := os.MkdirAll(exportDir, 0o755); err != nil {
		t.Fatal(err)
	}
	old := filepath.Join(exportDir, "old.txt")
	if err := os.WriteFile(old, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}

	orig := writeFile
	writeFile = func(string, []byte, os.FileMode) error {
		return errors.New("disk full")
	}
	defer func() { writeFile = orig }()

	err := WriteExport([]AppleNote{{ID: "1", Title: "Title", Body: "Body"}}, exportDir)
	if err == nil || !strings.Contains(err.Error(), "disk full") {
		t.Fatalf("error = %v", err)
	}
	got, _ := os.ReadFile(old)
	if string(got) != "old" {
		t.Fatalf("old export = %q", got)
	}
	matches, _ := filepath.Glob(filepath.Join(filepath.Dir(exportDir), ".apple-notes-*"))
	if len(matches) != 0 {
		t.Fatalf("leftover staging: %v", matches)
	}
}

func TestWriteExportRestoresOldExportWhenFinalReplaceFails(t *testing.T) {
	root := t.TempDir()
	exportDir := filepath.Join(root, "docs", "apple-notes")
	if err := os.MkdirAll(exportDir, 0o755); err != nil {
		t.Fatal(err)
	}
	old := filepath.Join(exportDir, "old.txt")
	if err := os.WriteFile(old, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}

	orig := renamePath
	failed := false
	renamePath = func(source, target string) error {
		if target == exportDir && !failed {
			failed = true
			return errors.New("rename failed")
		}
		return orig(source, target)
	}
	defer func() { renamePath = orig }()

	err := WriteExport([]AppleNote{{ID: "1", Title: "Title", Body: "New body"}}, exportDir)
	if err == nil || !strings.Contains(err.Error(), "rename failed") {
		t.Fatalf("error = %v", err)
	}
	got, _ := os.ReadFile(old)
	if string(got) != "old" {
		t.Fatalf("old export = %q", got)
	}
	matches, _ := filepath.Glob(filepath.Join(filepath.Dir(exportDir), ".apple-notes-*"))
	if len(matches) != 0 {
		t.Fatalf("leftover staging: %v", matches)
	}
}

func TestSyncBuildsStagingThenSwapsExistingDB(t *testing.T) {
	root := t.TempDir()
	exportDir := filepath.Join(root, "docs", "apple-notes")
	dbDir := filepath.Join(root, "db")
	if err := os.Mkdir(dbDir, 0o755); err != nil {
		t.Fatal(err)
	}
	oldIndex := filepath.Join(dbDir, "old-index")
	if err := os.WriteFile(oldIndex, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}
	var events []string
	fetch := func() ([]AppleNote, int, error) {
		events = append(events, "fetch")
		return []AppleNote{{ID: "1", Title: "Private title", Body: "Private body"}}, 2, nil
	}
	rebuild := func(docsDir, stagingDBDir string) error {
		events = append(events, "rebuild")
		if docsDir != filepath.Dir(exportDir) {
			t.Fatalf("docsDir = %q", docsDir)
		}
		if filepath.Dir(stagingDBDir) != root {
			t.Fatalf("staging parent = %q", filepath.Dir(stagingDBDir))
		}
		if !strings.HasPrefix(filepath.Base(stagingDBDir), ".db-staging-") {
			t.Fatalf("staging name = %q", stagingDBDir)
		}
		if _, err := os.Stat(stagingDBDir); !os.IsNotExist(err) {
			t.Fatal("staging should not exist yet")
		}
		if _, err := os.Stat(oldIndex); err != nil {
			t.Fatal("old index should still exist during rebuild")
		}
		if err := os.Mkdir(stagingDBDir, 0o755); err != nil {
			return err
		}
		return os.WriteFile(filepath.Join(stagingDBDir, "new-index"), []byte("new"), 0o644)
	}

	exported, skipped, err := Sync(exportDir, dbDir, fetch, rebuild)
	if err != nil {
		t.Fatal(err)
	}
	if exported != 1 || skipped != 2 {
		t.Fatalf("exported=%d skipped=%d", exported, skipped)
	}
	if strings.Join(events, ",") != "fetch,rebuild" {
		t.Fatalf("events = %v", events)
	}
	if _, err := os.Stat(oldIndex); !os.IsNotExist(err) {
		t.Fatal("old index still present")
	}
	got, _ := os.ReadFile(filepath.Join(dbDir, "new-index"))
	if string(got) != "new" {
		t.Fatalf("new index = %q", got)
	}
	leftover, _ := filepath.Glob(filepath.Join(root, ".db-*"))
	if len(leftover) != 0 {
		t.Fatalf("leftover = %v", leftover)
	}
}

func TestSyncPreservesExistingDBWhenRebuildFails(t *testing.T) {
	root := t.TempDir()
	dbDir := filepath.Join(root, "db")
	if err := os.Mkdir(dbDir, 0o755); err != nil {
		t.Fatal(err)
	}
	oldIndex := filepath.Join(dbDir, "old-index")
	if err := os.WriteFile(oldIndex, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}
	rebuild := func(_ string, stagingDBDir string) error {
		if _, err := os.Stat(stagingDBDir); !os.IsNotExist(err) {
			t.Fatal("staging should not exist")
		}
		if err := os.Mkdir(stagingDBDir, 0o755); err != nil {
			return err
		}
		if err := os.WriteFile(filepath.Join(stagingDBDir, "partial"), []byte("partial"), 0o644); err != nil {
			return err
		}
		return errors.New("sensitive rebuild details")
	}

	_, _, err := Sync(filepath.Join(root, "docs", "apple-notes"), dbDir, func() ([]AppleNote, int, error) {
		return nil, 0, nil
	}, rebuild)
	if err == nil || err.Error() != "Notes were exported, but the index rebuild failed." {
		t.Fatalf("error = %v", err)
	}
	got, _ := os.ReadFile(oldIndex)
	if string(got) != "old" {
		t.Fatalf("old index = %q", got)
	}
	leftover, _ := filepath.Glob(filepath.Join(root, ".db-*"))
	if len(leftover) != 0 {
		t.Fatalf("leftover = %v", leftover)
	}
}

func TestSyncRestoresExistingDBWhenFinalSwapFails(t *testing.T) {
	root := t.TempDir()
	dbDir := filepath.Join(root, "db")
	if err := os.Mkdir(dbDir, 0o755); err != nil {
		t.Fatal(err)
	}
	oldIndex := filepath.Join(dbDir, "old-index")
	if err := os.WriteFile(oldIndex, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}

	orig := renamePath
	renamePath = func(source, target string) error {
		if strings.HasPrefix(filepath.Base(source), ".db-staging-") && target == dbDir {
			return errors.New("sensitive rename details")
		}
		return orig(source, target)
	}
	defer func() { renamePath = orig }()

	rebuild := func(_ string, stagingDBDir string) error {
		if err := os.Mkdir(stagingDBDir, 0o755); err != nil {
			return err
		}
		return os.WriteFile(filepath.Join(stagingDBDir, "new-index"), []byte("new"), 0o644)
	}

	_, _, err := Sync(filepath.Join(root, "docs", "apple-notes"), dbDir, func() ([]AppleNote, int, error) {
		return nil, 0, nil
	}, rebuild)
	if err == nil || err.Error() != "Notes were exported, but the index rebuild failed." {
		t.Fatalf("error = %v", err)
	}
	got, _ := os.ReadFile(oldIndex)
	if string(got) != "old" {
		t.Fatalf("old index = %q", got)
	}
	leftover, _ := filepath.Glob(filepath.Join(root, ".db-*"))
	if len(leftover) != 0 {
		t.Fatalf("leftover = %v", leftover)
	}
}

func TestSyncPromotesStagingWhenNoOldDBExists(t *testing.T) {
	root := t.TempDir()
	dbDir := filepath.Join(root, "db")
	rebuild := func(_ string, stagingDBDir string) error {
		if _, err := os.Stat(dbDir); !os.IsNotExist(err) {
			t.Fatal("db should not exist")
		}
		if _, err := os.Stat(stagingDBDir); !os.IsNotExist(err) {
			t.Fatal("staging should not exist")
		}
		if err := os.Mkdir(stagingDBDir, 0o755); err != nil {
			return err
		}
		return os.WriteFile(filepath.Join(stagingDBDir, "new-index"), []byte("new"), 0o644)
	}

	exported, skipped, err := Sync(filepath.Join(root, "docs", "apple-notes"), dbDir, func() ([]AppleNote, int, error) {
		return nil, 3, nil
	}, rebuild)
	if err != nil {
		t.Fatal(err)
	}
	if exported != 0 || skipped != 3 {
		t.Fatalf("exported=%d skipped=%d", exported, skipped)
	}
	if _, err := os.Stat(filepath.Join(dbDir, "new-index")); err != nil {
		t.Fatal(err)
	}
	leftover, _ := filepath.Glob(filepath.Join(root, ".db-*"))
	if len(leftover) != 0 {
		t.Fatalf("leftover = %v", leftover)
	}
}

func TestSyncPreservesDBWhenFetchFails(t *testing.T) {
	root := t.TempDir()
	dbDir := filepath.Join(root, "db")
	if err := os.Mkdir(dbDir, 0o755); err != nil {
		t.Fatal(err)
	}
	marker := filepath.Join(dbDir, "keep")
	if err := os.WriteFile(marker, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}
	rebuildCalled := false
	_, _, err := Sync(filepath.Join(root, "docs", "apple-notes"), dbDir, func() ([]AppleNote, int, error) {
		return nil, 0, &ExportError{Msg: "safe failure"}
	}, func(string, string) error {
		rebuildCalled = true
		return nil
	})
	if err == nil || err.Error() != "safe failure" {
		t.Fatalf("error = %v", err)
	}
	if _, err := os.Stat(marker); err != nil {
		t.Fatal("db was modified")
	}
	if rebuildCalled {
		t.Fatal("rebuild should not run")
	}
}

func TestSyncPreservesDBWhenExportStagingFails(t *testing.T) {
	root := t.TempDir()
	dbDir := filepath.Join(root, "db")
	if err := os.Mkdir(dbDir, 0o755); err != nil {
		t.Fatal(err)
	}
	marker := filepath.Join(dbDir, "keep")
	if err := os.WriteFile(marker, []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}
	orig := writeExport
	writeExport = func([]AppleNote, string) error {
		return errors.New("disk full")
	}
	defer func() { writeExport = orig }()

	rebuildCalled := false
	_, _, err := Sync(filepath.Join(root, "docs", "apple-notes"), dbDir, func() ([]AppleNote, int, error) {
		return nil, 0, nil
	}, func(string, string) error {
		rebuildCalled = true
		return nil
	})
	if err == nil || err.Error() != "Apple Notes export failed." {
		t.Fatalf("error = %v", err)
	}
	if _, err := os.Stat(marker); err != nil {
		t.Fatal("db was modified")
	}
	if rebuildCalled {
		t.Fatal("rebuild should not run")
	}
}

func TestSyncWrapsRebuildFailureWithoutSensitiveText(t *testing.T) {
	root := t.TempDir()
	exportDir := filepath.Join(root, "docs", "apple-notes")
	sensitive := "private embedding credentials"
	_, _, err := Sync(exportDir, filepath.Join(root, "db"), func() ([]AppleNote, int, error) {
		return []AppleNote{{ID: "1", Title: "Secret title", Body: "Secret body"}}, 0, nil
	}, func(string, string) error {
		return errors.New(sensitive)
	})
	if err == nil || err.Error() != "Notes were exported, but the index rebuild failed." {
		t.Fatalf("error = %v", err)
	}
	if strings.Contains(err.Error(), sensitive) {
		t.Fatal("leaked sensitive text")
	}
	if _, err := os.Stat(exportDir); err != nil {
		t.Fatal("export dir missing")
	}
	if _, err := os.Stat(filepath.Join(root, "db")); !os.IsNotExist(err) {
		t.Fatal("db should not exist")
	}
	leftover, _ := filepath.Glob(filepath.Join(root, ".db-*"))
	if len(leftover) != 0 {
		t.Fatalf("leftover = %v", leftover)
	}
}
