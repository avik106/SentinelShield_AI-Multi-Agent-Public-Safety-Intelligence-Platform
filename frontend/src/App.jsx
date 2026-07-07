import React, { useState, useEffect, useRef } from 'react';
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
  RefreshCw
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Comprehensive mock data that aligns perfectly with our backend schema
const MOCK_INITIAL_RESULT = {
  case_id: "CASE-2026-9081",
  overall_risk_score: 0.88,
  risk_level: "HIGH",
  scam_result: {
    risk_score: 0.9,
    risk_level: "HIGH",
    scam_type: "digital_arrest",
    confidence: 0.92,
    entities: {
      phone_numbers: ["+91 98765 43210", "+91 81302 99421"],
      upi_ids: ["cbi.officer@ybl", "payment.police@paytm"],
      bank_accounts: ["30219482103 (SBI)", "88291048231 (HDFC)"],
      urls: ["http://cbi-arrest-verification.in", "https://fake-police-portal.gov.in"],
      amounts: ["₹50,000", "₹1,20,000"],
      names: ["Rajesh Kumar", "DCP Sanjay Sharma (Suspect)"],
      emails: ["dcp.sharma@fake-cbi.gov.in"],
      ip_addresses: ["192.168.4.12", "103.242.118.9"]
    },
    explanation: "High-urgency social engineering scam involving impersonation of central law enforcement officials (CBI/IPS). The suspect used threat vectors ('Digital Arrest') via WhatsApp video call, demanding payment to resolve fictitious money laundering allegations.",
    language: "en",
    intent_flags: {
      urgency: true,
      impersonation: true,
      payment_request: true
    }
  },
  voice_result: {
    transcript: "This is Deputy Commissioner Sanjay Sharma from the Crime Branch. Your Aadhaar number has been flagged in a cross-border money laundering scheme. You are under digital arrest. Transfer fifty thousand rupees to the designated verification account immediately to clear your name or a police team will be dispatched.",
    is_deepfake: true,
    deepfake_confidence: 0.94,
    emotion: "aggressive",
    speaker_count: 1,
    audio_duration_seconds: 22.4,
    risk_score: 0.95,
    risk_level: "CRITICAL",
    explanation: "Speech synthesis analysis shows anomalous spectral characteristics matching known voice-cloning models. Emotion is highly coercive and threatening, intended to induce immediate panic."
  },
  counterfeit_result: {
    is_counterfeit: true,
    confidence: 0.89,
    denomination: "500",
    serial_number: "5AP 882910",
    security_features: {
      security_thread: "fail",
      watermark: "pass",
      microprint: "fail",
      color_shift: "fail",
      serial_pattern: "fail",
      uv_feature: "fail"
    },
    risk_score: 0.75,
    risk_level: "HIGH",
    explanation: "Currency note image shows security thread anomalies (no color-shift/optically variable ink property) and microprinting blurriness under magnification."
  },
  graph_result: {
    entities_added: [
      "Complaint_CASE-2026-9081",
      "Phone_+91 98765 43210",
      "Phone_+91 81302 99421",
      "UPI_cbi.officer@ybl",
      "UPI_payment.police@paytm",
      "BankAccount_30219482103 (SBI)"
    ],
    edges_added: 8,
    pagerank_scores: {
      "UPI_cbi.officer@ybl": 0.324,
      "Phone_+91 81302 99421": 0.285,
      "BankAccount_30219482103 (SBI)": 0.182,
      "UPI_payment.police@paytm": 0.118,
      "Phone_+91 98765 43210": 0.091
    },
    fraud_rings: [
      {
        ring_id: "RING-401",
        members: ["UPI_cbi.officer@ybl", "Phone_+91 81302 99421", "BankAccount_30219482103 (SBI)"],
        size: 3,
        risk_level: "CRITICAL",
        fraud_types: ["digital_arrest", "upi_fraud"]
      }
    ],
    high_risk_nodes: ["UPI_cbi.officer@ybl", "Phone_+91 81302 99421"],
    risk_score: 0.85,
    risk_level: "HIGH",
    explanation: "Louvain clustering detected an active fraud ring (RING-401) linking the suspect phone number to the target bank account and UPI address. PageRank highlights UPI_cbi.officer@ybl as a high-influence collection node."
  },
  geo_result: {
    hotspots: [
      {
        lat: 22.8046,
        lon: 86.2029,
        radius_km: 1.25,
        complaint_count: 13,
        dominant_fraud_type: "upi_fraud",
        risk_level: "HIGH"
      },
      {
        lat: 22.8396,
        lon: 86.1679,
        radius_km: 0.95,
        complaint_count: 9,
        dominant_fraud_type: "digital_arrest",
        risk_level: "MEDIUM"
      }
    ],
    patrol_recommendations: [
      "Deploy patrol to Jamshedpur City Center (22.8046, 86.2029) — 13 upi_fraud complaints within 1.25 km.",
      "Deploy patrol to Adityapur Industrial Area (22.8396, 86.1679) — 9 digital_arrest complaints within 0.95 km."
    ],
    temporal_trend: {
      "9": 1, "10": 2, "11": 4, "12": 6, "13": 5, "14": 3, "15": 2, "16": 4, "17": 5, "18": 8, "19": 9, "20": 11, "21": 7, "22": 4
    },
    total_complaints_analyzed: 22,
    risk_zones: []
  },
  evidence_package: {
    fir_draft: "FIRST INFORMATION REPORT\n(Under Section 154 CrPC / BNS equivalent)\n\n1. District: Jamshedpur East, Jharkhand\n2. Case ID: CASE-2026-9081\n3. IPC/BNS Sections: Section 66D IT Act, Section 318 BNS (Cheating), Section 319 BNS (Impersonation)\n4. Date & Time: 2026-07-07 10:15 UTC\n5. Complainant: Rajesh Kumar (+91 98765 43210)\n6. Accused Party: Impersonator DCP Sanjay Sharma (+91 81302 99421)\n7. Brief Facts: The complainant was subjected to a WhatsApp video call from a suspect claiming to be DCP Sanjay Sharma of CBI. The suspect placed the victim under 'digital arrest' and extorted ₹50,000 via UPI transaction to designated address 'cbi.officer@ybl'. Investigation details reveal cloned voice characteristics and a localized fraud ring.",
    executive_summary: "High-urgency social engineering scam involving impersonation of central law enforcement officials (CBI/IPS). The suspect used threat vectors ('Digital Arrest') via WhatsApp video call, demanding payment to resolve fictitious money laundering allegations.",
    ipc_sections: ["Section 66D IT Act", "Section 318 BNS (Cheating)", "Section 319 BNS (Impersonation)"],
    recommended_actions: [
      "Freeze target UPI account 'cbi.officer@ybl' and linked State Bank of India account.",
      "Issue Section 91 CrPC notice to telecom operator for suspect number +91 81302 99421.",
      "Establish intelligence monitoring on identified Jamshedpur hotspot zones."
    ]
  }
};

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
  const [pipelineStage, setPipelineStage] = useState('idle'); // idle, uploading, executing, done, error
  const [pipelineResult, setPipelineResult] = useState(MOCK_INITIAL_RESULT);
  const [errorMsg, setErrorMsg] = useState('');

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
  
  // SVG Graph interactive state
  const [hoveredNode, setHoveredNode] = useState(null);
  const [clickedNode, setClickedNode] = useState(null);

  // References for terminal scroll and copy notifications
  const chatEndRef = useRef(null);
  const [copiedFir, setCopiedFir] = useState(false);
  const [copiedSummary, setCopiedSummary] = useState(false);

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
    } else {
      setCopiedSummary(true);
      setTimeout(() => setCopiedSummary(false), 2000);
    }
  };

  // Print Report helper
  const handlePrintReport = () => {
    const printContent = `
      =======================================================
      SENTINELSHIELD AI - INVESTIGATION REPORT
      =======================================================
      Case ID: ${pipelineResult.case_id}
      Overall Risk: ${(pipelineResult.overall_risk_score * 100).toFixed(0)}% (${pipelineResult.risk_level})
      Complainant: ${complainantName} (${complainantContact})
      Coordinates: ${lat}, ${lon}
      
      -------------------------------------------------------
      EXECUTIVE SUMMARY:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.executive_summary || 'N/A'}
      
      -------------------------------------------------------
      RECOMMENDED ACTIONS:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.recommended_actions?.map(a => `- ${a}`).join('\n') || 'N/A'}
      
      -------------------------------------------------------
      IPC / BNS SECTIONS:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.ipc_sections?.join(', ') || 'N/A'}
      
      -------------------------------------------------------
      FIR DRAFT:
      -------------------------------------------------------
      ${pipelineResult.evidence_package?.fir_draft || 'N/A'}
      =======================================================
    `;
    const win = window.open('', '_blank');
    win.document.write(`<pre style="font-family: monospace; padding: 20px; font-size: 14px; background: #0f172a; color: #f1f5f9;">${printContent}</pre>`);
    win.document.close();
    win.print();
  };

  // Trigger Multi-Agent Pipeline
  const handleRunPipeline = async (e) => {
    e.preventDefault();
    setExecuting(true);
    setPipelineStage('uploading');
    setErrorMsg('');

    // If backend is offline, simulate pipeline steps with realistic delay
    if (!backendLive) {
      setTimeout(() => setPipelineStage('scam_analysis'), 600);
      setTimeout(() => setPipelineStage('voice_analysis'), 1200);
      setTimeout(() => setPipelineStage('counterfeit_analysis'), 1800);
      setTimeout(() => setPipelineStage('graph_analysis'), 2400);
      setTimeout(() => setPipelineStage('geo_analysis'), 3000);
      setTimeout(() => {
        // Construct mock result representing the user's inputs
        const hasAudio = !!audioFile;
        const hasImage = !!imageFile;
        const mockResult = {
          ...MOCK_INITIAL_RESULT,
          case_id: caseId,
          overall_risk_score: hasAudio ? 0.92 : 0.82,
          risk_level: hasAudio ? "CRITICAL" : "HIGH",
          scam_result: {
            ...MOCK_INITIAL_RESULT.scam_result,
            ocr_text: hasImage ? "₹500 Bank Note Specimen OCR Text" : null,
            entities: {
              ...MOCK_INITIAL_RESULT.scam_result.entities,
              names: [complainantName, "Suspect (Unknown)"],
              phone_numbers: [complainantContact, "+91 81302 99421"]
            }
          },
          voice_result: hasAudio ? MOCK_INITIAL_RESULT.voice_result : null,
          counterfeit_result: hasImage ? MOCK_INITIAL_RESULT.counterfeit_result : null,
          geo_result: {
            ...MOCK_INITIAL_RESULT.geo_result,
            hotspots: [
              {
                lat: parseFloat(lat),
                lon: parseFloat(lon),
                radius_km: 1.5,
                complaint_count: 15,
                dominant_fraud_type: "upi_fraud",
                risk_level: "HIGH"
              },
              {
                lat: parseFloat(lat) + 0.03,
                lon: parseFloat(lon) - 0.02,
                radius_km: 0.8,
                complaint_count: 7,
                dominant_fraud_type: "digital_arrest",
                risk_level: "MEDIUM"
              }
            ],
            patrol_recommendations: [
              `Deploy patrol near case center (${parseFloat(lat).toFixed(4)}, ${parseFloat(lon).toFixed(4)}) — 15 upi_fraud complaints within 1.5 km.`,
              `Establish safety surveillance near regional cluster (${(parseFloat(lat) + 0.03).toFixed(4)}, ${(parseFloat(lon) - 0.02).toFixed(4)}) — 7 complaints.`
            ]
          },
          evidence_package: {
            ...MOCK_INITIAL_RESULT.evidence_package,
            case_id: caseId,
            fir_draft: `FIRST INFORMATION REPORT\n(Under Section 154 CrPC / BNS equivalent)\n\n1. District: Investigation Zone\n2. Case ID: ${caseId}\n3. IPC/BNS Sections: Section 66D IT Act, Section 318 BNS (Cheating), Section 319 BNS (Impersonation)\n4. Complainant: ${complainantName} (${complainantContact})\n5. Facts of Complaint: Victim reports digital arrest extortion. Source text: "${textInput.slice(0, 150)}..."\n6. Accused: Suspect using number +91 81302 99421.\n7. Digital Sign: SENTINELSHIELD_VERIFIED_SECURE`,
            recommended_actions: [
              "Freeze target UPI account 'cbi.officer@ybl'.",
              `Draft Section 91 CrPC notice for contact details on case ${caseId}.`,
              `Deploy patrol units to geospatial hotspots at center (${parseFloat(lat).toFixed(4)}, ${parseFloat(lon).toFixed(4)}).`
            ]
          }
        };
        setPipelineResult(mockResult);
        setPipelineStage('done');
        setExecuting(false);
      }, 3600);
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
      if (audioFile) formData.append('audio_file', audioFile);
      if (imageFile) formData.append('image_file', imageFile);

      setPipelineStage('executing');
      const res = await fetch(`${apiUrl}/api/pipeline/upload`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`API returned error status: ${res.status}`);
      }

      const data = await res.json();
      setPipelineResult(data);
      setPipelineStage('done');
    } catch (err) {
      console.error(err);
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
          answer = "The Fraud Graph Agent ingested the following primary suspects: suspect telephone +91 81302 99421 and UPI address cbi.officer@ybl. Louvain clustering reveals these belong to Fraud Ring RING-401. This community represents a highly connected ring targeting victims in the Jamshedpur region.";
          citations = [
            { source_id: "graph_extracted_entities", chunk_text: "Ingested UPI ID cbi.officer@ybl with PageRank centrality of 0.324. Clustered with phone number +91 81302 99421 inside RING-401.", relevance_score: 0.952, source_type: "case" }
          ];
        } else if (textLower.includes('voice') || textLower.includes('deepfake') || textLower.includes('audio')) {
          answer = "Voice Intelligence analyzed the suspect's audio and flagged it as a deepfake with 94% confidence. Emotional signature shows aggressive coercion, typical of digital arrest threat calls.";
          citations = [
            { source_id: "voice_analysis_speech", chunk_text: "Audio sample features speech pattern anomalies. Deepfake classification models triggered deepfake_confidence = 0.94.", relevance_score: 0.931, source_type: "evidence" }
          ];
        }

        setChatHistory(prev => [...prev, {
          role: 'assistant',
          content: answer,
          citations: citations,
          similarCases: ["CASE-2026-4412", "CASE-2025-9910"]
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
        similarCases: data.similar_cases || []
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
      size: 32
    });

    const entities = pipelineResult?.scam_result?.entities;
    if (!entities) {
      // Dummy visual placeholder nodes if no case results
      return { nodes, edges };
    }

    const items = [];
    if (entities.phone_numbers) entities.phone_numbers.forEach(p => items.push({ val: p, type: 'Phone' }));
    if (entities.upi_ids) entities.upi_ids.forEach(u => items.push({ val: u, type: 'UPI' }));
    if (entities.bank_accounts) entities.bank_accounts.forEach(b => items.push({ val: b, type: 'Bank' }));
    if (entities.urls) entities.urls.forEach(url => items.push({ val: url, type: 'URL' }));
    if (entities.names) entities.names.forEach(n => {
      if (n.includes('Suspect') || n.includes('DCP')) {
        items.push({ val: n, type: 'Suspect' });
      }
    });

    const total = items.length;
    items.forEach((item, index) => {
      // Distribute nodes radially around the central case node
      const angle = (2 * Math.PI * index) / total;
      const radius = 160;
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
        relation: 'MENTIONS'
      });
    });

    return { nodes, edges };
  };

  const { nodes: graphNodes, edges: graphEdges } = buildGraphNodesAndEdges();

  // Convert geo temporal trend dictionary to recharts array
  const getTemporalChartData = () => {
    const trend = pipelineResult?.geo_result?.temporal_trend || {};
    return Object.entries(trend).map(([hour, count]) => ({
      hour: `${hour}:00`,
      complaints: count
    })).sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-slate-950 border-r border-slate-805 flex flex-col justify-between z-20 shadow-2xl">
        <div>
          {/* Logo brand title */}
          <div className="p-5 flex items-center gap-3 border-b border-slate-800 bg-slate-950">
            <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
              <Shield className="w-7 h-7 text-emerald-400 animate-pulse" />
            </div>
            <div>
              <h1 className="font-bold text-md tracking-wider text-slate-100 font-mono">SENTINEL SHIELD</h1>
              <span className="text-[10px] text-emerald-400 font-bold tracking-widest uppercase">AI Safety Platform</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            {[
              { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
              { id: 'analyzer', label: 'File Analyzer & Run', icon: FileSearch },
              { id: 'graph', label: 'Fraud Graph Analyzer', icon: Network },
              { id: 'heatmap', label: 'Geospatial Hotspots', icon: MapPin },
              { id: 'copilot', label: 'Investigation Copilot', icon: MessageSquareCode },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === item.id 
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-700/30 font-semibold' 
                      : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4.5 h-4.5" />
                    {item.label}
                  </div>
                  {item.id === 'copilot' && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/20 text-emerald-300 font-bold rounded-md uppercase border border-emerald-500/10">RAG</span>
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
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-900 transition-colors"
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
        <header className="h-16 border-b border-slate-800 bg-slate-950/40 backdrop-blur-md flex items-center justify-between px-8 z-15 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-mono bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Session: {pipelineResult.case_id}
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
          
          {/* TAB 1: OVERVIEW DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* Main KPIs Row */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                
                {/* Risk score gauge card */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800/80 flex flex-col justify-between shadow-xl">
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Aggregated Risk</p>
                    <span className={`p-1.5 rounded-lg text-xs ${
                      pipelineResult.overall_risk_score >= 0.8 
                        ? 'bg-rose-500/10 text-rose-400' 
                        : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      <AlertTriangle className="w-4 h-4"/>
                    </span>
                  </div>
                  <div className="mt-4 flex items-baseline gap-2">
                    <span className={`text-4xl font-extrabold font-mono ${
                      pipelineResult.overall_risk_score >= 0.8 ? 'text-rose-500' : 'text-amber-500'
                    }`}>
                      {(pipelineResult.overall_risk_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs text-slate-500 font-semibold">Risk Index</span>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full bg-slate-900 rounded-full h-1.5 mt-3 border border-slate-800/50">
                    <div 
                      className={`h-full rounded-full ${pipelineResult.overall_risk_score >= 0.8 ? 'bg-rose-500' : 'bg-amber-500'}`} 
                      style={{ width: `${pipelineResult.overall_risk_score * 100}%` }}
                    />
                  </div>
                </div>

                {/* Risk Level Category */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800/80 flex flex-col justify-between shadow-xl">
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Risk Classification</p>
                    <span className="p-1.5 bg-emerald-500/10 text-emerald-400 rounded-lg"><Shield className="w-4 h-4"/></span>
                  </div>
                  <div className="mt-4">
                    <span className="text-2xl font-extrabold tracking-wide uppercase text-slate-200">
                      {pipelineResult.risk_level}
                    </span>
                    <p className="text-[10px] text-slate-500 mt-1.5 font-bold tracking-wider uppercase">
                      Category: {pipelineResult.scam_result?.scam_type || 'Unknown'}
                    </p>
                  </div>
                </div>

                {/* Extracted IPC/BNS Section count */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800/80 flex flex-col justify-between shadow-xl">
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Applicable Sections</p>
                    <span className="p-1.5 bg-sky-500/10 text-sky-400 rounded-lg"><FileText className="w-4 h-4"/></span>
                  </div>
                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold font-mono text-sky-400">
                      {pipelineResult.evidence_package?.ipc_sections?.length || 0}
                    </span>
                    <span className="text-xs text-slate-500 font-semibold">Charges Linked</span>
                  </div>
                </div>

                {/* Analyzed Evidence Pieces */}
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800/80 flex flex-col justify-between shadow-xl">
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Pipeline Engine</p>
                    <span className="p-1.5 bg-purple-500/10 text-purple-400 rounded-lg"><Activity className="w-4 h-4"/></span>
                  </div>
                  <div className="mt-4">
                    <span className="text-xs font-bold text-slate-300">Active Agents:</span>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {['Scam', 'Graph', 'Geo', pipelineResult.voice_result && 'Voice', pipelineResult.counterfeit_result && 'Currency'].filter(Boolean).map(agent => (
                        <span key={agent} className="text-[9px] bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded text-emerald-400 font-bold font-mono">
                          {agent}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

              </div>

              {/* Core Details Grid: Docket & FIR Draft */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Executive Summary Docket */}
                <div className="bg-slate-950 rounded-2xl border border-slate-800 shadow-xl p-6 lg:col-span-1 space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Info className="w-4.5 h-4.5 text-emerald-400" /> Executive Docket
                    </h3>
                    <button
                      onClick={() => handleCopyToClipboard(pipelineResult.evidence_package?.executive_summary || '', 'summary')}
                      className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
                    >
                      {copiedSummary ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      {copiedSummary ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                  
                  <div className="space-y-4 text-sm leading-relaxed text-slate-300">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase block">Victim Details</span>
                      <p className="font-semibold text-slate-200 mt-0.5">{complainantName || 'N/A'}</p>
                      <p className="text-xs text-slate-400">{complainantContact || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase block">Crime Location Coordinates</span>
                      <p className="font-mono text-slate-200 mt-0.5">{lat}, {lon}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase block">Aggregated Summary</span>
                      <p className="text-slate-400 mt-1 bg-slate-900/60 p-3.5 border border-slate-800/80 rounded-xl text-xs leading-relaxed font-sans">
                        {pipelineResult.evidence_package?.executive_summary || 'No pipeline execution has occurred yet.'}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-slate-800/80 pt-4 space-y-2">
                    <span className="text-[10px] text-slate-500 font-bold uppercase block">Recommended Police Actions</span>
                    <ul className="space-y-2 text-xs">
                      {(pipelineResult.evidence_package?.recommended_actions || []).map((action, idx) => (
                        <li key={idx} className="flex gap-2 text-slate-300 bg-slate-900/40 border border-slate-800/50 p-2.5 rounded-xl items-start">
                          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* FIR Draft Terminal View */}
                <div className="bg-slate-950 rounded-2xl border border-slate-800 shadow-xl lg:col-span-2 overflow-hidden flex flex-col justify-between">
                  {/* Title Bar */}
                  <div className="bg-slate-950 border-b border-slate-800 px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                        <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      </div>
                      <span className="text-xs font-mono text-slate-400 font-bold tracking-wide ml-2 uppercase">Official_FIR_Draft.txt</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleCopyToClipboard(pipelineResult.evidence_package?.fir_draft || '', 'fir')}
                        className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg transition-all"
                      >
                        {copiedFir ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        {copiedFir ? 'Copied Draft' : 'Copy Draft'}
                      </button>
                      <button
                        onClick={handlePrintReport}
                        className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg transition-all"
                      >
                        <Printer className="w-3.5 h-3.5" /> Print Docket
                      </button>
                    </div>
                  </div>

                  {/* Terminal Text Area */}
                  <div className="flex-1 bg-slate-950 p-6 font-mono text-xs overflow-y-auto leading-relaxed max-h-[460px] text-slate-300">
                    <div className="space-y-1">
                      {pipelineResult.evidence_package?.fir_draft ? (
                        pipelineResult.evidence_package.fir_draft.split('\n').map((line, idx) => (
                          <div key={idx} className="flex">
                            <span className="w-8 text-slate-600 select-none text-right pr-4 font-mono">{idx + 1}</span>
                            <span className="text-emerald-400/90 whitespace-pre-wrap">{line}</span>
                          </div>
                        ))
                      ) : (
                        <div className="text-slate-500 text-center py-10 font-sans">
                          No evidence package analyzed. Run the File Analyzer pipeline to generate the FIR draft here.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Charges chips footer */}
                  <div className="bg-slate-950/80 border-t border-slate-800 px-6 py-4 flex items-center justify-between flex-wrap gap-2.5">
                    <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Applicable IPC / BNS charges:</div>
                    <div className="flex flex-wrap gap-2">
                      {(pipelineResult.evidence_package?.ipc_sections || []).map((sec, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-900/60 text-slate-300 border border-slate-800 font-mono font-bold px-2 py-1 rounded-lg shadow-sm">
                          {sec}
                        </span>
                      ))}
                    </div>
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
                        onClick={() => {
                          setLat('22.8046');
                          setLon('86.2029');
                        }}
                        className="text-[10px] bg-slate-900 border border-slate-800 px-2 py-1 rounded hover:bg-slate-800 font-mono text-slate-400 font-bold"
                      >
                        Jamshedpur
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setLat('23.3441');
                          setLon('85.3096');
                        }}
                        className="text-[10px] bg-slate-900 border border-slate-800 px-2 py-1 rounded hover:bg-slate-800 font-mono text-slate-400 font-bold"
                      >
                        Ranchi
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
                          className="bg-slate-900 hover:bg-slate-800 border border-slate-805 text-slate-400 p-2 rounded-xl text-xs transition-colors"
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
                        className="w-full mt-1 bg-slate-900 border border-slate-805 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-sans"
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
                        className="w-full mt-1 bg-slate-900 border border-slate-805 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
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
                        className="w-full mt-1 bg-slate-900 border border-slate-805 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
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
                        className="w-full mt-1 bg-slate-900 border border-slate-805 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-mono"
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
                      className="w-full mt-1 bg-slate-900 border border-slate-805 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-600 font-sans leading-relaxed"
                      placeholder="Input the core details of the WhatsApp call, QR Scam details, or banking fraud details..."
                    />
                  </div>

                  {/* Drag Drop uploads */}
                  <div className="grid grid-cols-2 gap-4">
                    
                    {/* Audio upload */}
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

                    {/* Image upload */}
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
                  
                  {/* Status Tracker */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-4">Orchestrator Node Pipeline Progress</h4>
                    
                    <div className="space-y-3">
                      {[
                        { stage: 'uploading', label: 'Ingesting evidence payload...' },
                        { stage: 'scam_analysis', label: 'Executing Scam Detection Agent...' },
                        { stage: 'voice_analysis', label: 'Auditing speaker voice deepfake signature...' },
                        { stage: 'counterfeit_analysis', label: 'Verifying suspect currency authenticity...' },
                        { stage: 'graph_analysis', label: 'Ingesting entities into local fraud graph...' },
                        { stage: 'geo_analysis', label: 'Clustering complaint coordinates...' },
                        { stage: 'done', label: 'Evidence generation finished.' }
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
                                  : 'bg-slate-900 text-slate-600 border-slate-800'
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

                  {/* Granular Result Cards (If done) */}
                  {pipelineStage === 'done' && (
                    <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
                      
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
                      {pipelineResult.voice_result && (
                        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
                          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                            <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                              <Shield className="w-4 h-4 text-rose-500" /> Voice Deepfake Audit
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                              pipelineResult.voice_result.is_deepfake 
                                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
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
                      {pipelineResult.counterfeit_result && (
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
                            {Object.entries(pipelineResult.counterfeit_result.security_features).map(([feat, status]) => (
                              <div key={feat} className="bg-slate-900 border border-slate-800 p-2 rounded flex flex-col justify-between">
                                <span className="text-[8px] text-slate-500 font-bold uppercase tracking-wider">{feat.replace('_', ' ')}</span>
                                <span className={`text-[10px] font-bold font-mono ${
                                  status === 'pass' ? 'text-emerald-400' : status === 'fail' ? 'text-rose-400' : 'text-slate-500'
                                }`}>
                                  {status.toUpperCase()}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    </div>
                  )}

                </div>

              </div>

            </div>
          )}

          {/* TAB 3: FRAUD GRAPH ANALYZER */}
          {activeTab === 'graph' && (
            <div className="space-y-6">
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* SVG Visual Graph Panel */}
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl lg:col-span-2 flex flex-col justify-between min-h-[500px]">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Network className="w-4.5 h-4.5 text-emerald-400" /> Interactive Graph Workspace
                    </h3>
                    <span className="text-[10px] bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                      Nodes: {graphNodes.length} | Edges: {graphEdges.length}
                    </span>
                  </div>

                  {/* SVG Viewport */}
                  <div className="flex-1 bg-slate-950/60 rounded-xl relative overflow-hidden mt-4 border border-slate-900 flex items-center justify-center">
                    {graphNodes.length <= 1 ? (
                      <div className="text-xs text-slate-500 text-center font-sans">
                        No case network mapped. Ingest evidence in the File Analyzer to generate entity associations.
                      </div>
                    ) : (
                      <svg width="100%" height="400" viewBox="0 0 600 400" className="select-none">
                        
                        {/* Edges Paths */}
                        {graphEdges.map((edge, idx) => {
                          const fromNode = graphNodes.find(n => n.id === edge.from);
                          const toNode = graphNodes.find(n => n.id === edge.to);
                          if (!fromNode || !toNode) return null;
                          return (
                            <g key={idx}>
                              <line
                                x1={fromNode.x}
                                y1={fromNode.y}
                                x2={toNode.x}
                                y2={toNode.y}
                                stroke="#1e293b"
                                strokeWidth="2.5"
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
                          
                          return (
                            <g 
                              key={node.id}
                              onMouseEnter={() => setHoveredNode(node.id)}
                              onMouseLeave={() => setHoveredNode(null)}
                              onClick={() => setClickedNode(node)}
                              className="cursor-pointer transition-transform duration-150"
                            >
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
                                className="font-mono pointer-events-none"
                              >
                                {node.label.length > 15 ? `${node.label.slice(0, 12)}...` : node.label}
                              </text>
                            </g>
                          );
                        })}

                      </svg>
                    )}
                  </div>

                  <div className="flex gap-4 mt-2 text-[10px] text-slate-500 font-bold justify-center uppercase">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-900 border border-emerald-400" /> Case ID</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> Phones</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500" /> UPI IDs</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Bank Accounts</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-pink-500" /> Suspect Name</span>
                  </div>

                </div>

                {/* Node Details & Ring communities sidebar */}
                <div className="space-y-6">
                  
                  {/* Selected Node Details Card */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl min-h-[180px]">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-3">Entity Graph Inspector</h4>
                    
                    {clickedNode || hoveredNode ? (
                      (() => {
                        const targetNode = clickedNode || graphNodes.find(n => n.id === hoveredNode);
                        if (!targetNode) return null;
                        return (
                          <div className="space-y-3">
                            <div className="flex justify-between items-start">
                              <span className="text-[9px] bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded uppercase font-bold font-mono">
                                {targetNode.type}
                              </span>
                              <span className="text-xs font-semibold text-slate-400">PageRank: {targetNode.pr?.toFixed(3) || '0.000'}</span>
                            </div>
                            <p className="text-sm font-mono font-bold text-slate-200 break-all">{targetNode.label}</p>
                            {targetNode.type !== 'Case' && (
                              <div className="bg-slate-900 p-2.5 rounded border border-slate-800/80 text-[10px] text-slate-400 leading-relaxed font-sans">
                                Ingested from complaint case file evidence. Multi-agent scoring highlights this as a 
                                {targetNode.pr > 0.2 ? ' high-influence collection node' : ' standard connection entity'}.
                              </div>
                            )}
                          </div>
                        );
                      })()
                    ) : (
                      <div className="text-xs text-slate-500 text-center py-6 font-sans">
                        Hover or click any network node to inspect its central properties and PageRank connections.
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
                            <span className="font-bold text-rose-400">{ring.ring_id}</span>
                            <span className="text-[9px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-1.5 py-0.5 rounded font-bold uppercase">
                              {ring.risk_level}
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-500">Suspected cluster members:</p>
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
                        No communities detected.
                      </div>
                    )}
                  </div>

                </div>

              </div>

            </div>
          )}

          {/* TAB 4: CRIME HOTSPOTS HEATMAP LAYOUT */}
          {activeTab === 'heatmap' && (
            <div className="space-y-6 animate-fadeIn">
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Simulated folium map display / Radar */}
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl lg:col-span-2 flex flex-col justify-between min-h-[460px]">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                    <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Map className="w-4.5 h-4.5 text-emerald-400" /> Geospatial Safety Heatmap
                    </h3>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">Location: Jamshedpur East</span>
                  </div>

                  {/* Pulsing Visual Radar Simulation Map */}
                  <div className="flex-1 bg-slate-950/70 border border-slate-900 rounded-xl relative overflow-hidden mt-4 flex items-center justify-center">
                    
                    {/* Glowing concentric background grids */}
                    <div className="absolute w-[360px] h-[360px] border border-slate-800/20 rounded-full animate-pulse" />
                    <div className="absolute w-[240px] h-[240px] border border-slate-800/35 rounded-full" />
                    <div className="absolute w-[120px] h-[120px] border border-slate-800/40 rounded-full" />
                    
                    {/* Crosshairs */}
                    <div className="absolute w-full h-[1px] bg-slate-800/30" />
                    <div className="absolute h-full w-[1px] bg-slate-800/30" />

                    {/* Glowing hotspots pulsing */}
                    {(pipelineResult.geo_result?.hotspots || []).map((hs, idx) => {
                      const offsets = [
                        { x: 40, y: -20 },
                        { x: -50, y: 60 }
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
                          
                          <div className="bg-slate-950 border border-slate-800 rounded px-2 py-1 mt-1 text-[9px] font-mono text-slate-300 pointer-events-none">
                            <span className="font-bold text-slate-200">Cluster {idx + 1}: </span>
                            {hs.complaint_count} {hs.dominant_fraud_type.replace('_', ' ')} cases
                          </div>
                        </div>
                      );
                    })}

                    <div className="absolute bottom-4 left-4 text-[9px] font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-400">
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
                      {(pipelineResult.geo_result?.patrol_recommendations || []).map((rec, idx) => (
                        <div key={idx} className="bg-slate-900/60 border border-slate-800/80 p-3 rounded-xl text-[11px] leading-relaxed text-slate-300 flex items-start gap-2.5">
                          <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
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
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold border ${
                        msg.role === 'user' 
                          ? 'bg-emerald-500/25 border-emerald-500/30 text-emerald-400' 
                          : 'bg-slate-900 border-slate-850 text-slate-400'
                      }`}>
                        {msg.role === 'user' ? 'NJ' : 'AI'}
                      </div>
                      
                      {/* Message Content bubble */}
                      <div className={`rounded-2xl p-4 text-xs leading-relaxed ${
                        msg.role === 'user' 
                          ? 'bg-emerald-600 text-white rounded-tr-none' 
                          : 'bg-slate-900 border border-slate-800 rounded-tl-none text-slate-300'
                      }`}>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        
                        {/* Similar Cases block */}
                        {msg.similarCases && msg.similarCases.length > 0 && (
                          <div className="mt-3 border-t border-slate-800/80 pt-2 text-[10px] text-slate-500">
                            <span className="font-bold uppercase tracking-wider block">Correlated Case Dossiers:</span>
                            <div className="flex gap-1.5 mt-1">
                              {msg.similarCases.map((cId, cIdx) => (
                                <span key={cIdx} className="bg-slate-950 px-2 py-0.5 border border-slate-850 rounded text-slate-450 font-mono">
                                  {cId}
                                </span>
                              ))}
                            </div>
                          </div>
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
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Synthesizing retrieved facts...
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {/* Input box form */}
                <form onSubmit={handleChatSubmit} className="bg-slate-950 border-t border-slate-805 p-4 flex gap-3">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask regarding applicable BNS sections, suspect phone links, or deepfake metrics..."
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
              <div className="w-80 bg-slate-950 border border-slate-805 rounded-2xl p-5 shadow-xl flex flex-col">
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-1">
                  <FileText className="w-4 h-4 text-emerald-400" /> Fusion RAG Citations
                </h4>
                
                <div className="flex-1 overflow-y-auto mt-4 space-y-4">
                  {chatHistory[chatHistory.length - 1]?.citations && chatHistory[chatHistory.length - 1].citations.length > 0 ? (
                    chatHistory[chatHistory.length - 1].citations.map((cite, idx) => (
                      <div key={idx} className="bg-slate-900 border border-slate-850 rounded-xl p-3.5 space-y-2">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="font-mono text-emerald-400 font-bold">{cite.source_id}</span>
                          <span className="text-[9px] bg-slate-950 border border-slate-800 text-slate-500 px-1.5 py-0.5 rounded font-mono">
                            Score: {cite.relevance_score}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed italic font-sans">
                          "...{cite.chunk_text}..."
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 text-center py-10">
                      Query response citation audit chunks will display here automatically.
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