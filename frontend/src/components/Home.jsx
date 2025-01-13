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
                    Benvenuti su <span className="text-yellow-300">SpeedyBot</span>
                </h1>
                <p className="text-lg mt-4">
                    Trasforma il tuo apprendimento linguistico con la nostra piattaforma interattiva.
                </p>
                <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
                    <button className="bg-yellow-300 text-gray-800 py-3 px-8 rounded-full font-semibold hover:bg-yellow-400 hover:shadow-xl transition duration-300">
                        Scopri di più
                    </button>
                    <button
                        className="bg-gray-800 text-white py-3 px-8 rounded-full font-semibold hover:bg-gray-900 hover:shadow-xl transition duration-300"
                        onClick={handleStart}
                    >
                        Inizia ora
                    </button>
                </div>
            </header>

            {/* About Section */}
            <section className="py-16">
                <h2 className="text-4xl font-bold text-gray-800 text-center">
                    Perché scegliere SpeedyBot?
                </h2>
                <p className="text-gray-600 text-center mt-4 max-w-2xl mx-auto">
                    SpeedyBot offre un modo semplice e personalizzato per imparare l'italiano tecnico,
                    essenziale per operazioni ferroviarie sicure e efficienti.
                </p>
                <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 px-4">
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <ClockIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">Interattività 24/7</h3>
                        <p className="text-gray-600 mt-2">
                            Studia quando vuoi, con esercizi e quiz progettati per adattarsi alle tue esigenze.
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <AcademicCapIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">Italiano tecnico ferroviario</h3>
                        <p className="text-gray-600 mt-2">
                            Contenuti specifici per macchinisti che lavorano in contesti tecnici e operativi.
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="flex items-center justify-center bg-green-500 rounded-full w-20 h-20 mx-auto shadow-lg hover:scale-110 transition duration-300">
                            <DeviceMobileIcon className="h-10 w-10 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">Piattaforma user-friendly</h3>
                        <p className="text-gray-600 mt-2">
                            Un'interfaccia semplice da usare, progettata per garantire un apprendimento rapido.
                        </p>
                    </div>
                </div>
            </section>

            {/* Call to Action */}
            <section className="bg-gradient-to-t from-gray-100 to-white py-16 text-center">
                <h2 className="text-4xl font-bold text-gray-800">
                    Pronto a migliorare le tue competenze?
                </h2>
                <p className="text-gray-600 mt-4 max-w-xl mx-auto">
                    SpeedyBot è il tuo compagno ideale per apprendere l'italiano tecnico.
                    Semplifica il tuo apprendimento con la nostra piattaforma interattiva.
                </p>
                <button
                    className="mt-6 bg-green-500 text-white py-3 px-8 rounded-full font-semibold hover:bg-green-600 hover:shadow-xl transition duration-300"
                    onClick={handleStart}
                >
                    Inizia ora
                </button>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-10">
                <div className="text-center">
                    <p className="text-gray-400">
                        &copy; {new Date().getFullYear()} SpeedyBot. Tutti i diritti riservati.
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default Home;