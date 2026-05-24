#!/usr/bin/env bash

set -euo pipefail

poetry run black --check src
