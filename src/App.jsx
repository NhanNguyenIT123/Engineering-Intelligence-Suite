import { motion, useScroll, useTransform } from "framer-motion";
import { Activity, Atom, BrainCircuit, DatabaseZap, Gauge, Network, Radar, Sparkles } from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useMemo, useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

const categories = ["Software Defect", "Requirement Gap", "Test Environment", "Data Issue", "Performance Issue"];

const metrics = [
  { label: "Synthetic Test F1", value: "1.000" },
  { label: "Challenge F1", value: "0.863" },
  { label: "Manual Challenge", value: "36" },
  { label: "Training Reports", value: "540" },
];

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

function CoreScene() {
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
            className="category"
            key={category}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.12, duration: 0.55 }}
          >
            {category}
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

function ExplainScene() {
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
        <p>The ERP connector sends customerId but the CRM endpoint expects customer_id.</p>
        <strong>Prediction: Integration Issue</strong>
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
      {["top", "data", "core", "training", "evaluation", "explain"].map((item) => (
        <a href={`#${item}`} key={item}>
          <Sparkles size={14} />
        </a>
      ))}
    </nav>
  );
}

export function App() {
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
      <DataScene />
      <CoreScene />
      <TrainingScene />
      <EvaluationScene />
      <ExplainScene />
      <FinalScene />
      <div className="ambient-glow ambient-a" />
      <div className="ambient-glow ambient-b" />
      <Gauge className="corner-glyph" />
      <Network className="corner-glyph second" />
    </main>
  );
}
