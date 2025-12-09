import React, { useState } from "react";
import WalletCard from "./components/WalletCard";
import logoWhite from "./publish/img/psylogo_white.png";
import imgLace from "./publish/img/lace.png";
import imgYoroi from "./publish/img/yoroi.png";
import imgMidnight from "./publish/img/midnight.png";


type SupportedWallet = "lace";

const App: React.FC = () => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);

  // 2. Thêm state để quản lý việc Ẩn/Hiện Popup
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleConnect = async (wallet: SupportedWallet) => {
    setIsModalOpen(false);
    let connected = false;
    let address = null;

    try {
      switch (wallet) {
        case "lace": {
          if (!window.midnight?.mnLace) {
            alert(
              "Lace wallet not detected. Please install the Lace browser extension to connect."
            );
            return;
          }

          const connectorAPI = await window.midnight.mnLace.enable();
          const isEnabled = await window.midnight.mnLace.isEnabled();
          if (isEnabled) {
            connected = true;
            const state = await connectorAPI.state?.();
            address = state?.address ?? null;
            alert("Lace wallet connected successfully.");
          } else {
            alert(
              "Wallet connection was not authorized. Please approve the request in Lace."
            );
          }
          break;
        }
        default:
          alert("Unsupported wallet selection.");
          return;
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
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
    <>
      <header>
        <div className="container">
          <nav className="navbar">
            <a href="#" className="logo">
              <img src={logoWhite} alt="PsycheScore Logo" />
            </a>
            <div className="nav-right">
              <button id="theme-toggle" className="theme-toggle-btn">
                <i className="fa-solid fa-moon"></i>
              </button>
              <a href="#" className="btn btn-secondary">
                <i className="fa-solid fa-file-lines"></i>
                Whitepaper
              </a>
            </div>
          </nav>
        </div>
      </header>
      <div className="container">
        <main className="hero-section">
          <div className="hero-content">
            <h1>
              Experience <span className="highlight">PsycheCredit</span> – The
              decentralized protocol
            </h1>
            <p>
              Unlock powerful AI tools for your business — deploy smart
              chatbots, automate workflows, analyze data, and more with zero
              coding. Scalable. Secure. Lightning fast.
            </p>
            <div className="cta-buttons">
              {/* 4. Gắn sự kiện onClick để mở Popup */}
              {!isConnected ? (
                <button
                  className="btn btn-primary"
                  onClick={() => setIsModalOpen(true)}
                >
                  <i className="fa-solid fa-wallet"></i> Connect wallet
                </button>
              ) : (
                <button
                  className="btn btn-secondary"
                  onClick={handleDisconnect}
                >
                  Disconnect
                </button>
              )}

              <a href="#" className="btn btn-secondary">
                Watch Demo
              </a>
            </div>
            <div style={{ marginTop: "2rem" }}>
              <WalletCard
                isConnected={isConnected}
                walletAddress={walletAddress}
                onConnect={() => void handleConnect("lace")}
                onDisconnect={handleDisconnect}
              />
            </div>
          </div>
        </main>

        <footer>
          <div className="social-icons">
            <a href="#">
              <i className="fab fa-facebook-f"></i>
            </a>
            <a href="#">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="#">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="#">
              <i className="fab fa-telegram"></i>
            </a>
          </div>
          <div className="copyright">
            <p>&copy; 2025. PsycheScore</p>
          </div>
        </footer>
      </div>

      {isModalOpen && (
        <div
          className="wallet-popup-overlay"
          id="walletPopup"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsModalOpen(false);
            }
          }}
        >
          <div className="wallet-popup">
            <div className="popup-header">
              <h2>Connect Wallet</h2>
              {/* Nút đóng popup */}
              <button
                className="close-btn"
                onClick={() => setIsModalOpen(false)}
              >
                &times;
              </button>
            </div>
            <p className="popup-subheading">Choose how you want to connect</p>
            <ul className="wallet-list">
              <li
                className="wallet-item"
                onClick={() => void handleConnect("lace")}
                style={{ cursor: "pointer" }}
              >
                <a>
                  <img src={imgLace} alt="Lace Wallet" />
                  Lace wallet
                </a>
              </li>
              <li className="wallet-item">
                <a href="#">
                  <img src={imgYoroi} alt="Yoroi Wallet" />
                  Yoroi Wallet
                </a>
              </li>

              <li className="wallet-item" style={{ cursor: "not-allowed", opacity: 0.6 }}>
                <a>
                  <img src={imgMidnight} alt="Midnight" />
                  Midnight (coming soon)
                </a>
              </li>
            </ul>
          </div>
        </div>
      )}
    </>
  );
};

export default App;
