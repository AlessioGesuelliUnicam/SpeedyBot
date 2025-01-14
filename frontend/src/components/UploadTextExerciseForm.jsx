import React, { useState, useEffect } from 'react';

function UploadTextExerciseForm() {
    const [exerciseTypeId, setExerciseTypeId] = useState('');
    const [exerciseOptions, setExerciseOptions] = useState([]); // List of exercise types
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        // Fetch exercise types with exerciseWithImage=False from the API
        const fetchExerciseTypes = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/exercise-types-no-image'); // Specific endpoint
                const data = await response.json();
                setExerciseOptions(data);
            } catch (error) {
                console.error('Error fetching exercise types:', error);
            }
        };

        fetchExerciseTypes();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const payload = {
            exercise_type_id: exerciseTypeId,
            question,
            answer,
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/upload-text-exercise', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            console.log('Success:', data);

            setExerciseTypeId('')
            setQuestion('')
            setAnswer('')
            setSuccessMessage('Text exercise added successfully!');

            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    return (
        <form className="p-4" onSubmit={handleSubmit}>
            <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Exercise Type:</label>
                <select
                    value={exerciseTypeId}
                    onChange={(e) => setExerciseTypeId(e.target.value)}
                    className="w-full border border-gray-300 p-2"
                >
                    <option value="">Select an exercise type</option>
                    {exerciseOptions.map((option) => (
                        <option key={option.id} value={option.id}>
                            {option.exerciseType}
                        </option>
                    ))}
                </select>
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Question:</label>
                <input
                    type="text"
                    placeholder="Enter question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="w-full border border-gray-300 p-2"
                />
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Answer:</label>
                <input
                    type="text"
                    placeholder="Enter answer"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    className="w-full border border-gray-300 p-2"
                />
            </div>

            {successMessage && (
                <div className="mb-4 text-green-600 font-semibold">
                    {successMessage}
                </div>
            )}

            <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
                Upload
            </button>
        </form>
    )
}

export default UploadTextExerciseForm