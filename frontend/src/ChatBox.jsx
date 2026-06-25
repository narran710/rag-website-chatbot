import { useState, useRef, useEffect } from "react";
import api from "./api";

function ChatBox({ isReady }) {

    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const bottomRef = useRef(null);

    useEffect(() => {

        bottomRef.current?.scrollIntoView({
            behavior: "smooth"
        });

    }, [messages, loading]);

    async function askQuestion() {

        if (!isReady) return;

        if (!question.trim()) return;

        const userQuestion = question;

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                text: userQuestion
            }
        ]);

        setQuestion("");

        setLoading(true);

        try {

            const response = await api.post(
                "/chat",
                {
                    question: userQuestion
                }
            );

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    text: response.data.answer,
                    sources: response.data.sources
                }
            ]);

        } catch (error) {

            let message = "Cannot connect to backend.";

            if (error.response) {

                message =
                    error.response.data.detail ||
                    "Backend error.";

            }

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    text: message
                }
            ]);

        }

        setLoading(false);

    }

    return (

        <div style={{ marginTop: "40px" }}>

            <h2>💬 Chat</h2>

            {
                !isReady && (

                    <p
                        style={{
                            color: "red",
                            fontWeight: "bold"
                        }}
                    >
                        Please ingest a website before asking questions.
                    </p>

                )
            }

            <div
                style={{
                    border: "1px solid #ddd",
                    borderRadius: "10px",
                    padding: "15px",
                    height: "450px",
                    overflowY: "auto",
                    background: "#fafafa",
                    marginBottom: "15px"
                }}
            >

                {
                    messages.map((msg, index) => (

                        <div
                            key={index}
                            style={{
                                marginBottom: "20px",
                                textAlign:
                                    msg.role === "user"
                                        ? "right"
                                        : "left"
                            }}
                        >

                            <strong>

                                {
                                    msg.role === "user"
                                        ? "🧑 You"
                                        : "🤖 Assistant"
                                }

                            </strong>

                            <div
                                style={{
                                    display: "inline-block",
                                    background:
                                        msg.role === "user"
                                            ? "#dbeafe"
                                            : "#f3f4f6",
                                    padding: "12px",
                                    borderRadius: "10px",
                                    marginTop: "5px",
                                    maxWidth: "80%"
                                }}
                            >

                                {msg.text}

                            </div>

                            {

                                msg.sources && (

                                    <div
                                        style={{
                                            marginTop: "10px"
                                        }}
                                    >

                                        <strong>

                                            📚 Sources

                                        </strong>

                                        <ul>

                                            {

                                                msg.sources.map(
                                                    (source, i) => (

                                                        <li key={i}>

                                                            📄 {source.source_file}

                                                            {" (Chunk "}

                                                            {source.chunk_id}

                                                            {")"}

                                                        </li>

                                                    )
                                                )

                                            }

                                        </ul>

                                    </div>

                                )

                            }

                        </div>

                    ))
                }

                {
                    loading && (

                        <div
                            style={{
                                color: "gray",
                                fontStyle: "italic"
                            }}
                        >
                            🤖 Assistant is typing...
                        </div>

                    )
                }

                <div ref={bottomRef}></div>

            </div>

            <input

                value={question}

                disabled={!isReady || loading}

                onChange={(e) =>
                    setQuestion(e.target.value)
                }

                onKeyDown={(e) => {

                    if (e.key === "Enter") {

                        askQuestion();

                    }

                }}

                placeholder={
                    isReady
                        ? "Ask a question..."
                        : "Ingest a website first"
                }

                style={{
                    width: "75%",
                    padding: "12px",
                    fontSize: "16px"
                }}

            />

            <button

                disabled={!isReady || loading}

                onClick={askQuestion}

                style={{
                    marginLeft: "10px",
                    padding: "12px 20px"
                }}

            >

                {
                    loading
                        ? "Sending..."
                        : "Send"
                }

            </button>

        </div>

    );

}

export default ChatBox;