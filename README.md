# NetSage AI — Frontend

**AI-Assisted Cisco Network Troubleshooting & Diagnosis Platform**

NetSage AI is an enterprise network diagnostics operations center frontend built with React, Vite, Tailwind CSS, Recharts, and Lucide Icons.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create a `.env` file in the `frontend` root:
```env
VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The frontend will run at `http://localhost:5173`.

---

## 🏛️ Project Architecture

```
frontend/
├── src/
│   ├── components/       # Reusable UI widgets & Badges
│   │   ├── Sidebar.jsx
│   │   ├── Topbar.jsx
│   │   ├── StatCard.jsx
│   │   ├── RiskBadge.jsx
│   │   ├── SeverityBadge.jsx
│   │   ├── CaseCard.jsx
│   │   ├── FindingCard.jsx
│   │   ├── EvidencePanel.jsx
│   │   ├── DiagnosisCard.jsx
│   │   ├── ReviewPanel.jsx
│   │   ├── EmptyState.jsx
│   │   ├── LoadingState.jsx
│   │   └── ErrorState.jsx
│   ├── pages/            # View controllers
│   │   ├── Dashboard.jsx
│   │   ├── Cases.jsx
│   │   ├── NewCase.jsx
│   │   ├── Diagnosis.jsx
│   │   └── HumanReview.jsx
│   ├── services/
│   │   ├── api.js        # Centralized REST API client
│   │   └── mockData.js   # Isolated fallback mock data
│   ├── hooks/
│   │   └── useApi.js     # React async fetch hooks
│   ├── utils/
│   │   └── formatters.js # Formatting helpers
│   ├── App.jsx           # Layout & Routing configuration
│   ├── main.jsx          # Entrypoint
│   └── index.css         # Theme styles
├── package.json
└── vite.config.js
```

---

## 🔒 Security & AI Safety Principle

NetSage AI is strictly an **evidence-based advisory assistant**. It **never** executes automated configuration changes to production network equipment. All AI diagnoses are presented with deterministic rule verification and require human review.
