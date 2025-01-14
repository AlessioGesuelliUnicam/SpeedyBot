import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ClockIcon, AcademicCapIcon, DeviceMobileIcon } from '@heroicons/react/outline';

const Home = () => {
    const navigate = useNavigate();

    const handleStart = () => {
        navigate('/chatbot');
    };

    return (
        <div className="container mx-auto px-6">
            {/* Header Section */}
            <header className="text-center py-20 bg-gradient-to-br from-green-400 to-green-600 text-white">
                <h1 className="text-5xl font-extrabold">
                    Welcome to <span className="text-yellow-300">SpeedyBot</span>
                </h1>
                <p className="text-lg mt-4">
                    Transform your language learning experience with our interactive platform.
                </p>
                <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
                    <button
                        className="bg-gray-800 text-white py-3 px-8 rounded-full font-semibold hover:bg-gray-900 hover:shadow-xl transition duration-300"
                        onClick={handleStart}
                    >
                        Start Now
                    </button>
                </div>
            </header>

            {/* About Section */}
            <section className="py-16">
                <h2 className="text-4xl font-bold text-gray-800 text-center">
                    Why Choose SpeedyBot?
                </h2>
                <p className="text-gray-600 text-center mt-4 max-w-2xl mx-auto">
                    SpeedyBot offers a simple and personalized way to learn technical Italian,
                    essential for safe and efficient railway operations.
                </p>
                <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 px-4">
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <ClockIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">24/7 Interactivity</h3>
                        <p className="text-gray-600 mt-2">
                            Study anytime with exercises and quizzes tailored to your needs.
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <AcademicCapIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">Technical Railway Italian</h3>
                        <p className="text-gray-600 mt-2">
                            Specific content for train operators working in technical and operational contexts.
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <DeviceMobileIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">User-Friendly Platform</h3>
                        <p className="text-gray-600 mt-2">
                            A simple-to-use interface designed to ensure fast learning.
                        </p>
                    </div>
                </div>
            </section>

            {/* Call to Action */}
            <section className="bg-gradient-to-t from-gray-100 to-white py-16 text-center">
                <h2 className="text-4xl font-bold text-gray-800">
                    Ready to Enhance Your Skills?
                </h2>
                <p className="text-gray-600 mt-4 max-w-xl mx-auto">
                    SpeedyBot is your ideal companion for learning technical Italian.
                    Simplify your learning process with our interactive platform.
                </p>
                <button
                    className="mt-6 bg-green-500 text-white py-3 px-8 rounded-full font-semibold hover:bg-green-600 hover:shadow-xl transition duration-300"
                    onClick={handleStart}
                >
                    Start Now
                </button>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-10">
                <div className="text-center">
                    <p className="text-gray-400">
                        &copy; {new Date().getFullYear()} SpeedyBot. All rights reserved.
                    </p>
                </div>
            </footer>
        </div>
    )
}

export default Home