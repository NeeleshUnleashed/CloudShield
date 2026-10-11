// CloudShield Frontend Application Logic with Human-in-the-Loop & RBAC

const PRESETS = {
  cyclone: {
    name: "Severe Cyclone Veronica",
    type: "CYCLONE",
    region: "Pilbara Coastal Region",
    affected: 22000,
    displaced: 8500,
    hazard: 0.90,
    vuln: 0.75,
    coping: 0.35,
    infra: 0.80
  },
  quake: {
    name: "Magnitude 7.2 Fault Rupture",
    type: "EARTHQUAKE",
    region: "Central Metropolitan Basin",
    affected: 35000,
    displaced: 15000,
    hazard: 0.95,
    vuln: 0.80,
    coping: 0.30,
    infra: 0.90
  },
  flood: {
    name: "Major River Basin Flash Flood",
    type: "FLOOD",
    region: "Northern Delta Plains",
    affected: 14000,
    displaced: 4200,
    hazard: 0.70,
    vuln: 0.60,
    coping: 0.50,
    infra: 0.60
  },
  wildfire: {
    name: "Extreme Forest Firestorm",
    type: "WILDFIRE",
    region: "East Gippsland Escarpment",
    affected: 7500,
    displaced: 2400,
    hazard: 0.85,
    vuln: 0.50,
    coping: 0.60,
    infra: 0.50
  }
};

let currentIncidentId = null;

function getActiveRole() {
  const sel = document.getElementById("roleSelector");
  return sel ? sel.value : "LOGISTICS_DIRECTOR";
}

document.addEventListener("DOMContentLoaded", () => {
  setupSliderSync();
  setupEventListeners();
  loadInventory();
  loadHistory();
  checkHealth();
});

function setupSliderSync() {
  const sliders = [
    { id: "hazard", label: "hazardVal" },
    { id: "vulnerability", label: "vulnVal" },
    { id: "coping", label: "copingVal" },
    { id: "infra", label: "infraVal" }
  ];
  sliders.forEach(s => {
    const input = document.getElementById(s.id);
    const label = document.getElementById(s.label);
    input.addEventListener("input", () => {
      label.textContent = parseFloat(input.value).toFixed(2);
    });
  });
}

function setupEventListeners() {
  document.getElementById("btnProposeWorkflow").addEventListener("click", handleProposeWorkflow);
  document.getElementById("disasterForm").addEventListener("submit", handleFastAutoApprove);
  document.getElementById("btnApproveDispatch").addEventListener("click", handleApproveDispatch);
  document.getElementById("btnRejectDispatch").addEventListener("click", handleRejectDispatch);
  document.getElementById("btnResetInv").addEventListener("click", handleResetInventory);
}

function loadPreset(key) {
  const p = PRESETS[key];
  if (!p) return;
  document.getElementById("incidentName").value = p.name;
  document.getElementById("disasterType").value = p.type;
  document.getElementById("region").value = p.region;
  document.getElementById("affectedPop").value = p.affected;
  document.getElementById("displacedPop").value = p.displaced;
  
  document.getElementById("hazard").value = p.hazard;
  document.getElementById("hazardVal").textContent = p.hazard.toFixed(2);
  
  document.getElementById("vulnerability").value = p.vuln;
  document.getElementById("vulnVal").textContent = p.vuln.toFixed(2);
  
  document.getElementById("coping").value = p.coping;
  document.getElementById("copingVal").textContent = p.coping.toFixed(2);
  
  document.getElementById("infra").value = p.infra;
  document.getElementById("infraVal").textContent = p.infra.toFixed(2);
}
window.loadPreset = loadPreset;

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    document.getElementById("awsModeVal").textContent = data.aws_mode || "mock";
  } catch (err) {
    console.error("Health check error:", err);
  }
}

async function loadInventory() {
  const tbody = document.getElementById("inventoryBody");
  try {
    const res = await fetch("/api/inventory");
    const data = await res.json();
    tbody.innerHTML = "";
    
    if (!data.stock || data.stock.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">No inventory records found.</td></tr>`;
      return;
    }
    
    data.stock.forEach(item => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${item.warehouse_id}</code></td>
        <td><strong>${item.warehouse_name}</strong></td>
        <td>${item.location}</td>
        <td><span class="badge badge-info">${item.category}</span></td>
        <td>${item.item_name}</td>
        <td><strong style="color: ${item.quantity_available < 500 ? '#ef4444' : '#10b981'}">${item.quantity_available.toLocaleString()}</strong></td>
        <td>${item.unit}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">Error loading inventory data.</td></tr>`;
    console.error(err);
  }
}

async function loadHistory() {
  const tbody = document.getElementById("historyBody");
  try {
    const res = await fetch("/api/disaster/history");
    const data = await res.json();
    tbody.innerHTML = "";
    
    if (!data || data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" class="empty-cell">No incident audit logs recorded yet.</td></tr>`;
      return;
    }
    
    data.forEach(inc => {
      const statusClass = inc.status === "APPROVED_DISPATCHED" ? "badge-success" : (inc.status === "REJECTED" ? "badge-danger" : "badge-warning");
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${inc.incident_id}</code></td>
        <td><strong>${inc.incident_name}</strong></td>
        <td>${inc.region}</td>
        <td><span class="badge badge-info">${inc.disaster_type}</span></td>
        <td><strong>${inc.dpri_score.toFixed(4)}</strong></td>
        <td><span class="badge badge-${inc.risk_level.toLowerCase()}">${inc.risk_level}</span></td>
        <td><span class="badge ${statusClass}">${inc.status}</span></td>
        <td><small>${inc.created_by_role || '--'}</small></td>
        <td><small>${inc.approved_by_role || '--'}</small></td>
        <td><small>${inc.created_at || '--'}</small></td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty-cell">Error loading audit history.</td></tr>`;
    console.error(err);
  }
}

function getDisasterPayload() {
  return {
    incident_name: document.getElementById("incidentName").value,
    disaster_type: document.getElementById("disasterType").value,
    region: document.getElementById("region").value,
    affected_population: parseInt(document.getElementById("affectedPop").value, 10),
    displaced_population: parseInt(document.getElementById("displacedPop").value, 10),
    hazard_intensity: parseFloat(document.getElementById("hazard").value),
    vulnerability_score: parseFloat(document.getElementById("vulnerability").value),
    coping_capacity: parseFloat(document.getElementById("coping").value),
    infrastructure_damage: parseFloat(document.getElementById("infra").value)
  };
}

// Stage 1: Propose Workflow (Zero inventory deduction)
async function handleProposeWorkflow() {
  const btn = document.getElementById("btnProposeWorkflow");
  btn.disabled = true;
  btn.textContent = "⏳ Calculating Proposal...";

  const payload = getDisasterPayload();
  const role = getActiveRole();

  try {
    const res = await fetch("/api/disaster/propose", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": role
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Proposal generation failed");
    }

    const data = await res.json();
    currentIncidentId = data.incident_id;
    renderProposalResults(data);
    await loadHistory();
    // Do NOT reload inventory because 0 stock was deducted!
  } catch (err) {
    alert("Proposal Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "📝 1. Submit Allocation Proposal (Human-in-the-Loop)";
  }
}

// Stage 2: Authorize Dispatch
async function handleApproveDispatch() {
  if (!currentIncidentId) {
    alert("No active proposal to approve.");
    return;
  }
  const btn = document.getElementById("btnApproveDispatch");
  btn.disabled = true;
  btn.textContent = "⏳ Authorizing & Dispatching...";

  const role = getActiveRole();

  try {
    const res = await fetch(`/api/disaster/approve/${currentIncidentId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": role
      },
      body: JSON.stringify({ notes: `Approved via UI by ${role}` })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Approval authorization failed");
    }

    const data = await res.json();
    renderApprovalSuccess(data);
    await loadInventory(); // Stock is now decremented!
    await loadHistory();
  } catch (err) {
    alert("Authorization Gate Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "✅ Authorize & Dispatch (Logistics Director)";
  }
}

// Stage 2b: Reject Proposal
async function handleRejectDispatch() {
  if (!currentIncidentId) {
    alert("No active proposal to reject.");
    return;
  }
  const btn = document.getElementById("btnRejectDispatch");
  btn.disabled = true;
  btn.textContent = "⏳ Rejecting...";

  const role = getActiveRole();

  try {
    const res = await fetch(`/api/disaster/reject/${currentIncidentId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Role": role
      },
      body: JSON.stringify({ reason: `Rejected via UI by ${role}` })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Rejection failed");
    }

    const data = await res.json();
    renderRejectionSuccess(data);
    await loadHistory();
  } catch (err) {
    alert("Rejection Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "❌ Reject Proposal";
  }
}

// Single-Click Demo: Fast Auto-Approve
async function handleFastAutoApprove(e) {
  e.preventDefault();
  const btn = document.getElementById("btnExecuteWorkflow");
  btn.disabled = true;
  btn.textContent = "⏳ Calculating & Dispatching...";

  const payload = getDisasterPayload();

  try {
    const res = await fetch("/api/disaster/workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Workflow execution failed");
    }

    const data = await res.json();
    currentIncidentId = data.execution_id;
    renderFastAutoApproveResults(data);
    await loadInventory();
    await loadHistory();
  } catch (err) {
    alert("Workflow Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "⚡ Fast Auto-Approve (Single-Click Demo)";
  }
}

async function handleResetInventory() {
  try {
    const btn = document.getElementById("btnResetInv");
    btn.disabled = true;
    btn.textContent = "Resetting...";
    const res = await fetch("/api/inventory/reset", {
      method: "POST",
      headers: { "X-User-Role": getActiveRole() }
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Reset failed");
    }
    await loadInventory();
    await loadHistory();
    btn.textContent = "🔄 Reset Inventory";
    btn.disabled = false;
  } catch (err) {
    alert("Inventory Reset Error: " + err.message);
    document.getElementById("btnResetInv").disabled = false;
    document.getElementById("btnResetInv").textContent = "🔄 Reset Inventory";
  }
}

function renderProposalResults(prop) {
  // Gate Status
  document.getElementById("activeIncId").textContent = prop.incident_id;
  const statusBadge = document.getElementById("proposalStatusBadge");
  statusBadge.textContent = "PENDING APPROVAL";
  statusBadge.className = "badge badge-warning";
  
  document.getElementById("createdRoleBadge").textContent = prop.created_by_role;
  document.getElementById("approvedRoleBadge").textContent = "AWAITING AUTHORIZATION";
  document.getElementById("approvalActionCluster").style.display = "flex";

  // DPRI
  renderDpriComponents(prop.dpri_result);

  // Shortages & Dispatch Plan
  renderShortagesAndPlan(prop.allocation_plan);

  // SNS Broadcast shows Pending
  document.getElementById("snsTopic").textContent = "arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts";
  document.getElementById("snsMsgId").textContent = "PENDING_AUTHORIZATION";
  document.getElementById("snsTime").textContent = "Awaiting Director Approval";
  document.getElementById("snsBodyText").textContent = "NOTICE: Proposed dispatch allocation is pending authorization from LOGISTICS_DIRECTOR. Zero inventory deducted.";
}

function renderApprovalSuccess(appr) {
  const statusBadge = document.getElementById("proposalStatusBadge");
  statusBadge.textContent = "APPROVED & DISPATCHED";
  statusBadge.className = "badge badge-success";
  
  document.getElementById("approvedRoleBadge").textContent = appr.approved_by_role;
  document.getElementById("approvedRoleBadge").className = "badge badge-success";
  document.getElementById("approvalActionCluster").style.display = "none";

  // SNS Broadcast
  const sns = appr.sns_alert;
  document.getElementById("snsTopic").textContent = sns.topic_arn;
  document.getElementById("snsMsgId").textContent = sns.message_id;
  document.getElementById("snsTime").textContent = sns.timestamp;
  document.getElementById("snsBodyText").textContent = sns.message;
}

function renderRejectionSuccess(rej) {
  const statusBadge = document.getElementById("proposalStatusBadge");
  statusBadge.textContent = "REJECTED";
  statusBadge.className = "badge badge-danger";
  
  document.getElementById("approvedRoleBadge").textContent = `REJECTED (${rej.rejected_by_role})`;
  document.getElementById("approvedRoleBadge").className = "badge badge-danger";
  document.getElementById("approvalActionCluster").style.display = "none";

  document.getElementById("snsMsgId").textContent = "REJECTED_NO_BROADCAST";
  document.getElementById("snsBodyText").textContent = `REJECTION NOTICE: Proposal ${rej.incident_id} was rejected by ${rej.rejected_by_role}. Reason: ${rej.reason}. Zero stock was deducted.`;
}

function renderFastAutoApproveResults(result) {
  document.getElementById("activeIncId").textContent = result.execution_id;
  const statusBadge = document.getElementById("proposalStatusBadge");
  statusBadge.textContent = "APPROVED & DISPATCHED";
  statusBadge.className = "badge badge-success";
  
  document.getElementById("createdRoleBadge").textContent = "EMERGENCY_OFFICER";
  document.getElementById("approvedRoleBadge").textContent = "LOGISTICS_DIRECTOR (Auto)";
  document.getElementById("approvedRoleBadge").className = "badge badge-success";
  document.getElementById("approvalActionCluster").style.display = "none";

  renderDpriComponents(result.dpri_result);
  renderShortagesAndPlan(result.allocation_plan);

  const sns = result.sns_alert;
  document.getElementById("snsTopic").textContent = sns.topic_arn;
  document.getElementById("snsMsgId").textContent = sns.message_id;
  document.getElementById("snsTime").textContent = sns.timestamp;
  document.getElementById("snsBodyText").textContent = sns.message;
}

function renderDpriComponents(dpri) {
  document.getElementById("dpriScoreText").textContent = dpri.dpri_score.toFixed(4);
  document.getElementById("dpriHazard").textContent = dpri.hazard_component.toFixed(2);
  document.getElementById("dpriVuln").textContent = dpri.vulnerability_component.toFixed(2);
  document.getElementById("dpriCoping").textContent = dpri.coping_deficit.toFixed(2);
  document.getElementById("dpriInfra").textContent = dpri.infrastructure_penalty.toFixed(2);
  document.getElementById("dpriExplanation").textContent = dpri.explanation;

  const riskBadge = document.getElementById("dpriRiskBadge");
  riskBadge.textContent = dpri.risk_level;
  riskBadge.className = `badge badge-${dpri.risk_level.toLowerCase()}`;
}

function renderShortagesAndPlan(alloc) {
  const fulfillmentBadge = document.getElementById("fulfillmentBadge");
  fulfillmentBadge.textContent = `${alloc.overall_fulfillment_rate}% Network Fulfillment`;
  fulfillmentBadge.className = alloc.overall_fulfillment_rate >= 90 ? "badge badge-success" : "badge badge-warning";

  const shortageBody = document.getElementById("shortageBody");
  shortageBody.innerHTML = "";
  alloc.shortage_breakdown.forEach(s => {
    const row = document.createElement("tr");
    const isShortfall = s.shortage_quantity > 0;
    row.innerHTML = `
      <td><strong>${s.item_name}</strong> (${s.category})</td>
      <td>${s.demanded.toLocaleString()}</td>
      <td>${s.available_network_stock.toLocaleString()}</td>
      <td style="color: ${isShortfall ? '#ef4444' : '#10b981'}; font-weight: 600;">
        ${isShortfall ? '-' + s.shortage_quantity.toLocaleString() : '0 (Fulfilled)'}
      </td>
      <td>
        <div class="progress-bar-container">
          <div class="progress-fill ${s.fulfillment_percentage < 100 ? 'partial' : ''}" style="width: ${s.fulfillment_percentage}%"></div>
        </div>
        <span>${s.fulfillment_percentage}%</span>
      </td>
    `;
    shortageBody.appendChild(row);
  });

  const dispatchBody = document.getElementById("dispatchBody");
  dispatchBody.innerHTML = "";
  if (alloc.dispatch_plan.length === 0) {
    dispatchBody.innerHTML = `<tr><td colspan="4" class="empty-cell">No depots had available stock to dispatch.</td></tr>`;
  } else {
    alloc.dispatch_plan.forEach(d => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${d.warehouse_id}</code> - <strong>${d.warehouse_name}</strong></td>
        <td>${d.item_name}</td>
        <td><strong style="color: #38bdf8">${d.dispatched_quantity.toLocaleString()}</strong> ${d.unit}</td>
        <td><span class="badge badge-success">ALLOCATED</span></td>
      `;
      dispatchBody.appendChild(row);
    });
  }
}

// Multi-Region Prioritization Demo
async function runMultiRegionDemo() {
  const panel = document.getElementById("multiRegionPanel");
  panel.style.display = "block";
  const tbody = document.getElementById("multiRegionBody");
  tbody.innerHTML = `<tr><td colspan="7" class="loading-cell">Evaluating 3 regional hazard models...</td></tr>`;

  const sampleBatch = [
    {
      incident_name: "Cyclone Veronica",
      disaster_type: "CYCLONE",
      region: "Pilbara Coastal Sector",
      affected_population: 24000,
      displaced_population: 9000,
      hazard_intensity: 0.90,
      vulnerability_score: 0.75,
      coping_capacity: 0.35,
      infrastructure_damage: 0.80
    },
    {
      incident_name: "Urban Basin Rupture",
      disaster_type: "EARTHQUAKE",
      region: "Central Metro District",
      affected_population: 40000,
      displaced_population: 18000,
      hazard_intensity: 0.95,
      vulnerability_score: 0.85,
      coping_capacity: 0.25,
      infrastructure_damage: 0.90
    },
    {
      incident_name: "Delta River Overflow",
      disaster_type: "FLOOD",
      region: "Northern Lowlands",
      affected_population: 12000,
      displaced_population: 3200,
      hazard_intensity: 0.65,
      vulnerability_score: 0.55,
      coping_capacity: 0.55,
      infrastructure_damage: 0.50
    }
  ];

  try {
    const res = await fetch("/api/disaster/prioritize-regions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sampleBatch)
    });
    const data = await res.json();
    tbody.innerHTML = "";
    data.ranked_regions.forEach(item => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong style="color: #38bdf8; font-size: 1.1rem;">#${item.rank}</strong></td>
        <td><strong>${item.incident_name}</strong></td>
        <td>${item.region}</td>
        <td><span class="badge badge-info">${item.disaster_type}</span></td>
        <td><strong>${item.dpri_score.toFixed(4)}</strong></td>
        <td><span class="badge badge-${item.risk_level.toLowerCase()}">${item.risk_level}</span></td>
        <td><strong>${item.urgency_tier}</strong><br><small style="color: #94a3b8;">${item.recommended_action}</small></td>
      `;
      tbody.appendChild(row);
    });
    document.getElementById("multiRegionRationale").textContent = "Prioritization Rationale: " + data.prioritization_rationale;
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">Failed to evaluate multi-region rankings.</td></tr>`;
    console.error(err);
  }
}
window.runMultiRegionDemo = runMultiRegionDemo;
