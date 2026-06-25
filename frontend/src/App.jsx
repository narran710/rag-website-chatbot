import UploadURL from "./UploadURL";

function App() {

    return (

        <div
            style={{
                maxWidth: "900px",
                margin: "40px auto",
                padding: "20px",
                fontFamily: "Arial"
            }}
        >

            <h1>
                RAG Website Chatbot
            </h1>

            <UploadURL />

        </div>

    );

}

export default App;