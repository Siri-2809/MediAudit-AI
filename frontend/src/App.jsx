import { useCallback, useEffect, useState } from "react";

import {

  Activity,

  AlertTriangle,

  ClipboardCheck,

  Search,

  Download,

  ShieldCheck,

  RefreshCw,

  LayoutDashboard,

  FileSearch,

  X,

  ArrowUpRight,

  CircleCheck,
  Sparkles,
  FileUp,
} from "lucide-react";

import "./App.css";



const API = "http://127.0.0.1:8000";



function App() {

  const [activeTab, setActiveTab] = useState("overview");

  const [summary, setSummary] = useState(null);

  const [claims, setClaims] = useState([]);

  const [search, setSearch] = useState("");

  const [flaggedOnly, setFlaggedOnly] = useState(true);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [selected, setSelected] = useState(null);
  const [aiExplanation, setAiExplanation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [hasUploaded, setHasUploaded] = useState(false);



  const loadData = useCallback(async () => {

    setLoading(true);

    setError("");



    try {

      const [summaryResponse, claimsResponse] = await Promise.all([

        fetch(`${API}/api/summary`),

        fetch(

          `${API}/api/claims?flagged_only=${flaggedOnly}&limit=1000`

        ),

      ]);



      if (!summaryResponse.ok || !claimsResponse.ok) {

        throw new Error("The API returned an error.");

      }



      const summaryData = await summaryResponse.json();

      const claimsData = await claimsResponse.json();



      setSummary(summaryData);

      setClaims(claimsData.items ?? []);

    } catch (err) {

      setError(

        "Cannot connect to MediAudit AI. Check that the FastAPI backend is running on port 8000."

      );

    } finally {

      setLoading(false);

    }

  }, [flaggedOnly]);



  useEffect(() => {

    function handleKeyDown(event) {

      if (event.key === "Escape") setSelected(null);

    }



    window.addEventListener("keydown", handleKeyDown);

    return () => window.removeEventListener("keydown", handleKeyDown);

  }, []);



  const filteredClaims = claims.filter((claim) => {

    const claimId = String(claim.CLM_ID ?? "");

    const matchesSearch = claimId

      .toLowerCase()

      .includes(search.trim().toLowerCase());



    return matchesSearch;

  });



  function formatNumber(value) {

    return Number(value ?? 0).toLocaleString("en-US");

  }



  function formatMoney(value) {

    if (value === null || value === undefined || value === "") {

      return "—";

    }



    return Number(value).toLocaleString("en-US", {

      maximumFractionDigits: 2,

    });

  }



  function downloadReport() {

    window.open(

      `${API}/api/report?flagged_only=${flaggedOnly}`,

      "_blank",

      "noopener,noreferrer"

    );

  }



  function openClaim(claim) {
    setSelected(claim);
    setAiExplanation(null);
    setAiError("");
    setAiLoading(false);
  }

  async function handleUpload(event) {
    event.preventDefault();
    if (!uploadFile) {
      setUploadError("Choose a CSV file first.");
      setUploadMessage("");
      return;
    }

    setUploadLoading(true);
    setUploadError("");
    setUploadMessage("");

    try {
      const formData = new FormData();
      formData.append("file", uploadFile);

      const response = await fetch(`${API}/api/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed. Please check the CSV file.");
      }

      setUploadMessage(
        `${data.filename || uploadFile.name} analyzed successfully: ${formatNumber(data.total_claims)} claims processed.`
      );
      setHasUploaded(true);
      setUploadFile(null);
      const input = document.getElementById("claims-csv-upload");
      if (input) input.value = "";
      await loadData();
    } catch (err) {
      setUploadError(`This CSV could not be validated or analyzed. ${err.message || "Please choose a valid claims CSV file."}`);
    } finally {
      setUploadLoading(false);
    }
  }

  async function generateAIExplanation() {
    if (!selected) return;

    setAiLoading(true);
    setAiError("");
    setAiExplanation(null);

    try {
      const response = await fetch(
        `${API}/api/claims/${encodeURIComponent(String(selected.CLM_ID))}/ai-explanation`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not generate an AI explanation.");
      }

      setAiExplanation(data.ai_explanation);
    } catch (err) {
      setAiError(
        err.message || "AI explanation is unavailable. Check that the backend is running."
      );
    } finally {
      setAiLoading(false);
    }
  }



  return (

    <div className="app-shell">

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-icon">

            <ShieldCheck size={25} />

          </div>

          <div>

            <h2>

              MediAudit <span>AI</span>

            </h2>

            <p>CLAIMS INTELLIGENCE</p>

          </div>

        </div>



        <div className="nav-label">WORKSPACE</div>



        <button

          type="button"

          className={`nav-item ${

            activeTab === "overview" ? "active" : ""

          }`}

          onClick={() => setActiveTab("overview")}

          aria-current={activeTab === "overview" ? "page" : undefined}

        >

          <Activity size={18} />

          <span>Overview</span>

        </button>



        <button

          type="button"

          className={`nav-item ${

            activeTab === "audit" ? "active" : ""

          }`}

          onClick={() => setActiveTab("audit")}

          aria-current={activeTab === "audit" ? "page" : undefined}

        >

          <ClipboardCheck size={18} />

          <span>Claims Audit</span>

        </button>



        <div className="sidebar-note">

          <ShieldCheck size={20} />

          <strong>Human-led auditing</strong>

          <p>

            AI identifies unusual claims for review. A flag is not proof

            of fraud.

          </p>

        </div>



        <div className="sidebar-footer">MEDAUDIT AI · PROTOTYPE</div>

      </aside>



      <main className="main-content">

        <header className="topbar">

          <div>

            <p className="eyebrow">

              WORKSPACE / {!hasUploaded ? "UPLOAD DATASET" : activeTab === "overview" ? "OVERVIEW" : "CLAIMS AUDIT"}

            </p>



            <h1>
              {!hasUploaded
                ? "Upload claims dataset"
                : activeTab === "overview"
                  ? "Claims Overview"
                  : "Claims Audit"}
            </h1>



            <p className="subtitle">
              {!hasUploaded
                ? "Upload a compatible CSV to start auditing."
                : activeTab === "overview"
                  ? "Understand unusual billing patterns and review the evidence."
                  : "Investigate unusual claims, understand the evidence, and prepare audit findings."}
            </p>

          </div>



          {hasUploaded && (
            <button
              type="button"
              className="refresh-button"
              onClick={loadData}
              disabled={loading}
            >
              <RefreshCw size={16} />
              {loading ? "Loading..." : "Refresh"}
            </button>
          )}

        </header>



        {!hasUploaded ? (
          <section className="upload-panel upload-first-panel">
            <div className="upload-first-icon"><FileUp size={28} /></div>
            <h2>Start a new audit</h2>
            <p className="upload-first-description">
              Upload a claims CSV to validate the data, detect unusual patterns, and generate an audit report.
              Your dashboard will appear here after analysis succeeds.
            </p>
            <form className="upload-form upload-first-form" onSubmit={handleUpload}>
              <input
                id="claims-csv-upload"
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => {
                  setUploadFile(event.target.files?.[0] ?? null);
                  setUploadError("");
                  setUploadMessage("");
                }}
                disabled={uploadLoading}
                aria-label="Choose claims CSV file"
              />
              <button type="submit" className="download-button" disabled={uploadLoading || !uploadFile}>
                <FileUp size={16} />
                {uploadLoading ? "Validating & analyzing..." : "Upload & Analyze"}
              </button>
            </form>
            {uploadLoading && <p className="upload-status" role="status">Analyzing your file. Larger datasets may take a little while; please keep this page open.</p>}
            {uploadError && <p className="upload-error" role="alert">{uploadError}</p>}
            <p className="upload-first-footnote">Compatible claims CSV required. Audit flags are for human review, not proof of fraud.</p>
          </section>
        ) : (
          <>
            <section className="upload-panel upload-compact-panel">
              <div className="upload-copy">
                <div className="upload-icon"><FileUp size={21} /></div>
                <div>
                  <h2>Dataset uploaded</h2>
                  <p>Upload another compatible CSV to replace the active audit dataset.</p>
                </div>
              </div>
              <form className="upload-form" onSubmit={handleUpload}>
                <input
                  id="claims-csv-upload"
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(event) => {
                    setUploadFile(event.target.files?.[0] ?? null);
                    setUploadError("");
                    setUploadMessage("");
                  }}
                  disabled={uploadLoading}
                  aria-label="Choose claims CSV file"
                />
                <button type="submit" className="download-button" disabled={uploadLoading || !uploadFile}>
                  <FileUp size={16} />
                  {uploadLoading ? "Analyzing CSV..." : "Upload & Analyze"}
                </button>
              </form>
              {uploadLoading && <p className="upload-status" role="status">Processing the CSV. Please keep this page open.</p>}
              {uploadMessage && <p className="upload-success" role="status">{uploadMessage}</p>}
              {uploadError && <p className="upload-error" role="alert">{uploadError}</p>}
            </section>

            {error && (

          <div className="error-banner" role="alert">

            <AlertTriangle size={18} />

            <span>{error}</span>

            <button type="button" onClick={loadData}>

              Retry

            </button>

          </div>

        )}



        {loading && !summary ? (

          <div className="loading">Loading claims data...</div>

        ) : summary ? (

          <>

            {activeTab === "overview" && (

              <>

                <section className="stats-grid">

                  <StatCard

                    label="Claims Analyzed"

                    value={summary.total_claims}

                    icon={<ClipboardCheck />}

                  />

                  <StatCard

                    label="Need Review"

                    value={summary.claims_needing_review}

                    icon={<AlertTriangle />}

                    accent

                  />

                  <StatCard

                    label="ML Anomalies"

                    value={summary.anomaly_flags}

                    icon={<Activity />}

                  />

                  <StatCard

                    label="Rule Flags"

                    value={summary.rule_flags}

                    icon={<ShieldCheck />}

                  />

                </section>



                <section className="notice">

                  <AlertTriangle size={20} />

                  <div>

                    <strong>Review findings, not fraud verdicts</strong>

                    <p>

                      Anomaly detection and audit rules identify claims

                      that may need investigation. An auditor must verify

                      each finding.

                    </p>

                  </div>

                </section>



                <section className="overview-panel">

                  <div>

                    <div className="overview-icon">

                      <FileSearch size={23} />

                    </div>

                    <h2>Ready to investigate?</h2>

                    <p>

                      Explore claims, examine the rules that were

                      triggered, and review recommended verification

                      steps.

                    </p>

                    <button

                      type="button"

                      className="download-button"

                      onClick={() => setActiveTab("audit")}

                    >

                      Open Claims Audit

                      <ArrowUpRight size={16} />

                    </button>

                  </div>



                  <div className="overview-highlights">

                    <div>

                      <CircleCheck size={17} />

                      <span>Machine-learning anomaly detection</span>

                    </div>

                    <div>

                      <CircleCheck size={17} />

                      <span>Transparent audit rules</span>

                    </div>

                    <div>

                      <CircleCheck size={17} />

                      <span>Explanations and recommended checks</span>

                    </div>

                    <div>

                      <CircleCheck size={17} />

                      <span>CSV audit report export</span>

                    </div>

                  </div>

                </section>

              </>

            )}



            <section className="claims-panel">

              <div className="panel-header">

                <div>

                  <h2>

                    {activeTab === "overview"

                      ? "Claims Explorer"

                      : "Audit Queue"}

                  </h2>

                  <p>

                    {activeTab === "overview"

                      ? "Search and inspect claims in the loaded results."

                      : "Review flagged claims, their evidence, and recommended next steps."}

                  </p>

                </div>



                <button

                  type="button"

                  className="download-button"

                  onClick={downloadReport}

                >

                  <Download size={16} />

                  Export CSV

                </button>

              </div>



              <div className="toolbar">

                <div className="search-box">

                  <Search size={17} />

                  <input

                    type="search"

                    placeholder="Search by claim ID..."

                    value={search}

                    onChange={(event) => setSearch(event.target.value)}

                    aria-label="Search by claim ID"

                  />

                </div>



                <label className="filter-toggle">

                  <input

                    type="checkbox"

                    checked={flaggedOnly}

                    onChange={(event) =>

                      setFlaggedOnly(event.target.checked)

                    }

                  />

                  Needs review only

                </label>

              </div>



              <div className="table-wrap">

                <table>

                  <thead>

                    <tr>

                      <th>Claim ID</th>

                      <th>Payment</th>

                      <th>Length of Stay</th>

                      <th>ML Anomaly</th>

                      <th>Audit Rules</th>

                      <th>Finding</th>

                    </tr>

                  </thead>



                  <tbody>

                    {filteredClaims.map((claim) => (

                      <tr key={claim.CLM_ID}>

                        <td className="claim-id">{claim.CLM_ID}</td>

                        <td>{formatMoney(claim.CLM_PMT_AMT)}</td>

                        <td>

                          {claim.LENGTH_OF_STAY ?? "—"}

                          {claim.LENGTH_OF_STAY !== null &&

                          claim.LENGTH_OF_STAY !== undefined

                            ? " days"

                            : ""}

                        </td>

                        <td>

                          <span

                            className={`pill ${

                              claim.ANOMALY_FLAG

                                ? "pill-red"

                                : "pill-gray"

                            }`}

                          >

                            {claim.ANOMALY_FLAG ? "Flagged" : "Normal"}

                          </span>

                        </td>

                        <td>{claim.RULE_FLAGS || "—"}</td>

                        <td>

                          <button

                            type="button"

                            className="view-button"

                            onClick={() => openClaim(claim)}

                          >

                            View details

                          </button>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>



                {!loading && filteredClaims.length === 0 && (

                  <p className="empty-state">

                    No claims match your search. Try another claim ID or

                    change the review filter.

                  </p>

                )}

              </div>



              <div className="table-footer">

                Showing {formatNumber(filteredClaims.length)} of{" "}

                {formatNumber(claims.length)} loaded claims.

                {claims.length === 1000 &&

                  " The current API request is limited to 1,000 records."}

              </div>

            </section>

          </>

        ) : null}
          </>
        )}

      </main>



      {selected && (

        <div

          className="modal-backdrop"

          onClick={() => setSelected(null)}

        >

          <section

            className="detail-modal"

            role="dialog"

            aria-modal="true"

            aria-labelledby="claim-detail-title"

            onClick={(event) => event.stopPropagation()}

          >

            <button

              type="button"

              className="modal-close"

              onClick={() => setSelected(null)}

              aria-label="Close claim details"

            >

              <X size={23} />

            </button>



            <p className="eyebrow">CLAIM DETAILS</p>

            <h2 id="claim-detail-title">{selected.CLM_ID}</h2>



            <div className="detail-stats">

              <div>

                <span>Payment</span>

                <strong>{formatMoney(selected.CLM_PMT_AMT)}</strong>

              </div>

              <div>

                <span>Length of stay</span>

                <strong>

                  {selected.LENGTH_OF_STAY ?? "—"}

                  {selected.LENGTH_OF_STAY != null ? " days" : ""}

                </strong>

              </div>

              <div>

                <span>Anomaly score</span>

                <strong>

                  {selected.ANOMALY_SCORE != null

                    ? Number(selected.ANOMALY_SCORE).toFixed(4)

                    : "—"}

                </strong>

              </div>

            </div>



            <h3>Why it was flagged</h3>

            <p>

              {selected.AUDIT_EXPLANATION ||

                "No explanation is available for this claim."}

            </p>



            <h3>Recommended auditor checks</h3>

            <p>

              {selected.RECOMMENDED_CHECK ||

                "No specific check is available."}

            </p>



            <h3>Triggered rules</h3>

            <p>{selected.RULE_FLAGS || "No configured audit rule triggered."}</p>



            {selected.RULE_REASONS && (

              <>

                <h3>Rule evidence</h3>

                <p>{selected.RULE_REASONS}</p>

              </>

            )}



            <section className="ai-explanation-panel" aria-live="polite">
                <div className="ai-explanation-heading">
                  <div>
                    <h3><Sparkles size={17} /> Gemini AI Explanation</h3>
                    <p>AI-generated audit support based only on the available claim evidence.</p>
                  </div>
                  <button
                    type="button"
                    className="download-button"
                    onClick={generateAIExplanation}
                    disabled={aiLoading}
                  >
                    <Sparkles size={16} />
                    {aiLoading ? "Generating..." : aiExplanation ? "Regenerate" : "Generate AI Explanation"}
                  </button>
                </div>

                {aiLoading && (
                  <p className="ai-status">Gemini is reviewing the available evidence...</p>
                )}

                {aiError && (
                  <p className="ai-error" role="alert">{aiError}</p>
                )}

                {aiExplanation && (
                  <div className="ai-explanation-content">
                    <div>
                      <h4>Summary</h4>
                      <p>{aiExplanation.summary}</p>
                    </div>
                    <div>
                      <h4>Evidence</h4>
                      <p>{aiExplanation.evidence}</p>
                    </div>
                    <div>
                      <h4>Recommended checks</h4>
                      <p>{aiExplanation.recommended_checks}</p>
                    </div>
                    <div>
                      <h4>Limitations</h4>
                      <p>{aiExplanation.limitations}</p>
                    </div>
                  </div>
                )}
              </section>

              <div className="modal-actions">

              <button

                type="button"

                className="download-button"

                onClick={() => setSelected(null)}

              >

                Close details

              </button>

            </div>



            <p className="modal-disclaimer">

              This is an audit-support finding, not a determination of

              fraud or improper billing.

            </p>

          </section>

        </div>

      )}

    </div>

  );

}



function StatCard({ label, value, icon, accent = false }) {

  return (

    <div className={`stat-card ${accent ? "stat-accent" : ""}`}>

      <div className="stat-top">

        <span>{label}</span>

        <div className="stat-icon">{icon}</div>

      </div>

      <strong>{Number(value ?? 0).toLocaleString("en-US")}</strong>

    </div>

  );

}



export default App;
