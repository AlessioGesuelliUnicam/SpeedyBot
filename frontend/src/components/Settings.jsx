import React, { useState, useEffect } from 'react';

function Settings() {
    const [settings, setSettings] = useState({
        OPENAI_API_KEY: '',
        OPENAI_MODEL: '',
        OLLAMA_BASE_URL: '',
        OLLAMA_MODEL: '',
        HUGGINGFACE_API_TOKEN: '',
        HUGGINGFACE_MODEL: '',
        AZURE_OPENAI_API_KEY: '',
        AZURE_RESOURCE_NAME: '',
        AZURE_DEPLOYMENT_NAME: ''
    });

    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/settings')
            .then(response => response.json())
            .then(data => {
                setSettings(data);
                setIsLoading(false);
            })
            .catch(error => {
                console.error('Error fetching settings:', error);
                setIsLoading(false);
                setMessage('Error loading settings.');
            });
    }, []);

    const handleChange = (e) => {
        setSettings({ ...settings, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage('');

        fetch('http://127.0.0.1:5000/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings),
        })
            .then(response => response.json())
            .then(data => {
                setMessage('Settings updated successfully!');
                setIsSaving(false);
            })
            .catch(error => {
                console.error('Error updating settings:', error);
                setMessage('Failed to update settings.');
                setIsSaving(false);
            });
    };

    if (isLoading) {
        return <div className="p-4 text-gray-600">Loading settings...</div>;
    }

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Settings</h2>

            {message && (
                <div className={`mb-4 p-2 text-white rounded ${message.includes('successfully') ? 'bg-green-500' : 'bg-red-500'}`}>
                    {message}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                {/* OpenAI Settings */}
                <div>
                    <label className="block font-semibold">OpenAI API Key:</label>
                    <input
                        type="text"
                        name="OPENAI_API_KEY"
                        value={settings.OPENAI_API_KEY}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">OpenAI Model:</label>
                    <input
                        type="text"
                        name="OPENAI_MODEL"
                        value={settings.OPENAI_MODEL}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>

                {/* Ollama Settings */}
                <div>
                    <label className="block font-semibold">Ollama Base URL:</label>
                    <input
                        type="text"
                        name="OLLAMA_BASE_URL"
                        value={settings.OLLAMA_BASE_URL}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">Ollama Model:</label>
                    <input
                        type="text"
                        name="OLLAMA_MODEL"
                        value={settings.OLLAMA_MODEL}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>

                {/* Hugging Face Settings */}
                <div>
                    <label className="block font-semibold">Hugging Face API Token:</label>
                    <input
                        type="text"
                        name="HUGGINGFACE_API_TOKEN"
                        value={settings.HUGGINGFACE_API_TOKEN}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">Hugging Face Model:</label>
                    <input
                        type="text"
                        name="HUGGINGFACE_MODEL"
                        value={settings.HUGGINGFACE_MODEL}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">Azure API Key</label>
                    <input
                        type="text"
                        name="AZURE_OPENAI_API_KEY"
                        value={settings.AZURE_OPENAI_API_KEY}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">Azure Resource Name</label>
                    <input
                        type="text"
                        name="AZURE_RESOURCE_NAME"
                        value={settings.AZURE_RESOURCE_NAME}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>
                <div>
                    <label className="block font-semibold">Azure Deployment Name</label>
                    <input
                        type="text"
                        name="AZURE_DEPLOYMENT_NAME"
                        value={settings.AZURE_DEPLOYMENT_NAME}
                        onChange={handleChange}
                        className="w-full border p-2"
                    />
                </div>

                <button
                    type="submit"
                    disabled={isSaving}
                    className={`px-4 py-2 rounded text-white ${isSaving ? 'bg-gray-500 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'}`}
                >
                    {isSaving ? 'Saving...' : 'Save Settings'}
                </button>
            </form>
        </div>
    );
}

export default Settings;