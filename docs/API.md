# API Reference

The package API reference is generated from the `vse_sim` package docstrings
with pdoc and published in the GitHub Pages site.

- [Generated `vse_sim` API reference](./api/vse_sim.html)
- [Notebook usage template](./JUPYTER_EXAMPLES.md)
- [Installation guide](./INSTALL.md)

## Rebuild Locally

From a repository checkout:

```shell
python -m pip install -e ".[docs]"
python tools/build_api_docs.py
```

Check that the committed API reference matches the current source:

```shell
python tools/build_api_docs.py --check
```

The default `nox` quality gate includes the same generated-docs check, and the
`Lint and Style` GitHub Actions workflow runs it on pull requests.
