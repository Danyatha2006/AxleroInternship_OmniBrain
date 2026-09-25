import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, AlertTriangle, BarChart3, Bot, Check, CheckCircle2, ChevronDown,
  ChevronRight, CircleHelp, Clock3, Copy, Cpu, Database, FileImage,
  FileText, FolderOpen, Gauge, Image as ImageIcon, Info, Layers3, LayoutDashboard,
  Menu, MessageSquare, MoreHorizontal, Paperclip, Plus, RefreshCw, Search,
  Send, Settings, ShieldCheck, Sparkles, Table2, UploadCloud, X, Zap
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const DEMO_MODE = String(import.meta.env.VITE_DEMO_MODE || "false").toLowerCase() === "true";

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

const demoDocument = {
  document_id: "demo-omnibrain",
  filename: "data science.pdf",
  status: "completed",
  pages: 6,
  words: 1847,
  sentences: 118,
  tables: 3,
  images: 7
};

const demoImages = [
  { id: 1, page: 1, title: "Project architecture / overview", type: "diagram" },
  { id: 2, page: 2, title: "Week-wise development plan", type: "table" },
  { id: 3, page: 3, title: "Federated Learning architecture", type: "diagram" },
  { id: 4, page: 5, title: "3D Simulation UI", type: "visual" }
];

const demoAnswer = {
  answer:
    "OmniBrain is an Agentic Multi-Modal RAG Orchestrator. Its goal is to answer questions over complex documents by combining a LangGraph supervisor with specialized Search, SQL and Vision agents. The system is designed to retrieve grounded context, reason over visual content, and return cited answers rather than relying only on a standard LLM.",
  sources: [
    { document_name: "data science.pdf", page_number: 1, score: 0.96, content_type: "text", text: "Project 1 — OmniBrain: Agentic Multi-Modal RAG Orchestrator." },
    { document_name: "data science.pdf", page_number: 1, score: 0.93, content_type: "text", text: "The LangGraph supervisor dynamically routes tasks to specialized AI agents." },
    { document_name: "data science.pdf", page_number: 2, score: 0.88, content_type: "image", text: "Week-wise development plan.", image_reference: "Visual reference · page 2" }
  ],
  trace: [
    { agent: "Supervisor", action: "Classified query", detail: "Document-grounded semantic search", time: "42 ms", state: "done" },
    { agent: "Search Agent", action: "Qdrant retrieval", detail: "Retrieved 5 relevant chunks", time: "118 ms", state: "done" },
    { agent: "Vision Agent", action: "Visual check", detail: "Inspected page 2 reference", time: "164 ms", state: "done" },
    { agent: "Self-RAG", action: "Relevance verification", detail: "Context accepted on first pass", time: "61 ms", state: "done" },
    { agent: "Guardrails", action: "Grounding check", detail: "Response stays within document scope", time: "29 ms", state: "done" }
  ],
  metrics: { latency: 414, tokens: 623, retrieved: 5, confidence: 94 }
};

function App() {
  const [mobileNav, setMobileNav] = useState(false);
  const [document, setDocument] = useState(null);
  const [status, setStatus] = useState("idle");
  const [chat, setChat] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [activeView, setActiveView] = useState("chat");
  const [selectedSource, setSelectedSource] = useState(null);
  const [showTrace, setShowTrace] = useState(true);
  const [images, setImages] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const inputRef = useRef(null);

  const ready = status === "completed" || document?.status === "completed";
  const latestAssistant = [...chat].reverse().find(m => m.role === "assistant");
  const currentTrace = latestAssistant?.trace || demoAnswer.trace;
  const currentMetrics = latestAssistant?.metrics || demoAnswer.metrics;

  useEffect(() => {
    const saved = localStorage.getItem("omnibrain_document");
    if (saved) {
      try {
        const doc = JSON.parse(saved);
        setDocument(doc);
        setStatus(doc.status || "completed");
      } catch {}
    }
  }, []);

  useEffect(() => {
    if (!document?.document_id || document.document_id === "demo-omnibrain") return;
    let active = true;
    Promise.all([
      api(`/api/v1/chat/${document.document_id}/history`).catch(() => null),
      api(`/api/v1/documents/${document.document_id}/analytics`).catch(() => null),
      api(`/api/v1/documents/${document.document_id}/images`).catch(() => null)
    ]).then(([history, stats, imgs]) => {
      if (!active) return;
      if (history?.history) {
        setChat(history.history.flatMap(x => [
          { role: "user", content: x.question },
          { role: "assistant", content: x.answer, sources: x.sources || [], trace: x.trace, metrics: x.metrics }
        ]));
      }
      if (stats) setAnalytics(stats);
      if (imgs?.images) setImages(imgs.images);
    });
    return () => { active = false; };
  }, [document?.document_id]);

  async function upload(file) {
    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are allowed.");
      return;
    }
    setError("");
    setUploading(true);
    setStatus("uploading");

    if (DEMO_MODE) {
      setTimeout(() => {
        const doc = { ...demoDocument, filename: file.name, uploadedAt: new Date().toISOString() };
        setDocument(doc);
        setStatus("completed");
        setUploading(false);
        setImages(demoImages);
        setAnalytics(doc);
      }, 800);
      return;
    }

    try {
      const fd = new FormData();
      fd.append("file", file);
      const d = await api("/api/v1/documents/upload", { method: "POST", body: fd });
      const doc = { document_id: d.document_id, filename: d.filename, status: "pending", uploadedAt: new Date().toISOString() };
      setDocument(doc);
      localStorage.setItem("omnibrain_document", JSON.stringify(doc));
      setStatus("processing");

      let tries = 0;
      const poll = setInterval(async () => {
        try {
          const s = await api(`/api/v1/documents/${d.document_id}/status`);
          tries++;
          setStatus(s.status);
          setDocument(prev => ({ ...prev, status: s.status }));
          if (s.status === "completed" || s.status === "failed" || tries > 40) {
            clearInterval(poll);
            setUploading(false);
          }
        } catch (e) {
          clearInterval(poll);
          setUploading(false);
          setError(e.message);
        }
      }, 1500);
    } catch (e) {
      setUploading(false);
      setStatus("error");
      setError(e.message);
    }
  }

  async function sendQuestion(text = input) {
    text = text.trim();
    if (!text || !document?.document_id || !ready || loading) return;
    setError("");
    setInput("");
    setLoading(true);
    setChat(prev => [...prev, { role: "user", content: text }]);

    if (DEMO_MODE || document.document_id === "demo-omnibrain") {
      setTimeout(() => {
        setChat(prev => [...prev, { role: "assistant", ...demoAnswer }]);
        setLoading(false);
        inputRef.current?.focus();
      }, 700);
      return;
    }

    try {
      const d = await api("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: document.document_id, question: text, top_k: 5 })
      });
      setChat(prev => [...prev, {
        role: "assistant",
        content: d.answer || "No answer returned.",
        sources: d.sources || [],
        trace: d.trace || [],
        metrics: d.metrics || null
      }]);
    } catch (e) {
      setError(e.message);
      setChat(prev => [...prev, {
        role: "assistant",
        content: "I could not process that request. Check the FastAPI connection or switch to demo mode.",
        sources: []
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function newChat() {
    setChat([]);
    setInput("");
    setActiveView("chat");
  }

  function loadDemo() {
    setDocument(demoDocument);
    setStatus("completed");
    setImages(demoImages);
    setAnalytics(demoDocument);
    localStorage.setItem("omnibrain_document", JSON.stringify(demoDocument));
  }

  const nav = [
    { id: "chat", label: "AI Chat", icon: MessageSquare },
    { id: "documents", label: "Document", icon: FileText },
    { id: "images", label: "Images & Charts", icon: ImageIcon },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "trace", label: "Agent Trace", icon: Activity }
  ];

  return (
    <div className="app">
      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <div className="brand">
          <div className="brandMark"><Sparkles size={18} /></div>
          <div><strong>OmniBrain</strong><span>Multi-Modal RAG</span></div>
        </div>

        <button className="newChat" onClick={newChat}><Plus size={17} /> New conversation</button>

        <div className="navGroup">
          <div className="navLabel">WORKSPACE</div>
          {nav.map(({ id, label, icon: Icon }) => (
            <button key={id} className={`navItem ${activeView === id ? "active" : ""}`} onClick={() => { setActiveView(id); setMobileNav(false); }}>
              <Icon size={17} /> {label}
              {id === "images" && <span className="count">{images.length}</span>}
            </button>
          ))}
        </div>

        <div className="sideDoc">
          <div className="navLabel">CURRENT PDF</div>
          {document ? (
            <div className="docMini">
              <div className="miniFile"><FileText size={16} /></div>
              <div className="docMiniText">
                <strong>{document.filename}</strong>
                <span><i className={`dot ${ready ? "ready" : ""}`} /> {ready ? "Indexed & ready" : "Processing…"}</span>
              </div>
              <MoreHorizontal size={15} />
            </div>
          ) : (
            <div className="emptyDoc">Upload a PDF to begin</div>
          )}
        </div>

        <div className="sidebarBottom">
          <button className="navItem"><Settings size={17} /> Settings</button>
          <button className="navItem"><CircleHelp size={17} /> Help</button>
          <div className="profile">
            <div className="avatar">O</div>
            <div><strong>OmniBrain User</strong><span>Research workspace</span></div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="mobileMenu" onClick={() => setMobileNav(!mobileNav)}><Menu /></button>
          <div className="topTitle">
            <span className="eyebrow">AGENTIC MULTI-MODAL RAG</span>
            <h1>{document?.filename || "Document Intelligence Workspace"}</h1>
          </div>
          <div className="topActions">
            <span className={`connection ${DEMO_MODE || document?.document_id === "demo-omnibrain" ? "demo" : ""}`}>
              <i /> {DEMO_MODE || document?.document_id === "demo-omnibrain" ? "Demo mode" : "Backend ready"}
            </span>
            <button className="iconBtn"><Settings size={17} /></button>
          </div>
        </header>

        {!document && (
          <section className="landing">
            <div className="landingGlow" />
            <div className="heroIcon"><Sparkles size={27} /></div>
            <div className="kicker">OMNIBRAIN WORKSPACE</div>
            <h2>Ask anything about a PDF.<br /><span>See where every answer came from.</span></h2>
            <p>Upload a document and explore grounded answers, extracted visuals, exact-page citations, document statistics, and the agent reasoning trace.</p>
            <UploadDrop onUpload={upload} uploading={uploading} />
            <button className="demoLink" onClick={loadDemo}><Zap size={14} /> Open interactive demo with sample data</button>

            <div className="capabilityGrid">
              <Capability icon={<Search />} title="Semantic Search" text="Retrieve the most relevant text chunks from Qdrant." />
              <Capability icon={<ImageIcon />} title="Vision Retrieval" text="Surface charts, diagrams and extracted document images." />
              <Capability icon={<Bot />} title="Agent Routing" text="Show how Supervisor, Search and Vision agents collaborate." />
              <Capability icon={<ShieldCheck />} title="Grounded Answers" text="Expose citations and guardrail status with every response." />
            </div>
          </section>
        )}

        {document && (
          <section className="workspace">
            <div className="workspaceHeader">
              <div>
                <span className="eyebrow">{ready ? "DOCUMENT READY" : "PROCESSING DOCUMENT"}</span>
                <h2>{viewTitle(activeView)}</h2>
              </div>
              <div className="headerBadges">
                <StatusBadge ready={ready} status={status} />
                {ready && <span className="secureBadge"><ShieldCheck size={13} /> Grounded</span>}
              </div>
            </div>

            {activeView === "chat" && (
              <ChatView
                chat={chat}
                loading={loading}
                ready={ready}
                input={input}
                setInput={setInput}
                sendQuestion={sendQuestion}
                inputRef={inputRef}
                selectedSource={selectedSource}
                setSelectedSource={setSelectedSource}
                showTrace={showTrace}
                setShowTrace={setShowTrace}
                currentTrace={currentTrace}
                currentMetrics={currentMetrics}
                onUpload={upload}
              />
            )}

            {activeView === "documents" && (
              <DocumentView document={document} ready={ready} status={status} analytics={analytics} onUpload={upload} />
            )}

            {activeView === "images" && (
              <ImagesView images={images.length ? images : demoImages} filename={document.filename} />
            )}

            {activeView === "analytics" && (
              <AnalyticsView analytics={analytics || document || demoDocument} metrics={currentMetrics} />
            )}

            {activeView === "trace" && (
              <TraceView trace={currentTrace} metrics={currentMetrics} />
            )}
          </section>
        )}

        {error && <div className="toast"><AlertTriangle size={16} /><span>{error}</span><X size={16} onClick={() => setError("")} /></div>}
      </main>
    </div>
  );
}

function viewTitle(view) {
  return {
    chat: "AI document chat",
    documents: "Document overview",
    images: "Images & charts",
    analytics: "Document analytics",
    trace: "Agent execution trace"
  }[view];
}

function StatusBadge({ ready, status }) {
  return <span className={`statusBadge ${ready ? "ready" : "processing"}`}><i /> {ready ? "Ready" : status === "processing" ? "Processing" : "Waiting"}</span>;
}

function UploadDrop({ onUpload, uploading }) {
  const ref = useRef();
  const [drag, setDrag] = useState(false);
  return (
    <div
      className={`upload ${drag ? "drag" : ""}`}
      onDragOver={e => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={e => { e.preventDefault(); setDrag(false); onUpload(e.dataTransfer.files?.[0]); }}
    >
      <div className="uploadIcon"><UploadCloud size={25} /></div>
      <h3>{uploading ? "Uploading your PDF…" : "Drop your PDF here"}</h3>
      <p>{uploading ? "OmniBrain is starting the ingestion pipeline." : "or click to browse from your computer"}</p>
      <button onClick={() => ref.current?.click()} disabled={uploading}>{uploading ? "Uploading…" : "Choose PDF"}</button>
      <input ref={ref} type="file" accept="application/pdf,.pdf" hidden onChange={e => onUpload(e.target.files?.[0])} />
      <span className="uploadMeta">PDF only · text + images · multi-modal retrieval</span>
    </div>
  );
}

function Capability({ icon, title, text }) {
  return <div className="capability"><div className="capIcon">{icon}</div><div><strong>{title}</strong><span>{text}</span></div></div>;
}

function ChatView(props) {
  const { chat, loading, ready, input, setInput, sendQuestion, inputRef, selectedSource, setSelectedSource, showTrace, setShowTrace, currentTrace, currentMetrics } = props;
  const suggestions = [
    "Summarize this document",
    "How many pages, words and sentences are there?",
    "What are the key modules of OmniBrain?",
    "Explain the week-wise development plan",
    "Which page contains the most relevant visual?"
  ];

  return (
    <div className="chatLayout">
      <div className="chatPanel">
        <div className="panelHead">
          <div><span className="eyebrow">GROUNDED ASSISTANT</span><h3>Ask your document</h3></div>
          <div className="miniStats"><span><Database size={12} /> Qdrant</span><span><ShieldCheck size={12} /> Guardrails</span></div>
        </div>

        <div className="messages">
          {!chat.length && ready && (
            <div className="chatWelcome">
              <div className="botCircle"><Bot size={22} /></div>
              <h3>Your document is ready.</h3>
              <p>Ask a factual question, request a summary, inspect a page, or ask for document statistics.</p>
              <div className="suggestions">
                {suggestions.map(s => <button key={s} onClick={() => sendQuestion(s)}>{s}<ChevronRight size={14} /></button>)}
              </div>
            </div>
          )}

          {!ready && !chat.length && (
            <div className="processingCard">
              <div className="loader"><span /><span /><span /></div>
              <div><strong>Preparing your document</strong><p>PDF ingestion → chunking → embeddings → Qdrant indexing.</p></div>
            </div>
          )}

          {chat.map((m, i) => (
            <React.Fragment key={i}>
              <div className={`message ${m.role}`}>
                {m.role === "assistant" && <div className="smallBot"><Bot size={15} /></div>}
                <div className="bubble">
                  {m.role === "assistant" && <div className="answerLabel"><CheckCircle2 size={12} /> Grounded answer</div>}
                  <div>{m.content}</div>
                </div>
              </div>

              {m.role === "assistant" && m.sources?.length > 0 && (
                <div className="sources">
                  <div className="sourceHeading"><span>REFERENCES</span><b>{m.sources.length}</b><small>Click a source to inspect it</small></div>
                  {m.sources.map((s, j) => (
                    <SourceCard key={j} source={s} selected={selectedSource === `${i}-${j}`} onClick={() => setSelectedSource(selectedSource === `${i}-${j}` ? null : `${i}-${j}`)} />
                  ))}
                </div>
              )}

              {m.role === "assistant" && (
                <div className="answerMeta">
                  <span><Clock3 size={12} /> {m.metrics?.latency || currentMetrics.latency} ms</span>
                  <span><Cpu size={12} /> {m.metrics?.tokens || currentMetrics.tokens} tokens</span>
                  <span><Gauge size={12} /> {m.metrics?.confidence || currentMetrics.confidence}% confidence</span>
                </div>
              )}
            </React.Fragment>
          ))}

          {loading && <div className="message assistant"><div className="smallBot"><Bot size={15} /></div><div className="bubble loadingBubble"><span /><span /><span /></div></div>}
        </div>

        <div className="composerWrap">
          <div className="composer">
            <button className="attach"><Paperclip size={17} /></button>
            <input ref={inputRef} disabled={!ready || loading} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendQuestion()} placeholder={ready ? "Ask anything about this PDF…" : "Waiting for document processing…"} />
            <button className="send" disabled={!ready || loading || !input.trim()} onClick={() => sendQuestion()}><Send size={16} /></button>
          </div>
          <div className="composerFoot"><span>Responses are grounded in retrieved document context.</span><span>Enter ↵</span></div>
        </div>
      </div>

      <aside className="inspector">
        <div className="inspectorHead">
          <div><span className="eyebrow">LIVE INSPECTOR</span><h3>AI pipeline</h3></div>
          <button className="iconBtn small" onClick={() => setShowTrace(!showTrace)}>{showTrace ? <ChevronDown size={15} /> : <ChevronRight size={15} />}</button>
        </div>

        <div className="pipelineCards">
          <Pipeline icon={<Layers3 />} label="Supervisor" state="Routes query" />
          <Pipeline icon={<Search />} label="Search Agent" state={`${currentMetrics.retrieved} chunks retrieved`} />
          <Pipeline icon={<ImageIcon />} label="Vision Agent" state="Visual references ready" />
          <Pipeline icon={<RefreshCw />} label="Self-RAG" state="Relevance checked" />
          <Pipeline icon={<ShieldCheck />} label="NeMo Guardrails" state="Scope protected" />
        </div>

        {showTrace && <TraceCompact trace={currentTrace} />}
      </aside>
    </div>
  );
}

function Pipeline({ icon, label, state }) {
  return <div className="pipeline"><div className="pipelineIcon">{icon}</div><div><strong>{label}</strong><span>{state}</span></div><Check size={14} className="pipelineCheck" /></div>;
}

function TraceCompact({ trace }) {
  return (
    <div className="traceCompact">
      <div className="sectionTitle"><span>EXECUTION TRACE</span><span>{trace.length} steps</span></div>
      {trace.map((t, i) => (
        <div className="traceRow" key={i}>
          <div className="traceLine"><i /><em /></div>
          <div><strong>{t.agent}</strong><span>{t.action}</span><small>{t.time} · {t.detail}</small></div>
        </div>
      ))}
    </div>
  );
}

function SourceCard({ source, selected, onClick }) {
  const isImage = source.content_type === "image";
  return (
    <div className={`sourceCard ${selected ? "selected" : ""}`}>
      <button onClick={onClick}>
        <div className={`sourceType ${isImage ? "image" : ""}`}>{isImage ? <ImageIcon size={14} /> : <FileText size={14} />}</div>
        <div className="sourceMain">
          <strong>{source.document_name || "Document source"}</strong>
          <span>Page {source.page_number || "—"} · {(source.score * 100).toFixed(0)}% relevance</span>
        </div>
        <ChevronDown size={15} className={selected ? "rotate" : ""} />
      </button>
      {selected && (
        <div className="sourceDetail">
          <div className="citationBadge"><FileText size={12} /> Exact citation · page {source.page_number}</div>
          <p>{source.text || "Visual reference available for this result."}</p>
          {source.image_reference && <div className="imageRef"><ImageIcon size={13} /> {source.image_reference}</div>}
          <button className="pageButton"><Search size={12} /> Open referenced page</button>
        </div>
      )}
    </div>
  );
}

function DocumentView({ document, ready, status, analytics, onUpload }) {
  const stats = analytics || demoDocument;
  return (
    <div className="viewGrid">
      <section className="card documentHero">
        <div className="fileLarge"><FileText size={27} /></div>
        <div className="documentTitle"><span className="eyebrow">ACTIVE DOCUMENT</span><h3>{document.filename}</h3><p>PDF · {ready ? "Indexed and available for grounded querying" : "Currently being processed"}</p></div>
        <StatusBadge ready={ready} status={status} />
      </section>

      <div className="statGrid">
        <StatCard icon={<FileText />} label="Pages" value={stats.pages ?? "—"} />
        <StatCard icon={<FileText />} label="Words" value={stats.words ?? "—"} />
        <StatCard icon={<MessageSquare />} label="Sentences" value={stats.sentences ?? "—"} />
        <StatCard icon={<Table2 />} label="Tables" value={stats.tables ?? "—"} />
        <StatCard icon={<ImageIcon />} label="Images" value={stats.images ?? "—"} />
      </div>

      <section className="card">
        <div className="cardHead"><div><span className="eyebrow">INGESTION PIPELINE</span><h3>Document processing</h3></div><span className="successText"><CheckCircle2 size={14} /> {ready ? "Complete" : "In progress"}</span></div>
        <div className="ingestionSteps">
          <IngestStep number="01" title="PDF parsed" done={ready} detail="Text and page structure extracted" />
          <IngestStep number="02" title="Images extracted" done={ready} detail="Charts and visual references prepared" />
          <IngestStep number="03" title="Embeddings created" done={ready} detail="Semantic representations generated" />
          <IngestStep number="04" title="Qdrant indexed" done={ready} detail="Text + image retrieval available" />
        </div>
      </section>

      <section className="card splitCard">
        <div><span className="eyebrow">INTEGRATION</span><h3>Ready for your team's backend</h3><p>The UI is intentionally separated from the FastAPI service. Keep the frontend and connect the API base URL when the group's routes are finalized.</p></div>
        <div className="apiBox"><span>API BASE</span><code>{API}</code><div><Check size={12} /> Frontend adapter configured</div></div>
      </section>
    </div>
  );
}

function IngestStep({ number, title, done, detail }) {
  return <div className={`ingestStep ${done ? "done" : ""}`}><div className="stepNo">{done ? <Check size={14} /> : number}</div><div><strong>{title}</strong><span>{detail}</span></div></div>;
}

function StatCard({ icon, label, value }) {
  return <div className="statCard"><div className="statIcon">{icon}</div><span>{label}</span><strong>{value}</strong></div>;
}

function ImagesView({ images, filename }) {
  return (
    <div className="imagesView">
      <div className="imagesIntro card">
        <div><span className="eyebrow">MULTI-MODAL INDEX</span><h3>Extracted images & charts</h3><p>Visual references returned by the retrieval layer can be surfaced next to grounded answers.</p></div>
        <div className="visualCount"><ImageIcon size={18} /><strong>{images.length}</strong><span>visual refs</span></div>
      </div>
      <div className="imageGrid">
        {images.map(img => <div className="imageTile card" key={img.id}>
          <div className="fakeVisual"><div className="visualTop"><span>PAGE {img.page}</span><ImageIcon size={15} /></div><div className="visualShape">{img.type === "table" ? <Table2 size={42} /> : <BarChart3 size={46} />}</div><div className="pageTag">PDF · {filename}</div></div>
          <div className="imageTileInfo"><strong>{img.title}</strong><span>Page {img.page} · {img.type}</span><button><Search size={12} /> View reference</button></div>
        </div>)}
      </div>
    </div>
  );
}

function AnalyticsView({ analytics, metrics }) {
  const items = [
    ["Pages", analytics.pages ?? "—", FileText],
    ["Words", analytics.words ?? "—", FileText],
    ["Sentences", analytics.sentences ?? "—", MessageSquare],
    ["Tables", analytics.tables ?? "—", Table2],
    ["Images", analytics.images ?? "—", ImageIcon]
  ];
  return (
    <div className="analyticsGrid">
      <div className="card analyticsMain">
        <div className="cardHead"><div><span className="eyebrow">DOCUMENT STATISTICS</span><h3>Content overview</h3></div><BarChart3 size={18} /></div>
        <div className="bigStats">{items.map(([label, value, Icon]) => <div className="bigStat" key={label}><Icon size={17} /><span>{label}</span><strong>{value}</strong></div>)}</div>
        <div className="statBars">
          {items.slice(0, 5).map(([label, value]) => <div className="barRow" key={label}><span>{label}</span><div><i style={{ width: `${Math.min(100, Number(value) / Math.max(1, Number(analytics.words || 2000)) * 100 + 8)}%` }} /></div><b>{value}</b></div>)}
        </div>
      </div>
      <div className="card metricsCard">
        <span className="eyebrow">LATEST ANSWER</span><h3>Runtime metrics</h3>
        <Metric label="End-to-end latency" value={`${metrics.latency} ms`} />
        <Metric label="LLM tokens" value={metrics.tokens} />
        <Metric label="Retrieved chunks" value={metrics.retrieved} />
        <Metric label="Grounding confidence" value={`${metrics.confidence}%`} />
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

function TraceView({ trace, metrics }) {
  return (
    <div className="traceView">
      <section className="card traceSummary">
        <div><span className="eyebrow">LANGGRAPH EXECUTION</span><h3>How OmniBrain answered</h3><p>The trace makes the agentic flow visible instead of hiding it behind a single chat bubble.</p></div>
        <div className="traceSummaryStats"><div><strong>{trace.length}</strong><span>steps</span></div><div><strong>{metrics.latency}</strong><span>ms</span></div><div><strong>{metrics.retrieved}</strong><span>retrieved</span></div></div>
      </section>
      <section className="card fullTrace">
        {trace.map((t, i) => <div className="fullTraceRow" key={i}><div className="traceNumber">{String(i + 1).padStart(2, "0")}</div><div className="agentGlyph"><Bot size={16} /></div><div className="traceContent"><div><strong>{t.agent}</strong><span>{t.action}</span></div><p>{t.detail}</p></div><div className="traceTime"><CheckCircle2 size={14} /> {t.time}</div></div>)}
      </section>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
