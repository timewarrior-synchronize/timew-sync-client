let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix/";
    ref = "refs/tags/3.1.1";
  }) {
    # optionally bring your own nixpkgs
    # pkgs = import <nixpkgs> {};

    # optionally specify the python version
    # python = "python38";

    # optionally update pypi data revision from https://github.com/DavHau/pypi-deps-db
    # pypiDataRev = "some_revision";
    # pypiDataSha256 = "some_sha256";
  };
in
mach-nix.buildPythonApplication {
  pname = "timewsync";
  version = "1.0.0";

  src = ./.;

  format = "pyproject";

  requirements = ''
    requests~=2.25.0
    colorama~=0.4.4
    jwcrypto~=0.8
    python_jwt~=3.3
    six~=1.9
  '';
}
