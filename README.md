
# Giges

The one hundred arms giant in charge of Tesselo integrations

## Install runtime dependencies

```
make install
```


## Install development dependencies

```
# This will also install the runtime dependencies
make dev_install
```

## Upgrade unpinned dependencies

```
make upgrade_dependencies
```

## Pre-commit hooks

We are using <https://pre-commit.com/> hooks, they are specified in the file `.pre-commit-config.yaml` and installed when you run `make dev_install`.
If the pre-commit configuration file is changed, remember to run `make dev_install` or `pre-commit install` again.

To manually force run the pre-commit tasks, you can type:

```bash
make pre-commit
```

## Make targets

The `Makefile` is a good resource to see how things are done.
Some of these targets include:

### Common checks before opening a PR

Includes the pre-commit hooks and running the tests with 
code coverage reports.

```bash
make check
```


### Extended checks to know more about the code

Includes security checks and other code smells.

```bash
make check-advanced
```

### Picky checks to be a code snob

Includes code complexity and documentation style checks.
```bash
make check-picky
```


## Environment variables

We are using a helper to load the environment variables, located in `scripts/loadenv`

It is a bash function that will inject the variables in the corresponding .env file and modify the prompt
depending on the environment.

To load the function:

```bash
source scripts/loadenv
```

After that, load the environment:
```bash
loadenv prod
```

The source files are: `.env.prod`, `.env.stag`, `.env.dev` and `.env.test`

Only `.env.test` is in git, the rest will contain secrets and should not be added to the repository.


## Flask CLI

Database management and other operations will be integrated into the Flask CLI

```bash
pip install -e .
loadenv dev
giges
```

### Create & upgrade the database

```bash
pip install -e .
loadenv dev
giges db upgrade head
```
