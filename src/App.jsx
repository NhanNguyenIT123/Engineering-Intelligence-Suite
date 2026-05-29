import { motion, useScroll, useTransform } from "framer-motion";
import { Activity, Atom, BrainCircuit, Cpu, DatabaseZap, Gauge, Network, Play, Radar, Send, Sparkles } from "lucide-react";
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

const samples = [
  "The ERP connector sends customerId but the CRM endpoint now expects customer_id.",
  "Search response time increased from 300ms to 4.8s after importing 100k records.",
  "Test passes locally but fails on staging because the payment sandbox endpoint is unreachable.",
  "The specification does not mention what should happen when the user cancels payment after OTP verification.",
];

function displayLabel(label) {
  const match = categories.find((category) => category.value === label);
  return match?.label ?? label?.replaceAll("_", " ");
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
        <span className="system-chip">ENGINEERING ISSUE TRIAGE AI</span>
        <h1>IssueSense ML</h1>
        <p>Transform engineering issues into explainable AI insights.</p>
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

function TriageScene({ result, setResult }) {
  const [text, setText] = useState(defaultIssue);
  const [model, setModel] = useState("textcnn");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function classify() {
    setStatus("running");
    setError("");
    try {
      const response = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, model }),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail);
      }
      const data = await response.json();
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
      body="Paste an engineering issue or test-report finding. The cinematic layer calls the local Python model, then carries the prediction into the core and explanation scenes."
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
            <strong>{displayLabel(result.label)}</strong>
            <div className="confidence-ring">
              <span>{Math.round(result.confidence * 100)}%</span>
              confidence
            </div>
            <p>{result.explanation?.reason}</p>
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
      eyebrow="Scene 03 / AI Classification Core"
      title="A classifier at the center of the machine."
      body="The PyTorch TextCNN model learns issue patterns while the baseline model provides a transparent comparison point."
      className="core-scene"
    >
      <Asset src="/assets/ai-core.svg" className="ai-core" alt="AI classification core" />
      <div className="category-orbit">
        {categories.map((category, index) => (
          <motion.div
            className={`category ${result?.label === category.value ? "active-category" : ""}`}
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

function TrainingScene() {
  return (
    <Scene
      id="training"
      eyebrow="Scene 04 / Model Training Chamber"
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

function EvaluationScene() {
  return (
    <Scene
      id="evaluation"
      eyebrow="Scene 05 / Evaluation Arena"
      title="The confusion matrix becomes a holographic wall."
      body="Correct predictions glow blue. Misclassifications glow orange and become evidence for the next dataset iteration."
      className="evaluation-scene"
    >
      <Asset src="/assets/confusion-matrix-engine.svg" className="matrix-engine" alt="Confusion matrix engine" />
      <div className="metric-constellation">
        {metrics.map((metric, index) => (
          <div className="floating-metric" key={metric.label} style={{ animationDelay: `${index * 0.35}s` }}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </div>
    </Scene>
  );
}

function ExplainScene({ result }) {
  const examples = result?.explanation?.similar_examples ?? [];
  return (
    <Scene
      id="explain"
      eyebrow="Scene 06 / Explainable AI Network"
      title="Predictions are grounded in similar cases."
      body="The system retrieves nearest labeled issue examples so a prediction can be inspected instead of blindly trusted."
      className="explain-scene"
    >
      <Asset src="/assets/rag-network.svg" className="rag-network" alt="RAG-style evidence network" />
      <div className="reasoning-panel">
        <span>QUERY</span>
        <p>{result?.query ?? "Classify an issue in the triage console to send a live query into this network."}</p>
        <strong>Prediction: {result ? displayLabel(result.label) : "Waiting for model output"}</strong>
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
        <span className="system-chip">FUTURE ROADMAP</span>
        <h2>Engineering Intelligence, Explained.</h2>
        <p>More reviewed data. Better uncertainty handling. Stronger retrieval evidence. A clearer path from raw engineering reports to AI-assisted triage.</p>
        <a href="#top">Explore the Future of Engineering AI</a>
      </div>
    </section>
  );
}

function NavRail() {
  return (
    <nav className="nav-rail" aria-label="Scene navigation">
      {["top", "triage", "data", "core", "training", "evaluation", "explain"].map((item) => (
        <a href={`#${item}`} key={item}>
          <Sparkles size={14} />
        </a>
      ))}
    </nav>
  );
}

export function App() {
  const [result, setResult] = useState(null);

  useEffect(() => {
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
      <TriageScene result={result} setResult={setResult} />
      <DataScene />
      <CoreScene result={result} />
      <TrainingScene />
      <EvaluationScene />
      <ExplainScene result={result} />
      <FinalScene />
      <div className="ambient-glow ambient-a" />
      <div className="ambient-glow ambient-b" />
      <Gauge className="corner-glyph" />
      <Network className="corner-glyph second" />
    </main>
  );
}
