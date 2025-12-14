# PropBot - AI Real Estate Assistant for Boston

MLOps Course Final Project - Group 18  
IE 7374 - Northeastern University  
**Milestone 1: Data Pipeline Submission**

## Team Members
- Dhanush Manoharan
- Pranav Rangbulla
- Gayatri Nair
- Priyanka Raj Rajendran
- Nishchay Gowda
- Shivakumar Hassan Lokesh

## 🎬 Demo
<p align="center">
  <img src="https://github.com/Dhanush-Manoharan/Mlops_ChatBot/blob/69d99c09f2a3f8bfc09a24611fbc49df4d0eb0eb/assets/images/propbot%20(1).gif" alt="PropBot Demo" width="800">
</p>
<p align="center">
  <i>PropBot in action at Google Cambridge MLOps Innovation Expo</i>
</p>

# PropBot - Boston Real Estate Chatbot with MLOps Pipeline

PropBot is an intelligent real estate chatbot powered by GPT-4o-mini and RAG (Retrieval Augmented Generation) technology, designed to help users find properties in Boston. This project implements a complete MLOps pipeline with automated monitoring, drift detection, and model retraining.

## 🎯 Features

### Core Functionality
- **Intelligent Property Search**: RAG-powered chatbot using ChromaDB and OpenAI GPT-4o-mini
- **Real-time Property Data**: Integration with Zillow and Boston property listings
- **Semantic Search**: Advanced embedding-based retrieval using Sentence Transformers
- **Interactive UI**: Streamlit-based frontend with real-time chat interface
- **FastAPI Backend**: High-performance REST API with monitoring endpoints

### MLOps Features
- **Automated Model Monitoring**: Real-time metrics collection and performance tracking
- **Data Drift Detection**: Jensen-Shannon divergence-based drift detection
- **Automated Retraining**: Trigger-based model retraining pipeline
- **Cloud Logging**: Structured logging to Google Cloud Platform
- **CI/CD Pipeline**: GitHub Actions workflow with automated testing and deployment
- **DVC Integration**: Data version control for model and dataset versioning
- **Health Monitoring**: Deployment verification and smoke testing

## 🏗️ Architecture

┌─────────────┐ ┌──────────────┐ ┌─────────────┐ │ Streamlit │ ──────> │ FastAPI │ ──────> │ ChromaDB │ │ Frontend │ <────── │ Backend │ <────── │ (Vector) │ └─────────────┘ └──────────────┘ └─────────────┘ │ ├──> OpenAI GPT-4o-mini ├──> Monitoring System ├──> Drift Detector └──> Retraining Pipeline

## 📁 Project Structure

project_mlops/ ├── backend/ │ ├── main.py # FastAPI application │ ├── requirements.txt # Python dependencies │ ├── dockerfile # Backend container │ ├── startup.sh # Cloud Run startup script │ ├── src/ │ │ └── rag_pipeline.py # RAG implementation │ ├── monitoring/ │ │ ├── metrics.py # Metrics collection │ │ ├── drift_detector.py # Data drift detection │ │ └── cloud_logger.py # Cloud logging │ ├── retraining/ │ │ └── trigger.py # Retraining triggers │ ├── scripts/ │ │ ├── retrain_model.py # Automated retraining pipeline │ │ └── verify_monitoring.py # Dependency verification │ ├── notifications/ │ │ └── alerts.py # Notification system │ └── mlflow_tracking/ │ └── tracker.py # MLflow experiment tracking ├── frontend/ │ ├── app.py # Streamlit application │ └── Dockerfile # Frontend container ├── .github/ │ └── workflows/ │ └── ci-cd.yml # CI/CD pipeline ├── tests/ # Unit and integration tests └── dvc.yaml # DVC pipeline configuration

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API Key
- Google Cloud Platform account (for deployment)
- Git with DVC

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/project_mlops.git
```
Set up environment variables
# Backend
cd backend

export OPENAI_API_KEY="your-openai-api-key"

export CHROMA_PATH="chroma_data"

Install dependencies
pip install -r requirements.txt

Verify monitoring system
python scripts/verify_monitoring.py

Start the backend
# Windows
start.bat

# Linux/Mac
python main.py
Backend will be available at http://localhost:8080

Start the frontend (in a new terminal)
cd frontend
streamlit run app.py
Frontend will be available at http://localhost:8501

🧪 Testing
Run Unit Tests
pytest tests/ -v

Run Monitoring Verification
cd backend
python scripts/verify_monitoring.py

Test Health Endpoint
curl http://localhost:8080/health

Test Chat Endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me properties in Back Bay", "conversation_id": "test123"}'

📊 Monitoring & MLOps
Metrics Collection

The system automatically collects:
Query response times
Number of documents retrieved
User satisfaction scores
System resource utilization
Drift Detection

Data drift is monitored using:
Jensen-Shannon divergence on query embeddings
Performance metric degradation detection
Threshold-based alerting
Automated Retraining

Retraining triggers when:
Data drift exceeds threshold (0.1)
Performance drops below baseline
Manual trigger via API endpoint
Retraining Pipeline

# Manual trigger
curl -X POST http://localhost:8080/api/monitoring/trigger-retraining
The pipeline executes:
Pull latest data from DVC
Retrain RAG model with updated data
Validate new model performance
Compare with baseline metrics
Deploy if better than current model

🔄 CI/CD Pipeline
GitHub Actions Workflow
Triggered on push to main branch:
Test Stage
Install dependencies
Run unit tests
Continue on test failures (for demo)
Deploy Backend (Currently disabled)
Pull latest models from DVC
Build Docker container
Deploy to Cloud Run
Health check verification
Smoke testing
Deploy Frontend (Currently disabled)
Build Streamlit container
Deploy to Cloud Run
Enable Deployment

To enable automatic deployment, update .github/workflows/ci-cd.yml:
# Change from:
if: false

# To:
if: github.ref == 'refs/heads/main'
Required GitHub Secrets
GCP_SA_KEY: Google Cloud service account JSON key
OPENAI_API_KEY: OpenAI API key

🌐 Deployment
Google Cloud Run Deployment

Prerequisites:
GCP project created
Cloud Run API enabled
Service account with Cloud Run permissions

Deploy Backend:
gcloud run deploy propbot-backend \
  --source backend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,MONITORING_ENABLED=true
Deploy Frontend:
gcloud run deploy propbot-frontend \
  --source frontend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BACKEND_API_URL=$BACKEND_URL
  
📈 Data Version Control (DVC)
DVC Pipeline Stages
Data Acquisition: Collect properties from Zillow
Preprocessing: Clean and normalize datasets
ChromaDB Ingestion: Embed and store in vector database

Pull Latest Data
dvc pull
Update Data
dvc repro
dvc push
🔧 API Endpoints
Health Check
GET /health
Chat
POST /chat
Body: {"query": "string", "conversation_id": "string"}
Monitoring Metrics
GET /api/monitoring/metrics
Drift Detection
GET /api/monitoring/drift
Trigger Retraining
POST /api/monitoring/trigger-retraining

🛠️ Technologies
Backend: FastAPI
ChromaDB
OpenAI GPT-4o-mini
Sentence Transformers
MLflow
Google Cloud Logging
Frontend: Streamlit
Python Requests
MLOps: GitHub Actions, DVC (Data Version Control), Docker

Google Cloud Run
Google Cloud Storage

Monitoring: Custom metrics collection
Jensen-Shannon divergence for drift
Cloud logging and monitoring

📝 Environment Variables
Backend
OPENAI_API_KEY=your-api-key
CHROMA_PATH=chroma_data
ENVIRONMENT=production
MONITORING_ENABLED=true

Frontend
BACKEND_API_URL=http://localhost:8080
🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request
📄 License
This project is part of an MLOps course submission.

🙏 Acknowledgments
Boston Open Data for property datasets
OpenAI for GPT-4o-mini API

## Known Issues & Limitations

1. **API Rate Limits:** Some data sources have rate limits; pipeline includes retry logic
2. **Large File Size:** ChromaDB backup is 3.8GB; requires DVC for versioning
3. **Processing Time:** Full pipeline takes ~45 minutes on standard hardware

---

## Future Improvements

1. Implement real-time data streaming
2. Add more sophisticated bias mitigation techniques
3. Expand to more Boston neighborhoods
4. Add data quality dashboards
5. Implement automated retraining pipeline

---

## License

MIT License - Academic Project

## Contact

For questions or issues, please contact:
- Pranav Rangbulla - rangbulla.p@northeastern.edu
- Dhanush Manoharan - manoharan.dh@northeastern.edu
- Priyanka Raj rajendran - rajendran.priy@northeastern.edu
- Gayatri Nair -
- Nishchay Linge Gowda - lingegowda.n@northeastern.edu
- Shivakumar Hassan Lokesh - 
---
