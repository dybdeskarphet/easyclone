{
  description = "easyclone - Rclone bulk backup wrapper";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    uv2nix.url = "github:pyproject-nix/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";

    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
    pyproject-build-systems.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems.inputs.uv2nix.follows = "uv2nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = import ./nix/package.nix {
            inherit pkgs uv2nix pyproject-nix pyproject-build-systems;
          };
          easyclone = self.packages.${system}.default;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pkg = self.packages.${system}.default;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkg
              pkgs.rclone
              pkgs.uv
              pkgs.python313
            ];
          };
        }
      );

      homeManagerModules.default = import ./nix/module.nix self;
      homeManagerModules.easyclone = self.homeManagerModules.default;
      homeModules.default = self.homeManagerModules.default;
      homeModules.easyclone = self.homeManagerModules.default;
    };
}
