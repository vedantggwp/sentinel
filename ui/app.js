const API_BASE = window.location.port === "5500" ? "http://localhost:8000" : "";

const state = {
  activeTraceId: null,
};

const els = {
  serviceState: document.querySelector("#service-state"),
  scenarioList: document.querySelector("#scenario-list"),
  verdict: document.querySelector("#verdict"),
  rule: document.querySelector("#rule"),
  strip: document.querySelector("#decision-strip"),
  conversation: document.querySelector("#conversation"),
  creative: document.querySelector("#creative"),
  scores: document.querySelector("#score-grid"),
  claims: document.querySelector("#claims"),
  receipt: document.querySelector("#receipt"),
  traceId: document.querySelector("#trace-id"),
  signatureState: document.querySelector("#signature-state"),
  escalationPanel: document.querySelector("#escalation-panel"),
  escalationCopy: document.querySelector("#escalation-copy"),
};

async function boot() {
  await checkHealth();
  const scenarios = await fetchJson("/v1/scenarios");
  renderScenarios(scenarios.data.scenarios);
  if (scenarios.data.scenarios.length > 0) {
    runScenario(scenarios.data.scenarios[0]);
  }
}

async function checkHealth() {
  try {
    const health = await fetchJson("/health");
    els.serviceState.textContent = health.data.status;
  } catch {
    els.serviceState.textContent = "offline";
  }
}

function renderScenarios(scenarios) {
  els.scenarioList.replaceChildren(
    ...scenarios.map((scenario) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "scenario-button";
      button.innerHTML = `
        <strong>${labelFor(scenario.id)} · ${scenario.expected}</strong>
        <span>${scenario.ad_creative}</span>
      `;
      button.addEventListener("click", () => runScenario(scenario));
      return button;
    })
  );
}

async function runScenario(scenario) {
  els.conversation.textContent = scenario.conversation;
  els.creative.textContent = scenario.ad_creative;
  els.rule.textContent = "running";
  els.verdict.textContent = "RUN";

  const response = await fetchJson("/v1/analyze", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      ad_id: scenario.id,
      conversation: scenario.conversation,
      ad_creative: scenario.ad_creative,
      advertiser: scenario.advertiser,
    }),
  });

  renderDecision(response.data);
}

function renderDecision(data) {
  const {result, attestation, trace} = data;
  const verdict = result.verdict.toLowerCase();
  state.activeTraceId = trace.trace_id;

  els.strip.className = `decision-strip ${verdict}`;
  els.verdict.textContent = result.verdict;
  els.rule.textContent = result.rule_fired;
  els.traceId.textContent = trace.trace_id.slice(0, 8);
  els.signatureState.textContent = attestation.signature ? "signed" : "unsigned";

  renderScores(result.scores);
  renderClaims(result.claims);
  els.receipt.textContent = JSON.stringify({
    ad_id: attestation.ad_id,
    verdict: attestation.verdict,
    ad_hash: attestation.ad_hash,
    issued_at: attestation.issued_at,
    signature: attestation.signature,
    public_key: attestation.public_key,
    rule_fired: result.rule_fired,
  }, null, 2);

  const needsReview = result.verdict === "ESCALATE";
  els.escalationPanel.hidden = !needsReview;
  els.escalationPanel.style.display = needsReview ? "" : "none";
  els.escalationCopy.textContent = result.reason;
}

function renderScores(scores) {
  els.scores.replaceChildren(
    ...Object.entries(scores).map(([name, value]) => {
      const item = document.createElement("div");
      item.className = "score-item";
      item.innerHTML = `
        <div class="score-name">${name.replaceAll("_", " ")}</div>
        <span class="score-value ${scoreClass(value)}">${Number(value).toFixed(1)}</span>
      `;
      return item;
    })
  );
}

function renderClaims(claims) {
  if (claims.length === 0) {
    els.claims.innerHTML = `<div class="claim"><span>No extracted claims</span><span class="claim-state mid">none</span></div>`;
    return;
  }

  els.claims.replaceChildren(
    ...claims.map((claim) => {
      const item = document.createElement("div");
      const status = claim.verified === true ? "verified" : claim.verified === false ? "false" : "unchecked";
      item.className = "claim";
      item.innerHTML = `
        <div>
          <strong>${claim.text}</strong>
          <small>${claim.type} · ${claim.actual_value || "no fixture value"} · ${claim.source_url || "no source"}</small>
        </div>
        <span class="claim-state ${claimClass(claim.verified)}">${status}</span>
      `;
      return item;
    })
  );
}

async function submitReview(decision) {
  if (!state.activeTraceId) {
    return;
  }
  const response = await fetchJson("/v1/escalations", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      trace_id: state.activeTraceId,
      decision,
      reviewer: "demo",
    }),
  });
  els.escalationCopy.textContent = `${response.data.decision} recorded by ${response.data.reviewer}.`;
}

async function fetchJson(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  const payload = await response.json();
  if (!payload.success) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

function labelFor(id) {
  return id.split("_").map((part) => part[0].toUpperCase() + part.slice(1)).join(" ");
}

function scoreClass(value) {
  if (value >= 4) return "good";
  if (value >= 3) return "mid";
  return "bad";
}

function claimClass(value) {
  if (value === true) return "good";
  if (value === false) return "bad";
  return "mid";
}

document.querySelectorAll("[data-review]").forEach((button) => {
  button.addEventListener("click", () => submitReview(button.dataset.review));
});

boot();
