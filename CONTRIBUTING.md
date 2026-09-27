# Contributing

Keep changes focused and explain the security problem they address. Use synthetic data in examples and tests. Do not include credentials, real incident records, VM images or proprietary datasets.

1. Create a branch and work in a Python 3.11 virtual environment.
2. Install the relevant requirements file.
3. Add meaningful tests for ingestion behavior, retrieval integrity or an API boundary when changing those paths.
4. Run `python -m unittest discover -s tests -v` and `python scripts/check_repo.py`.
5. Document any change to configuration, data flow or external provider behavior.

Generated rule examples must identify required telemetry, assumptions, false positives and validation status. Keep proposed work distinct from measured results. Dependency upgrades should include target-environment installation and integration checks; never commit `.env` or a local index to make CI pass.
