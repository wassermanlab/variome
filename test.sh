#!/usr/bin/env bash

set -u -o pipefail

POLL_SECONDS="${POLL_SECONDS:-1}"
ENABLE_NOTIFICATIONS="${ENABLE_NOTIFICATIONS:-1}"

VERBOSITY=0
BACKEND_FOCUS_TARGET=""
E2E_FOCUS_FILE=""
E2E_TIMEOUT_MS="20000"
TEST_SUITE="all"
USE_FAILFAST="1"

usage() {
  echo "Usage: $0 [-v|-vv|--verbose|--very-verbose] [-f MODULE.TEST_CLASS|FILE.spec.mjs] [-e TIMEOUT_MS] [-e2e|-unit] [-all]"
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -v|--verbose) VERBOSITY="$((VERBOSITY + 1))"; shift ;;
    -vv|--very-verbose) VERBOSITY="$((VERBOSITY + 2))"; shift ;;
    -f|--focus)
      [[ "$#" -ge 2 ]] || { echo "Error: $1 requires a test class or E2E spec file."; exit 1; }
      BACKEND_FOCUS_TARGET="$2"
      shift 2
      ;;
    -e|--e2e-timeout)
      [[ "$#" -ge 2 ]] || { echo "Error: $1 requires milliseconds."; exit 1; }
      E2E_TIMEOUT_MS="$2"
      shift 2
      ;;
    -e2e)
      [[ "$TEST_SUITE" == "all" ]] || { echo "Error: -e2e and -unit cannot be used together."; exit 1; }
      TEST_SUITE="e2e"
      shift
      ;;
    -unit)
      [[ "$TEST_SUITE" == "all" ]] || { echo "Error: -e2e and -unit cannot be used together."; exit 1; }
      TEST_SUITE="unit"
      shift
      ;;
    -all) USE_FAILFAST="0"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

[[ "$VERBOSITY" -le 2 ]] || VERBOSITY=2
[[ "$E2E_TIMEOUT_MS" =~ ^[1-9][0-9]*$ ]] || { echo "Error: E2E timeout must be a positive integer."; exit 1; }

if [[ -n "$BACKEND_FOCUS_TARGET" ]]; then
  if [[ "$BACKEND_FOCUS_TARGET" == *.mjs ]]; then
    E2E_FOCUS_FILE="$BACKEND_FOCUS_TARGET"
    BACKEND_FOCUS_TARGET=""
  elif [[ ! "$BACKEND_FOCUS_TARGET" =~ ^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$ ]]; then
    echo "Error: focus must be MODULE.TEST_CLASS or FILE.spec.mjs."
    exit 1
  fi
fi

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

notify_failure() {
  local suite="$1"
  local message="$2"

  [[ "$ENABLE_NOTIFICATIONS" == "1" ]] || return
  command -v osascript >/dev/null 2>&1 || return
  osascript -e "display notification \"${message}\" with title \"Variome tests\" subtitle \"${suite}\"" >/dev/null 2>&1 || true
}

run_suite() {
  local suite="$1"
  shift
  local start_ts end_ts elapsed exit_code quiet_log

  start_ts="$(date +%s)"
  echo "running ${suite}..."

  if [[ "$VERBOSITY" -eq 0 ]]; then
    quiet_log="$(mktemp)"
    "$@" >"$quiet_log" 2>&1
    exit_code=$?
    rm -f "$quiet_log"

    if [[ "$exit_code" -eq 0 ]]; then
      echo "${suite} OK"
      return 0
    fi

    echo "${suite} failed (exit ${exit_code})"
    notify_failure "$suite" "${suite} failed (exit ${exit_code})"
    return 1
  fi

  "$@"
  exit_code=$?
  end_ts="$(date +%s)"
  elapsed="$((end_ts - start_ts))"
  if [[ "$exit_code" -eq 0 ]]; then
    echo "${suite} passed (${elapsed}s)"
    return 0
  fi

  echo "${suite} failed (${elapsed}s)"
  notify_failure "$suite" "${suite} failed (${elapsed}s)"
  return 1
}

run_all_suites() {
  local -a django_test_args=(test)
  [[ "$USE_FAILFAST" == "1" ]] && django_test_args+=(--failfast)

  if [[ -n "$E2E_FOCUS_FILE" ]]; then
    run_suite "e2e" env E2E_WEB_LOGS="$([[ "$VERBOSITY" -ge 2 ]] && echo 1 || echo 0)" E2E_TIMEOUT_MS="$E2E_TIMEOUT_MS" npm test --prefix test/e2e -- "$E2E_FOCUS_FILE" --timeout="$E2E_TIMEOUT_MS" --max-failures=1
    return
  fi

  if [[ -n "$BACKEND_FOCUS_TARGET" ]]; then
    run_suite "unit" env DB= uv run manage.py "${django_test_args[@]}" "test.backend.variome_backend.${BACKEND_FOCUS_TARGET}" --verbosity="$((VERBOSITY + 1))"
    return
  fi

  if [[ "$TEST_SUITE" != "e2e" ]]; then
    run_suite "unit" env DB= uv run manage.py "${django_test_args[@]}" test.backend.variome_backend --verbosity="$((VERBOSITY + 1))" || return 1
  fi
  if [[ "$TEST_SUITE" != "unit" ]]; then
    run_suite "e2e" env E2E_WEB_LOGS="$([[ "$VERBOSITY" -ge 2 ]] && echo 1 || echo 0)" E2E_TIMEOUT_MS="$E2E_TIMEOUT_MS" npm test --prefix test/e2e -- --timeout="$E2E_TIMEOUT_MS" --max-failures=1 || return 1
  fi
}

compute_signature() {
  find "$@" \
    -type d \( -name .git -o -name .venv -o -name .vite -o -name node_modules -o -name __pycache__ -o -name test-results \) -prune -o \
    -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.mjs' -o -name '*.json' -o -name '*.toml' -o -name '*.sh' \) -print0 2>/dev/null \
    | xargs -0 stat -f '%m %N' 2>/dev/null \
    | shasum \
    | awk '{print $1}'
}

watch_all_suites() {
  local last_signature current_signature
  last_signature="$(compute_signature "$@")"

  while true; do
    current_signature="$(compute_signature "$@")"
    if [[ "$current_signature" != "$last_signature" ]]; then
      last_signature="$current_signature"
      run_all_suites || true
    fi
    sleep "$POLL_SECONDS"
  done
}

initial_failed=0
run_all_suites || initial_failed=1

if [[ "$VERBOSITY" -eq 0 ]]; then
  [[ "$initial_failed" -eq 0 ]] && echo "✅" || echo "❌"
fi

[[ -t 0 ]] || exit "$initial_failed"

watch_all_suites "$PROJECT_ROOT/variome_backend" "$PROJECT_ROOT/frontend" "$PROJECT_ROOT/test" "$PROJECT_ROOT/test.sh" &
ALL_WATCH_PID=$!

listen_for_enter() {
  local line
  echo "waiting... [ enter: rerun all suites ]"
  while IFS= read -r line; do
    [[ -z "$line" ]] && run_all_suites || true
  done < /dev/tty
}

listen_for_enter &
MANUAL_TRIGGER_PID=$!

cleanup() {
  kill "$MANUAL_TRIGGER_PID" >/dev/null 2>&1 || true
  kill "$ALL_WATCH_PID" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM
wait
