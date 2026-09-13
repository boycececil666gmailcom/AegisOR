# AegisOR

> Autonomous ambient clinical intelligence system and surgical safety guardrail enforcing The Universal Protocol and Closed-Loop Communication in sterile operating room environments using AssemblyAI.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![AegisOR](https://img.shields.io/badge/AegisOR-Safety%20Guardrail-007ACC?style=flat)
![AssemblyAI](https://img.shields.io/badge/AssemblyAI-Platform-blue?style=flat)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

AegisOR is an ambient clinical intelligence engine and surgical safety guardrail that listens to operating room communications, validates surgical safety checklists in real time, and produces structured, immutable operative records.

---

## 1. End-to-End Pipeline Overview

```mermaid
---
config:
  theme: neutral
---
flowchart LR
    A[Operating Room Audio Stream] --> B[AssemblyAI Speech Engine]
    B --> C[AegisOR Protocol Verifier]
    C --> D[Real-Time Safety HUD]
    D --> E[Immutable Operative Audit Ledger]
```

---

## 2. Core Purpose & Business Value

AegisOR transforms surgical room audio into an active patient safety barrier and automated clinical record, safeguarding healthcare institutions from preventable surgical errors while alleviating cognitive exhaustion for clinical staff.

- **Zero Never Events**: Prevents wrong-patient, wrong-site, and wrong-procedure surgeries by enforcing mandatory verbal verification across surgical disciplines prior to incision.
- **Automated Medicolegal Protection**: Produces an incontrovertible acoustic audit log verifying adherence to patient safety protocols, shielding hospitals from costly malpractice claims.
- **Uncompromised Surgical Focus**: Eliminates manual keyboard and computer interactions during procedures, allowing surgical teams to concentrate entirely on patient care.
- **Regulatory Accreditation Compliance**: Guarantees adherence to Joint Commission and World Health Organization surgical safety standards without introducing procedural delays.
- **Optimized Operating Room Turnover**: Accelerates postoperative documentation and phase transitions, improving procedural capacity and reducing hospital overhead.

---

## 3. Functional & Non-Functional Requirements

### Functional Requirements (FR)

- **FR-1 (Acoustic Ingestion & Diarization)**: Ingest multi-channel operating room audio streams, apply surgical acoustic vocabulary boosting, and perform multi-speaker diarization to distinguish the primary surgeon, anesthesiologist, and circulating nurse.
- **FR-2 (Pre-Operative Time-Out Verification)**: Automatically detect and validate mandatory Universal Protocol checklist items (patient identity, planned procedure, operative site/side, informed consent, allergy confirmation, and antibiotic prophylaxis status) before incision authorization.
- **FR-3 (Intra-Operative Closed-Loop Tracking)**: Capture critical verbal directives (medication administrations, blood loss estimations, sponge/needle counts) and match them against explicit verbal read-backs to enforce closed-loop communication closure.
- **FR-4 (Post-Operative Sign-Out & Reporting)**: Aggregate surgical milestones, instrument count verifications, specimen labels, and clinical summaries into a standardized, timestamped operative report ready for electronic medical record integration.

### Non-Functional Requirements (NFR)

- **NFR-1 (Performance & Latency)**: Audio chunk transcription p95 latency <= 500ms; closed-loop order-readback reconciliation latency p95 <= 250ms under continuous acoustic streaming.
- **NFR-2 (Reliability & Fail-Safe Operation)**: 99.99% operational uptime during active surgical sessions; zero audio frame loss via ring-buffered local fallback during temporary network disconnections.
- **NFR-3 (Security & HIPAA Compliance)**: Strict HIPAA-compliant data handling; all data in transit encrypted using TLS 1.3; all persisted surgical audit ledgers encrypted at rest using AES-256; zero local retention of unencrypted raw patient identifiable audio.
- **NFR-4 (Scalability & Isolation)**: Stateless processing core capable of isolating concurrent operating room sessions across multiple surgical suites with zero shared-memory leakage.

---

## 4. System Architecture & Technical Execution

The platform establishes an ambient intelligence loop over three sequential surgical phases: Pre-Operative Time-Out, Intra-Operative Closed-Loop Maintenance, and Post-Operative Sign-Out.

### Core Concept & Phased Execution Sequence

```mermaid
---
config:
  theme: neutral
---
sequenceDiagram
    autonumber
    actor Team as Surgical Team (Surgeon, Anesthesia, Nurse)
    participant Client as Scribe Client / Audio Streamer
    participant Core as Protocol Verification Engine
    participant AAI as AssemblyAI Cloud API
    participant Audit as Clinical Audit Record Store

    Note over Team, AAI: Phase 1: Pre-Op Universal Protocol Time-Out
    Team->>Client: Verbal Call-Out ("Commencing Time-Out. Patient PT-84021...")
    Client->>AAI: Stream In-Room Audio Chunks
    AAI-->>Core: Transcripts with Speaker Diarization & Entity Detection
    alt All Roles Verbally Confirmed
        rect rgb(235, 247, 238)
            Core->>Core: Validate Patient, Procedure, Site, and Allergy Checklist
            Core-->>Client: Time-Out Verified: Incision Authorized
        end
    else Incomplete Read-Back or Missing Role
        rect rgb(253, 237, 237)
            Core-->>Client: Safety Alert: Missing Anesthesia Oral Confirmation
        end
    end

    Note over Team, AAI: Phase 2: Intra-Op Closed-Loop Maintenance
    Team->>Client: Verbal Drug Directive ("Administer 5000 units Heparin")
    Client->>AAI: Stream Real-Time Audio Chunk
    AAI-->>Core: Detected Pharmaceutical Entity + Speaker ID
    Team->>Client: Verbal Read-Back ("Heparin 5000 units IV pushed")
    Core->>Core: Match Directive to Read-Back (Closed-Loop Closure)
    Core-->>Client: Append Verified Medication Timestamp to Live HUD

    Note over Team, Audit: Phase 3: Post-Op Sign-Out & Report Generation
    Team->>Client: Verbal Sign-Out ("Counts correct. Specimen labeled.")
    Client->>AAI: Request Operative Summarization & Key Milestones
    AAI-->>Core: Structured Clinical Briefing & Timeline Phases
    Core->>Audit: Persist Immutable Operative Record (JSON / Markdown)
```

### C1: System Context Diagram

```mermaid
---
config:
  layout: elk
  theme: neutral
---
flowchart TB

    subgraph ClinicalActors["Operating Room Team & Hospital Stakeholders"]
        Surgeon["Attending Surgeon<br/>[Person]<br/>Leads surgical procedure and announces procedural milestones"]
        Nurse["Circulating Nurse<br/>[Person]<br/>Initiates Time-Out checklist and confirms counts"]
        Anesthetist["Anesthesiologist<br/>[Person]<br/>Verifies patient airway, allergies, and drug administrations"]
        RiskOfficer["Hospital Risk & Compliance Officer<br/>[Person]<br/>Audits compliance logs and inspects surgical safety records"]
    end

    subgraph SystemBoundary["AegisOR Platform [Software System]"]
        ScribeSystem["AegisOR Platform<br/>[Software System]<br/>Ambient speech recognition, surgical safety guardrails, and automated operative documentation"]
    end

    subgraph ExternalSystems["External Dependencies"]
        AssemblyAI["AssemblyAI Cloud Platform<br/>[External SaaS API]<br/>Provides speech-to-text, speaker diarization, and clinical entity detection"]
        HospitalEHR["Hospital EHR / EMR System<br/>[External System: Epic / Cerner]<br/>Receives finalized operative notes via HL7 / FHIR gateways"]
        AuditStorage["Clinical Compliance Data Lake<br/>[External System: Secure S3 / Snowflake]<br/>Stores permanent cryptographic audit logs for liability defense"]
    end

    Surgeon -->|"Speaks procedural calls and surgical orders<br/>[Ambient Audio]"| ScribeSystem
    Nurse -->|"Reads checklist items and confirms equipment counts<br/>[Ambient Audio]"| ScribeSystem
    Anesthetist -->|"Confirms patient vitals and drug administrations<br/>[Ambient Audio]"| ScribeSystem
    RiskOfficer -->|"Reviews compliance ledgers and safety reports<br/>[HTTPS / Web UI]"| ScribeSystem

    ScribeSystem -->|"Streams encrypted audio for acoustic analysis<br/>[WSS / TLS 1.3]"| AssemblyAI
    ScribeSystem -->|"Transmits structured operative summary<br/>[HTTPS / FHIR JSON]"| HospitalEHR
    ScribeSystem -->|"Archives immutable surgical audit events<br/>[HTTPS / S3 API]"| AuditStorage
```

### C2: Container Diagram

```mermaid
---
config:
  layout: elk
  theme: neutral
---
flowchart TB

    subgraph OutsideWorld["Operating Room Client Environment"]
        AudioInput["Ceiling / Lapel Microphone Array<br/>[Hardware Client]<br/>Captures sterile multi-directional acoustic stream"]
        ORDisplay["OR Surgical HUD Display<br/>[Web Browser / Tablet]<br/>Presents real-time checklist status and closed-loop alerts"]
    end

    subgraph HostExposed["Exposed Host Boundary"]
        UIGateway["aegisor-ui-gateway<br/>[Container: FastAPI + Gradio / Uvicorn]<br/>Hosts interactive surgical HUD at /aegisor<br/>Port 7860"]
    end

    subgraph IsolatedNetwork["Isolated Application Network (Private Subnet)"]

        subgraph ScribeEngineCtr["scribe-core-engine (Python 3.11+, Port 8000)"]
            direction TB
            StreamIngest["POST /api/v1/audio/stream<br/>Audio Frame Ingestion"]
            ProtocolAPI["POST /api/v1/protocol/validate<br/>Time-Out & Closed-Loop Engine"]
            ReportAPI["GET /api/v1/reports/:session_id<br/>Operative Report Formatter"]
        end

        subgraph SessionCacheCtr["session-cache (Redis 7, Port 6379)"]
            ActiveChecklist["key: session:{id}:checklist<br/>TTL: 12h"]
            PendingOrders["key: session:{id}:pending_orders<br/>type: list"]
        end

        subgraph AuditDBCtr["audit-database (PostgreSQL 16, Port 5432)"]
            TableSessions[("table: surgical_sessions")]
            TableTimeOut[("table: timeout_verifications")]
            TableClosedLoop[("table: closed_loop_events")]
            TableReports[("table: operative_reports")]
        end

    end

    subgraph CloudVendor["AssemblyAI SaaS Infrastructure"]
        AssemblyEndpoint["api.assemblyai.com<br/>[External API Endpoint]<br/>High-accuracy transcription & audio intelligence"]
    end

    AudioInput -->|"PCM16 24kHz audio stream<br/>[WebSocket :7860]"| UIGateway
    ORDisplay -->|"Real-time visual HUD updates<br/>[HTTP / WebSocket :7860]"| UIGateway

    UIGateway -->|"Dispatches audio and state commands<br/>[HTTP :8000]"| ScribeEngineCtr
    StreamIngest -->|"Sends chunked audio for processing<br/>[HTTPS / WSS TLS 1.3]"| AssemblyEndpoint
    ProtocolAPI -->|"Reads/writes active session checklist<br/>[RESP :6379]"| SessionCacheCtr
    ProtocolAPI -->|"Persists verified safety milestones<br/>[SQL :5432]"| AuditDBCtr
    ReportAPI -->|"Compiles historical session audit data<br/>[SQL :5432]"| AuditDBCtr
```

### C3: Component Diagram

```mermaid
---
config:
  layout: elk
  theme: neutral
---
flowchart TB

    subgraph ExternalContainers["External Containers & Storage Layer"]
        UIGW["surgical-ui-gateway Container<br/>[Gradio Front-End]"]
        CacheStore[("session-cache Container<br/>[Redis 7 Cache]")]
        DBStore[("audit-database Container<br/>[PostgreSQL 16 DB]")]
        AAICloud["api.assemblyai.com<br/>[AssemblyAI Cloud API]"]
    end

    subgraph ScribeCoreContainer["scribe-core-engine Container [Container: Python + FastAPI]"]

        subgraph Controllers["Controller / Ingestion Layer"]
        SessionRouter["Session Controller<br/>[Component: FastAPI Router]<br/>Handles session initialization and operative closure"]
        AudioIngestor["Audio Frame Ingestor<br/>[Component: Async Audio Streamer]<br/>Buffers and dispatches PCM audio chunks"]
        end

        subgraph DomainServices["Clinical Domain Logic Layer"]
            ProtocolEngine["Universal Protocol Engine<br/>[Component: Python Domain Service]<br/>Enforces pre-incision checklist validation rules"]
            ClosedLoopMatcher["Closed-Loop Verifier<br/>[Component: Python Domain Service]<br/>Matches verbal medication orders to recipient read-backs"]
            LexiconManager["Medical Lexicon Manager<br/>[Component: Python Domain Service]<br/>Compiles surgical vocabulary boost and phonetic aliases"]
            ReportCompiler["Operative Report Formatter<br/>[Component: Python Domain Service]<br/>Assembles chronological narrative, chapters, and audit logs"]
        end

        subgraph InfrastructureLayer["Data Access & Service Clients"]
            AAIClient["AssemblyAI Service Client<br/>[Component: SDK Integration Wrapper]<br/>Executes transcription, diarization, and summarization"]
            CacheClient["Session Cache Client<br/>[Component: Redis Client Wrapper]<br/>Maintains active checklist state and pending directives"]
            AuditRepository["Audit Data Repository<br/>[Component: SQLAlchemy Async Session]<br/>Handles transactional persistence to PostgreSQL"]
        end

    end

    UIGW -->|"Submits audio stream"| AudioIngestor
    UIGW -->|"Dispatches session actions"| SessionRouter

    AudioIngestor -->|"Supplies boosted vocabulary"| LexiconManager
    AudioIngestor -->|"Dispatches audio to speech engine"| AAIClient
    AAIClient -->|"Streaming ASR & Diarization"| AAICloud

    AAIClient -->|"Emits transcribed utterances"| ProtocolEngine
    AAIClient -->|"Emits recognized entities & speakers"| ClosedLoopMatcher

    ProtocolEngine -->|"Validates checklist state"| CacheClient
    ProtocolEngine -->|"Logs verified milestone"| AuditRepository

    ClosedLoopMatcher -->|"Queries pending drug directives"| CacheClient
    ClosedLoopMatcher -->|"Persists confirmed order-readback pair"| AuditRepository

    SessionRouter -->|"Triggers post-op summary compilation"| ReportCompiler
    ReportCompiler -->|"Fetches full transcript and intelligence"| AAIClient
    ReportCompiler -->|"Persists signed operative note"| AuditRepository

    CacheClient -->|"RESP :6379"| CacheStore
    AuditRepository -->|"SQL :5432"| DBStore
```

> [!NOTE]
> **C4: Code Diagram (Intentionally Omitted)**: Level 4 (Code/Class) diagrams are intentionally omitted from README documentation to prevent high maintenance overhead and rapid obsolescence. Detailed code structures are documented via inline docstrings, type annotations, and module unit tests.

---

## 5. Repository Structure

```text
AegisOR/
├── src/
│   ├── __init__.py           # Source package exports
│   ├── app.py                # FastAPI server & Gradio mounting
│   ├── assembly_service.py   # AssemblyAI client & acoustic lexicon priming
│   ├── engine.py             # Protocol state machine & closed-loop matcher
│   ├── models.py             # Domain models, checklists, and report schemas
│   ├── samples.py            # Dedicated clinical scenario texts & mock data
│   └── ui/                   # Modular presentation layer
│       ├── __init__.py       # Exposes build_ui
│       ├── handlers.py       # TimeOut, IntraOp, and PostOp event handlers
│       └── layout.py         # Gradio tabbed blocks interface layout
├── tests/
│   ├── __init__.py
│   ├── integration/          # Integration workflow tests
│   │   ├── __init__.py
│   │   └── it_workflow.py
│   └── unit/                 # Isolated domain logic unit tests
│       ├── __init__.py
│       ├── ut_assembly_service.py
│       ├── ut_engine.py
│       └── ut_models.py
├── .env                      # Local AssemblyAI API credentials
├── .env.example              # Environment configuration template
├── .gitignore                # Git exclusion rules
├── README.md                 # System architecture and operational manual
├── app.py                    # Root entrypoint launcher delegating to src.app
├── requirements.txt          # Python dependencies (assemblyai, gradio, python-dotenv)
├── run.bat                   # Windows Explorer one-click execution script
└── run.sh                    # Bash execution script with ANSI logging
```

---

## 6. Getting Started

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or standard `pip`
- Valid AssemblyAI API key

### Installation & Configuration

1. Clone or navigate to the workspace directory:
   ```bash
   cd c:\Users\boyce\OneDrive\Desktop\ReAct_Demo
   ```

2. Configure environment credentials in `.env`:
   ```env
   assembly_ai_api=your_assemblyai_api_key_here
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Run test suite:
   ```bash
   uv run python -m unittest discover -s tests -p "*_*.py"
   ```

5. Launch the application:
   ```bash
   ./run.sh
   ```
   *On Windows, you can alternatively execute `run.bat` or run:*
   ```bash
   uv run gradio app.py
   ```

6. Access the AegisOR clinical HUD at `http://127.0.0.1:7860/aegisor` (or root `http://127.0.0.1:7860/` which redirects to `/aegisor`).

