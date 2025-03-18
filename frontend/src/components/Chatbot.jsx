import React, { useState, useEffect } from 'react';

function Chatbot() {
    const [selectedModel, setSelectedModel] = useState('ollama'); // Modello predefinito

    const sendModelChangeRequest = async (model) => {
        try {
            const response = await fetch('http://127.0.0.1:5000/set-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model })
            });
            const data = await response.json();
            //alert(data.message);
        } catch (error) {
            console.error("Error changing model:", error);
        }
    };

    const handleModelChange = (event) => {
        const model = event.target.value;
        setSelectedModel(model);
        sendModelChangeRequest(model);
    };
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

    useEffect(() => {
        try {
            const savedMessages = localStorage.getItem('chatMessages');
            if (savedMessages) {
                setMessages(JSON.parse(savedMessages));
            }
        } catch (error) {
            console.error("Failed to load messages from localStorage", error);
        }
    }, []);

    useEffect(() => {
        try {
            if (messages.length > 0) {
                localStorage.setItem('chatMessages', JSON.stringify(messages));
            }
        } catch (error) {
            console.error("Failed to save messages to localStorage", error);
        }
    }, [messages]);

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
            await handleUserResponse(input);
        } else {
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
            const messagesToAdd = [];

            if (data.message || data.feedback) {
                messagesToAdd.push({
                    sender: 'bot',
                    text: data.feedback || data.message,
                });
            }

            if (data.next_question) {
                messagesToAdd.push({
                    sender: 'bot',
                    text: data.next_question,
                });
                setIsWaitingForResponse(true);
            } else if (data.question) {
                messagesToAdd.push({
                    sender: 'bot',
                    text: data.question,
                });
                setIsWaitingForResponse(true);
            }

            // Associa l'immagine solo all'ultimo messaggio della lista, se esiste
            if (data.image && messagesToAdd.length > 0) {
                messagesToAdd[messagesToAdd.length - 1].image = data.image;
            }

            setMessages((prev) => [...prev, ...messagesToAdd]);

        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => [...prev, { sender: 'bot', text: 'Error communicating with server.' }]);
        }
    };

    const handleUserResponse = async (userResponse) => {
        await sendChatbotMessage(userResponse);
    };

    const handleRestartBackend = () => {
        fetch('http://127.0.0.1:5000/api/restart-backend', { method: 'POST' });
        setTimeout(() => {
            localStorage.removeItem('chatMessages');
            window.location.reload();
        }, 1);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="p-4 bg-white shadow">
                <label className="text-gray-700 font-bold">Select Model:</label>
                <select
                    value={selectedModel}
                    onChange={handleModelChange}
                    className="ml-2 p-2 border border-gray-300 rounded"
                >
                    <option value="ollama">Ollama (LLaMA 3)</option>
                    <option value="gpt">OpenAI GPT</option>
                    <option value="huggingface">HuggingFace</option>
                </select>
            </div>

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
                                className={`max-w-xs md:max-w-md lg:max-w-lg rounded-lg p-2 ${
                                    msg.sender === 'user'
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-300 text-black'
                                }`}
                            >
                                <p className="whitespace-pre-wrap">{msg.text}</p>
                                {msg.image && (
                                    <img
                                        src={msg.image}
                                        alt="Exercise"
                                        className="mt-2 rounded-lg max-w-full"
                                    />
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="p-4 border-t border-gray-300 bg-white flex space-x-2">
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
                <button
                    onClick={handleRestartBackend}
                    className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
                >
                    Restart
                </button>
            </div>
        </div>
    );
}

export default Chatbot;
