import { useState } from "react";
import api from "./api";

function UploadURL() {

    const [url, setUrl] = useState("");

    const [loading, setLoading] = useState(false);

    const [message, setMessage] = useState("");

    async function ingestWebsite() {

        if (!url.trim()) {

            setMessage("Enter a valid URL");
            return;
        }

        setLoading(true);
        setMessage("");

        try {

            const response = await api.post(
                "/ingest",
                {
                    url
                }
            );

            setMessage(
                `Successfully scraped ${response.data.pages_scraped} pages`
            );

        } catch (error) {

            if (error.response) {

                setMessage(error.response.data.detail);

            } else {

                setMessage("Backend not running");

            }

        }

        setLoading(false);
    }

    return (

        <div>

            <input

                type="text"

                placeholder="https://example.com"

                value={url}

                onChange={(e) =>
                    setUrl(e.target.value)
                }

                style={{
                    width: "75%",
                    padding: "12px",
                    fontSize: "16px"
                }}

            />

            <button

                onClick={ingestWebsite}

                style={{
                    marginLeft: "10px",
                    padding: "12px 20px"
                }}

            >

                {loading
                    ? "Processing..."
                    : "Ingest"}

            </button>

            <p>

                {message}

            </p>

        </div>

    );

}

export default UploadURL;