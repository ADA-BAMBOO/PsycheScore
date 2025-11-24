# Midnight Network App Migration Plan for PsycheScore

## Overview

This document outlines the step-by-step plan to migrate the PsycheScore project from its current custom implementation to the official Midnight Network app structure using `create-mn-app` and Compact smart contracts.

## Current Project Analysis

### ✅ Current Setup
- **Frontend**: React + Vite (Node.js compatible)
- **Backend**: Flask Python API
- **ZK Circuit**: Custom `score_circuit.compact` 
- **Proof Service**: Python-based with mock implementation
- **Proof Server**: Not yet configured (requires Midnight proof server)
- **Smart Contracts**: Aiken-based Cardano contracts
- **ML Model**: Python-based psychological scoring

### 📋 Migration Requirements
- Migrate from custom proof service to official MN app structure
- Set up Midnight proof server for ZK proof generation
- Update ZK circuit to use Compact Standard Library
- Integrate with Midnight testnet deployment
- Maintain existing ML model and user interface

## Phase 1: Environment Setup & MN App Creation

### Step 1: Set up Midnight Network Development Environment

```bash
# Install Node.js 20+ if not available
nvm install 20
nvm use 20

# Create new MN app structure
npx create-mn-app psychescore-mn
cd psychescore-mn
npm run setup
```

**Template Selection**: Use "Hello World" template as base and customize for psychological scoring.

### Step 2: Project Structure Analysis

**Current Structure:**
```
psychescore/
├── frontend/          # React app
├── backend/           # Flask API
├── midnight-contracts/ # Custom circuits
└── smart-contracts/   # Aiken contracts
```

**New MN App Structure:**
```
psychescore-mn/
├── contracts/         # Compact contracts
├── src/              # TypeScript source
├── managed/          # Compiled artifacts
└── package.json      # MN app dependencies
```

## Phase 2: Contract Migration

### Step 3: Migrate Existing Circuit to Official Compact Format

**Current Circuit**: [`score_circuit.compact`](../midnight-contracts/score_circuit.compact)

**New Compact Contract**: `contracts/psychescore.compact`

```compact
// contracts/psychescore.compact
pragma language_version >= 0.16;

import CompactStandardLibrary;

// Ledger declarations for on-chain storage
export ledger user_scores: Map<Address, Opaque<"uint32">>;
export ledger score_commitments: Map<Address, Opaque<"bytes32">>;
export ledger ml_model_hash: Opaque<"bytes32">;
export ledger survey_responses: Map<Address, Opaque<"bytes">>;

// Circuits for score computation and storage
export circuit computeAndStoreScore(
    encrypted_responses: [Field; 50],
    koios_features: [Field; 4],
    ml_model_weights: [Field; 54],
    ml_model_bias: Field,
    wallet_address: Address,
    response_commitment: Opaque<"bytes32">
): [] {
    // ZK computation logic from existing circuit
    var computed_score: Field = ml_model_bias;
    
    // Process survey responses (questions 1-50)
    for i in 0..50 {
        computed_score = computed_score + (encrypted_responses[i] * ml_model_weights[i]);
    }
    
    // Process KOIOS features (features 51-54)
    for i in 0..4 {
        computed_score = computed_score + (koios_features[i] * ml_model_weights[50 + i]);
    }
    
    // Ensure score is within valid range (0-100)
    assert(computed_score >= 0);
    assert(computed_score <= 100);
    
    // Verify response commitment
    var calculated_commitment: Field = 0;
    for i in 0..50 {
        calculated_commitment = calculated_commitment + encrypted_responses[i];
    }
    assert(calculated_commitment == response_commitment);
    
    // Store score with selective disclosure
    user_scores[wallet_address] = disclose(Opaque<"uint32">(computed_score));
    score_commitments[wallet_address] = response_commitment;
}

// Circuit to verify score without revealing computation
export circuit verifyScore(
    wallet_address: Address,
    expected_score: Opaque<"uint32">
): bool {
    let stored_score = user_scores[wallet_address];
    return disclose(stored_score == expected_score);
}
```

### Step 4: Additional Contract Features

```compact
// Optional: Circuit for updating ML model
export circuit updateMLModel(
    new_model_hash: Opaque<"bytes32">,
    admin_signature: Opaque<"bytes64">
): [] {
    // Verify admin signature
    // Update model hash
    ml_model_hash = new_model_hash;
}

// Optional: Circuit for batch processing
export circuit batchComputeScores(
    batch_responses: [Address, [Field; 50]][],
    batch_features: [Address, [Field; 4]][]
): [] {
    // Process multiple users in batch
    for i in 0..batch_responses.length {
        // Individual score computation
        // Batch storage
    }
}
```

## Phase 3: Compilation & Integration

### Step 5: Compile Contracts & Generate JavaScript Implementation

```bash
# Compile the main contract
compact compile contracts/psychescore.compact contracts/managed/psychescore

# Expected output structure:
# contracts/
# └── managed
#     └── psychescore
#         ├── compiler/     # Intermediate files
#         ├── contract/     # Compiled artifacts
#         ├── keys/         # Cryptographic keys
#         └── zkir/         # ZK intermediate representation
#         └── index.cjs     # Generated JavaScript implementation
#         └── index.cjs.map # Source maps for debugging
#         └── index.d.cts   # TypeScript declarations
```

#### Understanding the JavaScript Implementation

When you compile a Compact contract, the compiler generates more than just zero-knowledge circuits — it also emits a matching JavaScript implementation (`index.cjs`) that lets you execute and test your Compact contract logic directly in JavaScript.

**Key Generated Files:**
- `index.cjs` - CommonJS module for Node.js testing
- `index.cjs.map` - Source maps for debugging back to Compact source
- `index.d.cts` - TypeScript declarations for type safety

**Implementation Structure:**
1. **Runtime Safety Checks** - Verifies Compact runtime version compatibility
2. **Type Definitions** - JavaScript representations of Compact types (integers, booleans, enums, bytes)
3. **Composite Types** - Classes for complex types (Option, Maybe, records)
4. **Contract Class** - Wrapper for contract entry points with circuit execution
5. **ContractState Management** - Encapsulates on-chain state with StateValue components
6. **QueryContext Support** - Provides transaction processing context
7. **Exports** - Type-safe exports for JavaScript/TypeScript consumption

**Using the Implementation in Tests:**
```javascript
const { Contract, State } = require('./contracts/managed/psychescore/index.cjs');

// Instantiate contract with witness object
const contract = new Contract({
  localSecretKey: () => Buffer.from('aabbccddeeff00112233445566778899', 'hex')
});

// Test contract functions
const context = {
  originalState: { status: State.VACANT },
  transactionContext: { timestamp: Date.now() }
};

const { result, proofData } = contract.circuits.computeAndStoreScore(context, surveyData);
```

#### ContractState and StateValue Implementation

**ContractState Management:**
```javascript
// Initialize contract state with maps for user scores and commitments
const contractState = new ContractState();
const userScoresMap = StateValue.newMap(new StateMap());
const scoreCommitmentsMap = StateValue.newMap(new StateMap());
const mlModelHash = StateValue.newCell(/* AlignedValue for hash */);

// Set up the main state data structure
const mainState = StateValue.newMap(new StateMap());
// ... configure mainState with nested maps

contractState.data = mainState;

// Set contract operations
contractState.setOperation('computeAndStoreScore', computeAndStoreScoreOperation);
contractState.setOperation('verifyScore', verifyScoreOperation);
```

**StateValue Types for PsycheScore:**
- **Maps**: For `user_scores` and `score_commitments` (Address → Opaque values)
- **Cells**: For `ml_model_hash` (single hash value)
- **Arrays**: For batch processing operations
- **Bounded Merkle Trees**: For efficient commitment storage

**QueryContext Usage:**
```javascript
// Create query context for on-chain operations
const queryContext = new QueryContext(contractState.data, contractAddress);

// Run queries against contract state
const queryResults = queryContext.query(
  [/* operations to query user scores */],
  costModel
);

// Process transaction transcripts
const [guaranteedTranscript, fallibleTranscript] = queryContext.intoTranscript(
  program,
  costModel
);
```

### Step 6: Set up Midnight Proof Server

**Proof Server Setup:**

1. **Install Docker and Verify Access:**
```bash
# Search for Midnight proof server image
docker search midnightnetwork

# Pull the latest proof server image
docker pull midnightnetwork/proof-server:latest

# Verify download success
docker images | grep proof-server
```

2. **Start Proof Server:**
```bash
# Run proof server on port 6300
docker run -p 6300:6300 midnightnetwork/proof-server -- 'midnight-proof-server --network testnet'
```

3. **Optional: Set up as Systemd Service (Linux):**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/midnight-proof-server.service

# Add service configuration
[Unit]
Description=Midnight Network Proof Server
After=docker.service
Requires=docker.service

[Service]
ExecStart=/usr/bin/docker run -p 6300:6300 midnightnetwork/proof-server -- 'midnight-proof-server --network testnet'
Restart=always
RestartSec=5

[Install]
WantedBy=default.target

# Reload and start service
sudo systemctl daemon-reload
sudo systemctl start midnight-proof-server
sudo systemctl enable midnight-proof-server
```

**Privacy Considerations:**
- Proof server runs locally and doesn't open external network connections
- Only listens on port 6300 for requests from Chrome extension
- Generates proofs locally to protect private data
- Configured for Midnight Testnet validation

### Step 7: Update Backend Integration with JavaScript Implementation

**Current**: Python Flask API with custom proof service
**New**: Flask API calling MN app TypeScript services with Compact JavaScript implementation and proof server integration

**Backend Integration Strategy:**

1. **Create MN Service Wrapper** (`backend/services/mn_service.py`):
```python
import subprocess
import json
import os

class MNService:
    def __init__(self):
        self.mn_app_path = os.path.join('..', 'psychescore-mn')
    
    def generate_proof(self, survey_data, ml_data):
        """Call MN app TypeScript service to generate proof using Compact JavaScript implementation"""
        # Prepare input data for JavaScript implementation
        input_data = {
            "survey_responses": survey_data,
            "ml_weights": ml_data['weights'],
            "koios_features": ml_data['koios_data'],
            "wallet_address": ml_data['address'],
            "proof_server_url": "http://localhost:6300"  # Local proof server
        }
        
        # Call MN app service that uses the generated JavaScript implementation
        result = subprocess.run([
            'node', 'src/generateProof.js',
            json.dumps(input_data)
        ], cwd=self.mn_app_path, capture_output=True, text=True)
        
        return json.loads(result.stdout)
    
    def test_circuit_locally(self, test_data):
        """Test circuit logic locally using generated JavaScript implementation"""
        # Use the generated index.cjs for local testing without proof server
        test_script = f"""
        const {{ Contract, State }} = require('./contracts/managed/psychescore/index.cjs');
        const contract = new Contract({{
            localSecretKey: () => Buffer.from('test-key', 'hex')
        }});
        
        const result = contract.circuits.computeAndStoreScore(
            {{ originalState: {{ status: State.VACANT }}, transactionContext: {{}} }},
            {json.dumps(test_data)}
        );
        
        console.log(JSON.stringify(result));
        """
        
        # Execute JavaScript test
        result = subprocess.run(['node', '-e', test_script],
                              cwd=self.mn_app_path,
                              capture_output=True,
                              text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception(f"Local circuit test failed: {result.stderr}")
```

2. **Update Existing Services**:
- Keep [`ml_service.py`](../backend/services/ml_service.py) unchanged
- Update [`zk_proof_service.py`](../backend/services/zk_proof_service.py) to use MN service with Compact JavaScript implementation
- Maintain [`blockchain_service.py`](../backend/services/blockchain_service.py) for Midnight integration
- Update [`start_proof_server.sh`](../scripts/start_proof_server.sh) to use official Midnight proof server
- Add JavaScript unit tests for contract logic validation

### Step 7: Frontend Integration - Midnight Wallet Connection

**Current**: Custom Cardano wallet integration
**New**: Midnight wallet integration using DApp Connector API

#### Wallet Connection Implementation

Based on the Midnight wallet connection tutorial, we'll implement a React wallet connector using the Midnight DApp Connector API.

**1. Define TypeScript Interfaces** (`frontend/src/types.ts`):
```typescript
export interface WalletCardProps {
  isConnected: boolean;
  walletAddress: string | null;
  onConnect: () => void;
  onDisconnect: () => void;
}

export interface MidnightConnectorAPI {
  enable(): Promise<any>;
  isEnabled(): Promise<boolean>;
  state(): Promise<{ address: string }>;
}
```

**2. Create WalletCard Component** (`frontend/src/components/WalletCard.tsx`):
```typescript
import React from "react";
import type { WalletCardProps } from "../types";

const WalletCard: React.FC<WalletCardProps> = ({
  isConnected,
  walletAddress,
  onConnect,
  onDisconnect,
}) => {
  return (
    <div className="wallet-card">
      <div className="status-section">
        <h2>Connection Status</h2>
        <div className={isConnected ? "text-green-400" : "text-red-400"}>
          {isConnected ? "Connected" : "Disconnected"}
        </div>
      </div>

      <div className="address-section">
        {isConnected && walletAddress ? (
          <>
            <p>Wallet Address:</p>
            <p title={walletAddress} className="address-text">
              {walletAddress}
            </p>
          </>
        ) : (
          <p>Please connect your wallet to proceed.</p>
        )}
      </div>

      <div className="action-section">
        {isConnected ? (
          <button onClick={onDisconnect} className="disconnect-btn">
            Disconnect Wallet
          </button>
        ) : (
          <button onClick={onConnect} className="connect-btn">
            Connect Wallet
          </button>
        )}
      </div>
    </div>
  );
};

export default WalletCard;
```

**3. Update Main App Component** (`frontend/src/App.tsx`):
```typescript
import React, { useState } from 'react';
import WalletCard from './components/WalletCard';
import PsycheScoreDApp from './components/PsycheScoreDApp';

const App: React.FC = () => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);

  const handleConnect = async () => {
    let connected = false;
    let address = null;
    
    try {
      // Authorize DApp with Midnight Lace wallet
      const connectorAPI = await window.midnight?.mnLace.enable();

      // Check if DApp is authorized
      const isEnabled = await window.midnight?.mnLace.isEnabled();
      if (isEnabled) {
        connected = true;
        console.log("Connected to the wallet:", connectorAPI);

        // Get wallet state including address
        const state = await connectorAPI.state();
        address = state.address;
      }
    } catch (error) {
      console.log("An error occurred:", error);
    }

    setIsConnected(connected);
    setWalletAddress(address);
  };

  const handleDisconnect = () => {
    setWalletAddress(null);
    setIsConnected(false);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>PsycheScore - Midnight Network</h1>
      </header>
      <main className="app-main">
        <WalletCard
          isConnected={isConnected}
          walletAddress={walletAddress}
          onConnect={handleConnect}
          onDisconnect={handleDisconnect}
        />
        {isConnected && (
          <PsycheScoreDApp walletAddress={walletAddress} />
        )}
      </main>
    </div>
  );
};

export default App;
```

**4. Update Entry Point** (`frontend/src/main.tsx`):
```typescript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

**5. Update HTML File** (`frontend/index.html`):
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PsycheScore - Midnight Network</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**6. Update PsycheScoreDApp Component** (`frontend/src/components/PsycheScoreDApp.tsx`):
```typescript
import React from 'react';

interface PsycheScoreDAppProps {
  walletAddress: string | null;
}

const PsycheScoreDApp: React.FC<PsycheScoreDAppProps> = ({ walletAddress }) => {
  // Existing survey logic and ML integration
  // Updated to use Midnight wallet for transactions
  
  const handleSubmitScore = async (scoreData: any, proof: any) => {
    try {
      const connectorAPI = await window.midnight?.mnLace.enable();
      
      // Submit transaction to Midnight network
      const result = await connectorAPI.submitTransaction({
        contract: 'psychescore',
        method: 'computeAndStoreScore',
        inputs: scoreData,
        proof: proof
      });
      
      console.log('Transaction submitted:', result);
      return result;
    } catch (error) {
      console.error('Transaction failed:', error);
      throw error;
    }
  };

  return (
    <div className="psychescore-dapp">
      {/* Existing survey interface */}
      <h2>Psychological Assessment</h2>
      <p>Connected wallet: {walletAddress}</p>
      {/* Survey form and score display */}
    </div>
  );
};

export default PsycheScoreDApp;
```

#### Prerequisites for Wallet Integration
- Midnight Lace wallet extension installed in browser
- Familiarity with TypeScript/JavaScript
- Basic understanding of React
- Midnight DApp Connector API available via `window.midnight.mnLace`

#### Key Integration Points
1. **Wallet Connection Flow**: Enable DApp authorization → Check connection status → Get wallet state
2. **Transaction Submission**: Use connector API to submit transactions with proofs
3. **State Management**: Track connection status and wallet address
4. **Error Handling**: Graceful handling of connection failures and user rejections

## Phase 4: Deployment & Testing

### Step 8: Midnight Testnet Deployment

**Configuration Updates:**

1. **Update Environment Variables**:
```bash
# .env
MIDNIGHT_NETWORK=testnet
MIDNIGHT_RPC_URL=https://testnet.midnight.network
CONTRACT_ADDRESS= # Will be set after deployment
```

2. **Deployment Script** (`scripts/deploy_midnight.sh`):
```bash
#!/bin/bash

# Navigate to MN app directory
cd psychescore-mn

# Deploy contract to Midnight testnet
npm run deploy -- --network testnet

# Get contract address
CONTRACT_ADDRESS=$(node -e "console.log(require('./deployment.json').contractAddress)")

# Update backend configuration
echo "CONTRACT_ADDRESS=$CONTRACT_ADDRESS" >> ../backend/.env
```

### Step 9: Testing Strategy with Compact JavaScript Implementation

#### JavaScript Unit Testing with Generated Implementation

The Compact compiler generates a JavaScript implementation (`index.cjs`) that enables comprehensive off-chain testing of contract logic before deployment.

**Unit Tests with Jest/Vitest:**
```javascript
// tests/psychescore.test.js
const { Contract, State, ContractState, StateValue, QueryContext } = require('../contracts/managed/psychescore/index.cjs');

describe('PsycheScore Contract', () => {
  let contract;

  beforeEach(() => {
    contract = new Contract({
      localSecretKey: () => Buffer.from('test-key', 'hex')
    });
  });

  it('should compute and store score for valid inputs', () => {
    const context = {
      originalState: { status: State.VACANT },
      transactionContext: { timestamp: Date.now() }
    };
    
    const surveyData = {
      encrypted_responses: Array(50).fill(1),
      koios_features: Array(4).fill(0.5),
      ml_model_weights: Array(54).fill(0.02),
      ml_model_bias: 50,
      wallet_address: 'test-address',
      response_commitment: 25
    };

    const { result, proofData } = contract.circuits.computeAndStoreScore(context, surveyData);
    
    expect(result.status).toBe(State.OCCUPIED);
    expect(proofData.input).toBeDefined();
    expect(proofData.output).toBeDefined();
  });

  it('should reject invalid score range', () => {
    // Test boundary conditions
    const invalidData = { /* data that would produce score < 0 or > 100 */ };
    
    expect(() => {
      contract.circuits.computeAndStoreScore(context, invalidData);
    }).toThrow();
  });

  it('should manage ContractState correctly', () => {
    // Test state initialization and operations
    const contractState = new ContractState();
    expect(contractState.operations()).toContain('computeAndStoreScore');
    expect(contractState.operations()).toContain('verifyScore');
  });

  it('should handle StateValue maps for user scores', () => {
    // Test map operations for user scores storage
    const userScoresMap = StateValue.newMap(new StateMap());
    expect(userScoresMap.type()).toBe('map');
    expect(userScoresMap.asMap()).toBeDefined();
  });

  it('should use QueryContext for state queries', () => {
    const contractState = new ContractState();
    const queryContext = new QueryContext(contractState.data, 'test-address');
    const queryResults = queryContext.query([/* query operations */], costModel);
    expect(queryResults).toBeDefined();
  });
});
```

**TypeScript Testing with Generated Types:**
```typescript
// tests/psychescore.test.ts
import { Contract, State } from '../contracts/managed/psychescore';

describe('PsycheScore Contract TypeScript', () => {
  it('should provide type-safe contract interactions', () => {
    const contract = new Contract({
      localSecretKey: () => Buffer.from('test-key', 'hex')
    });

    // TypeScript will enforce correct parameter types
    const result = contract.circuits.computeAndStoreScore(
      { originalState: { status: State.VACANT }, transactionContext: {} },
      validSurveyData
    );

    // Type-safe result access
    expect(result.result.status).toBe(State.OCCUPIED);
  });
});
```

#### Integration Testing Strategy

**Unit Tests:**
- Test individual circuits using JavaScript implementation
- Verify proof generation and validation
- Test contract interactions with mock data
- Validate type safety with TypeScript

**Integration Tests:**
- End-to-end flow: Survey → ML → Proof → Blockchain
- Performance testing: Proof generation timing
- User experience testing with Midnight wallet
- Proof server integration testing

**Test Script** (`scripts/test_midnight_integration.py`):
```python
def test_complete_flow():
    # 1. Submit survey responses
    # 2. Generate ML score
    # 3. Create ZK proof using MN app JavaScript implementation
    # 4. Submit to Midnight testnet
    # 5. Verify on-chain storage
    pass

def test_javascript_implementation():
    """Test the generated JavaScript implementation"""
    import subprocess
    import json
    
    # Run JavaScript unit tests
    result = subprocess.run(['npm', 'test'],
                          cwd='psychescore-mn',
                          capture_output=True,
                          text=True)
    
    assert result.returncode == 0, f"JavaScript tests failed: {result.stderr}"
```

## Migration Timeline

### Week 1: Environment & Contract Setup
- Day 1-2: Set up MN app environment
- Day 3-4: Migrate and test Compact contracts
- Day 5: Compile and verify contracts

### Week 2: Proof Server & Backend Integration
- Day 1: Set up Midnight proof server (Docker installation and configuration)
- Day 2: Create MN service wrapper with proof server integration
- Day 3-4: Update backend API endpoints
- Day 5: Integration testing with proof server

### Week 3: Frontend & Deployment
- Day 1-2: Implement Midnight wallet connection using DApp Connector API
- Day 3: Update PsycheScoreDApp component for Midnight integration
- Day 4: Deploy to Midnight testnet
- Day 5: End-to-end testing and bug fixes

## Success Metrics

### Technical Metrics
- **Proof Generation**: <30 seconds for 50 questions (using official proof server)
- **Proof Server Uptime**: 99.9% local service availability
- **Transaction Confirmation**: <20 seconds on Midnight testnet
- **End-to-End Time**: <1 minute for complete flow
- **Proof Server Response**: <5 seconds for proof generation requests

### User Experience Metrics
- **Wallet Connection**: <5 seconds using Midnight DApp Connector
- **Survey Completion**: <10 minutes
- **Score Generation**: Real-time feedback
- **Transaction Success**: >95% success rate
- **DApp Authorization**: Single-click approval flow

## Risk Mitigation

### Technical Risks
- **Circuit Complexity**: Start with simplified version, then add features
- **Proof Server Setup**: Ensure Docker compatibility and network configuration
- **Integration Issues**: Use mock services during development, test with proof server early
- **Performance**: Profile proof generation timing and optimize early
- **Privacy**: Verify proof server runs locally without external connections

### Migration Risks
- **Data Loss**: Maintain backup of existing system
- **User Impact**: Gradual rollout with feature flags
- **Rollback Plan**: Keep previous version deployable

## Performance Optimization Guidelines

### Proof Generation Optimization

**Circuit Design Best Practices:**
```compact
// Optimized circuit design for PsycheScore
export circuit computeAndStoreScore(
    encrypted_responses: [Field; 50],
    koios_features: [Field; 4],
    ml_model_weights: [Field; 54],
    ml_model_bias: Field,
    wallet_address: Address,
    response_commitment: Opaque<"bytes32">
): [] {
    // Use batch operations where possible
    var computed_score: Field = ml_model_bias;
    
    // Optimized: Pre-compute common operations
    let weight_sum: Field = 0;
    for i in 0..54 {
        weight_sum = weight_sum + ml_model_weights[i];
    }
    
    // Process survey responses with reduced constraints
    for i in 0..50 {
        computed_score = computed_score + (encrypted_responses[i] * ml_model_weights[i]);
    }
    
    // Process KOIOS features
    for i in 0..4 {
        computed_score = computed_score + (koios_features[i] * ml_model_weights[50 + i]);
    }
    
    // Use efficient range checks
    assert(computed_score >= 0 && computed_score <= 100);
    
    // Optimized commitment verification
    let calculated_commitment: Field = 0;
    for i in 0..50 {
        calculated_commitment = calculated_commitment + encrypted_responses[i];
    }
    assert(calculated_commitment == response_commitment);
    
    // Efficient state updates
    user_scores[wallet_address] = disclose(Opaque<"uint32">(computed_score));
    score_commitments[wallet_address] = response_commitment;
}
```

**Proof Server Configuration:**
```bash
# Optimized proof server startup
docker run -p 6300:6300 midnightnetwork/proof-server -- \
  'midnight-proof-server --network testnet --max-parallel-proofs 4 --cache-size 1024'
```

**Performance Monitoring:**
```javascript
// Performance monitoring for proof generation
const startTime = Date.now();
const { result, proofData } = contract.circuits.computeAndStoreScore(context, surveyData);
const proofTime = Date.now() - startTime;

console.log(`Proof generation time: ${proofTime}ms`);
console.log(`Proof size: ${JSON.stringify(proofData).length} bytes`);

// Performance targets:
// - Proof generation: <30 seconds
// - Proof size: <100KB
// - Memory usage: <512MB
```

### Contract Execution Optimization

**StateValue Management:**
```javascript
// Optimized StateValue usage
const optimizedState = StateValue.newMap(new StateMap());

// Use appropriate StateValue types for performance:
// - Maps: For key-value lookups (O(log n))
// - Arrays: For sequential access (O(1) for small arrays)
// - Bounded Merkle Trees: For commitment storage
// - Cells: For single values

// Batch operations for better performance
const batchOperations = [
    /* multiple state updates in single transaction */
];

// Use QueryContext efficiently
const queryContext = new QueryContext(contractState.data, contractAddress);
const optimizedResults = queryContext.query(batchOperations, costModel);
```

**Memory and Resource Management:**
```javascript
// Memory optimization for large datasets
const MAX_BATCH_SIZE = 100; // Process in batches to avoid memory issues

// Resource cleanup
function cleanupResources() {
    // Clear temporary state
    // Release memory
    // Close connections
}

// Performance profiling
const performance = {
    proofGenerationTime: [],
    contractExecutionTime: [],
    memoryUsage: []
};
```

### Network and Deployment Optimization

**Network Configuration:**
```javascript
// Optimized network settings
setNetworkId('testnet'); // Use appropriate network ID

// Connection pooling for proof server
const proofServerPool = {
    maxConnections: 10,
    idleTimeout: 30000,
    connectionTimeout: 5000
};
```

**Deployment Optimization:**
```bash
# Optimized deployment script
#!/bin/bash

# Pre-compile contracts for faster deployment
compact compile contracts/psychescore.compact contracts/managed/psychescore --optimize

# Use deployment optimization flags
npm run deploy -- --network testnet --optimize --gas-limit 10000000

# Monitor deployment performance
echo "Deployment completed in $(($(date +%s) - start_time)) seconds"
```

### Performance Testing Strategy

**Load Testing:**
```javascript
// Performance test suite
describe('Performance Tests', () => {
  it('should handle concurrent proof generation', async () => {
    const concurrentRequests = 10;
    const promises = [];
    
    for (let i = 0; i < concurrentRequests; i++) {
      promises.push(contract.circuits.computeAndStoreScore(context, testData));
    }
    
    const results = await Promise.all(promises);
    expect(results).toHaveLength(concurrentRequests);
  });
  
  it('should maintain performance under load', async () => {
    const startTime = Date.now();
    // Generate 100 proofs sequentially
    for (let i = 0; i < 100; i++) {
      await contract.circuits.computeAndStoreScore(context, testData);
    }
    const totalTime = Date.now() - startTime;
    expect(totalTime).toBeLessThan(300000); // 5 minutes for 100 proofs
  });
});
```

**Performance Targets:**
- **Proof Generation**: <30 seconds per proof
- **Contract Execution**: <5 seconds per transaction
- **Memory Usage**: <512MB peak
- **Concurrent Users**: Support 100+ simultaneous users
- **Throughput**: 10+ proofs per minute
- **Response Time**: <2 seconds for API responses

**Monitoring and Alerting:**
```javascript
// Performance monitoring setup
const performanceMetrics = {
  proofGenerationTime: [],
  contractExecutionTime: [],
  memoryUsage: [],
  errorRate: 0,
  throughput: 0
};

// Set up alerts for performance degradation
if (performanceMetrics.proofGenerationTime > 45000) { // 45 seconds
  alert('Proof generation performance degraded');
}
```

## Post-Migration Enhancements

### Phase 5: Advanced Features
1. **Multi-party Computation**: Allow multiple data sources
2. **Dynamic Disclosure**: User-controlled data sharing
3. **Batch Processing**: Optimize for multiple users
4. **Cross-chain Integration**: Cardano-Midnight interoperability

### Phase 6: Production Optimization
1. **Performance Tuning**: Optimize proof generation
2. **Security Audits**: Third-party contract review
3. **Monitoring**: Real-time performance monitoring
4. **Scaling**: Horizontal scaling for high traffic

## Wallet Connection Benefits

### Enhanced User Experience
- **Seamless Integration**: Direct connection to Midnight Lace wallet via DApp Connector API
- **Single Authorization**: One-time DApp approval for persistent connection
- **Real-time Status**: Live connection status and wallet address display
- **Error Handling**: Graceful handling of connection failures and user rejections

### Developer Benefits
- **TypeScript Support**: Full type safety with defined interfaces
- **Standardized API**: Consistent wallet interaction patterns
- **Hot Reloading**: Development-friendly with instant updates
- **Production Ready**: Battle-tested connection flow

### Security Features
- **User Consent**: Explicit DApp authorization required
- **Secure Communication**: Encrypted wallet-DApp communication
- **State Verification**: Real-time wallet state validation
- **Transaction Signing**: Secure transaction submission

## Benefits of Compact JavaScript Implementation Design

The Compact JavaScript implementation is more than just a convenience feature—it's what makes zero-knowledge smart contract development practical and accessible.

### 1. Bridge Between ZK Circuits and Everyday Code
- **Human-Friendly Testing**: Run exactly the same logic as the ZK circuit in Node.js for debugging and validation
- **Local Validation**: Test contract behavior locally before touching the proof server or submitting to Midnight network
- **Debugging Capabilities**: Step through, log, and inspect contract logic in familiar JavaScript environment

### 2. Type Safety and Consistency
- **Identical Encoding**: Data passed into JavaScript tests uses the same encoding as on-chain execution
- **Eliminated Bugs**: No subtle differences in byte order, field alignment, or encoding length
- **Deterministic Behavior**: Same inputs produce identical behavior in JS tests and ZK circuits

### 3. Reproducibility and Proof Transparency
- **Structured Proof Data**: Each contract call returns `proofData` object with input/output/transcript information
- **Record and Replay**: Capture circuit executions for reproducible testing
- **Verification Support**: Use proof data for transparent verification without external tools

### 4. Developer Productivity Without Compromising Privacy
- **Familiar Tools**: Use TypeScript, Jest, VSCode, Node.js while working with privacy-preserving logic
- **Integration Testing**: Write tests in the same language as your application
- **Simulation Capabilities**: Simulate user flows off-chain before deployment
- **Logic Validation**: Validate logic changes before recompiling circuits

## Conclusion

This migration plan transforms PsycheScore from a custom implementation to an official Midnight Network app, leveraging:

- **Official Tooling**: `create-mn-app` CLI with hot reloading
- **Compact JavaScript Implementation**: Generated JavaScript for off-chain testing and development
- **Proof Server**: Local Docker-based proof generation for privacy protection
- **TypeScript APIs**: Auto-generated from compiled contracts with full type safety
- **Wallet Integration**: Built-in Midnight wallet support via DApp Connector API
- **Production Ready**: Pre-configured deployment with comprehensive testing
- **Privacy Guarantees**: Official Compact compiler security and local proof generation
- **Developer Experience**: Familiar JavaScript/TypeScript workflow for ZK development

The Compact JavaScript implementation serves as a crucial bridge between developer experience and cryptographic correctness, allowing you to reason about private, verifiable logic with ordinary code. The proof server integration ensures that all ZK proofs are generated locally, protecting sensitive user data while maintaining compatibility with the Midnight Network ecosystem.

The migration preserves existing ML model functionality while enhancing privacy, security, and developer experience through the official Midnight Network ecosystem. By exposing ZK logic through familiar JavaScript code, it shortens the gap between concept, implementation, and verification—making zero-knowledge smart contract development both accessible and practical.