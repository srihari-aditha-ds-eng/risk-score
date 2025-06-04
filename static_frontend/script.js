async function generateScore() {
    const fileInput = document.getElementById('file-upload');
    const fileIdInput = document.getElementById('file-id');
    const scoreValue = document.getElementById('score-value');
    const riskIndicator = document.getElementById('risk-indicator');
    const riskyClauses = document.getElementById('risky-clauses');
    const clausesList = document.getElementById('clauses-list');

    // Show loading state
    scoreValue.textContent = 'Analyzing...';
    riskIndicator.style.left = '50%';
    riskyClauses.classList.add('hidden');
    clausesList.innerHTML = '';

    try {
        if (!fileInput.files.length) {
            throw new Error('Please select a file to analyze');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0], fileInput.files[0].name);

        console.log('Sending request to API...');
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: {
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit',
            body: formData
        }).catch(error => {
            console.error('Network error:', error);
            throw new Error(`Network error: ${error.message}. This might be a CORS issue. Please ensure the API server is running and CORS is enabled.`);
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', errorText);
            throw new Error(`API request failed: ${response.status} ${errorText}`);
        }

        const data = await response.json();
        console.log('Received data:', data);
        
        // Update score display
        scoreValue.textContent = `${data.risk_score}%`;
        
        // Update risk indicator position (0-100 to percentage)
        riskIndicator.style.left = `${data.risk_score}%`;
        
        // Display risky clauses if any
        if (data.risky_clauses && data.risky_clauses.length > 0) {
            riskyClauses.classList.remove('hidden');

            clausesList.innerHTML = data.risky_clauses.map((clauseString, index) => {
                // Split the clause string into clause text and explanation
                const parts = clauseString.split(' - ', 2); // Split only on the first ' - '
                const clauseText = parts[0].trim();
                const explanation = parts.length > 1 ? parts[1].trim() : 'No explanation provided.';

                // Use index + 1 for sequential numbering in the circle
                const sequentialNumber = index + 1;

                return `
                    <div class="p-4 bg-red-50 rounded-lg border border-red-200">
                        <div class="flex items-start">
                            <span class="flex-shrink-0 w-6 h-6 bg-red-100 text-red-800 rounded-full flex items-center justify-center font-medium mr-3">${sequentialNumber}</span>
                            <div>
                                <p class="text-red-800 font-medium mb-2">${clauseText}</p>
                                <p class="text-red-600 text-sm">${explanation}</p>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            riskyClauses.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error details:', error);
        scoreValue.textContent = 'Error: ' + error.message;
        riskIndicator.style.left = '50%';
        riskyClauses.classList.add('hidden');
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'mt-4 p-4 bg-red-100 text-red-700 rounded-lg';
        errorDiv.innerHTML = `
            <p class="font-medium">Error: ${error.message}</p>
            <p class="mt-2 text-sm">Troubleshooting steps:</p>
            <ul class="mt-1 text-sm list-disc list-inside">
                <li>Ensure the API server is running at http://localhost:8000</li>
                <li>Check if CORS is enabled on the API server</li>
                <li>Try opening this page through a local web server instead of directly from the file system</li>
            </ul>
        `;
        clausesList.parentElement.appendChild(errorDiv);
    }
} 