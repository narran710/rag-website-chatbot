import { useState } from "react";

import UploadURL from "./components/UploadURL";
import ChatBox from "./components/ChatBox";
import MetricsPanel from "./components/MetricsPanel";

import "./styles/app.css";
function App() {

    const [isReady, setIsReady] = useState(false);
    const [latestResponse, setLatestResponse] = useState(null);

    return (

        <div className="app-container">

            <h1 className="app-title">

                🌐 RAG Website Chatbot

            </h1>

            <UploadURL
                setIsReady={setIsReady}
                setLatestResponse={setLatestResponse}
            />

            <ChatBox
                isReady={isReady}
                setLatestResponse={setLatestResponse}
            />

            <MetricsPanel
                latestResponse={latestResponse}
            />

        </div>

    );
}

export default App;