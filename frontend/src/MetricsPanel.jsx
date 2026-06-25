function MetricsPanel({ latestResponse }) {

    if (!latestResponse) {
        return null;
    }

    const sources = latestResponse.sources || [];
    const perplexity = latestResponse.perplexity;
    const retrieval = latestResponse.retrieval;

    return (

        <div
            style={{
                marginTop: "30px",
                border: "1px solid #ddd",
                borderRadius: "10px",
                padding: "15px"
            }}
        >

            <h3>📊 Retrieval Metrics</h3>

            <p>
                <b>Retrieval:</b> {retrieval}
            </p>

            {sources.map((source, index) => (

                <div
                    key={index}
                    style={{
                        marginBottom: "15px"
                    }}
                >

                    <b>{source.source_file}</b>

                    <br />

                    Chunk: {source.chunk_id}

                    <br />

                    Cosine Similarity:{" "}

                    {
                        source.cosine_similarity != null
                            ? source.cosine_similarity.toFixed(4)
                            : "N/A"
                    }

                </div>

            ))}

            <hr />

            <h3>📈 Perplexity</h3>

            <p>

                {

                    perplexity != null && (

                        <>

                            {

                                perplexity < 20

                                    ? "🟢"

                                    : perplexity < 40

                                    ? "🟡"

                                    : perplexity < 60

                                    ? "🟠"

                                    : "🔴"

                            }

                            {" "}

                            <b>{perplexity}</b>

                        </>

                    )

                }

            </p>

            <p>

                {

                    perplexity == null

                        ? "N/A"

                        : perplexity < 20

                        ? "Excellent confidence"

                        : perplexity < 40

                        ? "Good confidence"

                        : perplexity < 60

                        ? "Moderate confidence"

                        : "Low confidence"

                }

            </p>

        </div>

    );

}

export default MetricsPanel;