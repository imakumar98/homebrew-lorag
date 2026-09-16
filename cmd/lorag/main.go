package main

import (
	"os"

	"github.com/imakumar98/lorag/internal/cli"
)

func main() {
	os.Exit(cli.Main(os.Args[1:], cli.Options{}))
}
