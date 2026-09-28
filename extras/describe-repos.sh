#!/usr/bin/env bash
# Gives the repos descriptions and topics so pinned cards stop being blank.
# Needs the GitHub CLI logged in as ChPuru (gh auth login). Each one-liner
# comes from that repo's README; fix any that no longer match before running.
set -euo pipefail
O=ChPuru

gh repo edit "$O/hematite"  --description "x86-64 operating system written from scratch in Rust: kernel, window server, shell, libc and a C compiler. Runs in QEMU." --add-topic rust,operating-system,kernel,osdev,x86-64,no-std,qemu
gh repo edit "$O/Keel"      --description "Statically typed language that compiles to native executables, with its whole toolchain. No LLVM, zero dependencies." --add-topic rust,compiler,programming-language,codegen,language-server
gh repo edit "$O/quiver"    --description "Embedded database for Rust: vector search, records, key-value, full-text and transactions in one file." --add-topic rust,database,embedded-database,vector-database,hnsw,full-text-search
gh repo edit "$O/Container" --description "hull: a container engine written from scratch in Go that serves the Docker Engine API." --add-topic go,containers,docker,oci,cgroups,namespaces,wsl2
gh repo edit "$O/vcgit"     --description "vc: jj-style version control on plain git storage, plus vchub, a single-binary forge." --add-topic go,version-control,git,jujutsu,forge
gh repo edit "$O/Pylon"     --description "Programmable reverse proxy and HTTP server in Rust with sandboxed, hot-reloading WebAssembly plugins." --add-topic rust,reverse-proxy,webassembly,http2,tls,load-balancer
gh repo edit "$O/Relay"     --description "Local-first, git-native API client where requests are TOML files. Rust core, CLI and Tauri desktop app." --add-topic rust,api-client,http,tauri,cli
gh repo edit "$O/Torrent_client" --description "bTclient: BitTorrent daemon on libtorrent with a qBittorrent-compatible Web API and a web UI." --add-topic rust,bittorrent,libtorrent,qbittorrent
gh repo edit "$O/Blockchain" --description "Ferrum: UTXO blockchain from scratch in Rust with a stack-based script VM." --add-topic rust,blockchain,utxo,proof-of-work,cryptography
gh repo edit "$O/NN-"       --description "scratchgrad: deep learning framework in pure NumPy with hand-derived gradients, up to a mini-GPT." --add-topic python,numpy,deep-learning,autograd,transformer
gh repo edit "$O/Scratch_LLM" --description "TinyLLM: a 1.7M-parameter language model built from scratch in PyTorch that runs in a browser tab." --add-topic python,pytorch,llm,transformer,onnx
gh repo edit "$O/arc"       --description "ARC: local-first personal assistant with voice and memory that runs fully offline on one laptop." --add-topic python,assistant,voice-assistant,ollama,rag,local-first
gh repo edit "$O/SIH26_63"  --description "KASAUTI: forensic detection and provenance for synthetic media in Indian languages. SIH 2026." --add-topic python,deepfake-detection,forensics,provenance,sih2026
gh repo edit "$O/Framework" --description "Filum: fine-grained reactive UI framework. Signals plus compiled JSX, no virtual DOM." --add-topic typescript,ui-framework,signals,jsx,reactive
gh repo edit "$O/netscape"  --description "Netscape Matrix: privacy browser on CEF with a Rust ad blocker, Tor-routed private tabs and its own search engine." --add-topic rust,cpp,browser,cef,privacy,tor
gh repo edit "$O/Nuctify"   --description "One free music player for YouTube Music, JioSaavn, SoundCloud, Bandcamp, podcasts and local files." --add-topic typescript,music-player,android,windows
gh repo edit "$O/Environment" --description "Eleven tested Rust CLI tools, including warden, an encrypted backup tool that verifies its restores." --add-topic rust,cli,backup,encryption
gh repo edit "$O/quantum"   --description "Small Qiskit projects: Grover, Shor, QAOA, VQE, BB84 and error correction." --add-topic quantum-computing,qiskit,python

# Optional renames so repo names match project names. GitHub redirects the old
# URLs (the README links keep working); local clones need `git remote set-url`.
# gh repo rename hull        -R "$O/Container"      --yes
# gh repo rename filum       -R "$O/Framework"      --yes
# gh repo rename scratchgrad -R "$O/NN-"            --yes
# gh repo rename tinyllm     -R "$O/Scratch_LLM"    --yes
# gh repo rename ferrum      -R "$O/Blockchain"     --yes
# gh repo rename btclient    -R "$O/Torrent_client" --yes
