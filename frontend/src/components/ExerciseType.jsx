import React, { useState } from 'react'

function CreateExerciseType() {
    const [exerciseType, setExerciseType] = useState('')
    const [exerciseWithImage, setExerciseWithImage] = useState(false)
    const [message, setMessage] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()

        try {
            const response = await fetch('http://127.0.0.1:5000/api/exercise-types-with-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    exerciseType,
                    exerciseWithImage,
                    // prompt is intentionally omitted as it will be used in the future
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                setMessage(`Error: ${errorData.error}`)
            } else {
                setMessage('ExerciseType created successfully!')
                setExerciseType('') // Reset the fields
                setExerciseWithImage(false)
            }
        } catch (error) {
            console.error('Error:', error)
            setMessage('An error occurred. Please try again.')
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
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
    )
}

export default CreateExerciseType