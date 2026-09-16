package rag

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func ollamaBaseURL() string {
	host := strings.TrimSpace(os.Getenv("OLLAMA_HOST"))
	if host == "" {
		return "http://localhost:11434"
	}
	if strings.Contains(host, "://") {
		return strings.TrimRight(host, "/")
	}
	return "http://" + strings.TrimRight(host, "/")
}

type OllamaEmbedder struct {
	Model   string
	BaseURL string
	Client  *http.Client
}

func NewOllamaEmbedder(model string) *OllamaEmbedder {
	return &OllamaEmbedder{
		Model:   model,
		BaseURL: ollamaBaseURL(),
		Client:  http.DefaultClient,
	}
}

func (o *OllamaEmbedder) EmbedQuery(text string) ([]float32, error) {
	vectors, err := o.EmbedDocuments([]string{text})
	if err != nil {
		return nil, err
	}
	if len(vectors) == 0 {
		return nil, fmt.Errorf("no embeddings found in the response")
	}
	return vectors[0], nil
}

func (o *OllamaEmbedder) EmbedDocuments(texts []string) ([][]float32, error) {
	if len(texts) == 0 {
		return nil, nil
	}
	body, err := json.Marshal(map[string]any{
		"model": o.Model,
		"input": texts,
	})
	if err != nil {
		return nil, err
	}
	resp, err := o.do(http.MethodPost, "/api/embed", body)
	if err != nil {
		return nil, err
	}
	var parsed struct {
		Embeddings [][]float32 `json:"embeddings"`
		Error      string      `json:"error"`
	}
	if err := json.Unmarshal(resp, &parsed); err != nil {
		return nil, err
	}
	if parsed.Error != "" {
		return nil, fmt.Errorf("%s", parsed.Error)
	}
	if len(parsed.Embeddings) == 0 {
		return nil, fmt.Errorf("no embeddings found in the response")
	}
	return parsed.Embeddings, nil
}

func defaultChat(model, system, user string) (string, error) {
	think := false
	body, err := json.Marshal(map[string]any{
		"model": model,
		"messages": []map[string]string{
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		},
		"stream": false,
		"think":  think,
		"options": map[string]any{
			"temperature": 0,
			"num_predict": 300,
		},
	})
	if err != nil {
		return "", err
	}
	resp, err := (&OllamaEmbedder{BaseURL: ollamaBaseURL(), Client: http.DefaultClient}).do(http.MethodPost, "/api/chat", body)
	if err != nil {
		return "", err
	}
	var parsed struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
		Error string `json:"error"`
	}
	if err := json.Unmarshal(resp, &parsed); err != nil {
		return "", err
	}
	if parsed.Error != "" {
		return "", fmt.Errorf("%s", parsed.Error)
	}
	return parsed.Message.Content, nil
}

func (o *OllamaEmbedder) do(method, path string, body []byte) ([]byte, error) {
	client := o.Client
	if client == nil {
		client = http.DefaultClient
	}
	base := o.BaseURL
	if base == "" {
		base = ollamaBaseURL()
	}
	req, err := http.NewRequestWithContext(context.Background(), method, base+path, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode >= 400 {
		var parsed struct {
			Error string `json:"error"`
		}
		if err := json.Unmarshal(data, &parsed); err == nil && parsed.Error != "" {
			return nil, fmt.Errorf("%s", parsed.Error)
		}
		return nil, fmt.Errorf("ollama %s: %s", resp.Status, strings.TrimSpace(string(data)))
	}
	return data, nil
}
