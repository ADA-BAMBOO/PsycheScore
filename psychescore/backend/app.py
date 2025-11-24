"""
Flask Backend API for PsycheScore
Orchestrates ML model, ZK proof generation, and blockchain submission
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import services
from services.ml_service import MLService
from services.zk_proof_service import ZKProofService
from services.blockchain_service import BlockchainService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize services
ml_service = MLService()
zk_service = ZKProofService()
blockchain_service = BlockchainService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/process_survey', methods=['POST'])
def process_survey():
    """
    Process 50-question survey and generate ML score
    Expected payload:
    {
        "wallet_address": "addr_test1...",
        "survey_responses": [1, 2, 3, ...],  # 50 responses
        "user_metadata": {
            "age": 25,
            "gender": "male",
            "education": "bachelor"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['wallet_address', 'survey_responses']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        wallet_address = data['wallet_address']
        survey_responses = data['survey_responses']
        user_metadata = data.get('user_metadata', {})
        
        # Validate survey responses
        if len(survey_responses) != 20:
            return jsonify({
                'error': 'Survey must contain exactly 20 responses'
            }), 400
        
        logger.info(f"Processing survey for wallet: {wallet_address}")
        
        # Step 1: Generate ML score
        ml_result = ml_service.generate_score(wallet_address, survey_responses, user_metadata)
        
        # Step 2: Generate ZK proof (if enabled)
        zk_result = None
        if zk_service.is_available():
            zk_result = zk_service.generate_proof(survey_responses, ml_result)
        
        return jsonify({
            'success': True,
            'wallet_address': wallet_address,
            'ml_score': ml_result['score'],
            'ml_data': ml_result,
            'zk_proof': zk_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing survey: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Failed to process survey: {str(e)}'
        }), 500

@app.route('/generate_zk_proof', methods=['POST'])
def generate_zk_proof():
    """
    Generate ZK proof from encrypted survey responses
    Expected payload:
    {
        "encrypted_responses": "encrypted_data_here",
        "ml_score": 75.5,
        "wallet_address": "addr_test1..."
    }
    """
    try:
        data = request.get_json()
        
        if not zk_service.is_available():
            return jsonify({
                'error': 'ZK proof service not available'
            }), 503
        
        encrypted_responses = data.get('encrypted_responses')
        ml_score = data.get('ml_score')
        wallet_address = data.get('wallet_address')
        
        proof_result = zk_service.generate_proof(encrypted_responses, {
            'score': ml_score,
            'wallet_address': wallet_address
        })
        
        return jsonify({
            'success': True,
            'proof': proof_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating ZK proof: {str(e)}")
        return jsonify({
            'error': f'Failed to generate ZK proof: {str(e)}'
        }), 500

@app.route('/verify_proof', methods=['POST'])
def verify_proof():
    """
    Verify ZK proof validity
    Expected payload:
    {
        "proof": "proof_data_here",
        "public_inputs": ["input1", "input2"]
    }
    """
    try:
        data = request.get_json()
        
        if not zk_service.is_available():
            return jsonify({
                'error': 'ZK proof service not available'
            }), 503
        
        proof = data.get('proof')
        public_inputs = data.get('public_inputs', [])
        
        verification_result = zk_service.verify_proof(proof, public_inputs)
        
        return jsonify({
            'success': True,
            'is_valid': verification_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error verifying proof: {str(e)}")
        return jsonify({
            'error': f'Failed to verify proof: {str(e)}'
        }), 500

@app.route('/submit_to_blockchain', methods=['POST'])
def submit_to_blockchain():
    """
    Submit verified score to Cardano blockchain
    Expected payload:
    {
        "wallet_address": "addr_test1...",
        "ml_score": 75.5,
        "zk_proof": "proof_data_here",  # Optional
        "oracle_data": {
            "score": 75.5,
            "timestamp": 1234567890,
            "oracle_vkey": "vkey_hex",
            "signature": "sig_hex"
        }
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['wallet_address', 'ml_score']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        wallet_address = data['wallet_address']
        ml_score = data['ml_score']
        zk_proof = data.get('zk_proof')
        oracle_data = data.get('oracle_data')
        
        logger.info(f"Submitting to blockchain for wallet: {wallet_address}")
        
        # Submit to blockchain
        tx_result = blockchain_service.submit_score(
            wallet_address=wallet_address,
            score=ml_score,
            zk_proof=zk_proof,
            oracle_data=oracle_data
        )
        
        return jsonify({
            'success': True,
            'transaction': tx_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error submitting to blockchain: {str(e)}")
        return jsonify({
            'error': f'Failed to submit to blockchain: {str(e)}'
        }), 500

@app.route('/get_score', methods=['GET'])
def get_score():
    """
    Get score for a wallet address from blockchain
    Query parameter: wallet_address
    """
    try:
        wallet_address = request.args.get('wallet_address')
        
        if not wallet_address:
            return jsonify({
                'error': 'Missing wallet_address parameter'
            }), 400
        
        score_data = blockchain_service.get_score(wallet_address)
        
        return jsonify({
            'success': True,
            'wallet_address': wallet_address,
            'score': score_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting score: {str(e)}")
        return jsonify({
            'error': f'Failed to get score: {str(e)}'
        }), 500

@app.route('/verify_blockchain_submission', methods=['GET'])
def verify_blockchain_submission():
    """
    Verify blockchain submission for a wallet address
    Query parameter: wallet_address
    """
    try:
        wallet_address = request.args.get('wallet_address')
        
        if not wallet_address:
            return jsonify({
                'error': 'Missing wallet_address parameter'
            }), 400
        
        # Get score from blockchain
        score_data = blockchain_service.get_score(wallet_address)
        
        if score_data:
            return jsonify({
                'success': True,
                'verified': True,
                'wallet_address': wallet_address,
                'score_data': score_data,
                'message': 'Score successfully verified on Midnight Network blockchain',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'verified': False,
                'wallet_address': wallet_address,
                'message': 'No score found on Midnight Network blockchain for this wallet address',
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error verifying blockchain submission: {str(e)}")
        return jsonify({
            'error': f'Failed to verify blockchain submission: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )