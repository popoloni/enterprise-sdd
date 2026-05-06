#!/usr/bin/env bash
# jira-rest.sh — Token-safe Jira Cloud REST API helper
# Part of Enterprise SDD Wave 19 — jira-rest-ops skill
# Usage: source this file or call individual functions

set -euo pipefail

# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------
_jira_check_env() {
    local missing=()
    [[ -z "${JIRA_BASE_URL:-}" ]] && missing+=("JIRA_BASE_URL")
    [[ -z "${JIRA_API_TOKEN:-}" ]] && missing+=("JIRA_API_TOKEN")
    [[ -z "${JIRA_USER_EMAIL:-}" ]] && missing+=("JIRA_USER_EMAIL")

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: Missing required environment variables: ${missing[*]}" >&2
        echo "  Set JIRA_BASE_URL, JIRA_API_TOKEN, and JIRA_USER_EMAIL before running." >&2
        echo "  NEVER hardcode JIRA_API_TOKEN in scripts or source files." >&2
        exit 2
    fi
}

# Base64 encode credentials (without newline)
_jira_auth() {
    echo -n "${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}" | base64 | tr -d '\n'
}

# Internal helper — execute a request and return the response body
_jira_request() {
    local method="$1"
    local path="$2"
    local data="${3:-}"

    local url="${JIRA_BASE_URL}/rest/api/3${path}"
    local auth
    auth="$(_jira_auth)"

    local curl_args=(
        --silent
        --show-error
        --max-time 30
        --header "Authorization: Basic $auth"
        --header "Content-Type: application/json"
        --header "Accept: application/json"
        --request "$method"
        "$url"
    )

    if [[ -n "$data" ]]; then
        curl_args+=(--data "$data")
    fi

    curl "${curl_args[@]}"
}

# ---------------------------------------------------------------------------
# READ operations (no confirmation required)
# ---------------------------------------------------------------------------

# Get a single issue
# Usage: jira_get_issue PROJECT-123
jira_get_issue() {
    local key="$1"
    _jira_check_env
    echo "Fetching issue: $key"
    _jira_request GET "/issue/${key}"
}

# Search issues with JQL
# Usage: jira_search "project = MYPROJ AND status = 'In Progress'" [maxResults]
jira_search() {
    local jql="$1"
    local max_results="${2:-50}"
    _jira_check_env
    local encoded_jql
    encoded_jql=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$jql" 2>/dev/null || echo "$jql")
    echo "Searching: $jql (max: $max_results)"
    _jira_request GET "/search?jql=${encoded_jql}&maxResults=${max_results}"
}

# List all accessible projects
# Usage: jira_list_projects
jira_list_projects() {
    _jira_check_env
    echo "Listing projects..."
    _jira_request GET "/project"
}

# Get available transitions for an issue
# Usage: jira_get_transitions PROJECT-123
jira_get_transitions() {
    local key="$1"
    _jira_check_env
    echo "Fetching transitions for: $key"
    _jira_request GET "/issue/${key}/transitions"
}

# ---------------------------------------------------------------------------
# WRITE operations (require explicit confirmation)
# ---------------------------------------------------------------------------

# Create a new issue
# Usage: jira_create_issue '{"fields":{"project":{"key":"PROJ"},"summary":"...","issuetype":{"name":"Story"}}}'
jira_create_issue() {
    local payload="$1"
    _jira_check_env

    echo ""
    echo "=== WRITE OPERATION: Create Issue ==="
    echo "Payload: $payload"
    echo ""
    read -r -p "Confirm create issue? [yes/no]: " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi

    _jira_request POST "/issue" "$payload"
}

# Transition an issue to a new status
# Usage: jira_transition PROJECT-123 <transition-id>
jira_transition() {
    local key="$1"
    local transition_id="$2"
    _jira_check_env

    local payload="{\"transition\":{\"id\":\"${transition_id}\"}}"

    echo ""
    echo "=== WRITE OPERATION: Transition Issue ==="
    echo "Issue: $key  →  Transition ID: $transition_id"
    echo ""
    read -r -p "Confirm transition? [yes/no]: " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi

    _jira_request POST "/issue/${key}/transitions" "$payload"
}

# Add a comment to an issue
# Usage: jira_add_comment PROJECT-123 "Comment text"
jira_add_comment() {
    local key="$1"
    local comment_text="$2"
    _jira_check_env

    local payload="{\"body\":{\"type\":\"doc\",\"version\":1,\"content\":[{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"${comment_text}\"}]}]}}"

    echo ""
    echo "=== WRITE OPERATION: Add Comment ==="
    echo "Issue: $key"
    echo "Comment: $comment_text"
    echo ""
    read -r -p "Confirm add comment? [yes/no]: " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi

    _jira_request POST "/issue/${key}/comment" "$payload"
}

# ---------------------------------------------------------------------------
# Smoke verification
# ---------------------------------------------------------------------------

# Verify connectivity and authentication
# Usage: jira_smoke_check
jira_smoke_check() {
    _jira_check_env
    echo "Running Jira connectivity smoke check..."
    local response
    response=$(_jira_request GET "/myself")
    if echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK:', d.get('displayName', 'unknown'))" 2>/dev/null; then
        echo "Smoke check PASSED: authenticated successfully."
    else
        echo "Smoke check FAILED: unexpected response." >&2
        echo "$response" >&2
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Entry point (when run directly)
# ---------------------------------------------------------------------------
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    COMMAND="${1:-help}"
    case "$COMMAND" in
        get-issue)     jira_get_issue "${2:?usage: $0 get-issue <KEY>}" ;;
        search)        jira_search "${2:?usage: $0 search '<JQL>'}" "${3:-50}" ;;
        list-projects) jira_list_projects ;;
        get-transitions) jira_get_transitions "${2:?usage: $0 get-transitions <KEY>}" ;;
        create-issue)  jira_create_issue "${2:?usage: $0 create-issue '<JSON-payload>'}" ;;
        transition)    jira_transition "${2:?usage: $0 transition <KEY> <transition-id>"}" "${3:?}" ;;
        add-comment)   jira_add_comment "${2:?usage: $0 add-comment <KEY> '<text>'}" "${3:?}" ;;
        smoke-check)   jira_smoke_check ;;
        *)
            echo "Usage: $0 <command> [args]"
            echo ""
            echo "Read commands (no confirmation):"
            echo "  get-issue <KEY>            Fetch an issue by key"
            echo "  search '<JQL>' [maxResults] Search with JQL"
            echo "  list-projects              List accessible projects"
            echo "  get-transitions <KEY>      List available status transitions"
            echo ""
            echo "Write commands (require confirmation):"
            echo "  create-issue '<JSON>'      Create a new issue"
            echo "  transition <KEY> <id>      Transition issue status"
            echo "  add-comment <KEY> '<text>' Add a comment to an issue"
            echo ""
            echo "Utilities:"
            echo "  smoke-check               Verify connectivity and auth"
            echo ""
            echo "Required env vars: JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USER_EMAIL"
            ;;
    esac
fi
