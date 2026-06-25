import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import api from "../api";
import "../styles/chat.css";

function ChatBox({

    isReady,
    setLatestResponse

}) {

    const [question, setQuestion] = useState("");

    const [messages, setMessages] = useState([]);

    const [loading, setLoading] = useState(false);

    const [copied, setCopied] = useState(false);

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

            const start = Date.now();

            const response = await api.post(

                "/chat",

                {

                    question: userQuestion

                }

            );

            const elapsed = Date.now() - start;

            if (elapsed < 700) {

                await new Promise(resolve =>

                    setTimeout(resolve, 700 - elapsed)

                );

            }

            setLatestResponse(response.data);

            setMessages(prev => [

                ...prev,

                {

                    role: "assistant",

                    text: response.data.answer,

                    sources: response.data.sources

                }

            ]);

        }

        catch (error) {

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

        finally {

            setLoading(false);

        }

    }

    function copyAnswer(text) {

        navigator.clipboard.writeText(text);

        setCopied(true);

        setTimeout(() => {

            setCopied(false);

        }, 2000);

    }

    function clearChat() {

        setMessages([]);

        setLatestResponse(null);

    }

    return (

        <div className="chat-container">

            <div

                style={{

                    display: "flex",

                    justifyContent: "space-between",

                    alignItems: "center"

                }}

            >

                <h2 className="chat-title">

                    💬 Chat

                </h2>

                <button

                    className="copy-btn"

                    onClick={clearChat}

                >

                    🗑 Clear Chat

                </button>

            </div>

            {

                copied && (

                    <div

                        style={{

                            color: "green",

                            fontWeight: "bold",

                            marginBottom: "10px"

                        }}

                    >

                        ✅ Copied to clipboard!

                    </div>

                )

            }

            {

                !isReady && (

                    <p className="warning">

                        Please ingest a website before asking questions.

                    </p>

                )

            }

            <div className="chat-window">

                {

                    messages.map((msg, index) => (

                        <div

                            key={index}

                            className={`message ${

                                msg.role === "user"

                                    ? "user"

                                    : "assistant"

                            }`}

                        >

                            <div className="message-label">

                                {

                                    msg.role === "user"

                                        ? "🧑 You"

                                        : "🤖 Assistant"

                                }

                            </div>

                            <div

                                className={`message-bubble ${

                                    msg.role === "user"

                                        ? "user-bubble"

                                        : "assistant-bubble"

                                }`}

                            >

                                {

                                    msg.role === "assistant"

                                        ?

                                        <ReactMarkdown>

                                            {msg.text}

                                        </ReactMarkdown>

                                        :

                                        msg.text

                                }

                            </div>

                            {

                                msg.role === "assistant" && (

                                    <button

                                        className="copy-btn"

                                        onClick={() =>

                                            copyAnswer(msg.text)

                                        }

                                    >

                                        📋 Copy Answer

                                    </button>

                                )

                            }

                            {

                                msg.sources && (

                                    <div className="sources">

                                        <strong>

                                            📚 Sources

                                        </strong>

                                        <ul>

                                            {

                                                msg.sources.map(

                                                    (source, i) => (

                                                        <li key={i}>

                                                            📄 {source.source_file}

                                                            {" | Chunk "}

                                                            {source.chunk_id}

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

                        <div className="assistant">

                            <div className="message-label">

                                🤖 Assistant

                            </div>

                            <div className="message-bubble assistant-bubble">

                                <div className="thinking">

                                    <span></span>

                                    <span></span>

                                    <span></span>

                                    <small

                                        style={{

                                            marginLeft: "10px",

                                            color: "#666"

                                        }}

                                    >

                                        Thinking...

                                    </small>

                                </div>

                            </div>

                        </div>

                    )

                }

                <div ref={bottomRef}></div>

            </div>

            <div className="chat-input-row">

                <input

                    className="chat-input"

                    value={question}

                    disabled={!isReady || loading}

                    placeholder={

                        isReady

                            ? "Ask anything about the website..."

                            : "Ingest a website first"

                    }

                    onChange={(e) =>

                        setQuestion(

                            e.target.value

                        )

                    }

                    onKeyDown={(e) => {

                        if (e.key === "Enter") {

                            askQuestion();

                        }

                    }}

                />

                <button

                    className="chat-button"

                    disabled={!isReady || loading}

                    onClick={askQuestion}

                >

                    {

                        loading

                            ? "⏳ Sending..."

                            : "🚀 Send"

                    }

                </button>

            </div>

        </div>

    );

}

export default ChatBox;