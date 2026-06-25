function MetricsPanel({ sources }) {

    if (!sources || sources.length === 0) {

        return null;

    }

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

            {

                sources.map((source, index) => (

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

                        Cosine Similarity:

                        {" "}

                        {source.cosine_similarity.toFixed(4)}

                    </div>

                ))

            }

        </div>

    );

}

export default MetricsPanel;