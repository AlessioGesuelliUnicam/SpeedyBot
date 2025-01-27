import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Chatbot from './components/Chatbot'
import ExerciseType from "./components/ExerciseType"
import Home from "./components/Home"
import ImageExercisesManager from "./components/ImageExercisesManager"
import TextExercisesManager from "./components/TextExercisesManager"
function App() {
    return (
        <Router>
            <div className="flex h-screen">
                {/* Sidebar */}
                <Sidebar/>

                {/* Main content */}
                <div className="flex-grow p-4 overflow-y-auto">
                    <Routes>
                        <Route path="/" element={<Home/>}/>
                        <Route path="/chatbot" element={<Chatbot/>}/>
                        <Route path="/ExerciseType" element={<ExerciseType/>}/>
                        <Route path="/exercises_with_images_manager" element={<ImageExercisesManager/>}/>
                        <Route path="/text_exercise_manager" element={<TextExercisesManager/>}/>
                    </Routes>
                </div>
            </div>
        </Router>
    )
}

export default App