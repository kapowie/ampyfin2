# Contributor Guide

## Dev Environment Tips
Make sure you have Python 3.12 installed. Run `pre-commit` before committing to keep formatting consistent.

## Testing Instructions
The test suite requires TA-Lib and the libraries listed in `requirements.txt` and `requirements-dev.txt`. Install them with the commands below only when tests are needed:

```bash
python -m pip install --user -r requirements.txt
python -m pip install --user -r requirements-dev.txt
```

Run the tests with `pytest` after installing the dependencies. Skip this entire section for tasks that don't require running tests.
