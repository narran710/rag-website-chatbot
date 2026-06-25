import { useState } from "react";
import UploadURL from "./UploadURL";
import ChatBox from "./ChatBox";
import MetricsPanel from "./MetricsPanel";

function App() {

    const [isReady, setIsReady] = useState(false);
    const [latestResponse, setLatestResponse] = useState(null);

    return (

        <div
            style={{
                maxWidth: "900px",
                margin: "40px auto",
                padding: "20px",
                fontFamily: "Arial"
            }}
        >

            <h1>RAG Website Chatbot</h1>

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