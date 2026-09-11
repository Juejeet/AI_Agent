# Daily Internship Logbook

**Project Title:** Browser Automation Agent (Agentic AI)
**Intern Name:** ___________________________
**Institution:** Dibrugarh University
**Internship Duration:** 10th July 2026 to 9th August 2026

---

**Day 1 | Date: 10th July 2026 | Friday**

Joined the internship program. Received an overview of the project requirements and objectives from the supervisor. Studied the concept of agentic AI systems and how they differ from traditional automation scripts. Understood the core idea behind the project — building an AI agent that can autonomously operate a web browser using plain English instructions.

---

**Day 2 | Date: 11th July 2026 | Saturday**

Researched existing tools and systems similar to the project, including browser-use, OpenAI Operator, and Anthropic Computer-Use. Studied their architecture to understand how LLMs are used in combination with browser automation. Took notes on the Perceive, Reason, Act, and Observe loop that forms the foundation of such systems.

---

**12th July 2026 | Sunday — Holiday**

---

**Day 3 | Date: 13th July 2026 | Monday**

Studied the official Playwright documentation. Understood how browser automation works using Python including navigating pages, clicking elements, typing text, and taking screenshots. Explored the structure of a web page DOM and how interactive elements can be identified and targeted programmatically.

---

**Day 4 | Date: 14th July 2026 | Tuesday**

Studied how Large Language Models can be used for structured decision making. Explored the Google Gemini API and its ability to return responses in strict JSON format. Understood how this structured output can be used to make the agent's decisions reliable and directly executable by a program.

---

**Day 5 | Date: 15th July 2026 | Wednesday**

Planned the complete project architecture. Decided on the four core modules — Perception, Reasoning, Action, and the Agent Loop. Sketched out the folder structure with separate directories for perception, reasoning, action, evaluation, logs, and static files. Outlined the responsibilities of each module.

---

**Day 6 | Date: 16th July 2026 | Thursday**

Set up the Python virtual environment to isolate all project dependencies. Installed the initial required libraries including Playwright, Pandas, and Pytest. Ran Playwright's browser installation command to download the Chromium browser. Verified the setup by opening a browser window through a basic Python script.

---

**Day 7 | Date: 17th July 2026 | Friday**

Scaffolded the full project folder structure with all necessary directories and __init__.py files. Created the requirements.txt file listing all dependencies. Built action/browser_setup.py for the first Playwright browser test. Built perception/dom_extractor.py which injects JavaScript into a live webpage to extract all visible interactive elements, assigns each a unique agent-id, draws red outline highlights and numbered labels on the screen, and returns a clean text summary for the LLM. Created tests/test_perception.py and conftest.py to verify DOM extraction works correctly on any website.

---

**Day 8 | Date: 18th July 2026 | Saturday**

Updated test_perception.py to use generic dynamic assertions so the tests pass on any website instead of being hardcoded to a specific page. Fixed a UnicodeEncodeError that occurred when printing special characters on the Windows terminal during testing.

---

**19th July 2026 | Sunday — Holiday**

---

**Day 9 | Date: 20th July 2026 | Monday**

Added the google-genai library to requirements.txt and installed it. Built reasoning/llm_reasoner.py which sends the page information and the user goal to the Gemini API and forces it to return a structured JSON decision. Created tests/test_reasoning.py to verify that the LLM can reason correctly about a mock webpage. Fixed a 404 model error by switching to the correct available model gemini-1.5-flash. Built action/playwright_executor.py to physically translate LLM JSON decisions into real browser actions such as clicking and typing. Built agent_loop.py to orchestrate the complete Perception to Reasoning to Action loop. Fixed a critical bug where the agent was getting stuck in an infinite loop because it could not see what it had already typed into input fields. Solved this by updating dom_extractor.py to include the current live value of input fields in the DOM summary.

---

**Day 10 | Date: 21st July 2026 | Tuesday**

Implemented error handling across the action module. Modified playwright_executor.py to return detailed success or error strings instead of simple booleans, so the agent knows exactly what went wrong. Added short-term memory to the agent by feeding the history of past actions and their results back into every LLM prompt, allowing the agent to learn from its own mistakes. Replaced hardcoded time.sleep delays with Playwright's networkidle wait for more reliable page scanning. Added a new type_and_enter action type so the agent can press the Enter key after typing in search bars.

---

**Day 11 | Date: 22nd July 2026 | Wednesday**

Built the evaluation suite. Refactored agent_loop.py to return structured result data. Created eval/tasks.json containing 3 benchmark tasks covering SauceDemo login, Wikipedia search, and HerokuApp element interaction. Built eval/run_eval.py to automatically run all tasks in sequence and generate a Pandas report card, saving results as a timestamped CSV log file. Implemented CAPTCHA detection and Human-in-the-Loop handoff by adding a check_for_captcha() function in dom_extractor.py. Updated the agent loop to automatically pause and prompt the user in the terminal whenever a CAPTCHA or security challenge is detected.

---

**Day 12 | Date: 23rd July 2026 | Thursday**

Implemented vision based perception as an alternative to DOM reading. Built perception/vision_extractor.py to capture full-viewport screenshots of the browser. Built reasoning/vision_reasoner.py using the Gemini Multimodal Vision API, which analyzes the screenshot visually just as a human would. Updated agent_loop.py to support switching between DOM mode and Vision mode. Built eval/compare_eval.py to run side-by-side benchmark comparisons between both perception modes. Implemented the Hybrid Perception Engine by adding a hybrid mode to the agent loop that uses DOM by default but automatically switches to vision mode when DOM extraction returns empty results or when the agent encounters repeated consecutive errors. Documented all findings in eval/final_findings.md and completed the full development roadmap.

---

**Day 13 | Date: 24th July 2026 | Friday**

Fixed a Cloudflare CAPTCHA false-positive bug where already completed or hidden Cloudflare iframes were incorrectly triggering the CAPTCHA pause. Updated check_for_captcha() to check is_visible() instead of just count(). Expanded CAPTCHA detection to cover page title keywords, challenge-stage containers, cf-turnstile elements, and visible challenge text on the page. Added a premature exit guard in agent_loop.py to prevent the agent from declaring a task complete while a CAPTCHA is still active on screen.

---

**Day 14 | Date: 25th July 2026 | Saturday**

Ran the full benchmark evaluation across all 3 tasks in DOM, Vision, and Hybrid modes. Recorded results including success or failure, number of steps taken, and final URL reached for each task and each perception mode.

---

**26th July 2026 | Sunday — Holiday**

---

**Day 15 | Date: 27th July 2026 | Monday**

Analyzed the evaluation logs in detail. Compared step counts, success rates, and average speed across all three perception modes. Identified key trade-offs between DOM and Vision based approaches and documented the findings.

---

**Day 16 | Date: 28th July 2026 | Tuesday**

Studied FastAPI and WebSocket communication. Understood how WebSockets allow a server to push real-time updates to a connected browser client without the client needing to refresh or poll. Planned the design and structure of the web dashboard interface for the agent.

---

**Day 17 | Date: 29th July 2026 | Wednesday**

Added plain-English final answer extraction by updating the JSON schemas in llm_reasoner.py and vision_reasoner.py to include a final_answer field when the agent completes a task. Updated agent_loop.py to print and return this answer. Built the Interactive Web Dashboard using FastAPI and Uvicorn. Added fastapi, uvicorn, and websockets to requirements.txt. Updated agent_loop.py to support a step_callback function for real-time WebSocket streaming. Built server.py as the FastAPI backend. Built the frontend with static/index.html, static/style.css, and static/app.js featuring a glassmorphic dark-mode design with Prompt Template Chips, Perception Mode Selector, Live Action Step Cards, and CAPTCHA alert banners.

---

**Day 18 | Date: 30th July 2026 | Thursday**

Tested the web dashboard end to end. Opened the dashboard at http://127.0.0.1:8000, entered a task, selected a perception mode, and verified that live step updates were streaming correctly to the browser via WebSocket during agent execution.

---

**Day 19 | Date: 31st July 2026 | Friday**

Performed a final review of all project modules. Verified that all components including perception, reasoning, action execution, evaluation, and the web dashboard were working correctly together as a complete integrated system.

---

**Day 20 | Date: 1st August 2026 | Saturday**

Cleaned up the codebase by removing unused code and organizing the logs directory. Updated the README.md with complete documentation including project overview, architecture, setup instructions, and evaluation approach.

---

**2nd August 2026 | Sunday — Holiday**

---

**Day 21 | Date: 3rd August 2026 | Monday**

Began writing the project report. Completed the introduction, purpose and scope of the project, overview of developer responsibilities, requirement analysis, and hardware and software resources sections.

---

**Day 22 | Date: 4th August 2026 | Tuesday**

Continued the project report. Documented the tools and technologies used with descriptions. Wrote the step by step implementation of the project covering all modules from environment setup to final evaluation and findings.

---

**Day 23 | Date: 5th August 2026 | Wednesday**

Wrote the logbook and finalized the daily work entries. Reviewed all project modules one final time to ensure everything was complete, well documented, and properly organized for submission.

---

**Day 24 | Date: 6th August 2026 | Thursday**

Prepared the final project presentation slides summarizing the project objective, architecture, tools used, implementation steps, evaluation results, and key findings from the DOM versus Vision perception comparison.

---

**Day 25 | Date: 7th August 2026 | Friday**

Reviewed and refined the project presentation. Rehearsed the explanation of the agent's working process and the benchmark evaluation results. Made final corrections to the project report based on review feedback.

---

**8th August 2026 | Saturday — Holiday**

---

**9th August 2026 | Sunday — Holiday**

---

**Total Working Days: 25 Days**
**Total Duration: 10th July 2026 to 9th August 2026**
