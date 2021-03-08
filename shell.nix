{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python38.withPackages (ps: with ps; [ virtualenv ]))
  ];

  shellHook = ''
    unset SOURCE_DATE_EPOCH
    [ -d venv ] || virtualenv -p python3 venv
    source venv/bin/activate
  '';
}
