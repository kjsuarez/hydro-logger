
# Auto Logger
A quick and dirty tool for generating NOAA hydrographic survey logs from existing files.

### Run locally
While inside the working directory, execute the following:
```
$ py autologger.py
```
### Generate an executable with PyInstaller

While inside the working directory, execute the following:
```
$ pip install -U pyinstaller
$ pyinstaller autologger.spec
```
The usable executable should be generated at `./dist/autologger/autologger.exe`
