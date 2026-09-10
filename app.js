const $ = (selector) => document.querySelector(selector);
const resume = $("#resume"), job = $("#job"), file = $("#file"), error = $("#error");
let uploadedFile = null;

file.addEventListener("change", async () => {
  const chosen = file.files[0];
  if (!chosen) return;
  if (chosen.size > 5 * 1024 * 1024) return showError("Please choose a file smaller than 5 MB.");
  const encoded = await new Promise((resolve) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(",")[1]); reader.readAsDataURL(chosen); });
  uploadedFile = { name: chosen.name, content: encoded };
  $("#file-name").textContent = `Ready: ${chosen.name}`;
  resume.placeholder = "Your uploaded resume will be used for analysis.";
});

function showError(message) { error.textContent = message; }
function tags(items, empty) { return items.length ? items.map((item) => `<span>${item}</span>`).join("") : `<p class="muted">${empty}</p>`; }
function setMetric(id, value) { $(`#${id}`).textContent = `${value}%`; $(`#${id}-bar`).style.width = `${value}%`; }

function render(report) {
  const root = $("#results"); root.replaceChildren($("#result-template").content.cloneNode(true));
  $("#score").textContent = `${report.score}%`;
  setMetric("relevance", report.components.relevance); setMetric("coverage", report.components.coverage); setMetric("quality", report.components.quality);
  $("#matching").innerHTML = tags(report.matching_skills, "No clear overlapping skills detected yet.");
  $("#missing").innerHTML = tags(report.missing_skills, "No skill gaps were detected from our taxonomy.");
  $("#checks").innerHTML = report.checks.map((item) => `<li class="${item.passed ? "pass" : "fail"}"><b>${item.passed ? "✓" : "–"}</b>${item.label}</li>`).join("");
  $("#suggestion-list").innerHTML = report.suggestions.map((item, i) => `<article><span>0${i + 1}</span><div><h3>${item.title}</h3><p>${item.detail}</p></div></article>`).join("");
  $("#disclaimer").textContent = report.disclaimer; root.classList.remove("hidden"); root.scrollIntoView({ behavior: "smooth", block: "start" });
}

$("#analyze").addEventListener("click", async () => {
  showError(""); const button = $("#analyze");
  if (!uploadedFile && resume.value.trim().length < 40) return showError("Paste your resume or upload a PDF, DOCX, or TXT file.");
  if (job.value.trim().length < 40) return showError("Paste a fuller job description to get an accurate analysis.");
  button.disabled = true; button.innerHTML = "Analyzing <span>↻</span>";
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume: resume.value, job: job.value, file: uploadedFile }) });
    const data = await response.json(); if (!response.ok) throw new Error(data.error || "Something went wrong."); render(data);
  } catch (err) { showError(err.message); } finally { button.disabled = false; button.innerHTML = "Analyze alignment <span>→</span>"; }
});
