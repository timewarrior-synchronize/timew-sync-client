{ pkgs ? import <nixpkgs> {} }:
with pkgs.python38Packages;

buildPythonApplication rec {
  pname = "timewsync";
  version = "0.0.1";

  src = ./.;

  format = "pyproject";

  propagatedBuildInputs = [
    requests
  ];

  # meta = with pkgs; {
  #   homepage = "https://ytdl-org.github.io/youtube-dl/";
  #   description = "Timewarrior Synchronization Client";
  #   longDescription = ''
  #     youtube-dl is a small, Python-based command-line program
  #     to download videos from YouTube.com and a few more sites.
  #     youtube-dl is released to the public domain, which means
  #     you can modify it, redistribute it or use it however you like.
  #   '';
  #   license = licenses.mit;
  #   platforms = with platforms; linux ++ darwin;
  # };
}
