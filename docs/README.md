# Documentation Site Notes

The `docs/` directory contains the GitHub Pages site for the original VSE
write-up and generated report pages. It also contains package-maintainer notes
that are useful from the repository:

- `INSTALL.md`: PyPI, Jupyter, Python, GitHub, and editable install examples.
- `JUPYTER_EXAMPLES.md`: copy-paste notebook cookbook and end-user smoke tests.
- `API.md`: generated API reference notes and local build instructions.
- `PUBLISHING.md`: release and PyPI publishing workflow.
- `api/`: pdoc-generated API reference served by GitHub Pages.

Preview the Pages site locally with Jekyll:

```shell
jekyll serve -s docs/ --incremental
```

Then open <http://localhost:4000/vse-sim/>.

The large HTML files in this folder are retained as legacy report artifacts for
the existing Pages site.

Regenerate the API reference from the package docstrings with:

```shell
python tools/build_api_docs.py
```
