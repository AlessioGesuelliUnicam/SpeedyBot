import React, { useState, useEffect } from 'react';

function CreateExerciseType() {
    const [exerciseType, setExerciseType] = useState('');
    const [exerciseWithImage, setExerciseWithImage] = useState(false);
    const [message, setMessage] = useState('');
    const [exercises, setExercises] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false); // Stato per il popup

    // Fetch existing exercises
    useEffect(() => {
        const fetchExercises = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/exercise-types');
                if (!response.ok) {
                    throw new Error('Failed to fetch exercises');
                }
                const data = await response.json();
                setExercises(data);
            } catch (error) {
                console.error('Error fetching exercises:', error);
            }
        };

        fetchExercises();
    }, []);

    // Handle creation of a new exercise
    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://127.0.0.1:5000/api/exercise-types', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    exerciseType,
                    exerciseWithImage,
                    // prompt is intentionally omitted as it will be used in the future
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                setMessage(`Error: ${errorData.error}`);
            } else {
                setMessage('Exercise created successfully!');
                setExerciseType(''); // Reset the fields
                setExerciseWithImage(false);
                setIsModalOpen(false); // Chiudi il popup

                // Refresh the list of exercises
                const updatedExercises = await fetch('http://127.0.0.1:5000/api/exercise-types');
                const data = await updatedExercises.json();
                setExercises(data);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('An error occurred. Please try again.');
        }
    };

    // Handle deletion of an exercise
    const handleDelete = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/exercise-types/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete exercise');
            }

            setMessage('Exercise deleted successfully!');
            // Refresh the list of exercises
            const updatedExercises = await fetch('http://127.0.0.1:5000/api/exercise-types');
            const data = await updatedExercises.json();
            setExercises(data);
        } catch (error) {
            console.error('Error deleting exercise:', error);
            setMessage('An error occurred while deleting the exercise.');
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            {/* Header con pulsante per aprire il popup */}
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800">Exercise Types</h1>
                <button
                    onClick={() => setIsModalOpen(true)} // Apre il popup
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    +
                </button>
            </div>

            {/* Modale per la creazione */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-8 rounded shadow-md max-w-md w-full relative">
                        <button
                            onClick={() => setIsModalOpen(false)} // Chiude il popup
                            className="absolute top-2 right-2 bg-gray-500 text-white rounded-full px-2 py-1 hover:bg-gray-600"
                        >
                            X
                        </button>
                        <h2 className="text-2xl font-bold mb-4">Create Exercise Type</h2>
                        {message && <div className="mb-4 p-2 bg-blue-100 text-blue-800 rounded">{message}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="mb-4">
                                <label className="block text-gray-700 font-bold mb-2">Exercise Type</label>
                                <input
                                    type="text"
                                    value={exerciseType}
                                    onChange={(e) => setExerciseType(e.target.value)}
                                    placeholder="Enter exercise type"
                                    className="w-full border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Prompt field is hidden for now and will be implemented in the future */}
                            {/* <div className="mb-4">
                                <label className="block text-gray-700 font-bold mb-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Enter prompt"
                                    className="w-full border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                ></textarea>
                            </div> */}

                            <div className="mb-4">
                                <label className="flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={exerciseWithImage}
                                        onChange={(e) => setExerciseWithImage(e.target.checked)}
                                        className="mr-2"
                                    />
                                    Exercise with Image
                                </label>
                            </div>
                            <button
                                type="submit"
                                className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Create
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Lista degli esercizi */}
            <div className="bg-white p-8 rounded shadow-md mt-8">
                <h2 className="text-2xl font-bold mb-4">Existing Exercises</h2>
                {exercises.length === 0 ? (
                    <p className="text-gray-500">No exercises available.</p>
                ) : (
                    <ul>
                        {exercises.map((exercise) => (
                            <li
                                key={exercise.id}
                                className="flex justify-between items-center mb-4 border-b pb-2"
                            >
                                <div>
                                    <p className="font-bold text-gray-700">{exercise.exerciseType}</p>
                                    <p className="text-sm text-gray-500">
                                        {exercise.exerciseWithImage ? 'With Images' : 'No Images'}
                                    </p>
                                </div>
                                <button
                                    onClick={() => handleDelete(exercise.id)}
                                    className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                                >
                                    Delete
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default CreateExerciseType;