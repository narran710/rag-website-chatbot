import { useState } from "react";
import api from "./api";

function UploadURL({ setIsReady }) {

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

        // Disable chat until ingestion completes
        setIsReady(false);

        try {

            const response = await api.post(
                "/ingest",
                {
                    url
                }
            );

            setMessage(
                `Successfully scraped ${response.data.pages_scraped} pages. You can now start chatting.`
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

        <div>

            <input

                type="text"

                placeholder="https://example.com"

                value={url}

                disabled={loading}

                onChange={(e) =>
                    setUrl(e.target.value)
                }

                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        ingestWebsite();
                    }
                }}

                style={{
                    width: "75%",
                    padding: "12px",
                    fontSize: "16px"
                }}

            />

            <button

                onClick={ingestWebsite}

                disabled={loading}

                style={{
                    marginLeft: "10px",
                    padding: "12px 20px"
                }}

            >

                {
                    loading
                        ? "Processing..."
                        : "Ingest"
                }

            </button>

            <p>

                {message}

            </p>

        </div>

    );

}

export default UploadURL;