package paths

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFromHomeUsesSharedLoragDirectory(t *testing.T) {
	home := "/tmp/fake-home"
	got := FromHome(home)

	if got.DocsDir != filepath.Join(home, "lorag", "docs") {
		t.Fatalf("DocsDir = %q", got.DocsDir)
	}
	if got.DBDir != filepath.Join(home, "lorag", "database") {
		t.Fatalf("DBDir = %q", got.DBDir)
	}
	if got.ConfigPath != filepath.Join(home, ".lorag", "config.toml") {
		t.Fatalf("ConfigPath = %q", got.ConfigPath)
	}
	if got.NotesDir() != filepath.Join(home, "lorag", "docs", "apple-notes") {
		t.Fatalf("NotesDir = %q", got.NotesDir())
	}
}

func TestEnsureLayoutCreatesDocsAndStateDirs(t *testing.T) {
	home := t.TempDir()
	paths := FromHome(home)

	if err := EnsureLayout(paths); err != nil {
		t.Fatal(err)
	}

	if info, err := os.Stat(paths.DocsDir); err != nil || !info.IsDir() {
		t.Fatalf("docs dir missing: %v", err)
	}
	if info, err := os.Stat(filepath.Dir(paths.ConfigPath)); err != nil || !info.IsDir() {
		t.Fatalf("config dir missing: %v", err)
	}
	if _, err := os.Stat(paths.DBDir); !os.IsNotExist(err) {
		t.Fatalf("db dir should not exist yet, err=%v", err)
	}
}

func TestWriteDefaultConfigCreatesExpectedModels(t *testing.T) {
	home := t.TempDir()
	paths := FromHome(home)
	if err := EnsureLayout(paths); err != nil {
		t.Fatal(err)
	}
	if err := WriteDefaultConfig(paths); err != nil {
		t.Fatal(err)
	}

	config, err := LoadConfig(paths)
	if err != nil {
		t.Fatal(err)
	}
	if config.ChatModel != DefaultChatModel {
		t.Fatalf("chat_model = %q", config.ChatModel)
	}
	if config.EmbedModel != DefaultEmbedModel {
		t.Fatalf("embed_model = %q", config.EmbedModel)
	}
	if DefaultChatModel != "llama3.2:3b" {
		t.Fatalf("DefaultChatModel = %q", DefaultChatModel)
	}
	if DefaultEmbedModel != "nomic-embed-text" {
		t.Fatalf("DefaultEmbedModel = %q", DefaultEmbedModel)
	}
}

func TestWriteDefaultConfigDoesNotOverwriteExistingChatModel(t *testing.T) {
	home := t.TempDir()
	paths := FromHome(home)
	if err := EnsureLayout(paths); err != nil {
		t.Fatal(err)
	}
	if err := WriteDefaultConfig(paths); err != nil {
		t.Fatal(err)
	}
	if err := SetChatModel(paths, "qwen3.5:4b"); err != nil {
		t.Fatal(err)
	}
	if err := WriteDefaultConfig(paths); err != nil {
		t.Fatal(err)
	}

	config, err := LoadConfig(paths)
	if err != nil {
		t.Fatal(err)
	}
	if config.ChatModel != "qwen3.5:4b" {
		t.Fatalf("chat_model = %q", config.ChatModel)
	}
}

func TestLoadConfigReturnsDefaultsWhenFileMissing(t *testing.T) {
	paths := FromHome(t.TempDir())
	config, err := LoadConfig(paths)
	if err != nil {
		t.Fatal(err)
	}
	if config.ChatModel != "llama3.2:3b" {
		t.Fatalf("chat_model = %q", config.ChatModel)
	}
	if config.EmbedModel != "nomic-embed-text" {
		t.Fatalf("embed_model = %q", config.EmbedModel)
	}
}

func TestSetChatModelRoundTripsQuoteAndBackslash(t *testing.T) {
	home := t.TempDir()
	paths := FromHome(home)
	if err := EnsureLayout(paths); err != nil {
		t.Fatal(err)
	}
	if err := WriteDefaultConfig(paths); err != nil {
		t.Fatal(err)
	}

	tricky := `org/"custom\model"`
	if err := SetChatModel(paths, tricky); err != nil {
		t.Fatal(err)
	}

	config, err := LoadConfig(paths)
	if err != nil {
		t.Fatal(err)
	}
	if config.ChatModel != tricky {
		t.Fatalf("chat_model = %q", config.ChatModel)
	}
	if config.EmbedModel != DefaultEmbedModel {
		t.Fatalf("embed_model = %q", config.EmbedModel)
	}
}
