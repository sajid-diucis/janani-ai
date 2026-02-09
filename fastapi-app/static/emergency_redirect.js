
// Janani AI - Emergency Context Bridge (Hotfix)
// Intercepts Chat API responses to detect Emergency Action Tags and redirect to AR Dashboard
// Tags: [ACTION: NAVIGATE_AR_DASHBOARD:TYPE]

(function() {
    console.log("🛡️ Janani Emergency Bridge Active");

    const originalFetch = window.fetch;

    window.fetch = async function(...args) {
        const response = await originalFetch(...args);
        
        // Only intercept chat API calls
        if (args[0] && args[0].includes && (args[0].includes('/api/agent/chat') || args[0].includes('/api/chat/message'))) {
            try {
                // Clone response to read it without consuming the stream for the UI
                const clone = response.clone();
                const data = await clone.json();
                
                // Check for generic response field (depends on API structure)
                const text = data.response || data.text || JSON.stringify(data);
                
                // Regex to find action tags
                // Matches [ACTION: NAVIGATE_AR_DASHBOARD:BLEEDING] or [ACTION: NAVIGATE_AR_DASHBOARD]
                const match = text.match(/\[ACTION:\s*NAVIGATE_AR_DASHBOARD(?::(\w+))?\]/);
                
                if (match) {
                    const emergencyType = match[1] ? match[1].toLowerCase() : 'labor'; // Default to labor
                    console.log(`🚨 EMERGENCY DETECTED: ${emergencyType.toUpperCase()} - Redirecting...`);
                    
                    // Map generic types to specific scenario IDs if needed
                    const scenarioMap = {
                        'bleeding': 'bleeding',
                        'hemorrhage': 'bleeding',
                        'seizure': 'seizure',
                        'fit': 'seizure',
                        'eclampsia': 'seizure',
                        'labor': 'labor',
                        'delivery': 'labor',
                        'newborn': 'newborn',
                        'baby': 'newborn'
                    };
                    
                    const scenario = scenarioMap[emergencyType] || 'labor';
                    const userId = data.user_id || 'unknown_user';
                    
                    // Construct Smart URL
                    const targetUrl = `/api/ar-labor/dashboard?scenario=${scenario}&auto_start=true&user_id=${userId}`;
                    
                    // Redirect immediately
                    window.location.href = targetUrl;
                }
            } catch (e) {
                console.error("Emergency Bridge Error:", e);
            }
        }
        
        return response;
    };
})();
