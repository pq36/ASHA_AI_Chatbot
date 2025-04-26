import AuthPage from './login';
import './App.css';
import Chatbot from './chatbot';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
function App() {
  return (
    <Router>
            <Routes>
                <Route path="/" element={<Chatbot />} />
                <Route path="/login" element={<AuthPage />} />
            </Routes>
        </Router>
  );
}

export default App;
