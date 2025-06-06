{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.requests
    pkgs.python311Packages.beautifulsoup4
    pkgs.python311Packages.pandas
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.matplotlib
    pkgs.glibcLocales
  ];
}
