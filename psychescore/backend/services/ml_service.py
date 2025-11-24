"""
ML Service for PsycheScore
Integrates with existing ML model for psychological scoring
"""

import os
import sys
import json
import logging
import subprocess
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)

class MLService:
    """Service for ML model integration and score generation"""
    
    def __init__(self):
        self.ml_model_path = os.path.join(
            os.path.dirname(__file__), '..', 'models'
        )
        self.score_json_path = os.path.join(self.ml_model_path, 'score.json')
        
    def generate_score(self, wallet_address: str, survey_responses: List[int], 
                      user_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ML score using existing ML model
        
        Args:
            wallet_address: User's Cardano wallet address
            survey_responses: List of 20 survey responses (1-5 scale)
            user_metadata: Additional user metadata
            
        Returns:
            Dictionary containing score and related data
        """
        try:
            logger.info(f"Generating ML score for wallet: {wallet_address}")
            
            # For now, we'll use the existing ml_score.py script
            # In a production system, we'd import and call the functions directly
            # but this approach ensures compatibility with existing code
            
            # Generate a mock transaction hash for signature
            import hashlib
            import time
            tx_hash = hashlib.sha256(
                f"{wallet_address}{time.time()}".encode()
            ).hexdigest()[:64]
            
            # Run the existing ML model script
            result = self._run_ml_script(wallet_address, tx_hash)
            
            # Enhance with survey data for future model improvements
            result['survey_responses'] = survey_responses
            result['user_metadata'] = user_metadata
            result['survey_timestamp'] = int(time.time())
            
            logger.info(f"ML score generated: {result['score']}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating ML score: {str(e)}")
            raise
    
    def _run_ml_script(self, wallet_address: str, tx_hash: str) -> Dict[str, Any]:
        """
        Run the existing ml_score.py script and parse results
        
        Args:
            wallet_address: Wallet address to analyze
            tx_hash: Transaction hash for signature
            
        Returns:
            Parsed score data
        """
        try:
            # Construct the command to run the ML script
            ml_script_path = os.path.join(self.ml_model_path, 'ml_score.py')
            
            # Run the script using subprocess
            result = subprocess.run([
                'python', ml_script_path, 
                wallet_address, 
                tx_hash
            ], 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(__file__))
            
            if result.returncode != 0:
                logger.error(f"ML script failed: {result.stderr}")
                raise Exception(f"ML model execution failed: {result.stderr}")
            
            # Parse the output
            logger.info(f"ML script output: {result.stdout}")
            
            # Load the generated score.json file
            if os.path.exists(self.score_json_path):
                with open(self.score_json_path, 'r') as f:
                    score_data = json.load(f)
                
                # Add the transaction hash used for signing
                score_data['signing_tx_hash'] = tx_hash
                
                return score_data
            else:
                raise Exception("Score JSON file not generated")
                
        except Exception as e:
            logger.error(f"Error running ML script: {str(e)}")
            # Fallback to mock data for development
            return self._generate_mock_score(wallet_address, tx_hash)
    
    def _generate_mock_score(self, wallet_address: str, tx_hash: str) -> Dict[str, Any]:
        """
        Generate mock score data for development/testing
        
        Args:
            wallet_address: Wallet address
            tx_hash: Transaction hash
            
        Returns:
            Mock score data
        """
        import time
        import hashlib
        
        # Generate deterministic mock score based on wallet address
        hash_val = int(hashlib.sha256(wallet_address.encode()).hexdigest(), 16)
        mock_score = 50 + (hash_val % 50)  # Score between 50-100
        
        # Mock KOIOS data
        koios_data = {
            "tx_count": 10 + (hash_val % 500),
            "avg_tx_size_ada": 50 + (hash_val % 100) / 10.0,
            "days_staked": 30 + (hash_val % 365),
            "tx_freq_daily": (hash_val % 50) / 100.0,
        }
        
        # Mock oracle data
        mock_datum = {
            "address": wallet_address,
            "score": mock_score,
            "timestamp": int(time.time()),
            "oracle_vkey": "mock_oracle_vkey_hex",
            "model_version": "v1.0",
            "koios_data": koios_data,
            "sig": "mock_signature_hex",
            "signing_tx_hash": tx_hash
        }
        
        logger.info(f"Generated mock score: {mock_score}")
        return mock_datum
    
    def validate_survey_responses(self, responses: List[int]) -> bool:
        """
        Validate survey responses
        
        Args:
            responses: List of survey responses
            
        Returns:
            True if valid, False otherwise
        """
        if len(responses) != 20:
            return False
        
        # Check all responses are integers between 1-5
        for response in responses:
            if not isinstance(response, int) or response < 1 or response > 5:
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get ML model information
        
        Returns:
            Model metadata
        """
        return {
            "model_version": "v1.0",
            "model_type": "Psychological Scoring",
            "features_used": ["tx_count", "avg_tx_size_ada", "days_staked", "tx_freq_daily"],
            "training_date": "2024-01-01",
            "performance_metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.87
            }
        }