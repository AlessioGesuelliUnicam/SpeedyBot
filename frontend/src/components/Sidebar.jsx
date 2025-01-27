import React from 'react';
import { NavLink,Link } from 'react-router-dom';

function Sidebar() {
    return (
        <div className="w-64 h-full bg-gray-800 text-white flex flex-col">
            <Link to="/">
                <h2 className="text-center text-2xl font-bold p-4 border-b border-gray-700 hover:text-gray-300">
                    SpeedyBot
                </h2>
            </Link>
            <nav className="flex-grow">
                <ul className="space-y-4 p-4">
                    <li>
                        <NavLink
                            to="/chatbot"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Chatbot
                        </NavLink>
                    </li>
                    <li>
                        <NavLink
                            to="/exerciseType"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Exercise Type
                        </NavLink>
                    </li>
                    <li>
                        <NavLink
                            to="/upload_text_exercise"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Upload Esercizi con testo
                        </NavLink>
                    </li>
                    <li>
                        <NavLink
                            to="/upload_image_exercise"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Upload Esercizi con immagini
                        </NavLink>
                    </li>
                    <li>
                        <NavLink
                            to="/exercises_with_images_manager"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Manager degli Esercizi con immagini
                        </NavLink>
                    </li>
                    <li>
                        <NavLink
                            to="/text_exercise_manager"
                            className="block px-4 py-2 rounded hover:bg-gray-700"
                            activeClassName="bg-gray-700"
                        >
                            Manager degli Esercizi con testo
                        </NavLink>
                    </li>
                </ul>
            </nav>
        </div>
    );
}

export default Sidebar;