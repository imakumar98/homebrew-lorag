package paths

import (
	"os"
	"path/filepath"

	"github.com/pelletier/go-toml/v2"
)

const (
	DefaultChatModel  = "llama3.2:3b"
	DefaultEmbedModel = "nomic-embed-text"
)

type Paths struct {
	DocsDir    string
	DBDir      string
	ConfigPath string
}

func (p Paths) NotesDir() string {
	return filepath.Join(p.DocsDir, "apple-notes")
}

func FromHome(home string) Paths {
	return Paths{
		DocsDir:    filepath.Join(home, "lorag", "docs"),
		DBDir:      filepath.Join(home, "lorag", "database"),
		ConfigPath: filepath.Join(home, ".lorag", "config.toml"),
	}
}

type Config struct {
	ChatModel  string
	EmbedModel string
}

type fileConfig struct {
	ChatModel  string `toml:"chat_model"`
	EmbedModel string `toml:"embed_model"`
}

func EnsureLayout(paths Paths) error {
	if err := os.MkdirAll(paths.DocsDir, 0o755); err != nil {
		return err
	}
	return os.MkdirAll(filepath.Dir(paths.ConfigPath), 0o755)
}

func LoadConfig(paths Paths) (Config, error) {
	defaults := Config{ChatModel: DefaultChatModel, EmbedModel: DefaultEmbedModel}
	data, err := os.ReadFile(paths.ConfigPath)
	if err != nil {
		if os.IsNotExist(err) {
			return defaults, nil
		}
		return Config{}, err
	}

	var parsed fileConfig
	if err := toml.Unmarshal(data, &parsed); err != nil {
		return Config{}, err
	}
	if parsed.ChatModel == "" {
		parsed.ChatModel = DefaultChatModel
	}
	if parsed.EmbedModel == "" {
		parsed.EmbedModel = DefaultEmbedModel
	}
	return Config{ChatModel: parsed.ChatModel, EmbedModel: parsed.EmbedModel}, nil
}

func WriteDefaultConfig(paths Paths) error {
	if _, err := os.Stat(paths.ConfigPath); err == nil {
		return nil
	} else if !os.IsNotExist(err) {
		return err
	}
	return writeConfig(paths, Config{ChatModel: DefaultChatModel, EmbedModel: DefaultEmbedModel})
}

func SetChatModel(paths Paths, chatModel string) error {
	config, err := LoadConfig(paths)
	if err != nil {
		return err
	}
	return writeConfig(paths, Config{ChatModel: chatModel, EmbedModel: config.EmbedModel})
}

func writeConfig(paths Paths, config Config) error {
	if err := EnsureLayout(paths); err != nil {
		return err
	}
	data, err := toml.Marshal(fileConfig{
		ChatModel:  config.ChatModel,
		EmbedModel: config.EmbedModel,
	})
	if err != nil {
		return err
	}
	return os.WriteFile(paths.ConfigPath, data, 0o644)
}
