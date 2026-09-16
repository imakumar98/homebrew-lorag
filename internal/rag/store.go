package rag

import (
	"context"
	"fmt"
	"runtime"

	"github.com/philippgille/chromem-go"
)

func Rebuild(docsDir, dbDir, embedModel string, embed Embedder) error {
	if embed == nil {
		embed = NewOllamaEmbedder(embedModel)
	}
	batched := BatchedEmbeddings{Inner: embed, BatchSize: EmbedBatchSize}

	docs, err := LoadDocuments(docsDir)
	if err != nil {
		return err
	}
	fmt.Printf("Loaded %d documents. Splitting...\n", len(docs))
	chunks := SplitDocuments(docs)
	fmt.Printf("Created %d chunks. Building vectorstore...\n", len(chunks))
	texts := make([]string, len(chunks))
	for i, chunk := range chunks {
		texts[i] = chunk.Content
	}
	vectors, err := batched.EmbedDocuments(texts)
	if err != nil {
		return err
	}

	db, err := chromem.NewPersistentDB(dbDir, false)
	if err != nil {
		return err
	}
	collection, err := db.GetOrCreateCollection("lorag", nil, func(ctx context.Context, text string) ([]float32, error) {
		return batched.EmbedQuery(text)
	})
	if err != nil {
		return err
	}

	if len(chunks) == 0 {
		fmt.Printf("Vectorstore built with %d chunks.\n", len(chunks))
		return nil
	}

	documents := make([]chromem.Document, len(chunks))
	for i, chunk := range chunks {
		documents[i] = chromem.Document{
			ID:        chunkID(chunk.Source, i),
			Metadata:  map[string]string{"source": chunk.Source},
			Embedding: vectors[i],
			Content:   chunk.Content,
		}
	}
	workers := runtime.NumCPU()
	if workers < 1 {
		workers = 1
	}
	if err := collection.AddDocuments(context.Background(), documents, workers); err != nil {
		return err
	}
	fmt.Printf("Vectorstore built with %d chunks.\n", len(chunks))
	return nil
}

func defaultOpenStore(docsDir, dbDir, embedModel string) (VectorStore, error) {
	_ = docsDir
	return openStore(dbDir, NewOllamaEmbedder(embedModel))
}

func openStore(dbDir string, embed Embedder) (VectorStore, error) {
	batched := BatchedEmbeddings{Inner: embed, BatchSize: EmbedBatchSize}
	db, err := chromem.NewPersistentDB(dbDir, false)
	if err != nil {
		return nil, err
	}
	collection, err := db.GetOrCreateCollection("lorag", nil, func(ctx context.Context, text string) ([]float32, error) {
		return batched.EmbedQuery(text)
	})
	if err != nil {
		return nil, err
	}
	return chromemStore{collection: collection}, nil
}

type chromemStore struct {
	collection *chromem.Collection
}

func (s chromemStore) SimilaritySearch(query string, k int) ([]Document, error) {
	if k < 1 {
		k = 1
	}
	if s.collection.Count() == 0 {
		return nil, nil
	}
	if n := s.collection.Count(); k > n {
		k = n
	}
	results, err := s.collection.Query(context.Background(), query, k, nil, nil)
	if err != nil {
		return nil, err
	}
	docs := make([]Document, 0, len(results))
	for _, result := range results {
		source := result.Metadata["source"]
		if source == "" {
			source = "unknown"
		}
		docs = append(docs, Document{Content: result.Content, Source: source})
	}
	return docs, nil
}
