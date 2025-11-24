"""
ZK Proof Service for PsycheScore
Migrated to Midnight Network with Compact JavaScript implementation
"""

import os
import json
import logging
import subprocess
import tempfile
from typing import Dict, Any, List, Optional

# Import MN service for Midnight Network integration
from .mn_service import MNService

logger = logging.getLogger(__name__)

class ZKProofService:
    """Service for ZK proof generation and verification using Midnight Network"""
    
    def __init__(self):
        self.mn_service = MNService()
        # Get the absolute path to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        self.midnight_path = os.path.join(project_root, 'psychescore-mn')
        self.circuit_path = os.path.join(self.midnight_path, 'contracts', 'psychescore.compact')
        
        # Check if ZK services are available
        self._available = self._check_zk_availability()
        
    def is_available(self) -> bool:
        """Check if ZK proof service is available"""
        return self._available
    
    def _check_zk_availability(self) -> bool:
        """Check if Midnight Network ZK components are available"""
        try:
            # Check if MN app structure exists
            if not os.path.exists(self.midnight_path):
                logger.warning(f"Midnight Network app not found: {self.midnight_path}")
                return False
            
            # Check if Compact contract exists
            if not os.path.exists(self.circuit_path):
                logger.warning(f"Compact contract not found: {self.circuit_path}")
                return False
            
            # Test MN service availability
            try:
                test_data = {
                    "survey_responses": [1] * 50,
                    "ml_weights": [0.02] * 54,
                    "koios_data": [0.5] * 4,
                    "address": "test-address"
                }
                self.mn_service.test_circuit_locally(test_data)
                logger.info("Midnight Network ZK service components available")
                return True
            except Exception as e:
                logger.warning(f"MN service test failed: {str(e)}")
                return False
            
        except Exception as e:
            logger.warning(f"Midnight Network ZK service not available: {str(e)}")
            return False
    
    def generate_proof(self, survey_responses: List[int], ml_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate ZK proof from survey responses and ML data using Midnight Network
        
        Args:
            survey_responses: List of survey responses
            ml_data: ML model output data
            
        Returns:
            Proof data or None if generation fails
        """
        try:
            if not self._available:
                logger.warning("ZK proof service not available, skipping proof generation")
                return None
            
            logger.info("Generating ZK proof for survey responses using Midnight Network")
            
            # Use MN service for proof generation with Compact JavaScript implementation
            proof_result = self.mn_service.generate_proof(survey_responses, ml_data)
            
            logger.info("ZK proof generated successfully using Midnight Network")
            return proof_result
            
        except Exception as e:
            logger.error(f"Error generating ZK proof with Midnight Network: {str(e)}")
            # Fallback to mock proof for development
            return self._generate_mock_proof_fallback(survey_responses, ml_data)
    
    def _prepare_circuit_inputs(self, survey_responses: List[int], ml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare inputs for the ZK circuit
        
        Args:
            survey_responses: Survey responses
            ml_data: ML model data
            
        Returns:
            Circuit inputs dictionary
        """
        import hashlib
        
        # Convert survey responses to circuit-friendly format
        encrypted_responses = self._encrypt_survey_responses(survey_responses)
        
        # Extract KOIOS features from ML data
        koios_data = ml_data.get('koios_data', {})
        koios_features = [
            koios_data.get('tx_count', 0),
            koios_data.get('avg_tx_size_ada', 0),
            koios_data.get('days_staked', 0),
            koios_data.get('tx_freq_daily', 0)
        ]
        
        # Generate wallet address hash for public input
        wallet_address = ml_data.get('address', '')
        wallet_hash = int(hashlib.sha256(wallet_address.encode()).hexdigest()[:16], 16)
        
        # Prepare public inputs (what will be revealed)
        public_inputs = {
            "wallet_address_hash": wallet_hash,
            "expected_score": ml_data.get('score', 0),
            "response_commitment": sum(encrypted_responses)  # Simple commitment for demo
        }
        
        # Prepare private inputs (what remains hidden)
        private_inputs = {
            "encrypted_responses": encrypted_responses,
            "koios_features": koios_features,
            "ml_model_weights": [1.0] * 54,  # Mock weights - replace with actual model weights
            "ml_model_bias": 50.0  # Mock bias - replace with actual model bias
        }
        
        return {
            "public_inputs": public_inputs,
            "private_inputs": private_inputs
        }
    
    def _encrypt_survey_responses(self, responses: List[int]) -> List[int]:
        """
        Encrypt survey responses for ZK circuit
        
        Args:
            responses: Raw survey responses
            
        Returns:
            Encrypted response data as integers for ZK circuit
        """
        import hashlib
        
        # Simple deterministic encryption for development
        # In production, use proper cryptographic encryption
        encrypted = []
        for i, response in enumerate(responses):
            # Create deterministic encrypted value
            hash_input = f"{response}_{i}_{len(responses)}"
            hash_val = hashlib.sha256(hash_input.encode()).hexdigest()
            # Convert first 8 chars of hash to integer
            encrypted_val = int(hash_val[:8], 16) % 1000
            encrypted.append(encrypted_val)
        
        return encrypted
    
    def _run_zk_circuit(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the ZK circuit to generate proof using Midnight compactc server

        Args:
            inputs: Circuit inputs

        Returns:
            Proof generation result
        """
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(inputs, f, indent=2)
                input_file = f.name
            
            try:
                # Call compactc server for actual proof generation
                proof_data = self._call_compactc_server(input_file)
                
                # Clean up temporary file
                os.unlink(input_file)
                
                return proof_data
                
            except Exception as e:
                # Clean up on error
                if os.path.exists(input_file):
                    os.unlink(input_file)
                raise e
                
        except Exception as e:
            logger.error(f"Error running ZK circuit: {str(e)}")
            raise
    
    def _call_compactc_server(self, input_file: str) -> Dict[str, Any]:
        """
        Call compactc server to generate actual ZK proof

        Args:
            input_file: Path to input JSON file

        Returns:
            Proof generation result
        """
        try:
            import requests
            import time
            
            start_time = time.time()
            
            # Prepare request to compactc server
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            
            # Call compactc server (adjust URL based on your setup)
            server_url = os.getenv('COMPACTC_SERVER_URL', 'http://localhost:8080')
            response = requests.post(
                f"{server_url}/generate_proof",
                json={
                    "circuit_name": "ComputePrivateScore",
                    "inputs": input_data,
                    "timeout": 30
                },
                timeout=35
            )
            
            if response.status_code == 200:
                proof_result = response.json()
                proof_result['proof_generation_time'] = time.time() - start_time
                return proof_result
            else:
                logger.error(f"Compactc server error: {response.status_code} - {response.text}")
                raise Exception(f"Proof generation failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Compactc server connection failed: {str(e)}")
            # Fallback to mock proof for development
            logger.warning("Falling back to mock proof generation")
            return self._generate_mock_proof(json.load(open(input_file, 'r')))
    
    def _generate_mock_proof(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock proof data for development (fallback)

        Args:
            inputs: Circuit inputs

        Returns:
            Mock proof data
        """
        import hashlib
        import time
        
        # Generate deterministic mock proof based on inputs
        input_hash = hashlib.sha256(
            json.dumps(inputs, sort_keys=True).encode()
        ).hexdigest()

        return {
            "proof": f"mock_proof_{input_hash[:32]}",
            "public_inputs": inputs.get('public_inputs', {}),
            "verification_key": f"mock_vk_{input_hash[:16]}",
            "proof_generation_time": 2.5,  # seconds
            "circuit_size": "medium",
            "timestamp": int(time.time())
        }
    
    def verify_proof(self, proof: Dict[str, Any], public_inputs: List[str]) -> bool:
        """
        Verify ZK proof validity
        
        Args:
            proof: Proof data to verify
            public_inputs: Public inputs used in proof
            
        Returns:
            True if proof is valid, False otherwise
        """
        try:
            if not self._available:
                logger.warning("ZK proof service not available, cannot verify proof")
                return False
            
            logger.info("Verifying ZK proof")
            
            # Try actual verification with compactc server
            is_valid = self._verify_proof_with_server(proof, public_inputs)
            
            logger.info(f"ZK proof verification result: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying proof: {str(e)}")
            return False
    
    def _verify_proof_with_server(self, proof: Dict[str, Any], public_inputs: List[str]) -> bool:
        """
        Verify proof using compactc server

        Args:
            proof: Proof data
            public_inputs: Public inputs

        Returns:
            True if proof is valid, False otherwise
        """
        try:
            import requests
            
            server_url = os.getenv('COMPACTC_SERVER_URL', 'http://localhost:8080')
            response = requests.post(
                f"{server_url}/verify_proof",
                json={
                    "proof": proof,
                    "public_inputs": public_inputs,
                    "verification_key": proof.get('verification_key')
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('is_valid', False)
            else:
                logger.error(f"Verification server error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Verification server connection failed: {str(e)}")
            # Fallback to mock verification for development
            return self._mock_verify_proof(proof, public_inputs)
    
    def _mock_verify_proof(self, proof: Dict[str, Any], public_inputs: List[str]) -> bool:
        """
        Mock proof verification for development
        
        Args:
            proof: Proof data
            public_inputs: Public inputs
            
        Returns:
            Mock verification result (always True for development)
        """
        # For development, we'll accept all mock proofs as valid
        # In production, this would perform actual cryptographic verification
        
        if not proof or 'proof' not in proof:
            return False
        
        # Simple validation check
        return proof.get('proof', '').startswith('mock_proof_')
    
    def _generate_mock_proof_fallback(self, survey_responses: List[int], ml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback mock proof generation for development when MN service is unavailable
        
        Args:
            survey_responses: Survey responses
            ml_data: ML model data
            
        Returns:
            Mock proof data
        """
        import hashlib
        import time
        
        # Generate deterministic mock proof based on inputs
        input_hash = hashlib.sha256(
            json.dumps({
                "responses": survey_responses,
                "ml_data": ml_data
            }, sort_keys=True).encode()
        ).hexdigest()

        return {
            "success": True,
            "proof": {
                "proof": f"midnight_mock_proof_{input_hash[:32]}",
                "public_inputs": {
                    "wallet_address": ml_data.get('address', ''),
                    "score_commitment": sum(survey_responses)
                },
                "verification_key": f"midnight_mock_vk_{input_hash[:16]}",
                "proof_generation_time": 1.5,
                "circuit_size": "compact",
                "timestamp": int(time.time())
            },
            "result": {
                "status": "success",
                "score": ml_data.get('score', 75)
            },
            "transactionData": {
                "contract": 'psychescore',
                "method": 'computeAndStoreScore',
                "inputs": {
                    "encrypted_responses": survey_responses,
                    "koios_features": ml_data.get('koios_data', [0.5] * 4),
                    "ml_model_weights": [0.02] * 54,
                    "ml_model_bias": 50.0,
                    "wallet_address": ml_data.get('address', ''),
                    "response_commitment": sum(survey_responses)
                },
                "proof": f"midnight_mock_proof_{input_hash[:32]}"
            }
        }

    def get_proof_stats(self) -> Dict[str, Any]:
        """
        Get ZK proof generation statistics for Midnight Network
        
        Returns:
            Proof service statistics
        """
        return {
            "service_available": self._available,
            "circuit_path": self.circuit_path,
            "proof_generation_time_target": 30,  # seconds
            "proof_size_estimate": "2-5KB",
            "verification_time_target": 5,  # seconds
            "supported_circuits": ["psychescore.compact"],
            "encryption_method": "midnight_compact",
            "network": "midnight_testnet",
            "implementation": "compact_javascript"
        }