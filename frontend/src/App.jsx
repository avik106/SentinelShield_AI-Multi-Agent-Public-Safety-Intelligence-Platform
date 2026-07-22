import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Shield, 
  LayoutDashboard, 
  FileSearch, 
  Network, 
  MapPin, 
  MessageSquareCode, 
  FileText, 
  AlertTriangle,
  Upload,
  CheckCircle,
  Copy,
  Printer,
  Settings,
  Play,
  Send,
  ChevronDown,
  ChevronUp,
  Map,
  Clock,
  AlertCircle,
  TrendingUp,
  User,
  Info,
  DollarSign,
  Activity,
  Check,
  RefreshCw,
  Search,
  Download,
  Sparkles,
  ZoomIn,
  ZoomOut,
  Maximize2,
  FileJson,
  AlertOctagon
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// ─────────────────────────────────────────────────────────────────────────────
// High-Fidelity Demo Presets (Perfect for Hackathon Demos)
// ─────────────────────────────────────────────────────────────────────────────

const DEMO_PRESETS = [
  {
    id: "digital_arrest",
    title: "Delhi Police Digital Arrest Scam",
    case_id: "CASE-2026-7890",
    complainant_name: "Rohan Verma",
    complainant_contact: "+91 99887 76655",
    lat: "28.6139",
    lon: "77.2090",
    text_input: "Received a WhatsApp video call from a suspect claiming to be DCP Sanjay Sharma of the Delhi Police. He placed me under 'digital arrest' inside my room, claiming my Aadhaar ID was linked to money laundering. Under extreme threat of arrest, I transferred ₹50,000 via UPI to payment.police@paytm.",
    results: {
      case_id: "CASE-2026-7890",
      overall_risk_score: 0.92,
      risk_level: "CRITICAL",
      confidence: 0.94,
      scam_result: {
        status: "SUCCESS",
        risk_score: 0.95,
        risk_level: "CRITICAL",
        scam_type: "digital_arrest",
        confidence: 0.96,
        entities: {
          phone_numbers: ["+91 99887 76655", "+91 81302 99421"],
          upi_ids: ["payment.police@paytm", "cbi.officer@ybl"],
          bank_accounts: ["30219482103 (SBI)"],
          urls: ["http://cbi-arrest-verification.in"],
          amounts: ["₹50,000"],
          names: ["Rohan Verma", "DCP Sanjay Sharma (Suspect)"],
          emails: ["dcp.sharma@fake-cbi.gov.in"],
          domains: ["cbi-arrest-verification.in"],
          wallet_ids: [],
          locations: ["Delhi"]
        },
        explanation: "Coercive social engineering scam involving impersonation of central police agencies. Urgency intent and digital arrest threats were detected.",
        language: "en",
        intent_flags: { urgency: true, impersonation: true, payment_request: true },
        confidence_breakdown: { "Known Scam Pattern": 0.50, "Keyword Match": 0.25, "Urgency Language": 0.05, "Impersonation Language": 0.05, "Payment Request Language": 0.05, "Phone Detection": 0.05, "UPI Detection": 0.05 },
        ocr_confidence: 1.0,
      },
      voice_result: {
        status: "SUCCESS",
        transcript: "This is Deputy Commissioner Sanjay Sharma. You are under digital arrest. Transfer fifty thousand rupees to the designated verification account immediately or you will be arrested.",
        is_deepfake: true,
        deepfake_confidence: 0.98,
        emotion: "aggressive",
        speaker_count: 1,
        audio_duration_seconds: 18.2,
        risk_score: 0.95,
        risk_level: "CRITICAL",
        audio_quality: "excellent",
        speaker_confidence: 0.90,
        transcription_confidence: 0.97,
        confidence: 0.95,
        suspicious_timestamps: [
          { timestamp: "00:04", phrase: "under digital arrest" },
          { timestamp: "00:09", phrase: "Transfer fifty thousand rupees" }
        ],
        explanation: "Spectral parameters confirm AI voice synthesis. Highly hostile tone intended to force payment."
      },
      counterfeit_result: {
        status: "SKIPPED",
        reason: "No banknote image uploaded.",
        explanation: "Banknote verification was skipped because no image was provided."
      },
      graph_result: {
        status: "SUCCESS",
        entities_added: ["Complaint_CASE-2026-7890", "Phone_+91 81302 99421", "UPI_payment.police@paytm"],
        edges_added: 4,
        pagerank_scores: { "UPI_payment.police@paytm": 0.38, "Phone_+91 81302 99421": 0.25 },
        fraud_rings: [
          { ring_id: "RING-990", members: ["UPI_payment.police@paytm", "Phone_+91 81302 99421"], size: 2, risk_level: "HIGH", fraud_types: ["digital_arrest"] }
        ],
        high_risk_nodes: ["UPI_payment.police@paytm"],
        risk_score: 0.88,
        risk_level: "HIGH",
        explanation: "Fraud ring RING-990 connects this suspect number and UPI account to 3 previous complaints.",
        graph_explanations: ["Suspect UPI payment.police@paytm links this case to past complaint CASE-2026-4011."],
        edges_metadata: [
          { source: "Complaint_CASE-2026-7890", target: "Phone_+91 81302 99421", relationship: "MENTIONS", confidence: 0.95, source_agent: "scam_agent", evidence: "Parsed from statement text" }
        ]
      },
      geo_result: {
        status: "SUCCESS",
        hotspots: [
          { lat: 28.6139, lon: 77.2090, radius_km: 1.5, complaint_count: 14, dominant_fraud_type: "digital_arrest", risk_level: "HIGH" }
        ],
        patrol_recommendations: ["Increase patrol frequency near New Delhi Central District — 14 active cases reported."],
        temporal_trend: { "9": 2, "10": 4, "11": 7, "12": 11, "13": 8, "14": 5, "15": 4 },
        total_complaints_analyzed: 41,
        risk_zones: [],
        risk_score: 0.80,
        risk_level: "HIGH",
        temporal_hotspots: [{ cluster_id: 1, peak_hour: "12:00", size: 11 }],
        historical_trends: { "total_fraud_types": { "digital_arrest": 28, "upi_fraud": 13 } },
        confidence_interval: [28.612, 28.615, 77.207, 77.211],
        hotspot_explanation: "High-density digital arrest hotspot active between 11:00 AM and 2:00 PM."
      },
      evidence_package: {
        status: "SUCCESS",
        case_id: "CASE-2026-7890",
        overall_risk_score: 0.92,
        risk_level: "CRITICAL",
        fir_draft: "FIRST INFORMATION REPORT\n(Section 154 CrPC)\n\n1. Case ID: CASE-2026-7890\n2. Sections: Section 66D IT Act, Section 318 BNS (Cheating), Section 319 BNS (Impersonation)\n3. Complainant: Rohan Verma (+91 99887 76655)\n4. Suspect Accused: DCP Sanjay Sharma impersonator (+91 81302 99421)\n5. Incident Facts: The complainant was coerced via WhatsApp video call under the guise of digital arrest and extorted for ₹50,000 transferred to payment.police@paytm. Cloned deepfake speech verified.",
        executive_summary: "High-risk social engineering case involving law enforcement impersonation and digital arrest extortion. Evidence includes synthetic voice patterns and community graph linkages.",
        ipc_sections: ["Section 66D IT Act", "Section 318 BNS (Cheating)", "Section 319 BNS (Impersonation)"],
        recommended_actions: [
          "Freeze payment.police@paytm bank assets.",
          "Issue notice to telecom operator for suspect number +91 81302 99421.",
          "Escalate to cyber cell for immediate deepfake origin tracing."
        ],
        chain_of_custody: [
          { file_path: "N/A", file_type: "metadata", sha256: "ea829104fae89", description: "Scam Detection result metadata", source_agent: "scam_detection_agent", confidence: 0.96, timestamp: new Date() },
          { file_path: "N/A", file_type: "metadata", sha256: "0c9d921abcfef", description: "Voice Analysis result metadata", source_agent: "voice_intelligence_agent", confidence: 0.95, timestamp: new Date() }
        ],
        skipped_agents: [{ agent_name: "counterfeit_detection_agent", reason: "No banknote image uploaded." }]
      }
    }
  },
  {
    id: "upi_fraud",
    title: "Instant Loan QR Code Trap",
    case_id: "CASE-2026-4412",
    complainant_name: "Sunita Devi",
    complainant_contact: "+91 91234 56789",
    lat: "22.8046",
    lon: "86.2029",
    text_input: "Scanning a QR code sent via WhatsApp claiming to release an instant loan of ₹10,000. Instead, it debited ₹25,000 from my GPay account linked to UPI ID deviloan@okaxis. Suspect email loan-helper@gmail.com and domain quick-loan.com.",
    results: {
      case_id: "CASE-2026-4412",
      overall_risk_score: 0.68,
      risk_level: "HIGH",
      confidence: 0.85,
      scam_result: {
        status: "SUCCESS",
        risk_score: 0.75,
        risk_level: "HIGH",
        scam_type: "qr_code_scam",
        confidence: 0.88,
        entities: {
          phone_numbers: ["+91 91234 56789"],
          upi_ids: ["deviloan@okaxis"],
          bank_accounts: [],
          urls: ["http://quick-loan.com"],
          amounts: ["₹25,000"],
          names: ["Sunita Devi"],
          emails: ["loan-helper@gmail.com"],
          domains: ["quick-loan.com"],
          wallet_ids: [],
          locations: ["Jamshedpur"]
        },
        explanation: "Phishing scam utilizing deceptive QR codes to auto-debit funds. Intent flags for banking credential traps detected.",
        language: "en",
        intent_flags: { urgency: true, impersonation: false, payment_request: true },
        confidence_breakdown: { "Known Scam Pattern": 0.40, "Keyword Match": 0.20, "Payment Request Language": 0.05, "UPI Detection": 0.05 },
        ocr_confidence: 1.0,
      },
      voice_result: {
        status: "SKIPPED",
        reason: "No suspect call recording provided.",
        explanation: "Voice analysis was skipped because no audio file was uploaded."
      },
      counterfeit_result: {
        status: "SKIPPED",
        reason: "No banknote image uploaded.",
        explanation: "Banknote verification was skipped because no image was provided."
      },
      graph_result: {
        status: "SUCCESS",
        entities_added: ["Complaint_CASE-2026-4412", "UPI_deviloan@okaxis"],
        edges_added: 2,
        pagerank_scores: { "UPI_deviloan@okaxis": 0.22 },
        fraud_rings: [],
        high_risk_nodes: [],
        risk_score: 0.50,
        risk_level: "MEDIUM",
        explanation: "Suspect UPI ID deviloan@okaxis was found in 1 other pending cyber complaint.",
        graph_explanations: ["Suspect UPI deviloan@okaxis links this case to past complaint CASE-2026-3021."],
        edges_metadata: []
      },
      geo_result: {
        status: "SUCCESS",
        hotspots: [
          { lat: 22.8046, lon: 86.2029, radius_km: 1.25, complaint_count: 13, dominant_fraud_type: "upi_fraud", risk_level: "HIGH" }
        ],
        patrol_recommendations: ["Increase patrol near Jamshedpur City Center — 13 active upi_fraud cases reported."],
        temporal_trend: { "11": 1, "12": 3, "13": 5, "14": 4, "15": 2 },
        total_complaints_analyzed: 22,
        risk_zones: [],
        risk_score: 0.70,
        risk_level: "HIGH",
        temporal_hotspots: [{ cluster_id: 1, peak_hour: "13:00", size: 5 }],
        historical_trends: { "total_fraud_types": { "upi_fraud": 22 } },
        confidence_interval: [22.802, 22.807, 86.200, 86.205],
        hotspot_explanation: "High-density upi_fraud hotspot active during lunch hours."
      },
      evidence_package: {
        status: "SUCCESS",
        case_id: "CASE-2026-4412",
        overall_risk_score: 0.68,
        risk_level: "HIGH",
        fir_draft: "FIRST INFORMATION REPORT\n(Section 154 CrPC)\n\n1. Case ID: CASE-2026-4412\n2. Sections: Section 66D IT Act, Section 318 BNS (Cheating)\n3. Complainant: Sunita Devi (+91 91234 56789)\n4. facts: Complainant was scammed via a WhatsApp QR code claiming loan benefits, resulting in unauthorized debit of ₹25,000 to deviloan@okaxis.",
        executive_summary: "Medium-to-high risk UPI auto-debit scam utilizing QR codes. Suspect UPI shows prior links to cyber fraud database.",
        ipc_sections: ["Section 66D IT Act", "Section 318 BNS (Cheating)"],
        recommended_actions: [
          "Request GPay/NPCI to freeze UPI ID deviloan@okaxis.",
          "Perform domain blacklist query for quick-loan.com."
        ],
        chain_of_custody: [
          { file_path: "N/A", file_type: "metadata", sha256: "ab82910cde882", description: "Scam Detection result metadata", source_agent: "scam_detection_agent", confidence: 0.88, timestamp: new Date() }
        ],
        skipped_agents: [
          { agent_name: "voice_intelligence_agent", reason: "No suspect call recording provided." },
          { agent_name: "counterfeit_detection_agent", reason: "No banknote image uploaded." }
        ]
      }
    }
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [backendLive, setBackendLive] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Case inputs
  const [caseId, setCaseId] = useState('CASE-2026-9081');
  const [complainantName, setComplainantName] = useState('Rajesh Kumar');
  const [complainantContact, setComplainantContact] = useState('+91 98765 43210');
  const [lat, setLat] = useState('22.8046');
  const [lon, setLon] = useState('86.2029');
  const [textInput, setTextInput] = useState(
    "Received high-urgency digital arrest threat message on WhatsApp. Fraudster impersonated an IPS officer, claiming my Aadhaar card was linked to money laundering. Demanded immediate transfer of ₹50,000 via UPI ID cbi.officer@ybl to prevent arrest."
  );
  
  // File uploads
  const [imageFile, setImageFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  
  // Pipeline status and results
  const [executing, setExecuting] = useState(false);
  const [pipelineStage, setPipelineStage] = useState('idle'); 
  const [pipelineResult, setPipelineResult] = useState(DEMO_PRESETS[0].results);
  const [errorMsg, setErrorMsg] = useState('');

  // Timeline Event Stream
  const [timelineEvents, setTimelineEvents] = useState([
    { time: "19:40:32", event: "Docket Ingested", status: "SUCCESS" },
    { time: "19:40:33", event: "Scam Analysis Finished", status: "SUCCESS" },
    { time: "19:40:33", event: "Voice Deepfake Audit Finished", status: "SUCCESS" },
    { time: "19:40:34", event: "Graph Ring Detection Finished", status: "SUCCESS" },
    { time: "19:40:36", event: "Geospatial DBSCAN Finished", status: "SUCCESS" },
    { time: "19:40:36", event: "Evidence Manifest Generated", status: "SUCCESS" }
  ]);

  // Copilot Chat
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'assistant',
      content: 'Welcome Investigator. I am the SentinelShield AI Copilot. Ask me any details regarding the legal sections, fraud rings, or security features associated with the evidence package of this case.',
      citations: [],
      similarCases: []
    }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  
  // Interactive Graph Controls
  const [zoomScale, setZoomScale] = useState(1.0);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [clickedNode, setClickedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  // Evidence Search and Filters
  const [evidenceSearch, setEvidenceSearch] = useState('');
  const [evidenceFilter, setEvidenceFilter] = useState('all'); // all, communication, financial, identity, location, media

  // References for terminal scroll and copy notifications
  const chatEndRef = useRef(null);
  const timelineEndRef = useRef(null);
  const [copiedFir, setCopiedFir] = useState(false);
  const [copiedSummary, setCopiedSummary] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);

  // Check backend health on load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${apiUrl}/health`);
        if (res.ok) {
          setBackendLive(true);
        } else {
          setBackendLive(false);
        }
      } catch (err) {
        setBackendLive(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, chatLoading]);

  // Scroll timeline to bottom when new events arrive
  useEffect(() => {
    timelineEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [timelineEvents]);

  // Generate a random Case ID
  const handleGenerateCaseId = () => {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    setCaseId(`CASE-2026-${randomNum}`);
  };

  // Copy to clipboard helper
  const handleCopyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === 'fir') {
      setCopiedFir(true);
      setTimeout(() => setCopiedFir(false), 2000);
    } else if (type === 'json') {
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    } else {
      setCopiedSummary(true);
      setTimeout(() => setCopiedSummary(false), 2000);
    }
  };

  // Print PDF helper
  const handlePrintReport = () => {
    const printContent = `
      =======================================================
      SENTINELSHIELD AI - INVESTIGATION REPORT & CUSTODY DOCKET
      =======================================================
      Case ID: ${pipelineResult.case_id}
      Overall Risk Score: ${(pipelineResult.overall_risk_score * 100).toFixed(0)}% (${pipelineResult.risk_level})
      Complainant: ${complainantName} (${complainantContact})
      GPS Coordinates: ${lat}, ${lon}
      Date Generated: ${new Date().toUTCString()}
      
      -------------------------------------------------------
      EXECUTIVE SUMMARY:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.executive_summary || 'N/A'}
      
      -------------------------------------------------------
      CROSS-AGENT EVIDENCE CORRELATIONS:
      -------------------------------------------------------
      ${pipelineResult.geo_result?.hotspot_explanation || 'No cross-agent correlations identified.'}
      
      -------------------------------------------------------
      CHAIN OF CUSTODY AUDIT LOGS:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.chain_of_custody?.map(c => `- [${c.source_agent.toUpperCase()}] Confidence=${(c.confidence*100).toFixed(0)}% | Hash=${c.sha256}`).join('\n') || 'N/A'}
      
      -------------------------------------------------------
      RECOMMENDED LAW ENFORCEMENT ACTIONS:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.recommended_actions?.map(a => `- ${a}`).join('\n') || 'N/A'}
      
      -------------------------------------------------------
      IPC / BNS SECTIONS APPLIED:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.ipc_sections?.join(', ') || 'N/A'}
      
      -------------------------------------------------------
      FIR DRAFT (Section 154 CrPC equivalent):
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.fir_draft || 'N/A'}
      =======================================================
    `;
    const win = window.open('', '_blank');
    win.document.write(`<pre style="font-family: monospace; padding: 30px; font-size: 13px; background: #0b0f19; color: #34d399; border: 1px solid #1e293b; border-radius: 8px;">${printContent}</pre>`);
    win.document.close();
    win.print();
  };

  // Demo Preset Selection Trigger
  const handleLoadDemoPreset = (presetId) => {
    const preset = DEMO_PRESETS.find(p => p.id === presetId);
    if (!preset) return;

    // Load inputs
    setCaseId(preset.case_id);
    setComplainantName(preset.complainant_name);
    setComplainantContact(preset.complainant_contact);
    setLat(preset.lat);
    setLon(preset.lon);
    setTextInput(preset.text_input);
    setImageFile(null);
    setAudioFile(null);

    // Run simulated quick pipeline analysis
    setExecuting(true);
    setPipelineStage('uploading');
    
    const events = [];
    const addEvent = (step, label, status = "SUCCESS") => {
      const t = new Date().toLocaleTimeString('en-IN', { hour12: false });
      events.push({ time: t, event: label, status });
      setTimelineEvents([...events]);
      setPipelineStage(step);
    };

    setTimeout(() => addEvent('scam_analysis', 'Complaint Ingestion Complete'), 300);
    setTimeout(() => addEvent('voice_analysis', 'Scam Agent analysis success'), 600);
    setTimeout(() => addEvent('counterfeit_analysis', 'Voice deepfake signature check finished'), 900);
    setTimeout(() => addEvent('graph_analysis', 'Currency counterfeiting verify finished'), 1200);
    setTimeout(() => addEvent('geo_analysis', 'Graph nodes link ingestion finished'), 1500);
    setTimeout(() => addEvent('done', 'Geospatial DBSCAN hotspots completed'), 1800);
    
    setTimeout(() => {
      setPipelineResult(preset.results);
      setExecuting(false);
      // Add final reports finished event
      const t = new Date().toLocaleTimeString('en-IN', { hour12: false });
      setTimelineEvents(prev => [...prev, { time: t, event: 'Evidence package report finalized', status: 'SUCCESS' }]);
    }, 2000);
  };

  // Trigger Multi-Agent Pipeline (Form Submit)
  const handleRunPipeline = async (e) => {
    e.preventDefault();
    setExecuting(true);
    setPipelineStage('uploading');
    setErrorMsg('');
    setTimelineEvents([]);

    const tString = () => new Date().toLocaleTimeString('en-IN', { hour12: false });
    const logEvent = (evt, st = "SUCCESS") => {
      setTimelineEvents(prev => [...prev, { time: tString(), event: evt, status: st }]);
    };

    logEvent("Uploading complaint docket details...");

    // If backend is offline, simulate pipeline steps with realistic delay
    if (!backendLive) {
      setTimeout(() => { logEvent("Scam detection agent started..."); setPipelineStage('scam_analysis'); }, 500);
      setTimeout(() => { logEvent("Voice analysis deepfake audit started..."); setPipelineStage('voice_analysis'); }, 1000);
      setTimeout(() => { logEvent("Banknote counterfeit verification started..."); setPipelineStage('counterfeit_analysis'); }, 1500);
      setTimeout(() => { logEvent("Ingesting graph connections..."); setPipelineStage('graph_analysis'); }, 2000);
      setTimeout(() => { logEvent("Computing Geospatial DBSCAN hotspots..."); setPipelineStage('geo_analysis'); }, 2500);
      setTimeout(() => {
        const hasAudio = !!audioFile;
        const hasImage = !!imageFile;
        
        // Mock data aggregation matching inputs
        const mockResult = {
          case_id: caseId,
          overall_risk_score: hasAudio ? 0.90 : 0.72,
          risk_level: hasAudio ? "CRITICAL" : "HIGH",
          confidence: 0.85,
          scam_result: {
            status: "SUCCESS",
            risk_score: 0.80,
            risk_level: "HIGH",
            scam_type: "digital_arrest",
            confidence: 0.88,
            entities: {
              phone_numbers: [complainantContact, "+91 81302 99421"],
              upi_ids: ["cbi.officer@ybl"],
              bank_accounts: ["30219482103 (SBI)"],
              urls: [],
              amounts: ["₹50,000"],
              names: [complainantName, "DCP Sanjay Sharma (Suspect)"],
              emails: [],
              domains: [],
              wallet_ids: [],
              locations: ["Delhi"]
            },
            explanation: "Digital arrest scam involving authority impersonation. Threat content detected in statement.",
            language: "en",
            intent_flags: { urgency: true, impersonation: true, payment_request: true },
            confidence_breakdown: { "Known Scam Pattern": 0.45, "Keyword Match": 0.20, "Phone Detection": 0.05, "UPI Detection": 0.05 },
            ocr_confidence: 1.0
          },
          voice_result: hasAudio ? {
            status: "SUCCESS",
            transcript: "This is the police. Transfer ₹50,000 immediately to avoid arrest.",
            is_deepfake: true,
            deepfake_confidence: 0.92,
            emotion: "aggressive",
            speaker_count: 1,
            audio_duration_seconds: 12.5,
            risk_score: 0.90,
            risk_level: "CRITICAL",
            audio_quality: "good",
            speaker_confidence: 0.85,
            transcription_confidence: 0.94,
            confidence: 0.91,
            suspicious_timestamps: [{ timestamp: "00:03", phrase: "avoid arrest" }],
            explanation: "Speech matches synthetic deepfake patterns."
          } : {
            status: "SKIPPED",
            reason: "No suspect audio file uploaded.",
            explanation: "Voice analysis was skipped."
          },
          counterfeit_result: hasImage ? {
            status: "SUCCESS",
            is_counterfeit: true,
            confidence: 0.85,
            denomination: "500",
            serial_number: "5AP 882910",
            security_features: {
              security_thread: "fail",
              watermark: "pass",
              microprint: "fail",
              color_shift: "fail",
              serial_pattern: "fail",
              uv_feature: "fail",
              security_thread_conf: 0.85,
              watermark_conf: 0.80,
              serial_pattern_conf: 0.90,
              microprint_conf: 0.50,
              color_shift_conf: 0.50,
              uv_feature_conf: 0.50
            },
            risk_score: 0.75,
            risk_level: "HIGH",
            explanation: "Banknote shows security thread and microprint blur checks failure."
          } : {
            status: "SKIPPED",
            reason: "No banknote image file uploaded.",
            explanation: "Currency verification was skipped."
          },
          graph_result: {
            status: "SUCCESS",
            entities_added: ["Complaint_" + caseId, "Phone_+91 81302 99421", "UPI_cbi.officer@ybl"],
            edges_added: 4,
            pagerank_scores: { "UPI_cbi.officer@ybl": 0.32 },
            fraud_rings: [{ ring_id: "RING-401", members: ["UPI_cbi.officer@ybl", "Phone_+91 81302 99421"], size: 2, risk_level: "HIGH", fraud_types: ["digital_arrest"] }],
            high_risk_nodes: ["UPI_cbi.officer@ybl"],
            risk_score: 0.70,
            risk_level: "HIGH",
            explanation: "Suspect UPI cbi.officer@ybl belongs to detected Jamshedpur fraud ring.",
            graph_explanations: ["UPI account shares connections with past cases in the region."],
            edges_metadata: []
          },
          geo_result: {
            status: "SUCCESS",
            hotspots: [{ lat: parseFloat(lat), lon: parseFloat(lon), radius_km: 1.25, complaint_count: 13, dominant_fraud_type: "upi_fraud", risk_level: "HIGH" }],
            patrol_recommendations: [`Increase safety patrol near center coordinates (${parseFloat(lat).toFixed(4)}, ${parseFloat(lon).toFixed(4)})`],
            temporal_trend: { "11": 2, "12": 4, "13": 7, "14": 5 },
            total_complaints_analyzed: 13,
            risk_zones: [],
            risk_score: 0.65,
            risk_level: "HIGH",
            temporal_hotspots: [{ cluster_id: 1, peak_hour: "13:00", size: 7 }],
            historical_trends: { "total_fraud_types": { "upi_fraud": 13 } },
            confidence_interval: [parseFloat(lat)-0.002, parseFloat(lat)+0.002, parseFloat(lon)-0.002, parseFloat(lon)+0.002],
            hotspot_explanation: "Active digital fraud hotspot identified near location coordinates."
          },
          evidence_package: {
            status: "SUCCESS",
            case_id: caseId,
            overall_risk_score: hasAudio ? 0.90 : 0.72,
            risk_level: hasAudio ? "CRITICAL" : "HIGH",
            fir_draft: `FIRST INFORMATION REPORT\n\n1. Case ID: ${caseId}\n2. IPC sections: Section 66D IT Act, Section 318 BNS\n3. Complainant: ${complainantName}\n4. Facts: Social engineering scam coerced Sunita Devi for transfers to cbi.officer@ybl.`,
            executive_summary: "High risk fraud case with cross-channel voice/text indicators. Ingested suspects are flagged.",
            ipc_sections: ["Section 66D IT Act", "Section 318 BNS"],
            recommended_actions: ["Block suspect UPI account cbi.officer@ybl immediately.", "Deploy local patrol to coord hotspots."],
            chain_of_custody: [
              { file_path: "N/A", file_type: "metadata", sha256: "ea8829031cde8", description: "Ingested scam metadata", source_agent: "scam_detection_agent", confidence: 0.88, timestamp: new Date() }
            ],
            skipped_agents: []
          }
        };

        logEvent("Scam detection agent analysis complete.");
        logEvent("Voice intelligence deepfake audit complete.");
        logEvent("Currency security feature verification complete.");
        logEvent("Graph community detection completed.");
        logEvent("Geospatial DBSCAN clustering complete.");
        logEvent("Evidence Manifest & Custody report generated.");
        
        setPipelineResult(mockResult);
        setPipelineStage('done');
        setExecuting(false);
      }, 3000);
      return;
    }

    // Backend is live: perform real API request
    try {
      const formData = new FormData();
      formData.append('text_input', textInput);
      if (complainantName) formData.append('complainant_name', complainantName);
      if (complainantContact) formData.append('complainant_contact', complainantContact);
      if (lat) formData.append('lat', parseFloat(lat));
      if (lon) formData.append('lon', parseFloat(lon));
      if (audioFile) {
        formData.append('audio_file', audioFile);
        logEvent("Streaming audio evidence file to Voice Agent...");
      }
      if (imageFile) {
        formData.append('image_file', imageFile);
        logEvent("Streaming visual evidence file to Counterfeit Agent...");
      }

      setPipelineStage('executing');
      logEvent("Orchestrator running sub-agents parallel fan-out...");

      const res = await fetch(`${apiUrl}/api/pipeline/upload`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`API error status: ${res.status}`);
      }

      const data = await res.json();
      logEvent("Risk aggregation node score computed.");
      logEvent("Evidence package finalized.");
      
      setPipelineResult(data);
      setPipelineStage('done');
    } catch (err) {
      console.error(err);
      logEvent(`Orchestrator pipeline failed: ${err.message}`, "FAILED");
      setErrorMsg(err.message || 'Pipeline execution failed.');
      setPipelineStage('error');
    } finally {
      setExecuting(false);
    }
  };

  // Submit Copilot chat query
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    // If backend is offline, simulate copilot answer with keyword triggers
    if (!backendLive) {
      setTimeout(() => {
        let answer = "Regarding the details of this case, I have audited the multi-agent outputs. We have verified evidence of a digital arrest scam involving WhatsApp impersonation. The risk is high (88%), and immediate asset-freezing is recommended.";
        let citations = [];
        
        const textLower = userMessage.toLowerCase();
        if (textLower.includes('section') || textLower.includes('law') || textLower.includes('bns') || textLower.includes('ipc')) {
          answer = "Based on BNS (Bharatiya Nyaya Sanhita) classification, the suspect's actions map directly to Section 318 (Cheating) and Section 319 (Cheating by Impersonation). Since digital communications were employed, Section 66D of the IT Act (punishment for cheating by personation using computer resource) is also linked to the FIR draft.";
          citations = [
            { source_id: "legal_precedent_sec_318", chunk_text: "Section 318 BNS details punishment for cheating, replacing Section 420 IPC, and specifies imprisonment up to 7 years plus fines.", relevance_score: 0.912, source_type: "legal" },
            { source_id: "it_act_sec_66d", chunk_text: "Section 66D IT Act mandates imprisonment up to 3 years and fine up to 1 lakh for cheating by impersonation using a communication device.", relevance_score: 0.884, source_type: "legal" }
          ];
        } else if (textLower.includes('phone') || textLower.includes('upi') || textLower.includes('ring') || textLower.includes('entity')) {
          answer = "The Fraud Graph Agent audited the following suspect: UPI ID deviloan@okaxis or cbi.officer@ybl. Louvain clustering reveals these belong to Fraud Ring RING-401. This community represents a highly connected ring targeting victims in the region.";
          citations = [
            { source_id: "graph_extracted_entities", chunk_text: "Ingested UPI ID with high PageRank centrality. Clustered with suspect phone number inside regional fraud ring.", relevance_score: 0.952, source_type: "case" }
          ];
        } else if (textLower.includes('voice') || textLower.includes('deepfake') || textLower.includes('audio')) {
          answer = "Voice Intelligence analyzed the suspect's audio and flagged it as a deepfake with 92%+ confidence. Emotional signature shows aggressive coercion, typical of digital arrest threat calls.";
          citations = [
            { source_id: "voice_analysis_speech", chunk_text: "Audio sample features speech pattern anomalies. Deepfake classification models triggered deepfake_confidence = 0.92.", relevance_score: 0.931, source_type: "evidence" }
          ];
        }

        setChatHistory(prev => [...prev, {
          role: 'assistant',
          content: answer,
          citations: citations,
          similarCases: ["CASE-2026-4412", "CASE-2026-7890"]
        }]);
        setChatLoading(false);
      }, 1000);
      return;
    }

    // Backend is live: call /api/agents/rag
    try {
      const res = await fetch(`${apiUrl}/api/agents/rag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage,
          case_id: pipelineResult?.case_id || caseId,
          top_k: 5
        })
      });

      if (!res.ok) {
        throw new Error('Copilot API failed');
      }

      const data = await res.json();
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: data.answer || "No response received.",
        citations: data.citations || [],
        similarCases: data.similar_cases || [],
        hallucinationGuardTriggered: data.hallucination_guard_triggered
      }]);
    } catch (err) {
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: `Error connecting to RAG agent: ${err.message}`
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Convert geo temporal trend dictionary to recharts array
  const getTemporalChartData = () => {
    const trend = pipelineResult?.geo_result?.temporal_trend || {};
    return Object.entries(trend).map(([hour, count]) => ({
      hour: `${hour}:00`,
      complaints: count
    })).sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
  };

  // Build reactive graph nodes based on pipeline results
  const buildGraphNodesAndEdges = () => {
    const nodes = [];
    const edges = [];
    const currentCaseId = pipelineResult?.case_id || caseId;

    // Central case node
    nodes.push({
      id: 'case_node',
      label: currentCaseId,
      type: 'Case',
      x: 300,
      y: 200,
      size: 30
    });

    const entities = pipelineResult?.scam_result?.entities;
    if (!entities) {
      return { nodes, edges };
    }

    const items = [];
    if (entities.phone_numbers) entities.phone_numbers.forEach(p => items.push({ val: p, type: 'Phone' }));
    if (entities.upi_ids) entities.upi_ids.forEach(u => items.push({ val: u, type: 'UPI' }));
    if (entities.bank_accounts) entities.bank_accounts.forEach(b => items.push({ val: b, type: 'Bank' }));
    if (entities.urls) entities.urls.forEach(url => items.push({ val: url, type: 'URL' }));
    if (entities.wallet_ids) entities.wallet_ids.forEach(w => items.push({ val: w, type: 'Wallet' }));
    if (entities.names) entities.names.forEach(n => {
      if (n.includes('Suspect') || n.includes('DCP')) {
        items.push({ val: n, type: 'Suspect' });
      }
    });

    const total = items.length;
    items.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / total;
      const radius = 150;
      const x = 300 + radius * Math.cos(angle);
      const y = 200 + radius * Math.sin(angle);
      
      const prScore = pipelineResult?.graph_result?.pagerank_scores[`${item.type === 'Bank' ? 'BankAccount' : item.type}_${item.val}`] || 0.05;

      nodes.push({
        id: `node_${index}`,
        label: item.val,
        type: item.type,
        x,
        y,
        size: 20,
        pr: prScore
      });

      edges.push({
        from: 'case_node',
        to: `node_${index}`,
        relation: 'MENTIONS',
        confidence: 0.95,
        source_agent: 'scam_agent',
        evidence: 'Extracted from docket text'
      });
    });

    return { nodes, edges };
  };

  const { nodes: graphNodes, edges: graphEdges } = buildGraphNodesAndEdges();

  // SVG Pan and Zoom handlers
  const handleZoom = (direction) => {
    setZoomScale(prev => Math.min(Math.max(direction === 'in' ? prev + 0.1 : prev - 0.1, 0.5), 2.5));
  };

  const handleMouseDown = (e) => {
    setIsPanning(true);
    setStartPan({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e) => {
    if (!isPanning) return;
    setPanOffset({ x: e.clientX - startPan.x, y: e.clientY - startPan.y });
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  // Compile all entities into a flat list for the Evidence Viewer
  const allEvidenceItems = useMemo(() => {
    const list = [];
    const currentCaseId = pipelineResult?.case_id || caseId;
    const t = pipelineResult?.scam_result?.timestamp || new Date().toISOString();

    const add = (val, cat, type, score, src, desc) => {
      if (!val) return;
      list.push({
        value: val,
        category: cat, // communication, financial, identity, location, media
        type: type,
        confidence: score || 0.85,
        source: src || 'scam_detection_agent',
        timestamp: t,
        case_id: currentCaseId,
        description: desc
      });
    };

    const e = pipelineResult?.scam_result?.entities;
    if (e) {
      e.phone_numbers?.forEach(v => add(v, 'communication', 'Phone Number', 0.95, 'scam_detection_agent', 'Extracted suspect phone contact'));
      e.emails?.forEach(v => add(v, 'communication', 'Email Address', 0.90, 'scam_detection_agent', 'Linked suspect contact email'));
      e.urls?.forEach(v => add(v, 'communication', 'Website URL', 0.88, 'scam_detection_agent', 'Suspect phishing page link'));
      e.domains?.forEach(v => add(v, 'communication', 'Domain Name', 0.88, 'scam_detection_agent', 'Suspect web domain host'));
      
      e.upi_ids?.forEach(v => add(v, 'financial', 'UPI ID Address', 0.92, 'scam_detection_agent', 'Target money extortion receiver'));
      e.bank_accounts?.forEach(v => add(v, 'financial', 'Bank Account', 0.90, 'scam_detection_agent', 'Financial target ledger'));
      e.wallet_ids?.forEach(v => add(v, 'financial', 'Crypto Wallet ID', 0.85, 'scam_detection_agent', 'Flagged ledger wallet address'));

      e.names?.forEach(v => add(v, 'identity', 'Name', 0.80, 'scam_detection_agent', 'Extracted identity mention'));
      e.locations?.forEach(v => add(v, 'location', 'District / Location', 0.82, 'scam_detection_agent', 'Incident geography locator'));
    }

    if (pipelineResult.voice_result?.status === 'SUCCESS') {
      add("Audio recording file", "media", "Voice Clip", pipelineResult.voice_result.confidence, "voice_intelligence_agent", "Ingested suspect call clip");
    }

    if (pipelineResult.counterfeit_result?.status === 'SUCCESS') {
      add("Banknote image snapshot", "media", "Note Image", pipelineResult.counterfeit_result.confidence, "counterfeit_detection_agent", "Suspect counterfeit rupee snapshot");
    }

    if (lat && lon) {
      add(`${lat}, ${lon}`, "location", "GPS Coordinates", 0.95, "geo_intelligence_agent", "Current case epicenter location");
    }

    return list;
  }, [pipelineResult, caseId, lat, lon]);

  // Filter evidence based on search query and category tab
  const filteredEvidence = useMemo(() => {
    return allEvidenceItems.filter(item => {
      const matchesSearch = item.value.toLowerCase().includes(evidenceSearch.toLowerCase()) ||
                            item.type.toLowerCase().includes(evidenceSearch.toLowerCase()) ||
                            item.source.toLowerCase().includes(evidenceSearch.toLowerCase());
      const matchesFilter = evidenceFilter === 'all' || item.category === evidenceFilter;
      return matchesSearch && matchesFilter;
    });
  }, [allEvidenceItems, evidenceSearch, evidenceFilter]);

  // Aggregate sub-agent data for Live Multi-Agent Panel
  const agentExecutionList = useMemo(() => {
    const defaultList = [
      { name: 'scam_detection_agent', label: 'Scam Detection Agent', result: pipelineResult?.scam_result },
      { name: 'voice_intelligence_agent', label: 'Voice Intelligence Agent', result: pipelineResult?.voice_result },
      { name: 'counterfeit_detection_agent', label: 'Counterfeit Detection Agent', result: pipelineResult?.counterfeit_result },
      { name: 'fraud_graph_agent', label: 'Fraud Graph Agent', result: pipelineResult?.graph_result },
      { name: 'geo_intelligence_agent', label: 'Geospatial Agent', result: pipelineResult?.geo_result },
      { name: 'rag_copilot_agent', label: 'RAG Copilot', result: pipelineResult?.rag_result || (chatHistory.length > 1 ? { status: "SUCCESS", confidence: 0.90 } : null) },
      { name: 'evidence_generation_agent', label: 'Evidence Generator', result: pipelineResult?.evidence_package }
    ];
    return defaultList;
  }, [pipelineResult, chatHistory]);

  // Dynamic Summary Text Generator (No Raw JSON exposed!)
  const dynamicSummaryText = useMemo(() => {
    if (!pipelineResult) return "No complaint case results loaded. Enter details in the File Analyzer tab to execute.";
    
    const riskPct = (pipelineResult.overall_risk_score * 100).toFixed(0);
    const activeScamType = pipelineResult.scam_result?.scam_type?.replace('_', ' ') || "cyber_scam";
    const rings = pipelineResult.graph_result?.fraud_rings?.length || 0;
    
    let summary = `This complaint has been classified as ${pipelineResult.risk_level} RISK (Risk Score: ${riskPct}%) because critical fraud indicators were verified. `;
    
    if (pipelineResult.scam_result?.status === "SUCCESS") {
      summary += `Textual audit detects a ${activeScamType} pattern. `;
    }
    
    if (pipelineResult.voice_result?.status === "SUCCESS" && pipelineResult.voice_result.is_deepfake) {
      summary += `Audio analysis confirms a deepfake voice synthesis with ${(pipelineResult.voice_result.deepfake_confidence * 100).toFixed(0)}% confidence, indicating deliberate digital authority impersonation. `;
    }
    
    if (pipelineResult.counterfeit_result?.status === "SUCCESS" && pipelineResult.counterfeit_result.is_counterfeit) {
      summary += `The counterfeit currency node flagged visual security thread anomalies on the uploaded rupee note. `;
    }
    
    if (rings > 0) {
      summary += `Graph clustering exposes that the suspect variables belong to ${rings} identified fraud rings linking this session to previous complaints. `;
    }
    
    if (pipelineResult.geo_result?.status === "SUCCESS" && pipelineResult.geo_result.hotspots?.length > 0) {
      summary += `Geospatial tracking identifies ${pipelineResult.geo_result.hotspots.length} active crime clusters near the complainant's coordinates.`;
    }
    
    return summary;
  }, [pipelineResult]);

  // Download raw JSON helper
  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(pipelineResult, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `sentinelshield_case_${pipelineResult.case_id || 'export'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between z-20 shadow-2xl shrink-0">
        <div>
          {/* Logo brand title */}
          <div className="p-5 flex items-center gap-3 border-b border-slate-800 bg-slate-950">
            <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
              <Shield className="w-7 h-7 text-emerald-400 animate-pulse" />
            </div>
            <div>
              <h1 className="font-bold text-md tracking-wider text-slate-100 font-mono">SENTINEL SHIELD</h1>
              <span className="text-[10px] text-emerald-400 font-bold tracking-widest uppercase">AI Intelligence Console</span>
            </div>
          </div>

          {/* Quick Demo Selector */}
          <div className="p-4 border-b border-slate-800 bg-slate-950/40">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block mb-2">⚡ Start Hackathon Demo Preset</span>
            <div className="grid grid-cols-2 gap-2">
              <button 
                onClick={() => handleLoadDemoPreset('digital_arrest')}
                className="text-[9px] font-bold bg-slate-900 border border-slate-800 text-slate-300 hover:text-emerald-400 hover:border-emerald-500/50 p-2 rounded-lg transition-all text-left truncate flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3 h-3 text-emerald-400 shrink-0" /> Digital Arrest
              </button>
              <button 
                onClick={() => handleLoadDemoPreset('upi_fraud')}
                className="text-[9px] font-bold bg-slate-900 border border-slate-800 text-slate-300 hover:text-emerald-400 hover:border-emerald-500/50 p-2 rounded-lg transition-all text-left truncate flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3 h-3 text-emerald-400 shrink-0" /> QR Phishing
              </button>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            {[
              { id: 'dashboard', label: 'Console Dashboard', icon: LayoutDashboard },
              { id: 'analyzer', label: 'File Analyzer & Ingest', icon: FileSearch },
              { id: 'evidence', label: 'Evidence Repository', icon: FileText },
              { id: 'graph', label: 'Fraud Graph Network', icon: Network },
              { id: 'heatmap', label: 'Geospatial Hotspots', icon: MapPin },
              { id: 'copilot', label: 'Investigation Copilot', icon: MessageSquareCode },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                    activeTab === item.id 
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-700/30 font-semibold' 
                      : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </div>
                  {item.id === 'copilot' && (
                    <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/20 text-emerald-300 font-bold rounded uppercase border border-emerald-500/10">RAG</span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* User profile card & Settings Trigger */}
        <div className="border-t border-slate-800 bg-slate-950/70">
          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold text-xs border border-emerald-500/30">
                NJ
              </div>
              <div>
                <p className="text-xs font-bold text-slate-200">Nikhil Jha</p>
                <p className="text-[9px] text-slate-500 font-semibold">Investigator ID: #8131</p>
              </div>
            </div>
            <button 
              onClick={() => setShowSettings(!showSettings)} 
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-900 transition-colors cursor-pointer"
              title="Connection Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* RIGHT WORKSPACE */}
      <main className="flex-1 flex flex-col overflow-hidden bg-slate-900 relative">
        
        {/* Connection Settings drawer */}
        {showSettings && (
          <div className="absolute top-16 right-8 bg-slate-950 border border-slate-800 rounded-2xl p-4 shadow-2xl z-30 w-80 animate-fadeIn">
            <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider flex items-center gap-1.5">
              <Settings className="w-3.5 h-3.5" /> Core Endpoint Settings
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase">FastAPI Backend URL</label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full mt-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
                />
              </div>
              <div className="text-[10px] text-slate-400 leading-relaxed">
                Platform executes multi-agent processes by forwarding file streams to this host.
              </div>
            </div>
          </div>
        )}

        {/* Top Header Controls */}
        <header className="h-16 border-b border-slate-800 bg-slate-950/40 backdrop-blur-md flex items-center justify-between px-8 z-15 shadow-sm shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Session Case ID: {pipelineResult?.case_id || caseId}
              </span>
            </div>
            
            {/* Status indicator */}
            <span className={`flex items-center gap-1.5 text-[10px] font-bold px-2.5 py-1 rounded-full border ${
              backendLive 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${backendLive ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {backendLive ? 'AGENT HOST ONLINE' : 'SIMULATION MODE'}
            </span>
          </div>

          <div className="text-xs font-mono text-slate-400 font-semibold bg-slate-950/30 px-3 py-1 rounded-lg border border-slate-800/40">
            {new Date().toLocaleDateString('en-IN', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
          </div>
        </header>

        {/* SCROLLABLE ROUTED WORKSPACE */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* TAB 1: CONSOLE DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* Dashboard Summary Row (Requirement 8) */}
              <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
                {[
                  { label: "Total Ingested cases", val: 24, icon: FileText, color: "text-slate-400" },
                  { label: "High Risk cases", val: 19, icon: AlertTriangle, color: "text-rose-400" },
                  { label: "Fraud Rings Detected", val: pipelineResult?.graph_result?.fraud_rings?.length || 0, icon: Network, color: "text-purple-400" },
                  { label: "Evidence Manifest count", val: allEvidenceItems.length, icon: FileSearch, color: "text-sky-400" },
                  { label: "AI Agents Executed", val: agentExecutionList.filter(a => a.result && a.result.status === "SUCCESS").length, icon: Activity, color: "text-emerald-400" },
                  { label: "Average Risk Score", val: "79%", icon: TrendingUp, color: "text-amber-400" }
                ].map((card, idx) => {
                  const Icon = card.icon;
                  return (
                    <div key={idx} className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                      <div className="space-y-1">
                        <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">{card.label}</span>
                        <span className="text-lg font-bold font-mono text-slate-200 block">{card.val}</span>
                      </div>
                      <Icon className={`w-5 h-5 shrink-0 ${card.color}`} />
                    </div>
                  );
                })}
              </div>

              {/* Main Risk Dashboard (Requirement 3) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Risk Gauge Visual Card */}
                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
                  <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                    <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">Overall Case Threat</h3>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border uppercase ${
                      pipelineResult.risk_level === "CRITICAL" || pipelineResult.risk_level === "HIGH"
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse"
                        : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                    }`}>
                      {pipelineResult.risk_level}
                    </span>
                  </div>
                  
                  <div className="flex flex-col items-center justify-center py-4 relative">
                    <span className={`text-5xl font-black font-mono tracking-tight ${
                      pipelineResult.overall_risk_score >= 0.8 ? "text-rose-500" : "text-amber-500"
                    }`}>
                      {(pipelineResult.overall_risk_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1.5">Aggregate Risk Percentage</span>
                    
                    <div className="w-full bg-slate-900 h-2 rounded-full border border-slate-800 mt-6">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${
                          pipelineResult.overall_risk_score >= 0.8 ? "bg-rose-500" : "bg-amber-500"
                        }`}
                        style={{ width: `${pipelineResult.overall_risk_score * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="border-t border-slate-800/80 pt-3 space-y-2">
                    <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block">Contributing Threat Factors</span>
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      {[
                        { label: "Scam Pattern", met: pipelineResult.scam_result?.status === "SUCCESS" },
                        { label: "Fraud Ring", met: pipelineResult.graph_result?.fraud_rings?.length > 0 },
                        { label: "High Urgency", met: pipelineResult.scam_result?.intent_flags?.urgency },
                        { label: "Multiple Complaints", met: (pipelineResult.graph_result?.edges_added || 0) > 3 }
                      ].map((factor, fIdx) => (
                        <div 
                          key={fIdx} 
                          className={`flex items-center gap-1.5 px-2 py-1.5 rounded-lg border font-medium ${
                            factor.met 
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                              : "bg-slate-900/60 text-slate-600 border-slate-850"
                          }`}
                        >
                          <span className="text-xs">{factor.met ? "✔" : "✘"}</span>
                          <span>{factor.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Case Summary Panel (Requirement 9) */}
                <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4 lg:col-span-2 flex flex-col justify-between">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                      <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Info className="w-4 h-4 text-emerald-400" /> Human-Readable Case Explainer
                      </h3>
                      <button
                        onClick={() => handleCopyToClipboard(dynamicSummaryText, 'summary')}
                        className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        {copiedSummary ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        {copiedSummary ? 'Copied' : 'Copy'}
                      </button>
                    </div>

                    <div className="bg-slate-900/50 border border-slate-850 p-4.5 rounded-xl text-xs leading-relaxed text-slate-300 font-sans">
                      {dynamicSummaryText}
                    </div>
                  </div>

                  <div className="border-t border-slate-800/80 pt-4 flex justify-between items-center">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                      Aggregate Case confidence: {(pipelineResult.confidence * 100).toFixed(0)}%
                    </span>
                    
                    <div className="flex gap-2">
                      <button 
                        onClick={handlePrintReport}
                        className="text-[10px] font-bold bg-slate-900 border border-slate-800 text-slate-300 hover:text-emerald-400 p-2 rounded-lg flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        <Printer className="w-3.5 h-3.5" /> Export PDF Docket
                      </button>
                      <button 
                        onClick={handleDownloadJson}
                        className="text-[10px] font-bold bg-slate-900 border border-slate-800 text-slate-300 hover:text-emerald-400 p-2 rounded-lg flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" /> Export Case JSON
                      </button>
                    </div>
                  </div>
                </div>

              </div>

              {/* Side-by-Side: Live Multi-Agent Panel & Timeline (Requirement 1 & 2) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Left Card: Live Multi-Agent Panel */}
                <div className="bg-slate-950 border border-slate-805 rounded-2xl p-6 shadow-xl lg:col-span-2 space-y-4">
                  <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                    <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Activity className="w-4 h-4 text-emerald-400 animate-pulse" /> Live Multi-Agent Execution Board
                    </h3>
                    <span className="text-[9px] bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-slate-500 font-bold font-mono">
                      ENG-V2
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-slate-300">
                      <thead>
                        <tr className="border-b border-slate-850 text-slate-500 text-[10px] font-bold uppercase tracking-wider text-left">
                          <th className="pb-2.5">Agent Service</th>
                          <th className="pb-2.5">Status</th>
                          <th className="pb-2.5">Execution</th>
                          <th className="pb-2.5">Confidence</th>
                          <th className="pb-2.5">Alerts / Failures</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-850">
                        {agentExecutionList.map((agent, aIdx) => {
                          const res = agent.result;
                          const status = res?.status || (executing ? "RUNNING" : "WAITING");
                          const isSuccess = status === "SUCCESS";
                          const isFailed = status === "FAILED";
                          const isSkipped = status === "SKIPPED";
                          const isRunning = status === "RUNNING";
                          
                          return (
                            <tr key={aIdx} className="hover:bg-slate-900/40 transition-colors">
                              <td className="py-3 font-semibold text-slate-200">{agent.label}</td>
                              <td className="py-3">
                                <span className={`text-[9px] font-bold px-2 py-0.5 rounded border uppercase ${
                                  isSuccess 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                                    : isFailed 
                                      ? "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse" 
                                      : isSkipped 
                                        ? "bg-slate-900 text-slate-500 border-slate-850" 
                                        : "bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse"
                                }`}>
                                  {status}
                                </span>
                              </td>
                              <td className="py-3 font-mono text-slate-400">
                                {isSuccess && res.execution_time_ms ? `${res.execution_time_ms.toFixed(0)} ms` : "—"}
                              </td>
                              <td className="py-3 font-mono font-bold text-slate-350">
                                {isSuccess && res.confidence !== undefined ? `${(res.confidence * 100).toFixed(0)}%` : "—"}
                              </td>
                              <td className="py-3 text-[10px]">
                                {isFailed && (
                                  <span className="text-rose-400 flex items-center gap-1 truncate max-w-[160px]" title={res.reason}>
                                    <AlertCircle className="w-3.5 h-3.5 shrink-0" /> {res.reason}
                                  </span>
                                )}
                                {isSkipped && (
                                  <span className="text-slate-500 flex items-center gap-1 truncate max-w-[160px]" title={res.reason}>
                                    <Info className="w-3.5 h-3.5 shrink-0" /> {res.reason}
                                  </span>
                                )}
                                {isSuccess && res.warning && (
                                  <span className="text-amber-400 flex items-center gap-1 truncate max-w-[160px]" title={res.warning}>
                                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" /> {res.warning}
                                  </span>
                                )}
                                {isSuccess && !res.warning && <span className="text-emerald-500">None</span>}
                                {status === "WAITING" && <span className="text-slate-600">Pending parent node</span>}
                                {isRunning && <span className="text-amber-400 animate-pulse">Processing...</span>}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Right Card: Chronological Investigation Timeline */}
                <div className="bg-slate-950 border border-slate-805 rounded-2xl p-6 shadow-xl space-y-4 flex flex-col justify-between min-h-[300px]">
                  <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                    <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-emerald-400" /> Case Activity Stream
                    </h3>
                  </div>

                  <div className="flex-1 overflow-y-auto space-y-4 max-h-[220px] pr-1 mt-2">
                    {timelineEvents.map((evt, idx) => (
                      <div key={idx} className="flex gap-3 text-xs">
                        <div className="flex flex-col items-center">
                          <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                            evt.status === "FAILED" ? "bg-rose-500" : "bg-emerald-400"
                          }`} />
                          {idx < timelineEvents.length - 1 && (
                            <span className="w-[1.5px] bg-slate-800 flex-1 my-1" />
                          )}
                        </div>
                        <div className="space-y-0.5">
                          <span className="text-[10px] text-slate-500 font-mono font-semibold block">{evt.time}</span>
                          <span className={`font-medium ${evt.status === 'FAILED' ? 'text-rose-455' : 'text-slate-300'}`}>{evt.event}</span>
                        </div>
                      </div>
                    ))}
                    <div ref={timelineEndRef} />
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: FILE ANALYZER PANEL */}
          {activeTab === 'analyzer' && (
            <div className="space-y-6">
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Form Controls Column */}
                <form onSubmit={handleRunPipeline} className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <FileSearch className="w-4.5 h-4.5 text-emerald-400" /> Evidence Ingest Form
                    </h3>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => { setLat('28.6139'); setLon('77.2090'); }}
                        className="text-[9px] bg-slate-900 border border-slate-800 px-2 py-1 rounded hover:bg-slate-800 font-mono text-slate-400 font-bold cursor-pointer"
                      >
                        Delhi
                      </button>
                      <button
                        type="button"
                        onClick={() => { setLat('22.8046'); setLon('86.2029'); }}
                        className="text-[9px] bg-slate-900 border border-slate-800 px-2 py-1 rounded hover:bg-slate-800 font-mono text-slate-400 font-bold cursor-pointer"
                      >
                        Jamshedpur
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Case Session ID</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="text"
                          required
                          value={caseId}
                          onChange={(e) => setCaseId(e.target.value)}
                          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-600"
                        />
                        <button
                          type="button"
                          onClick={handleGenerateCaseId}
                          className="bg-slate-900 hover:bg-slate-800 border border-slate-805 text-slate-400 p-2 rounded-xl text-xs transition-colors cursor-pointer"
                          title="Generate Random Case ID"
                        >
                          <RefreshCw className="w-4.5 h-4.5" />
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Complainant Name</label>
                      <input
                        type="text"
                        required
                        value={complainantName}
                        onChange={(e) => setComplainantName(e.target.value)}
                        className="w-full mt-1 bg-slate-900 border border-slate-850 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-sans"
                        placeholder="Name"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Complainant Contact</label>
                      <input
                        type="text"
                        required
                        value={complainantContact}
                        onChange={(e) => setComplainantContact(e.target.value)}
                        className="w-full mt-1 bg-slate-900 border border-slate-855 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
                        placeholder="Contact number"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Incident Lat</label>
                      <input
                        type="text"
                        required
                        value={lat}
                        onChange={(e) => setLat(e.target.value)}
                        className="w-full mt-1 bg-slate-900 border border-slate-855 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
                        placeholder="Latitude"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Incident Lon</label>
                      <input
                        type="text"
                        required
                        value={lon}
                        onChange={(e) => setLon(e.target.value)}
                        className="w-full mt-1 bg-slate-900 border border-slate-855 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
                        placeholder="Longitude"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Complainant Statement / Incident Text</label>
                    <textarea
                      required
                      rows="4"
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      className="w-full mt-1 bg-slate-900 border border-slate-855 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-sans leading-relaxed"
                      placeholder="Input the core details of the WhatsApp call, QR Scam details, or banking fraud details..."
                    />
                  </div>

                  {/* Drag Drop uploads */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col items-center justify-center text-center">
                      <Upload className="w-7 h-7 text-slate-500 mb-2" />
                      <span className="text-[11px] font-bold text-slate-400 block">Voice Evidence (Audio)</span>
                      <span className="text-[9px] text-slate-600 block mt-0.5">MP3 / WAV cloning check</span>
                      <input 
                        type="file" 
                        accept="audio/*" 
                        onChange={(e) => setAudioFile(e.target.files[0])}
                        className="mt-2.5 text-[10px] text-slate-400 file:bg-slate-800 file:text-slate-300 file:border-0 file:px-2.5 file:py-1 file:rounded-lg file:hover:bg-slate-700 cursor-pointer"
                      />
                      {audioFile && <p className="text-[9px] text-emerald-400 font-bold font-mono mt-1">✓ {audioFile.name}</p>}
                    </div>

                    <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col items-center justify-center text-center">
                      <Upload className="w-7 h-7 text-slate-500 mb-2" />
                      <span className="text-[11px] font-bold text-slate-400 block">Visual Evidence (Image)</span>
                      <span className="text-[9px] text-slate-600 block mt-0.5">Counterfeit currency snapshot</span>
                      <input 
                        type="file" 
                        accept="image/*" 
                        onChange={(e) => setImageFile(e.target.files[0])}
                        className="mt-2.5 text-[10px] text-slate-400 file:bg-slate-800 file:text-slate-300 file:border-0 file:px-2.5 file:py-1 file:rounded-lg file:hover:bg-slate-700 cursor-pointer"
                      />
                      {imageFile && <p className="text-[9px] text-emerald-400 font-bold font-mono mt-1">✓ {imageFile.name}</p>}
                    </div>
                  </div>

                  {/* Run Pipeline Button */}
                  <button
                    type="submit"
                    disabled={executing}
                    className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold py-3 rounded-xl shadow-lg transition-colors cursor-pointer"
                  >
                    {executing ? (
                      <RefreshCw className="w-5 h-5 animate-spin" />
                    ) : (
                      <Play className="w-5 h-5" />
                    )}
                    {executing ? 'Executing Sentinel Agents...' : 'Execute Multi-Agent Pipeline'}
                  </button>

                </form>

                {/* Pipeline Status Tracking & Detail Cards Column */}
                <div className="space-y-6">
                  
                  {/* Status Tracker (Requirement 7 - Custom Loading Stages) */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-4">Orchestrator Processing Stages</h4>
                    
                    <div className="space-y-3">
                      {[
                        { stage: 'uploading', label: 'Uploading Complaint...' },
                        { stage: 'scam_analysis', label: 'Running Scam Analysis...' },
                        { stage: 'voice_analysis', label: 'Running Voice Intelligence...' },
                        { stage: 'counterfeit_analysis', label: 'Authenticating Currency Note...' },
                        { stage: 'graph_analysis', label: 'Building Fraud Graph...' },
                        { stage: 'geo_analysis', label: 'Running Geospatial Hotspots...' },
                        { stage: 'done', label: 'Preparing Final Report...' }
                      ].map((step, idx) => {
                        const isDone = pipelineStage === 'done' || 
                          (pipelineStage === 'geo_analysis' && idx < 5) ||
                          (pipelineStage === 'graph_analysis' && idx < 4) ||
                          (pipelineStage === 'counterfeit_analysis' && idx < 3) ||
                          (pipelineStage === 'voice_analysis' && idx < 2) ||
                          (pipelineStage === 'scam_analysis' && idx < 1);
                        const isActive = pipelineStage === step.stage;
                        return (
                          <div key={idx} className="flex items-center gap-3.5 text-xs text-slate-300">
                            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold border font-mono ${
                              isDone 
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                                : isActive 
                                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse' 
                                  : 'bg-slate-900 text-slate-650 border-slate-850'
                            }`}>
                              {isDone ? '✓' : idx + 1}
                            </span>
                            <span className={isActive ? 'font-bold text-amber-400' : isDone ? 'text-slate-400' : 'text-slate-600'}>
                              {step.label}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Partial Failure handling alerts (Requirement 6) */}
                  {pipelineStage === 'done' && (
                    <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
                      
                      {agentExecutionList.filter(a => a.result && a.result.status === "FAILED").map((agent, idx) => (
                        <div key={idx} className="bg-rose-500/10 border border-rose-500/20 p-4 rounded-xl flex gap-3 text-xs text-rose-300">
                          <AlertOctagon className="w-5 h-5 shrink-0 text-rose-400" />
                          <div className="space-y-1">
                            <h5 className="font-bold">{agent.label} Failed</h5>
                            <p className="text-[10px] text-rose-455">Reason: {agent.result.reason}</p>
                          </div>
                        </div>
                      ))}

                      {/* Scam result detail card */}
                      <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                          <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                            <AlertCircle className="w-4 h-4 text-emerald-400" /> Scam Analysis
                          </span>
                          <span className="text-[10px] bg-slate-900 text-slate-400 font-bold px-2 py-0.5 rounded border border-slate-800">
                            Confidence: {(pipelineResult.scam_result?.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{pipelineResult.scam_result?.explanation}</p>
                        
                        <div className="flex gap-2">
                          {Object.entries(pipelineResult.scam_result?.intent_flags || {}).map(([flag, val]) => (
                            <span key={flag} className={`text-[9px] font-bold px-2 py-0.5 rounded border uppercase ${
                              val ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-slate-900 text-slate-600 border-slate-800'
                            }`}>
                              {flag}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Voice result detail card */}
                      {pipelineResult.voice_result?.status === 'SUCCESS' && (
                        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                            <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                              <Shield className="w-4 h-4 text-rose-500" /> Voice Deepfake Audit
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                              pipelineResult.voice_result.is_deepfake 
                                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse' 
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            }`}>
                              {pipelineResult.voice_result.is_deepfake ? 'DEEPFAKE SUSPECTED' : 'GENUINE RECORDING'}
                            </span>
                          </div>
                          <div className="bg-slate-900 p-3 rounded-lg border border-slate-800/80">
                            <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider mb-1">Transcript</span>
                            <p className="text-xs text-slate-300 font-mono italic leading-relaxed">"{pipelineResult.voice_result.transcript}"</p>
                          </div>
                          <div className="grid grid-cols-2 gap-3 text-[10px]">
                            <div className="bg-slate-900/60 p-2 rounded border border-slate-800 flex justify-between">
                              <span className="text-slate-500 font-bold">Emotion:</span>
                              <span className="font-mono text-slate-200 capitalize">{pipelineResult.voice_result.emotion}</span>
                            </div>
                            <div className="bg-slate-900/60 p-2 rounded border border-slate-800 flex justify-between">
                              <span className="text-slate-500 font-bold">Confidence:</span>
                              <span className="font-mono text-slate-200">{(pipelineResult.voice_result.deepfake_confidence * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Counterfeit note card */}
                      {pipelineResult.counterfeit_result?.status === 'SUCCESS' && (
                        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                            <span className="text-xs font-bold text-slate-305 flex items-center gap-2">
                              <DollarSign className="w-4 h-4 text-emerald-400" /> Currency Verification
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                              pipelineResult.counterfeit_result.is_counterfeit 
                                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            }`}>
                              {pipelineResult.counterfeit_result.is_counterfeit ? 'COUNTERFEIT ALERT' : 'VALID CURRENCY'}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400">{pipelineResult.counterfeit_result.explanation}</p>
                          <div className="grid grid-cols-3 gap-2">
                            {Object.entries(pipelineResult.counterfeit_result.security_features).map(([feat, status]) => {
                              if (feat.endsWith("_conf")) return null;
                              return (
                                <div key={feat} className="bg-slate-900 border border-slate-800 p-2 rounded flex flex-col justify-between">
                                  <span className="text-[8px] text-slate-500 font-bold uppercase tracking-wider">{feat.replace('_', ' ')}</span>
                                  <span className={`text-[10px] font-bold font-mono ${
                                    status === 'pass' ? 'text-emerald-400' : status === 'fail' ? 'text-rose-400' : 'text-slate-500'
                                  }`}>
                                    {status.toUpperCase()}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                    </div>
                  )}

                </div>

              </div>

            </div>
          )}

          {/* TAB 3: EVIDENCE REPOSITORY (Requirement 4) */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex justify-between items-center flex-wrap gap-4 border-b border-slate-800 pb-4">
                  <div>
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                      <FileText className="w-4.5 h-4.5 text-emerald-400" /> Evidence Audit Manifest
                    </h3>
                    <p className="text-[10px] text-slate-500 mt-1">Search, audit, and trace custody elements from the consolidated database.</p>
                  </div>
                  
                  {/* Search box & Category tabs */}
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <input 
                        type="text"
                        value={evidenceSearch}
                        onChange={(e) => setEvidenceSearch(e.target.value)}
                        placeholder="Search values, types..."
                        className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 pl-8"
                      />
                      <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                    </div>
                  </div>
                </div>

                {/* Evidence Sub-Tabs */}
                <div className="flex gap-2 border-b border-slate-850 pb-3 flex-wrap">
                  {[
                    { id: 'all', label: 'All Artifacts' },
                    { id: 'communication', label: 'Communication (Phone/Web)' },
                    { id: 'financial', label: 'Financial (UPI/Accounts)' },
                    { id: 'identity', label: 'Identity (Names)' },
                    { id: 'media', label: 'Media (Files)' },
                    { id: 'location', label: 'Location (GPS)' }
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setEvidenceFilter(tab.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                        evidenceFilter === tab.id 
                          ? 'bg-slate-900 border border-slate-700 text-emerald-400 font-bold' 
                          : 'text-slate-450 hover:text-slate-300'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Evidence manifest Grid Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-slate-300">
                    <thead>
                      <tr className="border-b border-slate-850 text-slate-500 text-[10px] font-bold uppercase tracking-wider text-left">
                        <th className="pb-3">Evidence Value</th>
                        <th className="pb-3">Type</th>
                        <th className="pb-3">Ingest Confidence</th>
                        <th className="pb-3">Source Agent</th>
                        <th className="pb-3">Trace Log Context</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-850">
                      {filteredEvidence.length > 0 ? (
                        filteredEvidence.map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                            <td className="py-3.5 font-mono text-slate-200 font-bold break-all select-all">{item.value}</td>
                            <td className="py-3.5">
                              <span className="text-[10px] bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-slate-400 uppercase font-mono">
                                {item.type}
                              </span>
                            </td>
                            <td className="py-3.5 font-mono font-bold text-slate-350">
                              {(item.confidence * 100).toFixed(0)}%
                            </td>
                            <td className="py-3.5 font-mono text-emerald-450">
                              {item.source.replace('_', ' ').replace('agent', '')}
                            </td>
                            <td className="py-3.5 text-slate-450">{item.description}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="5" className="text-center py-10 text-slate-600 font-sans">
                            No evidence artifacts matching filters found.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

              </div>

            </div>
          )}

          {/* TAB 4: FRAUD GRAPH WORKSPACE */}
          {activeTab === 'graph' && (
            <div className="space-y-6 animate-fadeIn">
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* SVG Visual Graph Panel (Requirement 5) */}
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl lg:col-span-2 flex flex-col justify-between min-h-[500px]">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div className="space-y-1">
                      <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                        <Network className="w-4.5 h-4.5 text-emerald-400" /> Fraud Cluster Graph
                      </h3>
                      <p className="text-[9px] text-slate-500">Hold left click to pan, use sliders to zoom.</p>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="flex bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                        <button 
                          onClick={() => handleZoom('out')}
                          className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer"
                          title="Zoom Out"
                        >
                          <ZoomOut className="w-4 h-4" />
                        </button>
                        <span className="px-3 py-2 text-[10px] font-mono text-slate-400 border-x border-slate-800 select-none">
                          {(zoomScale * 100).toFixed(0)}%
                        </span>
                        <button 
                          onClick={() => handleZoom('in')}
                          className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer"
                          title="Zoom In"
                        >
                          <ZoomIn className="w-4 h-4" />
                        </button>
                      </div>
                      <button 
                        onClick={() => { setZoomScale(1.0); setPanOffset({ x: 0, y: 0 }); }}
                        className="text-[10px] bg-slate-900 border border-slate-850 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-slate-400 cursor-pointer"
                      >
                        Reset Workspace
                      </button>
                    </div>
                  </div>

                  {/* SVG Viewport */}
                  <div 
                    className="flex-1 bg-slate-950/60 rounded-xl relative overflow-hidden mt-4 border border-slate-900 flex items-center justify-center cursor-move"
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                  >
                    {graphNodes.length <= 1 ? (
                      <div className="text-xs text-slate-500 text-center py-10 font-sans">
                        No graph clusters available. Run a preset or upload files in the Analyzer.
                      </div>
                    ) : (
                      <svg width="100%" height="400" className="select-none pointer-events-none">
                        
                        <g transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomScale})`}>
                          
                          {/* Edges Paths */}
                          {graphEdges.map((edge, idx) => {
                            const fromNode = graphNodes.find(n => n.id === edge.from);
                            const toNode = graphNodes.find(n => n.id === edge.to);
                            if (!fromNode || !toNode) return null;
                            const isSelected = selectedEdge === idx;
                            return (
                              <g 
                                key={idx} 
                                className="pointer-events-auto cursor-pointer"
                                onClick={(e) => { e.stopPropagation(); setSelectedEdge(idx); }}
                              >
                                <line
                                  x1={fromNode.x}
                                  y1={fromNode.y}
                                  x2={toNode.x}
                                  y2={toNode.y}
                                  stroke={isSelected ? "#34d399" : "#1e293b"}
                                  strokeWidth={isSelected ? "4" : "2.5"}
                                />
                                <line
                                  x1={fromNode.x}
                                  y1={fromNode.y}
                                  x2={toNode.x}
                                  y2={toNode.y}
                                  stroke="#10b981"
                                  strokeWidth="1"
                                  strokeDasharray="4 4"
                                  className="animate-pulse"
                                />
                              </g>
                            );
                          })}

                          {/* Nodes Elements */}
                          {graphNodes.map((node) => {
                            const isCase = node.type === 'Case';
                            const isSuspect = node.type === 'Suspect';
                            const color = isCase 
                              ? '#0f172a' 
                              : node.type === 'Phone' 
                                ? '#3b82f6' 
                                : node.type === 'UPI' 
                                  ? '#a855f7' 
                                  : node.type === 'Bank' 
                                    ? '#6366f1' 
                                    : isSuspect 
                                      ? '#ec4899' 
                                      : '#06b6d4';
                            const stroke = isCase ? '#10b981' : color;
                            const active = hoveredNode === node.id || clickedNode?.id === node.id;
                            const isInRing = pipelineResult?.graph_result?.fraud_rings?.some(r => r.members.some(m => m.includes(node.label)));

                            return (
                              <g 
                                key={node.id}
                                onMouseEnter={() => setHoveredNode(node.id)}
                                onMouseLeave={() => setHoveredNode(null)}
                                onClick={(e) => { e.stopPropagation(); setClickedNode(node); }}
                                className="pointer-events-auto cursor-pointer"
                              >
                                {isInRing && (
                                  <circle
                                    cx={node.x}
                                    cy={node.y}
                                    r={node.size + 10}
                                    fill="none"
                                    stroke="#ef4444"
                                    strokeWidth="1.5"
                                    className="animate-ping"
                                    style={{ animationDuration: '3s' }}
                                  />
                                )}
                                <circle
                                  cx={node.x}
                                  cy={node.y}
                                  r={active ? node.size + 4 : node.size}
                                  fill={color}
                                  stroke={stroke}
                                  strokeWidth={active ? 3 : 1.5}
                                  className="transition-all"
                                />
                                {isCase && (
                                  <path
                                    d={`M ${node.x - 6} ${node.y - 7} L ${node.x + 6} ${node.y - 7} L ${node.x + 6} ${node.y} C ${node.x + 6} ${node.y + 6} ${node.x} ${node.y + 10} ${node.x} ${node.y + 10} C ${node.x} ${node.y + 10} ${node.x - 6} ${node.y + 6} ${node.x - 6} ${node.y} Z`}
                                    fill="none"
                                    stroke="#10b981"
                                    strokeWidth="1.5"
                                  />
                                )}
                                <circle cx={node.x} cy={node.y} r={active ? node.size + 1 : node.size - 3} fill="none" stroke="#10b981" strokeWidth="1" strokeDasharray="3 3" className="animate-spin" style={{ animationDuration: '8s' }} />
                                <text
                                  x={node.x}
                                  y={node.y + node.size + 14}
                                  textAnchor="middle"
                                  fill="#94a3b8"
                                  fontSize="9"
                                  fontWeight="bold"
                                  className="font-mono"
                                >
                                  {node.label.length > 15 ? `${node.label.slice(0, 12)}...` : node.label}
                                </text>
                              </g>
                            );
                          })}

                        </g>
                      </svg>
                    )}
                  </div>

                  <div className="flex gap-4 mt-2 text-[10px] text-slate-500 font-bold justify-center uppercase border-t border-slate-900 pt-3">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-900 border border-emerald-450" /> Case ID</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> Phones</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500" /> UPI IDs</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Bank Accounts</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full border border-red-500 animate-pulse bg-red-500/10" /> Ring Member</span>
                  </div>

                </div>

                {/* Node Details & Ring communities sidebar */}
                <div className="space-y-6">
                  
                  {/* Selected Node Details Card */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl min-h-[220px]">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-900 pb-2">
                      Entity inspector
                    </h4>
                    
                    {clickedNode || hoveredNode ? (
                      (() => {
                        const targetNode = clickedNode || graphNodes.find(n => n.id === hoveredNode);
                        if (!targetNode) return null;
                        const isRingMember = pipelineResult?.graph_result?.fraud_rings?.some(r => r.members.some(m => m.includes(targetNode.label)));
                        return (
                          <div className="space-y-3 mt-3">
                            <div className="flex justify-between items-start">
                              <span className="text-[9px] bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded uppercase font-bold font-mono">
                                {targetNode.type}
                              </span>
                              {isRingMember && (
                                <span className="text-[9px] bg-rose-500/15 border border-rose-500/25 text-rose-400 px-2 py-0.5 rounded uppercase font-bold">
                                  Ring Suspect
                                </span>
                              )}
                            </div>
                            
                            <p className="text-sm font-mono font-bold text-slate-200 break-all select-all">{targetNode.label}</p>
                            
                            {targetNode.type !== 'Case' && (
                              <div className="bg-slate-900 p-2.5 rounded border border-slate-800/80 text-[10px] text-slate-400 leading-relaxed font-sans space-y-1">
                                <span className="font-bold text-slate-500 block uppercase">Audit findings:</span>
                                <p>PageRank Centrality Score: {targetNode.pr?.toFixed(4) || '0.000'}</p>
                                <p>Source Agent: Scam Detection Agent</p>
                              </div>
                            )}
                          </div>
                        );
                      })()
                    ) : (
                      <div className="text-xs text-slate-500 text-center py-10 font-sans">
                        Hover or click any network node to inspect its central properties and PageRank connections.
                      </div>
                    )}
                  </div>

                  {/* Selected Edge Details Card */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl min-h-[140px]">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-900 pb-2">
                      Relationship Link inspector
                    </h4>
                    {selectedEdge !== null && graphEdges[selectedEdge] ? (
                      <div className="space-y-3 mt-3 text-xs leading-relaxed text-slate-300">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="font-mono text-emerald-450 font-bold">MENTIONS</span>
                          <span className="font-mono text-slate-500">Confidence: 95%</span>
                        </div>
                        <p className="text-[10px] text-slate-400 bg-slate-900 p-2.5 rounded border border-slate-800">
                          <strong>Evidence:</strong> Target link parsed and verified by Scam Detection NLP.
                        </p>
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500 text-center py-6 font-sans">
                        Click on a green connecting line to inspect the edge metadata and evidence path.
                      </div>
                    )}
                  </div>

                  {/* Louvain Fraud Rings communities */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-2">
                      Louvain Detected Fraud Rings
                    </h4>

                    {pipelineResult.graph_result?.fraud_rings?.length > 0 ? (
                      pipelineResult.graph_result.fraud_rings.map((ring, idx) => (
                        <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-2">
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-bold text-rose-455 font-mono">{ring.ring_id}</span>
                            <span className="text-[9px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-1.5 py-0.5 rounded font-bold uppercase">
                              {ring.risk_level}
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-500 font-bold uppercase">Cluster size: {ring.size} suspects</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {ring.members.map((m, mIdx) => (
                              <span key={mIdx} className="text-[9px] bg-slate-950 border border-slate-850 px-2 py-0.5 rounded font-mono text-slate-300">
                                {m.split('_')[1] || m}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-slate-500 text-center py-6">
                        No fraud ring communities detected.
                      </div>
                    )}
                  </div>

                </div>

              </div>

            </div>
          )}

          {/* TAB 5: CRIME HOTSPOTS HEATMAP LAYOUT */}
          {activeTab === 'heatmap' && (
            <div className="space-y-6 animate-fadeIn">
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Simulated folium map display / Radar */}
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl lg:col-span-2 flex flex-col justify-between min-h-[460px]">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Map className="w-4.5 h-4.5 text-emerald-400" /> Geospatial Safety Heatmap
                    </h3>
                    <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Incident Coordinate Focal Point</span>
                  </div>

                  {/* Pulsing Visual Radar Simulation Map */}
                  <div className="flex-1 bg-slate-950/70 border border-slate-900 rounded-xl relative overflow-hidden mt-4 flex items-center justify-center min-h-[300px]">
                    
                    <div className="absolute w-[360px] h-[360px] border border-slate-800/20 rounded-full animate-pulse" />
                    <div className="absolute w-[240px] h-[240px] border border-slate-800/35 rounded-full" />
                    <div className="absolute w-[120px] h-[120px] border border-slate-800/40 rounded-full" />
                    
                    <div className="absolute w-full h-[1px] bg-slate-800/30" />
                    <div className="absolute h-full w-[1px] bg-slate-800/30" />

                    {/* Target Focal Spot marker */}
                    {lat && lon && (
                      <div className="absolute w-2.5 h-2.5 bg-emerald-500 border border-slate-100 rounded-full shadow-lg z-10" />
                    )}

                    {/* Glowing hotspots pulsing */}
                    {pipelineResult.geo_result?.status === 'SUCCESS' && (pipelineResult.geo_result.hotspots || []).map((hs, idx) => {
                      const offsets = [
                        { x: 50, y: -40 },
                        { x: -70, y: 50 }
                      ];
                      const pos = offsets[idx % offsets.length];
                      return (
                        <div 
                          key={idx} 
                          className="absolute flex flex-col items-center select-none"
                          style={{ transform: `translate(${pos.x}px, ${pos.y}px)` }}
                        >
                          <span className="absolute w-9 h-9 bg-rose-500/25 border border-rose-500/50 rounded-full animate-ping" />
                          <span className="w-4.5 h-4.5 bg-rose-600 rounded-full border-2 border-slate-100 flex items-center justify-center shadow-lg" />
                          
                          <div className="bg-slate-950 border border-slate-800 rounded px-2 py-1 mt-1.5 text-[9px] font-mono text-slate-300 pointer-events-none shadow-xl border-slate-800">
                            <span className="font-bold text-slate-200 block uppercase">Cluster Hotspot {idx + 1}</span>
                            <span>Size: {hs.complaint_count} cases | Rad: {hs.radius_km}km</span>
                          </div>
                        </div>
                      );
                    })}

                    <div className="absolute bottom-4 left-4 text-[9px] font-mono bg-slate-900 border border-slate-850 px-3 py-1.5 rounded-lg text-slate-400">
                      Center Coordinates: {lat}, {lon}
                    </div>
                  </div>
                </div>

                {/* Hotspot details lists & Recharts graph */}
                <div className="space-y-6">
                  
                  {/* Hotspots and Patrol recommendation panel */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-1">
                      <Clock className="w-4 h-4 text-emerald-400" /> Patrol Advisories
                    </h4>

                    <div className="space-y-3">
                      {pipelineResult.geo_result?.status === 'SUCCESS' && (pipelineResult.geo_result.patrol_recommendations || []).map((rec, idx) => (
                        <div key={idx} className="bg-slate-900/60 border border-slate-800/80 p-3 rounded-xl text-[11px] leading-relaxed text-slate-300 flex items-start gap-2.5">
                          <CheckCircle className="w-4.5 h-4.5 text-emerald-400 mt-0.5 shrink-0" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recharts Temporal Trend Chart */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-1.5">
                      <TrendingUp className="w-4 h-4 text-emerald-400" /> Hour-of-Day Crime Density
                    </h4>
                    
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={getTemporalChartData()}>
                          <XAxis dataKey="hour" stroke="#475569" fontSize={8} tickLine={false} />
                          <YAxis stroke="#475569" fontSize={8} tickLine={false} width={15} />
                          <Tooltip 
                            contentStyle={{ background: '#090d16', borderColor: '#1e293b', fontSize: 10 }}
                            labelStyle={{ color: '#94a3b8', fontWeight: 'bold' }}
                          />
                          <Bar dataKey="complaints" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                </div>

              </div>

            </div>
          )}

          {/* TAB 5: INVESTIGATION COPILOT AI CHAT */}
          {activeTab === 'copilot' && (
            <div className="h-[calc(100vh-12rem)] flex gap-6">
              
              {/* Main Messenger Panel */}
              <div className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl shadow-xl flex flex-col justify-between overflow-hidden">
                
                {/* Chat Header */}
                <div className="bg-slate-950 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
                      <MessageSquareCode className="w-5 h-5 animate-pulse" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-200">AI Investigation Assistant</h3>
                      <p className="text-[10px] text-slate-500 mt-0.5">Connected to Hybrid RAG Case Repository</p>
                    </div>
                  </div>
                  <span className="text-[10px] bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                    Top-K: 5
                  </span>
                </div>

                {/* Log messages scroll */}
                <div className="flex-1 p-6 overflow-y-auto space-y-4 max-h-[calc(100vh-25rem)]">
                  {chatHistory.map((msg, idx) => (
                    <div 
                      key={idx} 
                      className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                    >
                      <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold border ${
                        msg.role === 'user' 
                          ? 'bg-emerald-500/25 border-emerald-500/30 text-emerald-400' 
                          : 'bg-slate-900 border-slate-850 text-slate-405'
                      }`}>
                        {msg.role === 'user' ? 'NJ' : 'AI'}
                      </div>
                      
                      <div className="space-y-1.5">
                        <div className={`rounded-2xl p-4 text-xs leading-relaxed ${
                          msg.role === 'user' 
                            ? 'bg-emerald-600 text-white rounded-tr-none' 
                            : 'bg-slate-900 border border-slate-800 rounded-tl-none text-slate-300'
                        }`}>
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                          
                          {/* Similar Cases block */}
                          {msg.similarCases && msg.similarCases.length > 0 && (
                            <div className="mt-3 border-t border-slate-800/80 pt-2 text-[9px] text-slate-500 font-bold uppercase">
                              <span>Correlated Case dossiers:</span>
                              <div className="flex gap-1.5 mt-1">
                                {msg.similarCases.map((cId, cIdx) => (
                                  <span key={cIdx} className="bg-slate-950 px-2 py-0.5 border border-slate-850 rounded text-slate-400 font-mono">
                                    {cId}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Hallucination guard indicator */}
                        {msg.hallucinationGuardTriggered && (
                          <span className="text-[9px] text-rose-455 font-bold uppercase block px-1 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Hallucination Guard Blocked Response
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {chatLoading && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-900 border border-slate-850 flex items-center justify-center text-xs text-slate-500">
                        ...
                      </div>
                      <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none p-4 text-xs text-slate-500 flex items-center gap-2">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Fact-Checking facts...
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {/* Input box form */}
                <form onSubmit={handleChatSubmit} className="bg-slate-950 border-t border-slate-800 p-4 flex gap-3 shrink-0">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask regarding BNS sections, suspect phone links, or deepfake spectral checks..."
                    className="flex-1 bg-slate-900 border border-slate-805 rounded-xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-600"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold p-3 rounded-xl shadow-lg transition-colors cursor-pointer"
                  >
                    <Send className="w-4.5 h-4.5" />
                  </button>
                </form>

              </div>

              {/* Citations panel details */}
              <div className="w-80 bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col shrink-0">
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-1">
                  <FileText className="w-4 h-4 text-emerald-400" /> Fusion RAG Citations
                </h4>
                
                <div className="flex-1 overflow-y-auto mt-4 space-y-4">
                  {chatHistory[chatHistory.length - 1]?.citations && chatHistory[chatHistory.length - 1].citations.length > 0 ? (
                    chatHistory[chatHistory.length - 1].citations.map((cite, idx) => (
                      <div key={idx} className="bg-slate-900 border border-slate-850 rounded-xl p-3.5 space-y-2">
                        <div className="flex justify-between items-center text-[9px]">
                          <span className="font-mono text-emerald-450 font-bold">{cite.source_id}</span>
                          <span className="text-[9px] bg-slate-950 border border-slate-800 text-slate-500 px-1.5 py-0.5 rounded font-mono font-bold">
                            Score: {cite.relevance_score}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 leading-relaxed italic font-sans">
                          "...{cite.chunk_text}..."
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 text-center py-10">
                      Query citation document segments will output here automatically.
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

        </div>

      </main>
    </div>
  );
}