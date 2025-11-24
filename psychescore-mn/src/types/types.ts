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

export interface SurveyResponse {
  questionId: number;
  response: number;
}

export interface MLScoreData {
  weights: number[];
  bias: number;
  koiosFeatures: number[];
}

export interface ProofData {
  input: any;
  output: any;
  proof: string;
}

// Extend Window interface for Midnight wallet
declare global {
  interface Window {
    midnight?: {
      mnLace: {
        enable(): Promise<any>;
        isEnabled(): Promise<boolean>;
        state(): Promise<{ address: string }>;
      };
    };
  }
}