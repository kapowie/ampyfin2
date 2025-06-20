# Contributor Guide

## Dev Environment Tips
Make sure you have Python 3.12 installed. Run `pre-commit` before committing to keep formatting consistent.

## Testing Instructions
The test suite requires TA-Lib and the libraries listed in `requirements.txt` and `requirements-dev.txt`. Install them with the commands below only when tests are needed:

```bash
export TA_LIB_VERSION=0.6.4
curl -L https://github.com/ta-lib/ta-lib/releases/download/v$TA_LIB_VERSION/ta-lib-$TA_LIB_VERSION-src.tar.gz > ta-lib-src.tar.gz && \
    tar -xzf ta-lib-src.tar.gz && \
    cd ta-lib-$TA_LIB_VERSION/ && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-$TA_LIB_VERSION ta-lib-src.tar.gz


python -m pip install --user -r requirements.txt
python -m pip install --user -r requirements-dev.txt
```

Run the tests with `pytest` after installing the dependencies. Skip this entire section for tasks that don't require running tests.
