# Census dashboards

The review suite planned in `docs/census-dashboards-plan.md`: a private Dashboard artifact
(`assets.json` names it) with one page per question.

- `build.py` reduces the census records to the datasets in `data/`, checks them against the
  records, and writes them. The tests are `tests/test_census_dashboards.py`.
- `page/` is the dashboard's page: `index.html` and its scripts, written to the dashboard
  runtime's one-writer rule (text in the HTML, data in drawings). `params.json` holds the
  filters' defaults.
- `dev/` renders the page locally with a stand-in for the runtime (`shim.js`), runs the
  runtime's checks (stray writes, overlapping or cut labels, empty charts, NaN, and marks
  whose shown value differs from the data) and screenshots each page:

      node examples/qec-census-4/dashboards/dev/render.js <d3.min.js> <out dir> [pages] [widths] [light|dark]

## Refreshing

1. `python examples/qec-census-4/dashboards/build.py` (about 30 s; the first run walks the
   records' git history for when each torus first appeared, then caches it).
2. Upload each changed `data/*.json` to the dashboard as an asset, then update its
   `datasets/<id>` document's `source.url`, `source.name` and `updated`.
3. A changed page file is written whole to `files/<name>` in the dashboard's store.
