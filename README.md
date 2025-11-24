# PsycheScore: Privacy-Preserving Credit Assessment on Midnight Network

A decentralized application (dApp) that calculates credit scores by combining psychological profiling with on-chain data using zero-knowledge proofs. The application provides private, verifiable credit assessment for underbanked populations by leveraging Midnight's privacy features and Compact smart contracts.

## Project Structure

```
psychescore/                       # Core services and backend
├── backend/                       # Flask API with Midnight Network integration
│   ├── app.py                     # Main Flask application
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend container configuration
│   ├── test_api.py                # API tests
│   ├── services/                  # Business logic services
│   │   ├── ml_service.py          # ML model integration
│   │   ├── blockchain_service.py  # Midnight Network interactions
│   │   ├── zk_proof_service.py    # ZK proof generation
│   │   └── mn_service.py          # Midnight Network service wrapper
│   ├── models/                    # ML model files and scoring logic
│   │   ├── ml_score.py            # ML scoring logic
│   │   ├── model.joblib           # Trained ML model
│   │   ├── scaler.joblib          # Feature scaler
│   │   ├── feature_columns.json   # Model features
│   │   ├── big_five_questions.py  # Survey questions (50 Big Five)
│   │   ├── prototype.py           # Model prototype
│   │   ├── oracle.skey            # Oracle signing key
│   │   └── score.json             # Generated scores
│   ├── routes/                    # API route handlers (future)
│   ├── utils/                     # Utility functions (future)
│   └── config/                    # Configuration files (future)
├── docs/                          # Documentation
│   ├── api_documentation.md       # API documentation
│   └── MIDNIGHT_NETWORK_MIGRATION_PLAN.md  # Migration plan
├── tests/                         # Test files
│   └── test_integration.py        # Integration tests
└── README.md                      # Project documentation

psychescore-mn/                    # Midnight Network frontend DApp
├── src/
│   ├── App.tsx                    # Main React component
│   ├── main.tsx                   # Application entry point
│   ├── index.css                  # Global styles
│   ├── components/                # React components
│   │   ├── PsycheScoreDApp.tsx    # Main DApp component
│   │   ├── SurveyComponent.tsx    # Survey interface
│   │   └── WalletCard.tsx         # Wallet connection
│   ├── utils/                     # Utility functions
│   │   └── generateProof.js       # Proof generation
│   ├── types/                     # TypeScript definitions
│   │   └── types.ts               # Type definitions
│   ├── hooks/                     # React hooks (future)
│   └── contexts/                  # React contexts (future)
├── contracts/                     # Smart contracts
│   └── psychescore.compact        # Midnight Network Compact contract
├── package.json                   # Frontend dependencies
├── tsconfig.json                  # TypeScript configuration
├── tsconfig.node.json             # Node.js TypeScript config
├── vite.config.js                 # Vite build configuration
└── index.html                     # HTML entry point

scripts/                           # Development and deployment scripts
├── deploy.js                      # Contract deployment
├── start_midnight_dev.bat         # Windows dev startup
├── start_midnight_dev.sh          # Linux/Mac dev startup
├── start_midnight_proof_server.bat # Windows proof server
├── start_midnight_proof_server.sh  # Linux/Mac proof server
└── verify_compact_installation.sh # Installation verification

docker-compose.midnight.yml        # Docker Compose for Midnight Network
Dockerfile.midnight                # Midnight Network Docker configuration
README.md                          # This file
```

## Key Features

- **Psychological Profiling**: 50-question Big Five personality assessment (OCEAN traits)
- **ML-Powered Scoring**: Machine learning model generates psychological scores (0-100)
- **Complete Privacy**: Zero-knowledge proofs via Midnight Network anonymize all sensitive data
- **Midnight-Native**: Built with Compact smart contracts and DApp Connector API
- **Hybrid Architecture**: Combines ML scoring with ZK privacy and on-chain verification
- **Modern Frontend**: React-based DApp with TypeScript support
- **RESTful API**: Flask backend with comprehensive API endpoints

## 🚀 Quick Start

### Prerequisites
- **Docker and Docker Compose** (recommended for full setup)
- **Midnight Lace wallet** browser extension
- **Node.js 18+** and **Python 3.8+** (for manual setup)

### Dockerized Setup (Recommended)

1. **Start Midnight Proof Server**
   ```bash
   # Windows
   scripts\start_midnight_proof_server.bat
   
   # Linux/Mac
   chmod +x scripts/start_midnight_proof_server.sh
   ./scripts/start_midnight_proof_server.sh
   ```

2. **Start Development Environment**
   ```bash
   docker-compose -f docker-compose.midnight.yml up --build
   ```

3. **Access Services**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **Proof Server**: http://localhost:6300

### Manual Setup

#### Backend Setup
```bash
cd psychescore/backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd psychescore-mn
npm install
npm run dev
```

## 🏗️ Architecture

The project follows a hybrid architecture pattern with:

### Phase 1: Data Collection & ML Processing
- **Frontend**: React/TypeScript with Midnight wallet integration
- **ML Model**: Psychological scoring using Big Five personality traits
- **Privacy**: All data processed locally with ZK proofs

### Phase 2: Privacy Computation
- **Compact Contracts**: Score computation with selective disclosure
- **Proof Server**: Local ZK proof generation for privacy
- **JavaScript Implementation**: Generated from Compact contracts for testing

### Phase 3: On-chain Verification
- **Midnight Network**: Private transaction submission with proofs
- **Selective Disclosure**: Users control what information is revealed
- **Verifiable Storage**: On-chain score storage with privacy guarantees

## 📖 Usage Flow

1. **User connects Midnight Lace wallet** via DApp Connector API
2. **Complete 50-question Big Five survey** via the React frontend
3. **ML model processes responses** and generates psychological score (0-100)
4. **Midnight Compact contract** computes ZK proof without revealing survey data
5. **Proof is generated locally** using Midnight proof server
6. **Transaction submitted** to Midnight Network with the proof
7. **User receives verifiable, private psychological credit score**

## 🛠️ Technology Stack

- **Blockchain**: Midnight Network (testnet/mainnet)
- **Smart Contracts**: Compact language with JavaScript implementation
- **ZK Proofs**: Midnight proof server for local proof generation
- **Frontend**: React.js with TypeScript and Vite
- **Wallet Integration**: Midnight Lace via DApp Connector API
- **ML Model**: scikit-learn (Python) for psychological scoring
- **Backend**: Flask API with MN service integration
- **Containerization**: Docker with docker-compose for all services

## 🔧 Development

### Contract Development
```bash
cd psychescore-mn
# Compile Compact contract
compact compile contracts/psychescore.compact contracts/managed/psychescore

# Test JavaScript implementation
node src/generateProof.js '{"test": "data"}'
```

### Testing
```bash
# Backend tests
cd psychescore/backend
python test_api.py

# Integration tests
cd psychescore/tests
python test_integration.py
```

## 🚨 Troubleshooting

### Common Issues

**Proof Server Connection Issues**
- Ensure Midnight proof server is running on port 6300
- Check firewall settings for proof server access
- Verify Midnight Network dependencies are installed

**Wallet Connection Problems**
- Ensure Midnight Lace wallet extension is installed and unlocked
- Check that the dApp is running on localhost:3000
- Verify network connection to Midnight testnet

**Backend API Connection**
- Confirm Flask backend is running on port 8000
- Check CORS settings for frontend-backend communication
- Verify all required Python dependencies are installed

**Docker Compose Issues**
- Ensure Docker and Docker Compose are properly installed
- Check available disk space for container images
- Verify no port conflicts (3000, 8000, 6300)

### Debug Mode

To enable debug logging for development:
```bash
# Backend debug mode
cd psychescore/backend
DEBUG=1 python app.py

# Frontend debug mode
cd psychescore-mn
npm run dev -- --debug
```

## 🎯 Performance Targets

- **Proof Generation**: <30 seconds for 50 questions
- **Wallet Connection**: <5 seconds using DApp Connector
- **Transaction Confirmation**: <20 seconds on Midnight testnet
- **End-to-End Time**: <1 minute for complete flow

## 📚 Documentation

- **[psychescore/README.md](psychescore/README.md)** - Detailed project documentation
- **[psychescore/docs/api_documentation.md](psychescore/docs/api_documentation.md)** - API reference
- **[psychescore/docs/MIDNIGHT_NETWORK_MIGRATION_PLAN.md](psychescore/docs/MIDNIGHT_NETWORK_MIGRATION_PLAN.md)** - Migration plan

## 🤝 Contributing

We welcome contributions! The project is fully migrated to Midnight Network with:
- Official Compact smart contracts
- Midnight wallet integration
- Containerized deployment
- Comprehensive documentation

## 🔗 Links

- [Midnight Network Documentation](https://docs.midnight.network)
- [Compact Language Reference](https://docs.midnight.network/compact)
- [DApp Connector API](https://docs.midnight.network/dapp-connector)

## 📄 License

MIT License – see `LICENSE` for details.