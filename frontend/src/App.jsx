import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import UploadImageExerciseForm from './components/UploadImageExerciseForm'
import Chatbot from './components/Chatbot'
import ExerciseType from "./components/ExerciseType"
import UploadTextExerciseForm from "./components/UploadTextExerciseForm"
import Home from "./components/Home"

function App() {
    return (
        <Router>
            <div className="flex h-screen">
                {/* Sidebar */}
                <Sidebar/>

                {/* Contenuto principale */}
                <div className="flex-grow p-4 overflow-y-auto">
                    <Routes>
                        <Route path="/" element={<Home/>}/>
                        <Route path="/upload_image_exercise" element={<UploadImageExerciseForm/>}/>
                        <Route path="/chatbot" element={<Chatbot/>}/>
                        <Route path="/ExerciseType" element={<ExerciseType/>}/>
                        <Route path="/upload_text_exercise" element={<UploadTextExerciseForm/>}/>
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;