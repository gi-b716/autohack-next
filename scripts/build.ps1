python -m pip install --upgrade pip
python -m pip install .
python -m build
python -m nuitka --standalone --onefile --follow-imports --remove-output --enable-plugins=upx --lto=yes --warn-implicit-exceptions --warn-unusual-code --file-version=$(python -m autohack --version) src\autohack\__main__.py
Move-Item __main__.exe autohack.exe
mkdir release-package
Copy-Item README.md release-package/
Copy-Item autohack.exe release-package/autohack.exe
Set-Location release-package
Compress-Archive -Path * -DestinationPath ../autohack-windows-$(python -m autohack --version).zip
Set-Location ..
Remove-Item autohack.exe
Remove-Item -Force -Recurse release-package
Copy-Item autohack-windows-$(python -m autohack --version).zip dist/nuitka/
Remove-Item autohack-windows-$(python -m autohack --version).zip
