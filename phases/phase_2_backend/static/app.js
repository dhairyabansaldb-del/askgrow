document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const sendButton = document.getElementById('send-button');

    // Automatically focus the input field
    userInput.focus();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Add User Message
        appendMessage(text, 'user-message');
        userInput.value = '';
        
        // 2. Add Typing Indicator for Bot
        const typingId = appendTypingIndicator();
        
        // Disable input while waiting
        userInput.disabled = true;
        sendButton.disabled = true;

        try {
            // 3. Make API Call to FastAPI backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: text })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Remove Typing Indicator
            removeTypingIndicator(typingId);
            
            // 5. Append Bot Response
            appendBotResponse(data);
            
        } catch (error) {
            console.error("Error communicating with backend:", error);
            removeTypingIndicator(typingId);
            appendMessage("Sorry, I encountered an error connecting to the server. Please ensure the backend is running.", 'bot-message');
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = className === 'user-message' 
            ? '<i class="fa-solid fa-user"></i>' 
            : '<i class="fa-solid fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Simple text escaping to prevent XSS
        const escapedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        
        // Handle newlines
        const formattedText = escapedText.split('\n').map(p => `<p>${p}</p>`).join('');
        contentDiv.innerHTML = formattedText;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot-message`;
        messageDiv.id = id;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) {
            el.remove();
        }
    }

    function appendBotResponse(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format the main response text
        const escapedText = data.response.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const formattedText = escapedText.split('\n').filter(p => p.trim() !== '').map(p => `<p>${p}</p>`).join('');
        
        let finalHTML = formattedText;

        // Create the metadata block (filter used + citations)
        if (data.filter_used || (data.citations && data.citations.length > 0) || data.pii_blocked) {
            let metaHTML = '<div class="message-meta">';
            
            // Show PII block warning if applicable
            if (data.pii_blocked) {
                metaHTML += `<div class="filter-badge" style="color: #fca5a5; border-color: rgba(252,165,165,0.3);"><i class="fa-solid fa-shield-halved"></i> PII Blocked</div>`;
            }

            // Show filter used
            if (data.filter_used) {
                metaHTML += `<div class="filter-badge"><i class="fa-solid fa-filter"></i> Context: ${data.filter_used}</div>`;
            }
            
            // Show citations
            if (data.citations && data.citations.length > 0) {
                metaHTML += `<div class="citations-list"><strong>Sources:</strong>`;
                data.citations.forEach((url, i) => {
                    metaHTML += `<a href="${url}" target="_blank" class="citation-link" rel="noopener noreferrer"><i class="fa-solid fa-link"></i> Source ${i+1}</a>`;
                });
                metaHTML += `</div>`;
            }
            
            metaHTML += '</div>';
            finalHTML += metaHTML;
        }

        contentDiv.innerHTML = finalHTML;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
