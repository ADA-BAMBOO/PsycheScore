import React, { useState } from 'react';
import SurveyComponent from './SurveyComponent';

interface PsycheScoreDAppProps {
  walletAddress: string | null;
}

const PsycheScoreDApp: React.FC<PsycheScoreDAppProps> = ({ walletAddress }) => {
  const [showSurvey, setShowSurvey] = useState<boolean>(false);
  const [surveyCompleted, setSurveyCompleted] = useState<boolean>(false);
  const [surveyScore, setSurveyScore] = useState<number | null>(null);
  const [surveyResponses, setSurveyResponses] = useState<number[] | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<string | null>(null);
  const [verificationData, setVerificationData] = useState<any>(null);

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

  const handleStartSurvey = () => {
    setShowSurvey(true);
    setSurveyCompleted(false);
    setSurveyScore(null);
    setSurveyResponses(null);
  };

  const handleSurveyComplete = (responses: number[], score: number) => {
    setSurveyCompleted(true);
    setSurveyScore(score);
    setSurveyResponses(responses);
    setShowSurvey(false);
    
    // Optionally submit to blockchain
    console.log('Survey completed with score:', score);
    console.log('Responses:', responses);
  };

  const handleSubmitToBlockchain = async () => {
    if (!surveyScore || !surveyResponses || !walletAddress) {
      alert('Missing required data to submit to blockchain');
      return;
    }

    try {
      // Submit to backend for blockchain processing
      const response = await fetch('http://localhost:8000/submit_to_blockchain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          ml_score: surveyScore,
          survey_responses: surveyResponses
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        alert('Score successfully submitted to blockchain!');
        console.log('Blockchain submission result:', result);
      } else {
        throw new Error(result.error || 'Failed to submit to blockchain');
      }
    } catch (error) {
      console.error('Blockchain submission error:', error);
      alert('Failed to submit to blockchain: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  const handleVerifyBlockchain = async () => {
    if (!walletAddress) {
      alert('Please connect your wallet first');
      return;
    }

    try {
      setVerificationStatus('Verifying...');
      
      const response = await fetch(`http://localhost:8000/verify_blockchain_submission?wallet_address=${walletAddress}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setVerificationStatus(result.verified ? 'Verified' : 'Not Found');
        setVerificationData(result);
        console.log('Blockchain verification result:', result);
      } else {
        throw new Error(result.error || 'Failed to verify blockchain submission');
      }
    } catch (error) {
      console.error('Blockchain verification error:', error);
      setVerificationStatus('Error');
      alert('Failed to verify blockchain submission: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <div className="psychescore-dapp">
      <h2>Psychological Assessment</h2>
      <p>Connected wallet: {walletAddress}</p>
      
      {/* Blockchain Verification Section */}
      <div className="verification-section">
        <h3>Blockchain Verification</h3>
        <p>Verify your score on the Midnight Network blockchain</p>
        <button onClick={handleVerifyBlockchain} className="verify-blockchain">
          Verify Blockchain Submission
        </button>
        
        {verificationStatus && (
          <div className={`verification-result ${verificationStatus.toLowerCase()}`}>
            <h4>Verification Status: {verificationStatus}</h4>
            {verificationData && (
              <div className="verification-details">
                {verificationData.verified ? (
                  <div>
                    <p>✅ Score successfully verified on Midnight Network blockchain!</p>
                    <div className="score-details">
                      <p><strong>Score:</strong> {verificationData.score_data?.score}</p>
                      <p><strong>Transaction Hash:</strong> {verificationData.score_data?.transaction_hash}</p>
                      <p><strong>Network:</strong> {verificationData.score_data?.network}</p>
                      <p><strong>Timestamp:</strong> {new Date(verificationData.score_data?.timestamp * 1000).toLocaleString()}</p>
                    </div>
                  </div>
                ) : (
                  <p>❌ No score found on Midnight Network blockchain for this wallet address.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      
      {!showSurvey && !surveyCompleted && (
        <div className="survey-section">
          <h3>Big Five Personality Assessment</h3>
          <p>Complete the survey to get your psychological score</p>
          <button onClick={handleStartSurvey}>
            Start Survey
          </button>
        </div>
      )}

      {showSurvey && (
        <SurveyComponent
          walletAddress={walletAddress}
          onSurveyComplete={handleSurveyComplete}
        />
      )}

      {surveyCompleted && surveyScore !== null && (
        <div className="survey-results">
          <h3>Survey Completed!</h3>
          <div className="score-display">
            <h4>Your Psychological Score: {surveyScore}</h4>
            <p>Based on your responses to the Big Five Personality Assessment</p>
          </div>
          
          <div className="score-breakdown">
            <h5>Score Interpretation:</h5>
            <ul>
              <li>0-20: Very Low</li>
              <li>21-40: Low</li>
              <li>41-60: Average</li>
              <li>61-80: High</li>
              <li>81-100: Very High</li>
            </ul>
          </div>

          <div className="action-buttons">
            <button onClick={handleSubmitToBlockchain} className="submit-blockchain">
              Submit Score to Blockchain
            </button>
            <button onClick={handleStartSurvey} className="retake-survey">
              Retake Survey
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PsycheScoreDApp;