# Browser Automation Agent (Agentic AI)

A general-purpose AI agent that takes a plain-English instruction and autonomously operates a real webpage to complete it — navigating, reading content, and taking actions (clicking, typing, extracting data) without hardcoded, task-specific scripts.

## Overview

Instead of pre-programming every click for a specific task, this agent:
1. **Perceives** the current state of a webpage (via DOM or screenshot)
2. **Reasons** about what action to take next, using an LLM
3. **Acts** on the page (click, type, scroll) via browser automation
4. **Observes** the result and repeats until the goal is complete

This mirrors the architecture behind tools like browser-use, OpenAI's Operator, and Anthropic's computer-use — scoped down to a project that can be realistically built, tested, and evaluated.

## Project Goals

- Build a working agent that completes simple, well-defined tasks (search, filter, extract, form-fill) on standard test websites
- Compare **DOM-based perception** vs. **vision-based perception** (screenshots) for reliability
- Evaluate performance using a structured benchmark of tasks, not just a single demo
- Produce findings on where and why the agent fails — not just where it succeeds

## Architecture

```
Goal (plain-English text)
      ↓
Perceive → extract page elements (DOM) or capture screenshot (vision)
      ↓
Reason  → LLM decides the next single action (structured JSON output)
      ↓
Act     → Playwright executes the action (click / type / scroll)
      ↓
Observe → capture new page state, check if goal is complete
      ↓
   (repeat until done or step limit reached)
```

## Tech Stack

| Component | Tool | Notes |
|---|---|---|
| Browser control | [Playwright](https://playwright.dev) (Python) | Handles navigation, clicks, typing, screenshots, DOM extraction |
| Reasoning | LLM API (Claude / GPT-4o / Gemini) via [Ollama](https://ollama.com) for local testing | Needs structured/function-calling output support |
| Orchestration | Custom Python loop (or [LangGraph](https://langchain-ai.github.io/langgraph/)) | Manages the reason → act → observe cycle |
| Vision perception | OpenCV + vision-capable LLM | Screenshot-based alternative to DOM reading |
| Evaluation | Pandas + JSON logs | Tracks success/failure per task across runs |

## Setup

```bash
# Install dependencies
pip install playwright pandas
playwright install

# (Optional) local LLM for free/offline testing
# Install Ollama from https://ollama.com, then:
ollama pull llama3
```

Set your LLM API key as an environment variable (if using an API provider instead of local):
```bash
export ANTHROPIC_API_KEY="your-key-here"
# or OPENAI_API_KEY / GOOGLE_API_KEY depending on provider
```

## Project Structure (proposed)

```
├── perception/         # DOM extraction + screenshot capture
├── reasoning/           # LLM prompt design + decision parsing
├── action/              # Playwright execution functions
├── agent_loop.py        # Main reason → act → observe loop
├── eval/
│   ├── tasks.json        # Benchmark task suite
│   └── run_eval.py       # Runs agent against tasks, logs results
├── logs/                # Per-run JSON logs (goal, state, action, outcome)
└── README.md
```

## Roadmap (Solo, ~8–10 weeks)

| Week | Milestone |
|---|---|
| 1 | Playwright setup — open a page, execute manual hardcoded actions |
| 2 | Build DOM-based perception — extract page elements into a structured list |
| 3 | Add LLM reasoning step — element list + goal → structured JSON decision |
| 4 | Close the loop — reason → act → observe, repeating until goal is met or step limit reached |
| 5 | Error handling & robustness — invalid actions, slow loads, retries |
| 6 | Build evaluation task suite (8–10 tasks across a few sandbox sites), run DOM-based agent, log results |
| 7–8 | Add vision-based perception (screenshot + vision LLM / OpenCV), re-run evaluation, compare DOM vs. vision |
| 9 | (Optional stretch) Hybrid mode — DOM first, fall back to vision when DOM extraction fails |
| 10 | Write-up of findings + final demo polish |

## Evaluation Approach

Rather than a single demo task, the agent is tested against a fixed benchmark of tasks (increasing difficulty, across multiple sandbox sites), tracking:
- Success / failure rate per task
- Number of steps taken vs. optimal
- Failure mode (misread element, wrong action, infinite loop, etc.)
- DOM-based vs. vision-based perception comparison

Test sites used: [saucedemo.com](https://www.saucedemo.com), [the-internet.herokuapp.com](https://the-internet.herokuapp.com), and custom local HTML pages — chosen specifically to avoid CAPTCHA/anti-bot walls so results reflect agent capability, not evasion.

## Known Limitations / Scope Boundaries

- No CAPTCHA bypassing — agent pauses and hands off to a human if blocked
- No payment or account-login automation — scoped to search, extract, filter, and form-fill tasks only
- Full generality (any website, any task) is out of scope; the project targets standard, well-structured sites

## License

For academic/internship demonstration purposes.
