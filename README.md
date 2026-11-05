# FileIndex Daemon

A Python standard-library local file indexing prototype. Builds a recursive snapshot of file paths, sizes, and modification timestamps; optionally computes SHA-256 checksums. Search a saved snapshot by filename, extension and minimum size. The Python API also compares snapshots to detect added, removed and changed files.

## Usage

```bash
python fileindex.py build . --output snapshot.json
python fileindex.py build . --output snapshot.json --hash
python fileindex.py search snapshot.json --query readme
python fileindex.py search snapshot.json --extension .py --min-size 100
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Eight tests run on Python 3.10, 3.12 and 3.13 via GitHub Actions.

## Limitations

Despite its name, this is a **snapshot CLI**, not a continuously running daemon. It does not watch file changes, index contents, provide an API, or guarantee atomic snapshots of changing directories. Symbolic links are skipped. The generated snapshot includes local file paths and should be handled as potentially sensitive metadata.
