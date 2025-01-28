import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { TrashIcon } from '@heroicons/react/solid'; // Importa l'icona TrashIcon

function MaterialsWithImagesManager() {
    const [materials, setMaterials] = useState([]);
    const [file, setFile] = useState(null);
    const [descriptionIt, setDescriptionIt] = useState('');
    const [descriptionEn, setDescriptionEn] = useState('');
    const [preview, setPreview] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedExerciseId, setSelectedExerciseId] = useState(null);

    useEffect(() => {
        const fetchMaterials = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/materials-with-images');
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

    const onDrop = (acceptedFiles) => {
        const selectedFile = acceptedFiles[0];
        setFile(selectedFile);
        setPreview(URL.createObjectURL(selectedFile)); // Genera un'anteprima
    };

    const handleDelete = async (materialId) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/materials/${materialId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete material');
            }

            setMaterials((prev) =>
                prev.map((group) => ({
                    ...group,
                    materials: group.materials.filter((material) => material.id !== materialId),
                }))
            );

            setSuccessMessage('Material deleted successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            console.error(err);
            setError('Error deleting material');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file || !selectedExerciseId || !descriptionIt || !descriptionEn) {
            setError('All fields are required');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('exercise_type', selectedExerciseId);
        formData.append('description_it', descriptionIt);
        formData.append('description_en', descriptionEn);

        try {
            const response = await fetch('http://127.0.0.1:5000/upload-image-exercise', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const updatedMaterials = await fetch('http://127.0.0.1:5000/api/materials-with-images');
            const updatedData = await updatedMaterials.json();
            setMaterials(updatedData.materials);

            setFile(null);
            setDescriptionIt('');
            setDescriptionEn('');
            setPreview(null);
            setIsModalOpen(false);

            setSuccessMessage('File uploaded successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            console.error(err);
            setError('Error uploading file');
        }
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: 'image/*',
    });

    return (
        <div className="p-4 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold mb-4 text-blue-600">Manage Materials with Images</h1>
            {error && <p className="text-red-500">{error}</p>}
            {successMessage && <p className="text-green-500">{successMessage}</p>}

            <div className="grid grid-cols-1 gap-6">
                {materials.map((group, index) => (
                    <div key={index} className="bg-white shadow rounded-lg p-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-semibold text-gray-800">{group.exerciseType}</h2>
                            <button
                                onClick={() => {
                                    setSelectedExerciseId(group.id);
                                    setIsModalOpen(true);
                                }}
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                +
                            </button>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mt-4">
                            {group.materials.map((material) => (
                                <div
                                    key={material.id}
                                    className="relative border p-2 rounded-lg shadow-md text-center bg-gray-50 w-[215px] h-[260px]"
                                >
                                    <img
                                        src={material.filePath}
                                        alt={material.descriptionEn}
                                        className="w-48 h-48 object-cover rounded mb-2"
                                    />
                                    <p className="font-semibold text-gray-700">{material.descriptionIt}</p>
                                    <p className="text-sm text-gray-500">{material.descriptionEn}</p>
                                    <button
                                        onClick={() => handleDelete(material.id)}
                                        className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
                                    >
                                        <TrashIcon className="h-5 w-5" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4">
                            Upload Image for Exercise ID {selectedExerciseId}
                        </h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div {...getRootProps()} className="border-2 border-dashed border-gray-400 p-6 text-center cursor-pointer">
                                <input {...getInputProps()} />
                                {!file ? (
                                    <p>Drag and drop an image here, or click to select one</p>
                                ) : (
                                    <p>{file.name}</p>
                                )}
                            </div>
                            {preview && <img src={preview} alt="Preview" className="w-48 h-48 object-cover rounded mx-auto" />}
                            <input
                                type="text"
                                value={descriptionIt}
                                onChange={(e) => setDescriptionIt(e.target.value)}
                                placeholder="Description in Italian"
                                className="w-full p-2 border rounded"
                            />
                            <input
                                type="text"
                                value={descriptionEn}
                                onChange={(e) => setDescriptionEn(e.target.value)}
                                placeholder="Description in English"
                                className="w-full p-2 border rounded"
                            />
                            <div className="flex justify-end space-x-2">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                >
                                    Upload
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MaterialsWithImagesManager;