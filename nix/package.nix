{
  pkgs,
  uv2nix,
  pyproject-nix,
  pyproject-build-systems,
}:

let
  workspace = uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = ../.;
  };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  python = pkgs.python313;
  pythonSet =
    (pkgs.callPackage pyproject-nix.build.packages {
      inherit python;
    }).overrideScope
      (
        pkgs.lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
          (final: prev: {
            easyclone = prev.easyclone.overrideAttrs (old: {
              src = pkgs.lib.cleanSource ../.;
            });
          })
        ]
      );

  virtualenv = pythonSet.mkVirtualEnv "easyclone-env" (
    workspace.deps.default
    // {
      easyclone = [ ];
    }
  );
in
pkgs.symlinkJoin {
  name = "easyclone";
  paths = [ virtualenv ];
  nativeBuildInputs = [ pkgs.makeWrapper ];
  postBuild = ''
    wrapProgram $out/bin/easyclone \
      --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.rclone ]}
  '';
  meta = {
    description = "Very convenient Rclone bulk backup wrapper";
    homepage = "https://github.com/dybdeskarphet/easyclone";
    mainProgram = "easyclone";
  };
}
