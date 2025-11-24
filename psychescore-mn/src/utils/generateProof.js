// Proof generation script using Compact JavaScript implementation
import { Contract, State } from './contracts/managed/psychescore/index.cjs';

async function generateProof(inputData) {
    try {
        // Initialize contract with witness object
        const contract = new Contract({
            localSecretKey: () => Buffer.from('test-key', 'hex')
        });

        // Prepare survey data for circuit
        const surveyData = {
            encrypted_responses: inputData.survey_responses,
            koios_features: inputData.koios_features,
            ml_model_weights: inputData.ml_weights,
            ml_model_bias: 50, // Default bias
            wallet_address: inputData.wallet_address,
            response_commitment: calculateCommitment(inputData.survey_responses)
        };

        // Create execution context
        const context = {
            originalState: { status: State.VACANT },
            transactionContext: { timestamp: Date.now() }
        };

        // Generate proof using Compact JavaScript implementation
        const { result, proofData } = contract.circuits.computeAndStoreScore(context, surveyData);

        // Return proof data for submission to Midnight network
        return {
            success: true,
            proof: proofData,
            result: result,
            transactionData: {
                contract: 'psychescore',
                method: 'computeAndStoreScore',
                inputs: surveyData,
                proof: proofData.proof
            }
        };

    } catch (error) {
        console.error('Proof generation failed:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

function calculateCommitment(responses) {
    // Simple commitment calculation - in production use cryptographic hash
    return responses.reduce((sum, response) => sum + response, 0);
}

// Main execution
if (process.argv.length > 2) {
    const inputData = JSON.parse(process.argv[2]);
    generateProof(inputData).then(result => {
        console.log(JSON.stringify(result, null, 2));
    }).catch(error => {
        console.error(JSON.stringify({
            success: false,
            error: error.message
        }));
    });
}

export { generateProof };