# CI and Branch Protection

This repository uses GitHub Actions for linting and tests. Configure branch protection rules
for the default branch (typically `main`) to require the following checks to pass before
merging:

- `Lint`
- `Unit Tests`
- `Integration Tests`
- `E2E Tests`

## Notes

- The required checks map to the job names in the workflows under `.github/workflows/`.
- Pre-commit is the entry point for linting and formatting.
- Unit, integration, and e2e tests are marked with the `unit`, `integration`, and `e2e`
  pytest markers, respectively.
