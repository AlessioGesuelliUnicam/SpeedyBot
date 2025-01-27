import React, { useState, useEffect } from 'react';

function TextualMaterialsManager() {
    const [materials, setMaterials] = useState([]);
    const [file, setFile] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        // Fetch textual materials
        const fetchMaterials = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/materials-text');
                if (!response.ok) {
                    throw new Error('Failed to fetch materials');
                }
                const data = await response.json();
                setMaterials(data.materials);
            } catch (err) {
                console.error(err);
                setError('Error loading materials');
            }
        };

        fetchMaterials();
    }, []);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
    };

    const handleUpload = async (e) => {
        e.preventDefault();

        if (!file) {
            setError('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/materials-text', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload file');
            }

            const data = await response.json();
            console.log('Success:', data);

            setFile(null);
            setSuccessMessage('File uploaded successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);

            // Ricarica i materiali
            const updatedMaterials = await fetch('http://127.0.0.1:5000/api/materials-text');
            const updatedData = await updatedMaterials.json();
            setMaterials(updatedData.materials);
        } catch (err) {
            console.error(err);
            setError('Error uploading file');
        }
    };

    const handleDelete = async (fileName) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/materials-text/${fileName}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete material');
            }

            const data = await response.json();
            console.log('Success:', data);

            setSuccessMessage('File deleted successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);

            // Ricarica i materiali
            setMaterials((prev) => prev.filter((material) => material.fileName !== fileName));
        } catch (err) {
            console.error(err);
            setError('Error deleting material');
        }
    };

    return (
        <div className="p-4 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold mb-4 text-blue-600">Manage Textual Materials</h1>
            {error && <p className="text-red-500">{error}</p>}
            {successMessage && <p className="text-green-500">{successMessage}</p>}

            <form onSubmit={handleUpload} className="mb-8">
                <input
                    type="file"
                    accept=".json"
                    onChange={handleFileChange}
                    className="mb-4 block w-full"
                />
                <button
                    type="submit"
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    Upload
                </button>
            </form>

            <div className="grid grid-cols-1 gap-6">
                {materials.map((material) => (
                    <div key={material.fileName} className="bg-white shadow rounded-lg p-4">
                        <h2 className="text-xl font-semibold text-gray-800">{material.fileName}</h2>
                        <ul className="list-disc pl-5">
                            {material.exercises.map((exercise, index) => (
                                <li key={index} className="text-gray-700">
                                    <strong>Question:</strong> {exercise.question} <br />
                                    <strong>Answer:</strong> {exercise.answer}
                                </li>
                            ))}
                        </ul>
                        <button
                            onClick={() => handleDelete(material.fileName)}
                            className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                        >
                            Delete File
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default TextualMaterialsManager;