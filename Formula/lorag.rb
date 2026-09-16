class Lorag < Formula
  desc "Ask questions over local documents and Apple Notes"
  homepage "https://github.com/imakumar98/homebrew-lorag"
  url "https://github.com/imakumar98/homebrew-lorag/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "55e2216e99e9f6458474410d072aa620a6028eada1d2cd872f63eff3a3607f09"
  license :cannot_represent
  head "https://github.com/imakumar98/homebrew-lorag.git", branch: "main"

  depends_on "go" => :build
  depends_on "ollama"
  depends_on :macos

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w"), "./cmd/lorag"
  end

  def post_install
    install_default_models
  end

  def caveats
    <<~EOS
      Export Apple Notes and build the index:

        lorag sync

      macOS may ask for Notes permission; allow it, then run lorag sync again.
    EOS
  end

  test do
    assert_match "usage: lorag", shell_output("#{bin}/lorag -h")
  end

  def install_default_models
    ollama = Formula["ollama"].opt_bin/"ollama"
    start_ollama! unless quiet_system ollama, "list"

    ohai "Pulling default Ollama models"
    system ollama, "pull", "llama3.2:3b"
    system ollama, "pull", "nomic-embed-text"
  end

  def start_ollama!
    ohai "Starting Ollama"
    prefix = Formula["ollama"].opt_prefix
    plist_src = Pathname.glob(prefix/"*.plist").max_by { |path| path.mtime }

    if plist_src
      dest = Pathname.new(Dir.home)/"Library/LaunchAgents"/plist_src.basename
      dest.dirname.mkpath
      cp plist_src, dest
      domain = "gui/#{Process.uid}"
      quiet_system "/bin/launchctl", "bootout", domain, dest.to_s
      quiet_system "/bin/launchctl", "bootstrap", domain, dest.to_s
    else
      pid = spawn((Formula["ollama"].opt_bin/"ollama").to_s, "serve",
                  out: File::NULL, err: File::NULL)
      Process.detach(pid)
    end

    ollama = Formula["ollama"].opt_bin/"ollama"
    30.times do
      return if quiet_system ollama, "list"

      sleep 1
    end
    odie "Ollama did not start. Open the Ollama app and re-run: brew reinstall lorag"
  end
end
