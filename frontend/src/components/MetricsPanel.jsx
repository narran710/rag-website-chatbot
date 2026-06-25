import "../styles/metrics.css";

function MetricsPanel({ latestResponse }) {

    if (!latestResponse) {

        return null;

    }

    const sources = latestResponse.sources || [];

    const perplexity = latestResponse.perplexity;

    const retrieval = latestResponse.retrieval;

    function getConfidence() {

        if (perplexity == null) {

            return "N/A";

        }

        if (perplexity < 20) {

            return "🟢 Excellent";

        }

        if (perplexity < 40) {

            return "🟡 Good";

        }

        if (perplexity < 60) {

            return "🟠 Moderate";

        }

        return "🔴 Low";

    }

    return (

        <div className="metrics-card">

            <h2>

                📊 Retrieval Metrics

            </h2>

            <div className="retrieval-box">

                <strong>

                    Retrieval Method

                </strong>

                <p>

                    {retrieval}

                </p>

            </div>

            <h3>

                Retrieved Chunks

            </h3>

            {
                sources.map((source, index) => (

                    <div
                        key={index}
                        className="source-card"
                    >

                        <div
                            style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center"
                            }}
                        >

                            <div className="source-header">

                                📄 {source.source_file}

                            </div>

                            <div
                                style={{
                                    background: "#2563eb",
                                    color: "white",
                                    padding: "4px 10px",
                                    borderRadius: "20px",
                                    fontSize: "13px"
                                }}
                            >

                                Chunk #{source.chunk_id}

                            </div>

                        </div>

                        <div className="similarity-section">

                            <div className="progress-bar">

                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${source.cosine_similarity * 100}%`
                                    }}
                                />

                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    marginTop: "8px"
                                }}
                            >

                                <span>

                                    Similarity Score

                                </span>

                                <strong>

                                    {(source.cosine_similarity * 100).toFixed(1)}%

                                </strong>

                            </div>

                        </div>

                    </div>

                ))
            }

            <div className="perplexity-card">

                <h3>

                    📈 Perplexity Score

                </h3>

                <h1>

                    {

                        perplexity != null

                            ? perplexity.toFixed(2)

                            : "N/A"

                    }

                </h1>

                <p>

                    {getConfidence()}

                </p>

            </div>

        </div>

    );

}

export default MetricsPanel;