import { useState } from "react";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [customers, setCustomers] = useState([]);
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState(null);

  const loadDuplicates = async () => {
    try {
      setInvestigation(null);
      setAction(null);

      const response = await fetch(`${API}/duplicates`);
      const data = await response.json();

      setCustomers(data.duplicates || data.candidates || []);
    } catch (error) {
      alert("Backend is not running!");
    }
  };

  const investigate = async (customer1, customer2) => {
    setLoading(true);
    setInvestigation(null);
    setAction(null);

    try {
      const response = await fetch(`${API}/investigate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          customer_1: customer1,
          customer_2: customer2,
        }),
      });

      const data = await response.json();

      setInvestigation(data.investigation);
    } catch (error) {
      alert("Could not connect to AI Investigator.");
    }

    setLoading(false);
  };

  const handleAction = (selectedAction) => {
    setAction(selectedAction);
  };

  return (
    <div className="app">

      {/* HEADER */}
      <header>
        <div>
          <h1>🧹 CleanMaster AI</h1>
          <p>Intelligent Data Cleaning & Duplicate Detection</p>
        </div>

        <div className="status">
          <span></span>
          System Online
        </div>
      </header>

      <main>

        {/* HERO */}
        <section className="hero">
          <h2>AI-Powered Data Cleaning</h2>

          <p>
            Detect duplicate customer records, investigate suspicious
            matches, and make intelligent cleanup decisions.
          </p>

          <button className="scan-btn" onClick={loadDuplicates}>
            🔍 Scan for Duplicates
          </button>
        </section>

        {/* DASHBOARD */}
        <section className="dashboard">

          <div className="card">
            <h3>📊 Duplicate Candidates</h3>

            <div className="number">
              {customers.length}
            </div>

            <p>Potential duplicate pairs detected</p>
          </div>

          <div className="card">
            <h3>🤖 AI Investigator</h3>

            <div className="number">
              {investigation ? "✓" : "—"}
            </div>

            <p>AI investigation status</p>
          </div>

          <div className="card">
            <h3>⚡ Decision Engine</h3>

            <div className="number">
              {action ? "✓" : "—"}
            </div>

            <p>Cleanup action status</p>
          </div>

        </section>

        {/* DUPLICATE RESULTS */}
        {customers.length > 0 && (
          <section className="results">

            <h2>🔎 Duplicate Candidates</h2>

            {customers.map((item, index) => (
              <div className="candidate" key={index}>

                <div className="candidate-info">

                  <h3>
                    {item.customer_1} ↔ {item.customer_2}
                  </h3>

                  <p>
                    Score:
                    <strong> {item.score}</strong>
                  </p>

                  <p>
                    Confidence:
                    <strong> {item.confidence}</strong>
                  </p>

                </div>

                <button
                  className="ai-btn"
                  onClick={() =>
                    investigate(
                      item.customer_1,
                      item.customer_2
                    )
                  }
                >
                  🤖 Investigate with AI
                </button>

              </div>
            ))}

          </section>
        )}

        {/* LOADING */}
        {loading && (
          <div className="loading">
            🤖 Gemini AI is investigating...
          </div>
        )}

        {/* AI RESULT */}
        {investigation && (
          <section className="investigation">

            <h2>🤖 AI Investigation Result</h2>

            <div className="decision">

              <h3>
                {investigation.decision}
              </h3>

              <p>
                Confidence:
                <strong> {investigation.confidence}</strong>
              </p>

            </div>

            <div className="reason">

              <h3>🔍 Reason</h3>

              <p>
                {investigation.reason}
              </p>

            </div>

            <div className="recommendation">

              <h3>💡 Recommendation</h3>

              <p>
                {investigation.recommendation}
              </p>

            </div>

            <p className="investigator">
              Investigated by:{" "}
              {investigation.investigated_by}
            </p>

            {/* ACTION BUTTONS */}
            <div className="actions">

              <h3>⚡ Cleanup Decision</h3>

              <div className="action-buttons">

                <button
                  className="merge-btn"
                  onClick={() => handleAction("MERGE")}
                >
                  🔗 Merge Records
                </button>

                <button
                  className="separate-btn"
                  onClick={() =>
                    handleAction("KEEP SEPARATE")
                  }
                >
                  🚫 Keep Separate
                </button>

                <button
                  className="review-btn"
                  onClick={() =>
                    handleAction("HUMAN REVIEW")
                  }
                >
                  👤 Send for Review
                </button>

              </div>

            </div>

            {/* ACTION RESULT */}
            {action && (
              <div className="action-result">

                <h3>✅ Action Selected</h3>

                <p>
                  Selected action:
                  <strong> {action}</strong>
                </p>

                <p>
                  This decision has been recorded for
                  the current session.
                </p>

              </div>
            )}

          </section>
        )}

      </main>

      <footer>
        <p>
          CleanMaster AI • Intelligent Data Quality Platform
        </p>
      </footer>

    </div>
  );
}

export default App;