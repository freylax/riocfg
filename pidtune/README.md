# Add the linuxcnc packages to module search path
The linuxcnc modules are in the /usr/lib/python3/dist-packages
directory. To bring it into the virtual environment we create
a file at ./.venv/lib/python3.13/site-packages/linuxcnc.pth
which contains one line
```
/usr/lib/python3/dist-packages
```

uv tool install mypy@latest
