# Documentation Site Notes

The `docs/` directory contains the GitHub Pages site for the original VSE
write-up and generated report pages. It also contains package-maintainer notes
that are useful from the repository:

- `INSTALL.md`: PyPI, Jupyter, Python, GitHub, and editable install examples.
- `PUBLISHING.md`: release and PyPI publishing workflow.

Preview the Pages site locally with Jekyll:

```shell
jekyll serve -s docs/ --incremental
```

Then open <http://localhost:4000/vse-sim/>.

The large HTML files in this folder are retained as legacy report artifacts for
the existing Pages site.
