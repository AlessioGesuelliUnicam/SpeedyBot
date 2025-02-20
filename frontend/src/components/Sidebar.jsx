import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { FaCog } from 'react-icons/fa';

function Sidebar() {
    return (
        <div className="w-64 h-full bg-gray-800 text-white flex flex-col justify-between">
            <div>
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
            <div className="p-4 border-t border-gray-700 flex justify-center">
                <Link to="/settings" className="text-white text-2xl hover:text-gray-400">
                    <FaCog />
                </Link> 
            </div>
        </div>
    );
}

export default Sidebar;
