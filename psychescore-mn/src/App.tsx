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
      // Check if Midnight Lace wallet is available
      if (!window.midnight?.mnLace) {
        console.error("Midnight Lace wallet not detected. Please install the Midnight Lace wallet browser extension to connect.");
        alert("Midnight Lace wallet not detected. Please install the Midnight Lace wallet browser extension to connect.");
        return;
      }

      // Authorize DApp with Midnight Lace wallet
      const connectorAPI = await window.midnight.mnLace.enable();

      // Check if DApp is authorized
      const isEnabled = await window.midnight.mnLace.isEnabled();
      if (isEnabled) {
        connected = true;
        console.log("Connected to the wallet:", connectorAPI);

        // Get wallet state including address
        const state = await connectorAPI.state();
        address = state.address;
      } else {
        alert("Wallet connection was not authorized. Please approve the connection request in your wallet.");
      }
    } catch (error) {
      console.error("An error occurred during wallet connection:", error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to connect wallet: ${errorMessage}`);
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