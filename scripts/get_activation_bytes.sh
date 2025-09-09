#!/usr/bin/env bash
set -euo pipefail

# This script helps retrieve Audible activation bytes using audible-activator.
# Prerequisites: Clone https://github.com/inAudible-NG/audible-activator first
# Set AUDIBLE_ACTIVATOR_DIR to point to your clone location
# Python env is created at ~/pyenv/audible-activator
# Requirements: git, python3, Firefox + geckodriver (brew install firefox geckodriver)
# Optional: set AUDIBLE_REGION to one of: us (default), uk, au, in, de, fr, jp

AUDIBLE_REGION="${AUDIBLE_REGION:-us}"
AUDIBLE_ACTIVATOR_DIR="${AUDIBLE_ACTIVATOR_DIR:-}"

signin_url_for_region() {
  case "$1" in
    us) echo "https://www.audible.com/signin" ;;
    uk) echo "https://www.audible.co.uk/signin" ;;
    au) echo "https://www.audible.com.au/signin" ;;
    in) echo "https://www.audible.in/signin" ;;
    de) echo "https://www.audible.de/signin" ;;
    fr) echo "https://www.audible.fr/signin" ;;
    jp) echo "https://www.audible.co.jp/signin" ;;
    *) echo "https://www.audible.com/signin" ;;
  esac
}

ENV_DIR="$HOME/pyenv/audible-activator"

command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }

if [ -z "${AUDIBLE_ACTIVATOR_DIR:-}" ]; then
  cat <<EOF
Error: AUDIBLE_ACTIVATOR_DIR is not set.

Please clone audible-activator first:
  git clone https://github.com/inAudible-NG/audible-activator.git
  export AUDIBLE_ACTIVATOR_DIR=\$(pwd)/audible-activator

Then run this script again.
EOF
  exit 1
fi

if [ ! -d "$AUDIBLE_ACTIVATOR_DIR" ]; then
  echo "AUDIBLE_ACTIVATOR_DIR does not exist: $AUDIBLE_ACTIVATOR_DIR" >&2
  exit 1
fi

echo "Using audible-activator at: $AUDIBLE_ACTIVATOR_DIR"

# Create central Python env per user preference
if [ ! -d "$ENV_DIR" ]; then
  echo "Creating Python env at $ENV_DIR"
  python3 -m venv "$ENV_DIR"
fi

# shellcheck disable=SC1090
source "$ENV_DIR/bin/activate"

pip install -U pip wheel setuptools >/dev/null
if [ -f "$AUDIBLE_ACTIVATOR_DIR/requirements.txt" ]; then
  pip install -r "$AUDIBLE_ACTIVATOR_DIR/requirements.txt" || true
fi
# Compatibility pins for old selenium usage (executable_path)
pip install "selenium<4" "urllib3<2" >/dev/null

LOGIN_URL="$(signin_url_for_region "$AUDIBLE_REGION")"

cat <<EOF

Dependencies note:
- Ensure Google Chrome and chromedriver are installed and compatible.
  macOS (Homebrew):
    brew install --cask google-chrome chromedriver

If a browser window does not open automatically, open this URL manually and sign in:
  $LOGIN_URL
(Region: $AUDIBLE_REGION — set AUDIBLE_REGION to override)

Running audible-activator now. Upon successful login, your activation bytes will be printed.
EOF

cd "$AUDIBLE_ACTIVATOR_DIR"
# Run in debug mode and honor locale/region setting
python audible-activator.py -d -f -l "$AUDIBLE_REGION" || true

echo "\nIf activation bytes were printed, copy them and set ACTIVATION_BYTES in your .env file."
