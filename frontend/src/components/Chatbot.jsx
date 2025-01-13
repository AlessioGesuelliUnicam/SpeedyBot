import React, { useState } from 'react';

function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

    const fetchWithTimeout = (url, options, timeout = 60000) => {
        return Promise.race([
            fetch(url, options),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timed out')), timeout)
            )
        ]);
    };

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { sender: 'user', text: input };
        setMessages((prev) => [...prev, userMessage]);

        if (isWaitingForResponse) {
            // Invia la risposta dell'utente per la valutazione
            await handleUserResponse(input);
        } else {
            // Invia un messaggio normale al chatbot
            await sendChatbotMessage(input);
        }

        setInput('');
    };

    const sendChatbotMessage = async (message) => {
        try {
            const response = await fetchWithTimeout('http://127.0.0.1:5000/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch');
            }

            const data = await response.json();

            const botMessage = {
                sender: 'bot',
                text: data.message || '',
                image: data.image || null,
                question: data.question || null,
                feedback: data.feedback || null,
            };

            setMessages((prev) => [...prev, botMessage]);

            // Se c'è una domanda o immagine, attiva l'attesa della risposta dell'utente
            if (data.question || data.image) {
                setIsWaitingForResponse(true);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => [...prev, { sender: 'bot', text: 'Error communicating with server.' }]);
        }
    };

    const handleUserResponse = async (userResponse) => {
        try {
            const response = await fetchWithTimeout('http://127.0.0.1:5000/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ response: userResponse }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch');
            }

            const data = await response.json();

            const feedbackMessage = {
                sender: 'bot',
                text: data.feedback || 'No feedback received.',
            };

            setMessages((prev) => [...prev, feedbackMessage]);

            // Controlla se l'utente vuole cambiare esercizio
            if (userResponse.toLowerCase().includes('cambia esercizio')) {
                setIsWaitingForResponse(false);
                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: 'Ok! Dimmi quale esercizio vuoi fare.' },
                ]);
            } else {
                // Altrimenti, continua con l'esercizio corrente
                await continueExercise();
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => [...prev, { sender: 'bot', text: 'Error evaluating response.' }]);
        }
    };

    const continueExercise = async () => {
        try {
            const response = await fetchWithTimeout('http://127.0.0.1:5000/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: 'continua esercizio' }),
            });

            if (!response.ok) {
                console.error('Error: Failed to fetch response for continue exercise.');
                throw new Error('Failed to fetch');
            }

            const data = await response.json();
            console.log('Received data for continue exercise:', data); // LOG

            if (data.error) {
                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: `Errore: ${data.error}` },
                ]);
                setIsWaitingForResponse(false);
                return;
            }

            const botMessage = {
                sender: 'bot',
                text: data.message || '',
                image: data.image || null,
                question: data.question || null,
            };

            setMessages((prev) => [...prev, botMessage]);

            // Mantieni l'attesa della risposta se c'è una domanda o immagine
            if (data.question || data.image) {
                setIsWaitingForResponse(true);
            }
        } catch (error) {
            console.error('Error continuing exercise:', error); // LOG
            setMessages((prev) => [...prev, { sender: 'bot', text: 'Error continuing exercise.' }]);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="flex-grow p-4 overflow-y-auto">
                <div className="space-y-4">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`flex ${
                                msg.sender === 'user' ? 'justify-end' : 'justify-start'
                            }`}
                        >
                            <div
                                className={`max-w-xs rounded-lg p-2 ${
                                    msg.sender === 'user'
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-300 text-black'
                                }`}
                            >
                                <p>{msg.text}</p>
                                {/* Renderizza un'immagine se esiste */}
                                {msg.image && (
                                    <img
                                        src={msg.image}
                                        alt="Exercise"
                                        className="mt-2 rounded-lg max-w-full"
                                    />
                                )}
                                {/* Renderizza una domanda se esiste */}
                                {msg.question && (
                                    <p className="mt-2 font-semibold">{msg.question}</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="p-4 border-t border-gray-300 bg-white flex">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    className="flex-grow border border-gray-300 rounded-l-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSendMessage}
                    className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600"
                >
                    Send
                </button>
            </div>
        </div>
    );
}

export default Chatbot;