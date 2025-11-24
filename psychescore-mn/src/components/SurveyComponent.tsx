import React, { useState } from 'react';

interface SurveyQuestion {
  id: string;
  trait: string;
  text: string;
  positive: boolean;
}

interface SurveyResponse {
  [key: string]: number;
}

interface SurveyComponentProps {
  walletAddress: string | null;
  onSurveyComplete: (responses: number[], score: number) => void;
}

const BIG_FIVE_QUESTIONS: SurveyQuestion[] = [
  // Openness to Experience (O)
  { id: "O1", trait: "O", text: "I have a vivid imagination.", positive: true },
  { id: "O2", trait: "O", text: "I am interested in many different things.", positive: true },
  { id: "O3", trait: "O", text: "I prefer work that is routine.", positive: false },
  { id: "O4", trait: "O", text: "I like to reflect on things.", positive: true },

  // Conscientiousness (C)
  { id: "C1", trait: "C", text: "I am always prepared.", positive: true },
  { id: "C2", trait: "C", text: "I pay attention to details.", positive: true },
  { id: "C3", trait: "C", text: "I often forget to put things back in their proper place.", positive: false },
  { id: "C4", trait: "C", text: "I make plans and stick to them.", positive: true },

  // Extraversion (E)
  { id: "E1", trait: "E", text: "I am the life of the party.", positive: true },
  { id: "E2", trait: "E", text: "I don't mind being the center of attention.", positive: true },
  { id: "E3", trait: "E", text: "I keep in the background.", positive: false },
  { id: "E4", trait: "E", text: "I start conversations easily.", positive: true },

  // Agreeableness (A)
  { id: "A1", trait: "A", text: "I sympathize with others' feelings.", positive: true },
  { id: "A2", trait: "A", text: "I take time out for others.", positive: true },
  { id: "A3", trait: "A", text: "I insult people.", positive: false },
  { id: "A4", trait: "A", text: "I feel others' emotions.", positive: true },

  // Neuroticism (N)
  { id: "N1", trait: "N", text: "I get stressed out easily.", positive: true },
  { id: "N2", trait: "N", text: "I worry about things.", positive: true },
  { id: "N3", trait: "N", text: "I am relaxed most of the time.", positive: false },
  { id: "N4", trait: "N", text: "I get upset easily.", positive: true },
];

const RESPONSE_SCALE: { [key: number]: string } = {
  1: "Strongly Disagree",
  2: "Disagree",
  3: "Neutral",
  4: "Agree",
  5: "Strongly Agree"
};

const SurveyComponent: React.FC<SurveyComponentProps> = ({ walletAddress, onSurveyComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  const [responses, setResponses] = useState<SurveyResponse>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleResponse = (questionId: string, value: number): void => {
    setResponses((prev: SurveyResponse) => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleNext = (): void => {
    if (currentQuestion < BIG_FIVE_QUESTIONS.length - 1) {
      setCurrentQuestion((prev: number) => prev + 1);
    }
  };

  const handlePrevious = (): void => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev: number) => prev - 1);
    }
  };

  const handleSubmit = async (): Promise<void> => {
    if (!walletAddress) {
      setError("Wallet address is required to submit survey");
      return;
    }

    // Check if all questions are answered
    const unansweredQuestions = BIG_FIVE_QUESTIONS.filter(q => !responses[q.id]);
    if (unansweredQuestions.length > 0) {
      setError("Please answer all questions before submitting");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Convert responses to array format expected by backend
      const surveyResponses = BIG_FIVE_QUESTIONS.map(q => responses[q.id]);

      // Submit to backend API
      const response = await fetch('http://localhost:8000/process_survey', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          survey_responses: surveyResponses,
          user_metadata: {
            // Add any additional metadata here
            timestamp: new Date().toISOString()
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        onSurveyComplete(surveyResponses, result.ml_score);
      } else {
        throw new Error(result.error || 'Failed to process survey');
      }
    } catch (err) {
      console.error('Survey submission error:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit survey');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentQuestionData = BIG_FIVE_QUESTIONS[currentQuestion];
  const progress = ((currentQuestion + 1) / BIG_FIVE_QUESTIONS.length) * 100;

  return (
    <div className="survey-component">
      <div className="survey-header">
        <h3>Big Five Personality Assessment</h3>
        <p>Question {currentQuestion + 1} of {BIG_FIVE_QUESTIONS.length}</p>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="survey-content">
        <div className="question-section">
          <h4>{currentQuestionData.text}</h4>
          <div className="response-options">
            {Object.entries(RESPONSE_SCALE).map(([value, label]) => (
              <label key={value} className="response-option">
                <input
                  type="radio"
                  name={`question-${currentQuestionData.id}`}
                  value={value}
                  checked={responses[currentQuestionData.id] === parseInt(value)}
                  onChange={() => handleResponse(currentQuestionData.id, parseInt(value))}
                />
                <span className="response-label">
                  <span className="response-value">{value}</span>
                  <span className="response-text">{label}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="survey-navigation">
          <button 
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="nav-button prev-button"
          >
            Previous
          </button>

          {currentQuestion < BIG_FIVE_QUESTIONS.length - 1 ? (
            <button 
              onClick={handleNext}
              disabled={!responses[currentQuestionData.id]}
              className="nav-button next-button"
            >
              Next
            </button>
          ) : (
            <button 
              onClick={handleSubmit}
              disabled={!responses[currentQuestionData.id] || isSubmitting}
              className="nav-button submit-button"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Survey'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SurveyComponent;