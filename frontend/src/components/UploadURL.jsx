import { useState } from "react";
import api from "../api";
import "../styles/upload.css";

function UploadURL({
    setIsReady,
    setLatestResponse
}) {

    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    async function ingestWebsite() {

        if (!url.trim()) {

            setMessage("Please enter a valid URL.");
            return;

        }

        setLoading(true);
        setMessage("");

        setIsReady(false);

        setLatestResponse(null);

        try {

            const response = await api.post(
                "/ingest",
                {
                    url
                }
            );

            setMessage(
                `✅ Successfully scraped ${response.data.pages_scraped} pages. You can now start chatting.`
            );

            setIsReady(true);

        } catch (error) {

            if (error.response) {

                setMessage(
                    error.response.data.detail ||
                    "Failed to ingest website."
                );

            } else {

                setMessage(
                    "Cannot connect to backend."
                );

            }

            setIsReady(false);

        }

        setLoading(false);

    }

    return (

        <div className="upload-container">

            <h2>

                🌐 Website Ingestion

            </h2>

            <p>

                Enter a website URL to crawl and build the knowledge base.

            </p>

            <div className="upload-row">

                <input

                    className="upload-input"

                    type="text"

                    placeholder="https://example.com"

                    value={url}

                    disabled={loading}

                    onChange={(e) =>
                        setUrl(
                            e.target.value
                        )
                    }

                    onKeyDown={(e) => {

                        if (e.key === "Enter") {

                            ingestWebsite();

                        }

                    }}

                />

                <button

                    className="upload-button"

                    onClick={ingestWebsite}

                    disabled={loading}

                >

                    {

                        loading

                            ? "⏳ Processing..."

                            : "🚀 Ingest"

                    }

                </button>

            </div>

            {

                message && (

                    <p className="upload-message">

                        {message}

                    </p>

                )

            }

        </div>

    );

}

export default UploadURL;