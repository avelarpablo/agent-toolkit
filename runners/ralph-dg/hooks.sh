#!/bin/bash
# hooks.sh — discount-genie-core routing overrides for ralph
#
# Sourced by ralph when RALPH_HOOKS points here. Defines multi-repo routing
# for the DG workspace where issues live on the core repo but code lives in
# nested sub-repos (discount-genie-backend, discount-genie).

BACKEND_DIR="$REPO_ROOT/discount-genie-backend"
FRONTEND_DIR="$REPO_ROOT/discount-genie"

_route_issue() {
  local title="$1"
  case "$title" in
    BE:*|be:*) echo "backend" ;;
    FE:*|fe:*) echo "frontend" ;;
    PRD:*|prd:*) echo "prd" ;;
    *) echo "unknown" ;;
  esac
}

_repo_dir() {
  case "$1" in
    backend)  echo "$BACKEND_DIR" ;;
    frontend) echo "$FRONTEND_DIR" ;;
    *) echo "" ;;
  esac
}

_repo_name() {
  case "$1" in
    backend)  echo "discount-genie-backend" ;;
    frontend) echo "discount-genie" ;;
    *) echo "" ;;
  esac
}

_ralph_init_extra() {
  for dir in "$BACKEND_DIR" "$FRONTEND_DIR"; do
    name=$(basename "$dir")
    [[ ! -d "$dir/.git" ]] && { warn "$name not found at $dir — run scripts/clone-repos.sh first"; continue; }
    log "✓ $name exists"

    if [[ -n "${FEATURE_BRANCH:-}" ]]; then
      current=$(git -C "$dir" branch --show-current)
      if git -C "$dir" show-ref --verify --quiet "refs/heads/$FEATURE_BRANCH" 2>/dev/null; then
        log "✓ $name: '$FEATURE_BRANCH' already exists"
      elif _is_protected "$current"; then
        log "Creating '$FEATURE_BRANCH' from 'develop' in $name"
        git -C "$dir" stash --include-untracked 2>/dev/null || true
        git -C "$dir" checkout develop 2>/dev/null || { warn "Cannot checkout develop in $name"; continue; }
        git -C "$dir" pull --ff-only origin develop 2>/dev/null || true
        git -C "$dir" checkout -b "$FEATURE_BRANCH"
      else
        log "✓ $name: already on non-protected branch '$current'"
      fi
    fi
  done
}

_ralph_check_extra() {
  for dir in "$BACKEND_DIR" "$FRONTEND_DIR"; do
    name=$(basename "$dir")
    if [[ -d "$dir/.git" ]]; then
      branch=$(git -C "$dir" branch --show-current)
      status=$(git -C "$dir" status --short | wc -l | tr -d ' ')
      if _is_protected "$branch"; then
        printf "  %-30s ✗  on protected branch '%s' (%s uncommitted)\n" "$name" "$branch" "$status"
      else
        printf "  %-30s ✓  branch: %s (%s uncommitted)\n" "$name" "$branch" "$status"
      fi
    else
      printf "  %-30s ✗  NOT FOUND\n" "$name"
    fi
  done
}
