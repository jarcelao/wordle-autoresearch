#!/bin/bash
set -euo pipefail

# Wordle Agent Benchmark Script
# Runs evaluation in test mode with FRESH random words from API each time

# Configuration
AGENT="simple"
GAMES=50
OUTPUT_FILE="temp/result.json"

# Run the harness in test mode (API words fetched fresh each time)
# Suppress progress output, only capture metrics
uv run python harness.py \
    --agent "$AGENT" \
    --mode test \
    --games "$GAMES" \
    --output "$OUTPUT_FILE" \
    2>/dev/null

# Extract metrics from the JSON output
if [[ -f "$OUTPUT_FILE" ]]; then
    AVG_ATTEMPTS_ON_WIN=$(jq -r '.avg_attempts_on_win // 0' "$OUTPUT_FILE")
    WIN_RATE=$(jq -r '.win_rate // 0' "$OUTPUT_FILE")
    AVG_ATTEMPTS=$(jq -r '.avg_attempts // 0' "$OUTPUT_FILE")
    WINS=$(jq -r '.wins // 0' "$OUTPUT_FILE")
    TOTAL=$(jq -r '.total_games // 0' "$OUTPUT_FILE")
    
    # Output METRIC lines for autoresearch parsing
    echo "METRIC avg_attempts_on_win=$AVG_ATTEMPTS_ON_WIN"
    echo "METRIC win_rate=$WIN_RATE"
    echo "METRIC avg_attempts=$AVG_ATTEMPTS"
    echo "METRIC wins=$WINS"
    echo "METRIC total_games=$TOTAL"
else
    echo "METRIC avg_attempts_on_win=0"
    echo "METRIC win_rate=0"
    echo "METRIC avg_attempts=0"
    echo "METRIC wins=0"
    echo "METRIC total_games=0"
    exit 1
fi
