import React, { useState, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'

function UploadImageExerciseForm() {
    const [file, setFile] = useState(null)
    const [exerciseType, setExerciseType] = useState('')
    const [exerciseOptions, setExerciseOptions] = useState([]); // List of exercise types
    const [descriptionIt, setDescriptionIt] = useState('')
    const [descriptionEn, setDescriptionEn] = useState('')
    const [preview, setPreview] = useState(null)
    const [successMessage, setSuccessMessage] = useState('')

    useEffect(() => {
        // Fetch exercise types from the API
        const fetchExerciseTypes = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/exercise-types-with-image')
                const data = await response.json()
                setExerciseOptions(data)
            } catch (error) {
                console.error('Error fetching exercise types:', error)
            }
        }

        fetchExerciseTypes()
    }, [])

    const onDrop = (acceptedFiles) => {
        const selectedFile = acceptedFiles[0]
        setFile(selectedFile)
        setPreview(URL.createObjectURL(selectedFile))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!file) {
            return
        }

        const formData = new FormData()
        formData.append('file', file)
        formData.append('exercise_type', exerciseType)
        formData.append('description_it', descriptionIt)
        formData.append('description_en', descriptionEn)

        try {
            const response = await fetch('http://127.0.0.1:5000/upload-image-exercise', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed')
            }

            const data = await response.json()
            console.log('Success:', data)

            setFile(null);
            setExerciseType('')
            setDescriptionIt('')
            setDescriptionEn('')
            setPreview(null)
            setSuccessMessage('File uploaded successfully!')

            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: 'image/*',
    })

    return (
        <form className="p-4" onSubmit={handleSubmit}>
            <div {...getRootProps()} className="mb-4 border-2 border-dashed border-gray-400 p-6 text-center cursor-pointer">
                <input {...getInputProps()} />
                {!file ? (
                    <p>Drag and drop an image here, or click to select one</p>
                ) : (
                    <p>{file.name}</p>
                )}
            </div>

            {preview && (
                <div className="mb-4">
                    <img src={preview} alt="Preview" className="max-w-full h-auto" />
                </div>
            )}

            <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Exercise Type:</label>
                <select
                    value={exerciseType}
                    onChange={(e) => setExerciseType(e.target.value)}
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
                <label className="block text-gray-700 font-bold mb-2">Description in Italian:</label>
                <input
                    type="text"
                    placeholder="Description in Italian"
                    value={descriptionIt}
                    onChange={(e) => setDescriptionIt(e.target.value)}
                    className="w-full border border-gray-300 p-2"
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Description in German:</label>
                <input
                    type="text"
                    placeholder="Description in German"
                    value={descriptionEn}
                    onChange={(e) => setDescriptionEn(e.target.value)}
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

export default UploadImageExerciseForm