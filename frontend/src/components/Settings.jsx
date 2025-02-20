import React, { useState, useEffect } from "react";

function Settings() {
    const [settings, setSettings] = useState({
        OPENAI_API_KEY: "",
        OPENAI_MODEL: "",
        OLLAMA_BASE_URL: "",
        OLLAMA_MODEL: ""
    });

    useEffect(() => {
        fetch("http://127.0.0.1:5000/api/settings")
            .then((response) => response.json())
            .then((data) => setSettings(data))
            .catch((error) => console.error("Error fetching settings:", error));
    }, []);

    const handleChange = (e) => {
        setSettings({ ...settings, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://127.0.0.1:5000/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settings),
            });
            if (response.ok) {
                alert("Settings updated successfully!");
            } else {
                alert("Failed to update settings.");
            }
        } catch (error) {
            console.error("Error updating settings:", error);
        }
    };

    return (
        <div className="p-4 max-w-lg mx-auto">
            <h2 className="text-2xl font-bold mb-4">API Settings</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                {Object.keys(settings).map((key) => (
                    <div key={key}>
                        <label className="block text-gray-700">{key}:</label>
                        <input
                            type="text"
                            name={key}
                            value={settings[key]}
                            onChange={handleChange}
                            className="w-full border border-gray-300 p-2 rounded"
                        />
                    </div>
                ))}
                <button
                    type="submit"
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    Save Settings
                </button>
            </form>
        </div>
    );
}

export default Settings;