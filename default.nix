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
  version = "1.1";

  src = ./.;

  format = "pyproject";

  requirements = ''
    colorama~=0.4.6
    jwcrypto~=1.5.6
    pyjwt~=2.8.0
    requests~=2.31.0
  '';
}
