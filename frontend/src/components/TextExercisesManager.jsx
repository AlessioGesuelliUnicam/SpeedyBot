import React, { useState, useEffect } from 'react';
import { TrashIcon, PlusCircleIcon } from '@heroicons/react/solid';
import Modal from 'react-modal';

function JsonExerciseEditor() {
    const [files, setFiles] = useState([]); // List of JSON files
    const [selectedFile, setSelectedFile] = useState(null); // Selected file name
    const [selectedExerciseName, setSelectedExerciseName] = useState(''); // Name of the exercise
    const [questions, setQuestions] = useState([]); // List of question-answer pairs
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false); // State for popup modal
    const [newQuestion, setNewQuestion] = useState('');
    const [newAnswer, setNewAnswer] = useState('');

    useEffect(() => {
        // Fetch the list of JSON files from the backend
        const fetchFiles = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/materials-text');
                const data = await response.json();
                const materials = data.materials.map((file) => ({
                    fileName: file.fileName,
                    exerciseName: formatExerciseName(Object.keys(file.exercises)[0]), // Format exercise name
                    rawExerciseName: Object.keys(file.exercises)[0], // Keep raw name for fetching data
                }));
                setFiles(materials);
            } catch (error) {
                console.error('Error fetching files:', error);
            }
        };

        fetchFiles();
    }, []);

    const formatExerciseName = (name) => {
        // Replace underscores with spaces and capitalize each word
        return name
            .replace(/_/g, ' ')
            .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
    };

    const handleFileSelect = async (fileName, rawExerciseName) => {
        try {
            setSelectedFile(fileName);
            setSelectedExerciseName(rawExerciseName);
            const response = await fetch(`http://127.0.0.1:5000/static/exercises/${fileName}`);
            const data = await response.json();
            setQuestions(data[rawExerciseName]); // Use raw name for data fetching
        } catch (error) {
            console.error('Error fetching file content:', error);
        }
    };

    const handleQuestionChange = (index, field, value) => {
        const updatedQuestions = [...questions];
        updatedQuestions[index][field] = value;
        setQuestions(updatedQuestions);
    };

    const handleDeleteQuestion = (index) => {
        const updatedQuestions = questions.filter((_, i) => i !== index);
        setQuestions(updatedQuestions);
    };

    const handleSave = async () => {
        try {
            const updatedData = {
                [selectedExerciseName]: questions, // Wrap the questions back into the JSON structure
            };
            const response = await fetch(`http://127.0.0.1:5000/api/materials-text/${selectedFile}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData, null, 2),
            });

            if (!response.ok) {
                throw new Error('Failed to save file');
            }

            setSuccessMessage('File saved successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error) {
            console.error('Error saving file:', error);
            setErrorMessage('Failed to save file.');
            setTimeout(() => setErrorMessage(''), 3000);
        }
    };

    const handleAddQuestion = async () => {
        const newEntry = { question: newQuestion, solution: newAnswer };
        const updatedQuestions = [...questions, newEntry];

        try {
            const updatedData = {
                [selectedExerciseName]: updatedQuestions, // Wrap the questions back into the JSON structure
            };
            const response = await fetch(`http://127.0.0.1:5000/api/materials-text/${selectedFile}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData, null, 2),
            });

            if (!response.ok) {
                throw new Error('Failed to add question');
            }

            setQuestions(updatedQuestions);
            setNewQuestion('');
            setNewAnswer('');
            setSuccessMessage('Question added successfully!');
            setIsModalOpen(false);
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error) {
            console.error('Error adding question:', error);
            setErrorMessage('Failed to add question.');
            setTimeout(() => setErrorMessage(''), 3000);
        }
    };

    return (
        <div className="p-4">
            <div className="mb-4">
                <h1 className="text-2xl font-bold">Text Exercise Editor</h1>
            </div>

            <div className="flex">
                {/* Sidebar with file list */}
                <div className="w-1/4 border-r p-2">
                    <h2 className="text-lg font-bold">Exercises</h2>
                    <ul>
                        {files.map((file, index) => (
                            <li
                                key={index}
                                className={`cursor-pointer p-2 ${
                                    selectedFile === file.fileName ? 'bg-blue-100' : ''
                                }`}
                                onClick={() => handleFileSelect(file.fileName, file.rawExerciseName)}
                            >
                                {file.exerciseName}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Editor area */}
                <div className="w-3/4 p-4">
                    {selectedFile ? (
                        <>
                            <h2 className="text-lg font-bold mb-2">Editing: {formatExerciseName(selectedExerciseName)}</h2>
                            {questions.map((q, index) => (
                                <div key={index} className="mb-4 border p-2 rounded flex items-center">
                                    <div className="flex-grow">
                                        <label className="block text-gray-700 font-bold">Question:</label>
                                        <input
                                            type="text"
                                            value={q.question}
                                            onChange={(e) => handleQuestionChange(index, 'question', e.target.value)}
                                            className="w-full border p-2 mb-2"
                                        />
                                        <label className="block text-gray-700 font-bold">Answer:</label>
                                        <input
                                            type="text"
                                            value={q.solution}
                                            onChange={(e) => handleQuestionChange(index, 'solution', e.target.value)}
                                            className="w-full border p-2"
                                        />
                                    </div>
                                    <button
                                        className="ml-4 bg-red-500 text-white p-2 rounded hover:bg-red-600 flex items-center"
                                        onClick={() => handleDeleteQuestion(index)}
                                    >
                                        <TrashIcon className="h-5 w-5 text-white" />
                                    </button>
                                </div>
                            ))}
                            <div className="mt-4 flex justify-between items-center">
                                <button
                                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                    onClick={handleSave}
                                >
                                    Save
                                </button>
                                <button
                                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 flex items-center"
                                    onClick={() => setIsModalOpen(true)}
                                >
                                    <PlusCircleIcon className="h-5 w-5 mr-2 text-white" /> Add Question
                                </button>
                            </div>
                            {successMessage && <p className="text-green-600 mt-2">{successMessage}</p>}
                            {errorMessage && <p className="text-red-600 mt-2">{errorMessage}</p>}
                        </>
                    ) : (
                        <p>Select an exercise to edit.</p>
                    )}
                </div>
            </div>

            {/* Modal for adding new question-answer pairs */}
            <Modal
                isOpen={isModalOpen}
                onRequestClose={() => setIsModalOpen(false)}
                contentLabel="Add New Question"
                className="bg-white p-6 rounded shadow-lg max-w-md mx-auto mt-20"
                overlayClassName="fixed inset-0 bg-black bg-opacity-50"
            >
                <h2 className="text-lg font-bold mb-4">Add New Question</h2>
                <label className="block text-gray-700 font-bold">Question:</label>
                <input
                    type="text"
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    className="w-full border p-2 mb-4"
                />
                <label className="block text-gray-700 font-bold">Answer:</label>
                <input
                    type="text"
                    value={newAnswer}
                    onChange={(e) => setNewAnswer(e.target.value)}
                    className="w-full border p-2 mb-4"
                />
                <div className="flex justify-end">
                    <button
                        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mr-2"
                        onClick={handleAddQuestion}
                    >
                        Add
                    </button>
                    <button
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                        onClick={() => setIsModalOpen(false)}
                    >
                        Cancel
                    </button>
                </div>
            </Modal>
        </div>
    );
}

export default JsonExerciseEditor;
