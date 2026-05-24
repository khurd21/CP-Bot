#!/usr/bin/env bash
set -euo pipefail

poetry run pylint src
