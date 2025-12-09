import React from "react";
import type { WalletCardProps } from "../types/types";

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
          <p>Please connect your Lace wallet to proceed.</p>
        )}
      </div>

      <div className="action-section">
        {isConnected ? (
          <button onClick={onDisconnect} className="disconnect-btn">
            Disconnect Wallet
          </button>
        ) : (
          <button onClick={onConnect} className="connect-btn">
            Connect Lace Wallet
          </button>
        )}
      </div>
    </div>
  );
};

export default WalletCard;