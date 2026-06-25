import { useState } from "react";
import UploadURL from "./UploadURL";
import ChatBox from "./ChatBox";

function App() {

    const [isReady, setIsReady] = useState(false);

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
            />

            <ChatBox
                isReady={isReady}
            />

        </div>

    );

}

export default App;