import subprocess
import json
import os
import logging

logger = logging.getLogger(__name__)

class MNService:
    def __init__(self):
        # Get the absolute path to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        self.mn_app_path = os.path.join(project_root, 'psychescore-mn')
        self.proof_server_url = "http://localhost:6300"
    
    def generate_proof(self, survey_data, ml_data):
        """Call MN app TypeScript service to generate proof using Compact JavaScript implementation"""
        # Prepare input data for JavaScript implementation
        input_data = {
            "survey_responses": survey_data,
            "ml_weights": ml_data['weights'],
            "koios_features": ml_data['koios_data'],
            "wallet_address": ml_data['address'],
            "proof_server_url": self.proof_server_url  # Local proof server
        }
        
        # Call MN app service that uses the generated JavaScript implementation
        try:
            result = subprocess.run([
                'node', 'src/generateProof.js',
                json.dumps(input_data)
            ], cwd=self.mn_app_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Proof generation failed: {result.stderr}")
                raise Exception(f"Proof generation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error calling MN service: {e}")
            raise
    
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
        try:
            result = subprocess.run(['node', '-e', test_script],
                                  cwd=self.mn_app_path,
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Local circuit test failed: {result.stderr}")
                raise Exception(f"Local circuit test failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error testing circuit locally: {e}")
            raise
    
    def compile_contract(self):
        """Compile the Compact contract and generate JavaScript implementation"""
        compile_script = """
        const {{ execSync }} = require('child_process');
        try {{
            execSync('compact compile contracts/psychescore.compact contracts/managed/psychescore', {{
                stdio: 'inherit',
                cwd: process.cwd()
            }});
            console.log('{{"status": "success", "message": "Contract compiled successfully"}}');
        }} catch (error) {{
            console.log('{{"status": "error", "message": "' + error.message + '"}}');
        }}
        """
        
        try:
            result = subprocess.run(['node', '-e', compile_script],
                                  cwd=self.mn_app_path,
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Contract compilation failed: {result.stderr}")
                raise Exception(f"Contract compilation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error compiling contract: {e}")
            raise