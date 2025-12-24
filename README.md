# mcp_admin
administration and serving of our mcp tools

## Test tiers

Install dependencies for the test suite:

```bash
pip install -r requirements-dev.txt
```

### Unit tests (tool discovery + hierarchy)

```bash
pytest tests/unit
```

### Functional tests (tool enable/disable + label navigation)

```bash
pytest tests/functional
```

### Integration tests (API endpoints)

```bash
pytest tests/integration
```

### End-to-end tests (admin UI)

The e2e tests use Playwright. Install the browsers before running:

```bash
python -m playwright install
pytest tests/e2e
```
