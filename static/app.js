// Agent Web Dashboard JavaScript Controller

document.addEventListener("DOMContentLoaded", () => {
    // DOM Element References
    const wsStatusText = document.getElementById("ws-status-text");
    const wsStatusDot = document.querySelector("#ws-status .status-dot");
    const urlInput = document.getElementById("url-input");
    const goalInput = document.getElementById("goal-input");
    const launchBtn = document.getElementById("launch-btn");
    const feedContainer = document.getElementById("feed-container");
    const emptyFeed = document.getElementById("empty-feed");
    const agentStateText = document.getElementById("agent-state-text");
    const agentStateBadge = document.getElementById("agent-state");
    const captchaAlert = document.getElementById("captcha-alert");
    
    // Perception Radio Cards Logic
    const radioCards = document.querySelectorAll(".radio-card");
    radioCards.forEach(card => {
        card.addEventListener("click", () => {
            radioCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            card.querySelector("input").checked = true;
        });
    });
    
    // Quick Prompt Templates Chips
    const chips = document.querySelectorAll(".chip");
    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            const url = chip.getAttribute("data-url");
            const goal = chip.getAttribute("data-goal");
            if (url) urlInput.value = url;
            if (goal) goalInput.value = goal;
        });
    });

    // WebSocket Connection
    let ws = null;

    function connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            wsStatusText.textContent = "Connected";
            wsStatusDot.classList.remove("disconnected");
            wsStatusDot.classList.add("connected");
        };

        ws.onclose = () => {
            wsStatusText.textContent = "Disconnected";
            wsStatusDot.classList.remove("connected");
            wsStatusDot.classList.add("disconnected");
            // Reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket Error:", err);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleServerMessage(data);
        };
    }

    connectWebSocket();

    // Launch Agent Action
    launchBtn.addEventListener("click", () => {
        const url = urlInput.value.trim();
        const goal = goalInput.value.trim();
        const selectedMode = document.querySelector('input[name="mode"]:checked').value;

        if (!url || !goal) {
            alert("Please enter both a Target URL and a Goal!");
            return;
        }

        // Reset UI State
        if (emptyFeed) emptyFeed.style.display = "none";
        feedContainer.innerHTML = "";
        captchaAlert.classList.add("hidden");
        
        setAgentState("Running", "running");
        launchBtn.disabled = true;

        // Send start command to WebSocket server
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                action: "start",
                url: url,
                goal: goal,
                mode: selectedMode,
                max_steps: 10
            }));
        } else {
            alert("Server connection lost. Trying to reconnect...");
        }
    });

    // Handle WebSocket Messages from Python Server
    function handleServerMessage(data) {
        if (data.type === "step_update") {
            appendStepCard(data);
        } else if (data.type === "captcha_detected") {
            captchaAlert.classList.remove("hidden");
            setAgentState("Waiting for Human", "warning");
        } else if (data.type === "completed") {
            launchBtn.disabled = false;
            captchaAlert.classList.add("hidden");
            
            if (data.outcome && data.outcome.success) {
                setAgentState("Goal Accomplished", "ready");
            } else {
                setAgentState("Finished", "ready");
            }
        }
    }

    // Dynamic Step Card Renderer
    function appendStepCard(stepData) {
        const card = document.createElement("div");
        card.className = "step-card";

        let actionDetails = `Action: <strong>${stepData.action_type.toUpperCase()}</strong>`;
        if (stepData.element_id) actionDetails += ` on Element <strong>#${stepData.element_id}</strong>`;
        if (stepData.text_to_type) actionDetails += ` ("${stepData.text_to_type}")`;

        card.innerHTML = `
            <div class="step-header">
                <span class="step-number">STEP ${stepData.step}</span>
                <span class="mode-tag">${stepData.mode.toUpperCase()}</span>
            </div>
            <div class="thought-box">
                <em>"${stepData.thought || 'Analyzing next step...'}"</em>
            </div>
            <div class="action-pill">
                ${actionDetails}
            </div>
        `;

        feedContainer.appendChild(card);
        feedContainer.scrollTop = feedContainer.scrollHeight;
    }

    function setAgentState(text, stateClass) {
        agentStateText.textContent = text;
        agentStateBadge.className = `agent-state-badge ${stateClass}`;
    }
});
