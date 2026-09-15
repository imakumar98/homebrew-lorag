class Lorag < Formula
  include Language::Python::Virtualenv

  desc "Ask questions over local documents and Apple Notes"
  homepage "https://github.com/imakumar98/homebrew-lorag"
  url "https://github.com/imakumar98/homebrew-lorag/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "06de9d410f579e6ec3600a6a02ff72d11f73a46434dc366a08fd99dc41eab745"
  license :cannot_represent
  head "https://github.com/imakumar98/homebrew-lorag.git", branch: "main"

  depends_on "python@3.14"
  depends_on "ollama"
  depends_on :macos

  def install
    virtualenv_create(libexec, "python3.14")

    src = libexec/"src"
    src.mkpath
    cp_r buildpath/"lorag", src
    cp buildpath/"pyproject.toml", src

    (libexec/"bin/lorag").write <<~SH
      #!/bin/bash
      exec "#{libexec}/bin/python" -m lorag "$@"
    SH
    chmod 0755, libexec/"bin/lorag"
    bin.install_symlink libexec/"bin/lorag"
  end

  def post_install
    system "python3.14", "-m", "pip", "--python=#{libexec}/bin/python",
           "install", "--upgrade", libexec/"src"
  end

  def caveats
    <<~EOS
      Start Ollama, pull the default models, then initialize:

        brew services start ollama
        ollama pull llama3.2:3b
        ollama pull nomic-embed-text
        lorag init
    EOS
  end

  test do
    assert_match "usage: lorag", shell_output("#{bin}/lorag -h")
  end
end
