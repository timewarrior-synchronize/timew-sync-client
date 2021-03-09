{ pkgs ? import <nixpkgs> {} }:
with pkgs.python38Packages;

buildPythonApplication rec {
  pname = "timewsync";
  version = "0.0.1";

  src = ./.;

  format = "pyproject";

  propagatedBuildInputs = [
    requests
    jwcrypto
    colorama
  ];
}
