# Autoresearch: Optimize Wordle Agent Performance

## Objective
Optimize the Wordle agent to achieve the lowest average number of attempts to win games. The agent must use the feedback system (correct position, present letter, absent letter) to intelligently narrow down the search space and guess the target word in as few attempts as possible.

## Metrics
- **Primary**: `avg_attempts_on_win` (attempts, lower is better) — average number of guesses needed when the agent successfully wins a game
- **Secondary**:
  - `win_rate` (percentage, higher is better) — percentage of games won within 6 attempts
  - `avg_attempts` (attempts, lower is better) — average attempts across all games (including losses counted as 6)

## How to Run
`./autoresearch.sh` — runs the harness in test mode and outputs `METRIC` lines for parsing.

## Files in Scope
- `agents/base.py` — Agent base class and GuessResult dataclass
- `agents/simple_agent.py` — Current best agent implementation (reference/starting point)
- `agents/random_agent.py` — Random baseline agent
- `harness.py` — Evaluation harness (can modify to add new agents to registry)
- `temp/` — Cache directory for API words and results

## Off Limits
- `wordle.py` — Core game logic, feedback system, and UI must not be modified

## Constraints
- **No new dependencies** — only use Python stdlib and existing packages (requests)
- **Test mode for experiments** — actual benchmark runs must use `test` mode (API words)
- **Train mode for validation** — can use `train` mode to quickly validate agent logic
- **Agent registry** — new agents must be registered in `AGENT_REGISTRY` in `harness.py`

## What's Been Tried

### Baseline: RandomAgent
- Randomly selects from a small word pool (10 words)
- No feedback utilization
- Poor performance expected

### Baseline: SimpleAgent
- Uses "crane" as starting word (common Wordle strategy)
- Filters remaining words based on feedback:
  - Correct: letter must be at exact position
  - Absent: letter not in word (basic implementation)
  - Present: minimal handling
- Word list of 25 common 5-letter words
- Room for improvement in filtering logic and word selection strategy

### Potential Optimization Areas
1. **Starting word optimization** — "crane" may not be optimal
2. **Present letter handling** — current implementation is weak
3. **Letter frequency analysis** — prioritize words with common letters
4. **Word entropy/scoring** — information theory approach
5. **Position constraint tracking** — more sophisticated filtering
