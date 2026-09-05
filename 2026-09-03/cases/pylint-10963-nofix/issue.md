# Pylint OOM (exit code -9) in GitHub Actions when processing large number of files.

### Bug description

## Problem
Pylint is failing with exit code -9 (Out Of Memory) in GitHub Actions when processing multiple files, even with `--files` flag for changed files only. This prevents CI from completing successfully.

## Current Setup
- Using pylint v3.2.5 in pre-commit hooks
- GitHub Actions workflow runs pre-commit on changed files only
- Exit code -9 indicates OOM (process killed by OS)
- Issue occurs even with ~130 changed files

## Attempts Made
1. Added `--jobs=1` to force single-threaded processing
2. Added `--limit-inference-results=1000` and `--score=no` to reduce memory usage

## Requirements
Need a solution that:
- Allows pylint to run successfully in CI environment
- Processes all changed files in PRs
- Doesn't require manually excluding directories
- Works within GitHub Actions resource limits

### Configuration


.pre-commit-config.yml:
```yml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.1
    hooks:
      - id: mypy
        args: [--namespace-packages, --ignore-missing-imports, --install-types, --non-interactive]
        exclude: (?x)(setup\.py$)

  - repo: https://github.com/PyCQA/flake8
    rev: 7.1.0
    hooks:
      - id: flake8
        exclude: (?x)(setup\.py$)

  - repo: https://github.com/pylint-dev/pylint
    rev: v3.2.5
    hooks:
      - id: pylint
        args: [--disable=import-error, --verbose, --jobs=1, --limit-inference-results=500, --score=no]
        exclude: (?x)(setup\.py$)
```

.github/workflows/lint.yml: 
```yml
- name: Identify changed files
  run: |
    changed_files=$(git diff --diff-filter=AM --name-only origin/${{ github.event.pull_request.base.ref }} HEAD | grep -E '\.(py|yaml)$' | tr '\r\n' ' ' || true)
    echo "changed_files=$changed_files" >> $GITHUB_ENV

- name: Run pre-commit
  uses: sentinel-one/devops-github-actions/local-repos/pre-commit/action@master
  with:
    extra_args: "--files ${{ env.changed_files }}"
```

### Command used

```shell
pre-commit run --files <changed_files_list>

pre-commit run --all-files
```

### Pylint output

```python
pylint...................................................................Failed
- hook id: pylint
- exit code: -9
```

### Expected behavior

 pylint: Should analyze files without OOM (exit code -9)
 CI: Should complete successfully on PRs with changed files
 Memory: Pylint should stay within GitHub Actions runner limits (~7GB RAM)
 Performance: Analysis should complete within reasonable time (<10 minutes)


### Pylint version

```shell
v3.2.5
```

### OS / Environment

Github

### Additional dependencies

```python

```
