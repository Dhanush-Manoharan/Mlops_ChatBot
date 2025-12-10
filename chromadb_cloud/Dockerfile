FROM chromadb/chroma:latest

# Set working directory
WORKDIR /chroma

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV IS_PERSISTENT=TRUE
ENV ANONYMIZED_TELEMETRY=FALSE

# Start ChromaDB on the correct port
CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]