import { motion, useScroll, useTransform } from "framer-motion";
import {
  Activity,
  Atom,
  BrainCircuit,
  ClipboardCheck,
  Cpu,
  DatabaseZap,
  FileSearch,
  Gauge,
  Network,
  Play,
  Radar,
  Send,
  Sparkles,
} from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useMemo, useRef, useState } from "react";

gsap.registerPlugin(ScrollTrigger);

const categories = [
  { label: "Software Defect", value: "software_bug" },
  { label: "Requirement Gap", value: "requirement_gap" },
  { label: "Test Environment", value: "test_environment_issue" },
  { label: "Data Issue", value: "data_issue" },
  { label: "Performance Issue", value: "performance_issue" },
  { label: "Integration Issue", value: "integration_issue" },
];

const metrics = [
  { label: "Synthetic Test F1", value: "1.000" },
  { label: "Challenge F1", value: "0.863" },
  { label: "Manual Challenge", value: "36" },
  { label: "Training Reports", value: "540" },
];

const apiUrl = "http://127.0.0.1:8765";
const defaultIssue =
  "During regression testing, the login API returns HTTP 500 only when the password contains special characters. The expected behavior is HTTP 401 for invalid credentials.";
const defaultRequirement =
  "The CRM connector must map customerId to customer_id, reject malformed payloads, and keep workflow status synchronized across ERP and CRM services.";

const samples = [
  "The ERP connector sends customerId but the CRM endpoint now expects customer_id.",
  "Search response time increased from 300ms to 4.8s after importing 100k records.",
  "Test passes locally but fails on staging because the payment sandbox endpoint is unreachable.",
  "The specification does not mention what should happen when the user cancels payment after OTP verification.",
];

const suiteModules = [
  {
    name: "IssueSense ML",
    role: "AI triage engine",
    detail: "Classify issue type, estimate likely cause, retrieve similar cases, and flag uncertainty.",
  },
  {
    name: "EngiAgent",
    role: "Agentic workflow layer",
    detail: "Expand triage findings into investigation plans, evidence-grounded summaries, and 8D drafts.",
  },
  {
    name: "QAForge AI",
    role: "QA validation layer",
    detail: "Turn confirmed risks into requirement-linked tests, edge cases, and coverage checks.",
  },
];

function displayLabel(label) {
  const match = categories.find((category) => category.value === label);
  return match?.label ?? label?.replaceAll("_", " ");
}

function isNeedsReview(result) {
  return result?.status === "needs_review";
}

async function postJson(path, payload) {
  const response = await fetch(`${apiUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail);
  }
  return response.json();
}

function outputTitle(result) {
  if (!result) {
    return "Awaiting issue packet";
  }
  return isNeedsReview(result) ? "Needs Review" : displayLabel(result.label);
}

function ParticleField({ count = 90 }) {
  const particles = useMemo(
    () =>
      Array.from({ length: count }, (_, index) => ({
        id: index,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        delay: `${Math.random() * 8}s`,
        duration: `${5 + Math.random() * 9}s`,
        size: `${1 + Math.random() * 3}px`,
      })),
    [count]
  );

  return (
    <div className="particle-field" aria-hidden="true">
      {particles.map((particle) => (
        <span
          key={particle.id}
          style={{
            left: particle.left,
            top: particle.top,
            width: particle.size,
            height: particle.size,
            animationDelay: particle.delay,
            animationDuration: particle.duration,
          }}
        />
      ))}
    </div>
  );
}

function Asset({ src, className, alt }) {
  return <img className={className} src={src} alt={alt} draggable="false" />;
}

function Scene({ id, eyebrow, title, body, children, className = "" }) {
  return (
    <section id={id} className={`scene ${className}`}>
      <div className="scene-copy">
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
      {children}
    </section>
  );
}

function IntroScene() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const cityScale = useTransform(scrollYProgress, [0, 1], [1.08, 1.32]);
  const cityY = useTransform(scrollYProgress, [0, 1], [0, 120]);
  const copyY = useTransform(scrollYProgress, [0, 1], [0, -90]);

  return (
    <section ref={ref} className="hero-scene">
      <motion.div className="city-camera" style={{ scale: cityScale, y: cityY }}>
        <Asset src="/assets/lab-city.svg" className="city-asset" alt="Futuristic engineering city" />
      </motion.div>
      <ParticleField count={120} />
      <div className="scanner scanner-a" />
      <div className="scanner scanner-b" />
      <motion.div className="hero-copy" style={{ y: copyY }}>
        <span className="system-chip">ENGINEERING INTELLIGENCE SUITE</span>
        <h1>IssueSense ML</h1>
        <p>AI triage engine for engineering issue classification and root-cause inspection.</p>
      </motion.div>
      <div className="scroll-hint">
        <span />
        Enter the facility
      </div>
    </section>
  );
}

function DataScene() {
  return (
    <Scene
      id="data"
      eyebrow="Scene 02 / Data Collection"
      title="Reports become signal."
      body="Bug reports, validation failures, performance logs, and test findings stream into a structured engineering issue dataset."
      className="data-scene"
    >
      <Asset src="/assets/data-stream.svg" className="stream stream-one" alt="Animated data stream" />
      <Asset src="/assets/data-stream.svg" className="stream stream-two" alt="Animated data stream" />
      <Asset src="/assets/report-packets.svg" className="packets" alt="Engineering report packets" />
      <div className="data-vortex">
        <DatabaseZap size={44} />
      </div>
    </Scene>
  );
}

function TriageScene({ result, setResult, onSendToEngiAgent, onSendToQAForge }) {
  const [text, setText] = useState(defaultIssue);
  const [model, setModel] = useState("textcnn");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function classify() {
    setStatus("running");
    setError("");
    try {
      const data = await postJson("/predict", { text, model });
      setResult({ ...data, query: text });
      setStatus("done");
      document.getElementById("core")?.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (exc) {
      setStatus("error");
      setError("API is not running. Start it with scripts\\run_api.ps1, then classify again.");
    }
  }

  return (
    <Scene
      id="triage"
      eyebrow="Live System / Triage Console"
      title="Inject an issue into the machine."
      body="Paste an engineering issue or test-report finding. IssueSense predicts the issue type, estimates likely cause, retrieves similar cases, and prepares the finding for deeper engineering workflows."
      className="triage-scene"
    >
      <div className="triage-console">
        <div className="console-header">
          <span>LOCAL MODEL ENDPOINT</span>
          <strong>{apiUrl}/predict</strong>
        </div>
        <textarea value={text} onChange={(event) => setText(event.target.value)} />
        <div className="console-actions">
          <div className="model-toggle">
            <button className={model === "textcnn" ? "active" : ""} onClick={() => setModel("textcnn")}>
              PyTorch TextCNN
            </button>
            <button className={model === "baseline" ? "active" : ""} onClick={() => setModel("baseline")}>
              TF-IDF Baseline
            </button>
          </div>
          <button className="classify-button" onClick={classify} disabled={status === "running"}>
            {status === "running" ? <Cpu className="spin" size={18} /> : <Send size={18} />}
            {status === "running" ? "Classifying" : "Classify Issue"}
          </button>
        </div>
        <div className="sample-row">
          {samples.map((sample) => (
            <button key={sample} onClick={() => setText(sample)}>
              <Play size={13} />
              sample
            </button>
          ))}
        </div>
        {error && <div className="api-error">{error}</div>}
      </div>
      <div className={`live-output ${result ? "has-result" : ""}`}>
        <span className="output-kicker">MODEL OUTPUT</span>
        {result ? (
          <>
            <span className={`status-pill ${isNeedsReview(result) ? "review" : "auto"}`}>
              {isNeedsReview(result) ? "Human review recommended" : "Auto-classified"}
            </span>
            <strong>{outputTitle(result)}</strong>
            <div className={`confidence-ring ${isNeedsReview(result) ? "low" : ""}`}>
              <span>{Math.round(result.confidence * 100)}%</span>
              confidence
            </div>
            <div className="predicted-label">
              Best model guess: <b>{displayLabel(result.label)}</b>
            </div>
            {result.top_predictions?.length > 0 && (
              <div className="top-predictions">
                {result.top_predictions.map((item) => (
                  <div key={item.label}>
                    <span>{displayLabel(item.label)}</span>
                    <b>{Math.round(item.confidence * 100)}%</b>
                  </div>
                ))}
              </div>
            )}
            <p>{result.explanation?.reason}</p>
            {result.triage?.likely_cause && (
              <div className="cause-preview">
                Likely cause: <b>{result.triage.likely_cause}</b>
              </div>
            )}
            <div className="handoff-actions">
              <button onClick={() => onSendToEngiAgent(text, result)}>
                <FileSearch size={16} />
                Send to EngiAgent
              </button>
              <button onClick={() => onSendToQAForge(text, result)}>
                <ClipboardCheck size={16} />
                Send to QAForge
              </button>
            </div>
            {result.review_reasons?.length > 0 && (
              <ul className="review-reasons">
                {result.review_reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            )}
            <small>{result.model} · {result.latency_ms?.toFixed(2)} ms</small>
          </>
        ) : (
          <>
            <strong>Awaiting issue packet</strong>
            <p>The next prediction will illuminate the classification core and evidence network.</p>
          </>
        )}
      </div>
    </Scene>
  );
}

function CoreScene({ result }) {
  return (
    <Scene
      id="core"
      eyebrow="Scene 03 / Triage Core"
      title="The first decision layer in a larger system."
      body="IssueSense is not the final app. It is the triage engine that turns raw engineering findings into structured signals for agentic investigation and QA validation."
      className="core-scene"
    >
      <Asset src="/assets/ai-core.svg" className="ai-core" alt="AI classification core" />
      <div className="category-orbit">
        {categories.map((category, index) => (
          <motion.div
            className={`category ${!isNeedsReview(result) && result?.label === category.value ? "active-category" : ""}`}
            key={category.value}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.12, duration: 0.55 }}
          >
            {category.label}
          </motion.div>
        ))}
      </div>
    </Scene>
  );
}

function SuiteMapScene() {
  return (
    <Scene
      id="suite"
      eyebrow="Scene 04 / Suite Architecture"
      title="One module inside an engineering intelligence system."
      body="The portfolio is organized as a suite: IssueSense triages findings, EngiAgent performs workflow reasoning, and QAForge converts risks into test coverage."
      className="suite-scene"
    >
      <div className="suite-map">
        {suiteModules.map((module, index) => (
          <div className={`suite-node ${index === 0 ? "primary" : ""}`} key={module.name}>
            <span>{module.role}</span>
            <strong>{module.name}</strong>
            <p>{module.detail}</p>
          </div>
        ))}
        <div className="suite-link link-a" />
        <div className="suite-link link-b" />
      </div>
    </Scene>
  );
}

function EngiAgentScene({ input, setInput, triageResult, result, setResult }) {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function generateDraft() {
    setStatus("running");
    setError("");
    try {
      const data = await postJson("/engiagent/8d-draft", {
        text: input,
        triage: triageResult?.triage
          ? { ...triageResult.triage, predicted_label: triageResult.label }
          : null,
      });
      setResult(data);
      setStatus("done");
    } catch (exc) {
      setStatus("error");
      setError("EngiAgent endpoint is unavailable. Start scripts\\run_api.ps1 and try again.");
    }
  }

  const dEntries = result ? Object.entries(result.eight_d) : [];

  return (
    <Scene
      id="engiagent"
      eyebrow="Scene 05 / EngiAgent Investigation"
      title="Turn triage into an 8D investigation draft."
      body="EngiAgent is the workflow layer. It reads the issue context, extracts evidence, builds an investigation summary, and drafts D1-D8 actions for human review."
      className="module-scene engiagent-scene"
    >
      <div className="module-console">
        <div className="console-header">
          <span>ENGIAGENT ENDPOINT</span>
          <strong>{apiUrl}/engiagent/8d-draft</strong>
        </div>
        <textarea value={input} onChange={(event) => setInput(event.target.value)} />
        <button className="classify-button" onClick={generateDraft} disabled={status === "running"}>
          {status === "running" ? <Cpu className="spin" size={18} /> : <FileSearch size={18} />}
          {status === "running" ? "Drafting" : "Generate 8D Draft"}
        </button>
        {error && <div className="api-error">{error}</div>}
      </div>
      <div className="module-output engiagent-output">
        <span className="output-kicker">AGENT OUTPUT</span>
        {result ? (
          <>
            <strong>8D Draft Ready</strong>
            <p>{result.investigation_summary}</p>
            <div className="eight-d-grid">
              {dEntries.map(([key, value]) => (
                <div key={key}>
                  <span>{key.replaceAll("_", " ")}</span>
                  <p>{value}</p>
                </div>
              ))}
            </div>
            <div className="trace-strip">
              {result.tool_trace.map((trace) => (
                <div key={trace.tool}>
                  <b>{trace.tool}</b>
                  <span>{trace.result}</span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <strong>Waiting for issue context</strong>
            <p>Use the button in IssueSense output or paste a report here to produce an investigation draft.</p>
          </>
        )}
      </div>
    </Scene>
  );
}

function QAForgeScene({ input, setInput, triageResult, result, setResult }) {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function generateTests() {
    setStatus("running");
    setError("");
    try {
      const data = await postJson("/qaforge/generate-tests", {
        requirement: input,
        triage: triageResult?.triage
          ? { ...triageResult.triage, predicted_label: triageResult.label }
          : null,
      });
      setResult(data);
      setStatus("done");
    } catch (exc) {
      setStatus("error");
      setError("QAForge endpoint is unavailable. Start scripts\\run_api.ps1 and try again.");
    }
  }

  return (
    <Scene
      id="qaforge"
      eyebrow="Scene 06 / QAForge Validation"
      title="Convert engineering risk into test coverage."
      body="QAForge AI turns requirements or confirmed triage risks into manual test cases, traceability rows, and quality checks for weak or incomplete QA artifacts."
      className="module-scene qaforge-scene"
    >
      <div className="module-console">
        <div className="console-header">
          <span>QAFORGE ENDPOINT</span>
          <strong>{apiUrl}/qaforge/generate-tests</strong>
        </div>
        <textarea value={input} onChange={(event) => setInput(event.target.value)} />
        <button className="classify-button" onClick={generateTests} disabled={status === "running"}>
          {status === "running" ? <Cpu className="spin" size={18} /> : <ClipboardCheck size={18} />}
          {status === "running" ? "Generating" : "Generate Test Plan"}
        </button>
        {error && <div className="api-error">{error}</div>}
      </div>
      <div className="module-output qaforge-output">
        <span className="output-kicker">QA OUTPUT</span>
        {result ? (
          <>
            <strong>{result.coverage.coverage_percent}% coverage</strong>
            <p>{result.requirement_summary}</p>
            <div className="coverage-grid">
              <div>
                <span>Test cases</span>
                <b>{result.coverage.test_case_count}</b>
              </div>
              <div>
                <span>Fragments covered</span>
                <b>{result.coverage.covered_fragments}/{result.coverage.requirement_fragments}</b>
              </div>
              <div>
                <span>Checks passed</span>
                <b>{result.quality_checks.filter((check) => check.status === "pass").length}/{result.quality_checks.length}</b>
              </div>
            </div>
            <div className="qa-case-grid">
              {result.generated_cases.slice(0, 4).map((testCase) => (
                <div key={testCase.id}>
                  <span>{testCase.id} - {testCase.type}</span>
                  <b>{testCase.title}</b>
                  <p>{testCase.expected_result}</p>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <strong>Waiting for requirement</strong>
            <p>Send a triage finding or enter a requirement to generate traceable QA artifacts.</p>
          </>
        )}
      </div>
    </Scene>
  );
}

function TrainingScene() {
  return (
    <Scene
      id="training"
      eyebrow="Scene 07 / Model Training Chamber"
      title="Models compete under controlled experiments."
      body="TF-IDF Logistic Regression is the baseline. PyTorch TextCNN is trained locally with CUDA and compared against held-out and challenge data."
      className="training-scene"
    >
      <div className="engine-row">
        <ModelEngine icon={<Radar />} name="TF-IDF" score="0.972" caption="Challenge macro-F1" />
        <ModelEngine icon={<Activity />} name="LogReg" score="0.972" caption="Interpretable baseline" />
        <ModelEngine icon={<BrainCircuit />} name="PyTorch" score="0.863" caption="TextCNN challenge F1" />
      </div>
      <div className="training-beam" />
    </Scene>
  );
}

function ModelEngine({ icon, name, score, caption }) {
  return (
    <div className="model-engine">
      <div className="engine-ring">{icon}</div>
      <strong>{name}</strong>
      <span>{score}</span>
      <p>{caption}</p>
    </div>
  );
}

function findSplit(metricsData, name) {
  return metricsData?.metrics?.evaluation_splits?.find((split) => split.name === name);
}

function modelMetric(metricsData, splitName, modelName, key) {
  const split = findSplit(metricsData, splitName);
  const model = split?.models?.find((item) => item.model === modelName);
  return model?.[key];
}

function EvaluationScene({ metricsData }) {
  const challengeF1 = modelMetric(metricsData, "manual_challenge", "pytorch_textcnn", "macro_f1") ?? 0.863;
  const baselineF1 = modelMetric(metricsData, "manual_challenge", "tfidf_logistic_regression", "macro_f1") ?? 0.972;
  const dynamicMetrics = [
    { label: "Baseline Challenge F1", value: baselineF1.toFixed(3) },
    { label: "TextCNN Challenge F1", value: challengeF1.toFixed(3) },
    { label: "Manual Challenge", value: String(metricsData?.metrics?.challenge_dataset?.total_records ?? 36) },
    { label: "Training Reports", value: String(metricsData?.metrics?.dataset?.total_records ?? 540) },
  ];

  return (
    <Scene
      id="evaluation"
      eyebrow="Scene 08 / Evaluation Arena"
      title="The confusion matrix becomes a holographic wall."
      body="Correct predictions glow blue. Misclassifications glow orange and become evidence for the next dataset iteration."
      className="evaluation-scene"
    >
      <Asset src="/assets/confusion-matrix-engine.svg" className="matrix-engine" alt="Confusion matrix engine" />
      <div className="metric-constellation">
        {dynamicMetrics.map((metric, index) => (
          <div className="floating-metric" key={metric.label} style={{ animationDelay: `${index * 0.35}s` }}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </div>
    </Scene>
  );
}

function DatasetAnalysisScene({ metricsData }) {
  const distribution = metricsData?.metrics?.dataset?.label_distribution ?? {
    software_bug: 90,
    requirement_gap: 90,
    test_environment_issue: 90,
    data_issue: 90,
    performance_issue: 90,
    integration_issue: 90,
  };
  const challengeSplit = findSplit(metricsData, "manual_challenge");
  const textcnn = challengeSplit?.models?.find((model) => model.model === "pytorch_textcnn");
  const matrix = textcnn?.confusion_matrix ?? [
    [6, 0, 0, 0, 0, 0],
    [0, 4, 1, 0, 1, 0],
    [0, 0, 5, 0, 0, 1],
    [0, 0, 1, 5, 0, 0],
    [0, 0, 0, 0, 6, 0],
    [0, 0, 1, 0, 0, 5],
  ];
  const maxValue = Math.max(...Object.values(distribution));

  return (
    <Scene
      id="analysis"
      eyebrow="Scene 08B / Dataset Observatory"
      title="The numbers are visible, not hidden."
      body="IssueSense separates synthetic training data from manual challenge evaluation, then exposes class balance, confusion patterns, and experiment runs."
      className="analysis-scene"
    >
      <div className="analysis-lab">
        <div className="class-bars">
          {Object.entries(distribution).map(([label, value]) => (
            <div className="class-bar" key={label}>
              <span>{displayLabel(label)}</span>
              <div>
                <i style={{ width: `${(value / maxValue) * 100}%` }} />
              </div>
              <b>{value}</b>
            </div>
          ))}
        </div>
        <div className="matrix-grid">
          {matrix.flatMap((row, rowIndex) =>
            row.map((value, columnIndex) => (
              <span
                key={`${rowIndex}-${columnIndex}`}
                className={rowIndex === columnIndex ? "correct-cell" : value > 0 ? "error-cell" : ""}
                style={{ opacity: value ? 0.45 + value / 10 : 0.18 }}
              >
                {value}
              </span>
            ))
          )}
        </div>
        <div className="experiment-strip">
          {(metricsData?.runs ?? []).slice(-3).map((run) => (
            <div key={run.run_id}>
              <span>{run.run_id}</span>
              <b>{run.dataset_version.synthetic_records} synthetic / {run.dataset_version.challenge_records} challenge</b>
            </div>
          ))}
        </div>
      </div>
    </Scene>
  );
}

function ExplainScene({ result }) {
  const examples = result?.explanation?.similar_examples ?? [];
  return (
    <Scene
      id="explain"
      eyebrow="Scene 09 / Inspect Deeper"
      title="Open the triage finding and inspect the cause."
      body="A shallow label is not enough. The deeper view shows likely cause, evidence, uncertainty, and next investigation steps for the engineering workflow."
      className="explain-scene"
    >
      <Asset src="/assets/rag-network.svg" className="rag-network" alt="RAG-style evidence network" />
      <div className="reasoning-panel">
        <span>QUERY</span>
        <p>{result?.query ?? "Classify an issue in the triage console to send a live query into this network."}</p>
        <strong>
          Prediction: {result ? `${outputTitle(result)} (${displayLabel(result.label)})` : "Waiting for model output"}
        </strong>
        {result?.triage && (
          <div className="deep-inspection">
            <div>
              <span>LIKELY CAUSE</span>
              <b>{result.triage.likely_cause}</b>
            </div>
            <p>{result.triage.cause_rationale}</p>
            <ol>
              {result.triage.next_investigation_steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
        )}
        {result?.review_reasons?.length > 0 && (
          <div className="review-panel">
            {result.review_reasons.map((reason) => (
              <p key={reason}>{reason}</p>
            ))}
          </div>
        )}
        {examples.length > 0 && (
          <div className="evidence-stack">
            {examples.slice(0, 3).map((example) => (
              <div className="evidence-chip" key={example.id}>
                <b>{example.id}</b>
                <span>{displayLabel(example.label)} · {example.similarity.toFixed(2)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Scene>
  );
}

function FinalScene() {
  return (
    <section className="final-scene">
      <ParticleField count={160} />
      <div className="final-grid" />
      <motion.div
        className="final-core"
        initial={{ scale: 0.75, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.9 }}
      >
        <Atom size={96} />
      </motion.div>
      <div className="final-copy">
        <span className="system-chip">ENGINEERING INTELLIGENCE SUITE</span>
        <h2>Engineering Intelligence, Explained.</h2>
        <p>IssueSense ML classifies the issue. EngiAgent expands it into an investigation and 8D draft. QAForge AI converts the risk into requirement-linked test coverage.</p>
        <a href="#top">Explore the Future of Engineering AI</a>
      </div>
    </section>
  );
}

function NavRail() {
  return (
    <nav className="nav-rail" aria-label="Scene navigation">
      {["top", "triage", "data", "core", "suite", "engiagent", "qaforge", "training", "evaluation", "analysis", "explain"].map((item) => (
        <a href={`#${item}`} key={item}>
          <Sparkles size={14} />
        </a>
      ))}
    </nav>
  );
}

export function App() {
  const [result, setResult] = useState(null);
  const [metricsData, setMetricsData] = useState(null);
  const [engiInput, setEngiInput] = useState(defaultIssue);
  const [engiResult, setEngiResult] = useState(null);
  const [qaInput, setQaInput] = useState(defaultRequirement);
  const [qaResult, setQaResult] = useState(null);

  function sendToEngiAgent(issueText, triageResult) {
    const cause = triageResult?.triage?.likely_cause
      ? `\n\nLikely cause from IssueSense: ${triageResult.triage.likely_cause}`
      : "";
    setEngiInput(`${issueText}${cause}`);
    document.getElementById("engiagent")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function sendToQAForge(issueText, triageResult) {
    const label = triageResult?.label ? displayLabel(triageResult.label) : "Engineering Risk";
    const cause = triageResult?.triage?.likely_cause ?? "reported engineering issue";
    setQaInput(
      `Requirement: the system must handle the scenario without recurring ${label.toLowerCase()}.\n` +
        `Risk context: ${issueText}\n` +
        `Likely cause: ${cause}.\n` +
        "Generate tests for expected behavior, invalid input, edge cases, regression, and integration impact."
    );
    document.getElementById("qaforge")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  useEffect(() => {
    fetch(`${apiUrl}/metrics`)
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => {
        if (data) {
          setMetricsData(data);
        }
      })
      .catch(() => setMetricsData(null));

    const animated = gsap.utils.toArray(".scene, .final-scene");
    animated.forEach((section) => {
      gsap.fromTo(
        section.querySelectorAll(".scene-copy, .model-engine, .floating-metric, .reasoning-panel"),
        { y: 80, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 1,
          stagger: 0.08,
          ease: "power3.out",
          scrollTrigger: {
            trigger: section,
            start: "top 70%",
          },
        }
      );
    });

    gsap.to(".stream-one", {
      xPercent: 12,
      repeat: -1,
      yoyo: true,
      duration: 5,
      ease: "sine.inOut",
    });
    gsap.to(".stream-two", {
      xPercent: -10,
      repeat: -1,
      yoyo: true,
      duration: 6.5,
      ease: "sine.inOut",
    });
    gsap.to(".ai-core", {
      rotate: 360,
      duration: 44,
      repeat: -1,
      ease: "none",
    });
    gsap.to(".matrix-engine", {
      y: -18,
      repeat: -1,
      yoyo: true,
      duration: 3,
      ease: "sine.inOut",
    });

    return () => ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
  }, []);

  return (
    <main id="top">
      <NavRail />
      <IntroScene />
      <TriageScene
        result={result}
        setResult={setResult}
        onSendToEngiAgent={sendToEngiAgent}
        onSendToQAForge={sendToQAForge}
      />
      <DataScene />
      <CoreScene result={result} />
      <SuiteMapScene />
      <EngiAgentScene
        input={engiInput}
        setInput={setEngiInput}
        triageResult={result}
        result={engiResult}
        setResult={setEngiResult}
      />
      <QAForgeScene
        input={qaInput}
        setInput={setQaInput}
        triageResult={result}
        result={qaResult}
        setResult={setQaResult}
      />
      <TrainingScene />
      <EvaluationScene metricsData={metricsData} />
      <DatasetAnalysisScene metricsData={metricsData} />
      <ExplainScene result={result} />
      <FinalScene />
      <div className="ambient-glow ambient-a" />
      <div className="ambient-glow ambient-b" />
      <Gauge className="corner-glyph" />
      <Network className="corner-glyph second" />
    </main>
  );
}
