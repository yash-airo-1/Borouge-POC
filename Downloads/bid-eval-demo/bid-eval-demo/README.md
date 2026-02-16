# Airo Bid Evaluation Platform

**AI-Powered Bid Evaluation Demo for Borouge PLC**

A fully functional, enterprise-grade procurement evaluation platform powered by Anthropic's Claude API. Designed for evaluating supplier bids against complex tender requirements with AI-driven analysis, comparative dashboards, and intelligent chatbot assistance.

## Features

### 📄 Page 1: Tender Upload & Parsing
- Upload and extract RFP/tender documents (PDF, DOCX, TXT)
- AI-powered extraction of tender metadata, criteria, and requirements
- Customizable evaluation criteria with weight adjustment
- Support for technical, commercial, and compliance criteria

### 📋 Page 2: Supplier Bid Evaluation
- Multi-file upload for supplier bids
- AI-driven evaluation against tender requirements
- Automatic scoring across technical, commercial, and compliance dimensions
- Compliance status tracking (HSE, ESG, ISO certifications)
- Risk identification and completeness metrics

### 📊 Page 3: Comparative Dashboard
- Interactive supplier ranking with sortable table
- Multi-dimensional score comparisons (radar, bar, and grouped charts)
- Compliance matrix with mandatory requirement tracking
- HSE/ESG compliance status summary
- Risk heatmap and key risk highlights
- AI-generated trade-off analysis narrative

### 📑 Page 4: PDF Report Generation
- **Executive Summary**: One-page overview with top recommendations
- **Comparative Analysis**: Multi-page supplier comparison with charts
- **Individual Supplier Reports**: Detailed evaluation per vendor
- CSV and JSON data export for further analysis
- Professional Airo branding and "Confidential" watermark

### 💬 Page 5: Bid Intelligence Chatbot
- Context-aware assistant with full evaluation data
- Answer questions about specific suppliers, scores, and compliance
- Compare suppliers, analyze trade-offs, and summarize findings
- Quick-action buttons for common queries
- Full conversation history within session

## Tech Stack

- **Frontend & Backend**: [Streamlit](https://streamlit.io/) - Modern web app framework
- **AI Engine**: [Anthropic Claude API](https://www.anthropic.com/) - claude-sonnet-4-20250514 model
- **PDF Parsing**: PyMuPDF (fitz) - Advanced PDF text extraction
- **PDF Generation**: ReportLab - Professional PDF report creation
- **Charts**: Plotly - Interactive data visualization
- **Data Processing**: Pandas - Flexible data manipulation
- **Environment**: python-dotenv - Secure API key management

## Installation

### Prerequisites
- Python 3.10 or higher
- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

### Setup

1. **Clone or download the repository**
   ```bash
   cd bid-eval-demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   # Option 1: Create a .env file
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY

   # Option 2: Set environment variable
   export ANTHROPIC_API_KEY="sk-ant-..."

   # Option 3: Enter in Streamlit sidebar (no file needed)
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   ```
   Local URL: http://localhost:8501
   ```

## Quick Start

1. **Load Sample Data** (Recommended for demo):
   - Page 1: Click "Load Sample Tender" to get a realistic petrochemical RFQ
   - Page 2: Click "Load Sample Bids" to get 5 evaluated supplier responses
   - Page 3: View comparative dashboard with charts and trade-off analysis
   - Page 4: Download PDF reports and data exports
   - Page 5: Chat with the Bid Intelligence Assistant

2. **Use Your Own Data**:
   - Page 1: Upload your RFP/tender document
   - Page 2: Upload supplier bid responses
   - System will analyze and score all bids automatically
   - Continue through dashboard, reports, and chat

## Project Structure

```
bid-eval-demo/
├── app.py                    # Main Streamlit app and navigation
├── pages/
│   ├── 1_Upload_Tender.py    # Tender upload and criteria extraction
│   ├── 2_Upload_Bids.py      # Supplier bid upload and evaluation
│   ├── 3_Dashboard.py        # Comparative evaluation dashboard
│   ├── 4_Reports.py          # PDF report generation and download
│   └── 5_Chat.py             # Bid Intelligence Chatbot
├── utils/
│   ├── state.py              # Session state management
│   ├── pdf_parser.py         # PDF/DOCX/TXT text extraction
│   ├── ai_engine.py          # Claude API integration
│   └── report_gen.py         # PDF report generation
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Sample Data

The platform includes realistic sample data for a petrochemical procurement scenario:

- **Tender**: RFQ for Industrial Control Valves at Borouge Polyolefin Plant, Ruwais, UAE
- **5 Sample Suppliers**:
  - ValveTech Industries (Germany) - Premium quality, high cost
  - PetroFlow Solutions (UAE) - Local, competitive pricing
  - Shanghai Industrial Valves (China) - Lowest cost, ESG gaps
  - Flowserve Middle East (USA/UAE) - Global brand, premium pricing
  - Al Mansoori Valve Systems (UAE) - Local, balanced approach

- **Evaluation Criteria** (weighted):
  - Technical Capability (25%)
  - Delivery & Logistics (15%)
  - Commercial Terms (25%)
  - HSE Compliance (15%)
  - ESG & Sustainability (10%)
  - Past Performance (10%)

## API Usage

The platform uses Anthropic's Claude API with the following characteristics:

- **Model**: claude-sonnet-4-20250514 (latest Sonnet model)
- **Max Tokens**: 4096 for evaluations, 2048 for chat responses
- **Rate Limiting**: Standard Anthropic API limits apply
- **Cost**: Pricing based on input/output tokens. Sample data generation is cached in session

### API Calls Made

1. **Tender Analysis**: Extract structure and criteria from uploaded document
2. **Bid Evaluation**: Score each supplier bid against criteria (once per bid)
3. **Trade-off Analysis**: Compare top suppliers narratively (optional, on-demand)
4. **Chat Responses**: Answer questions with full evaluation context (per message)

## Features & Capabilities

### AI Analysis
- **Structured Data Extraction**: Convert unstructured tender documents to structured evaluation frameworks
- **Multi-dimensional Scoring**: Technical, commercial, and compliance dimensions
- **Compliance Tracking**: HSE, ESG, ISO certifications, and mandatory requirements
- **Risk Identification**: Automatic risk extraction from bid documents
- **Trade-off Analysis**: AI-generated narrative comparing supplier strategies
- **Context-Aware Chat**: Answer complex procurement questions with evidence

### User Interface
- **Clean, Professional Design**: Enterprise-grade layout suitable for C-level presentations
- **Color Scheme**: Airo branding (red #E63028, black #1A1A1A, white #FFFFFF)
- **Responsive Layout**: Works on desktop and tablet
- **Interactive Charts**: Hover, zoom, and export Plotly visualizations
- **Progress Indicators**: Step tracking (1-5) throughout the workflow

### Data Management
- **Session Persistence**: All data persists within a session
- **Data Export**: JSON and CSV export for further analysis
- **PDF Reports**: Professional, branded reports with multiple sections
- **Reset Function**: Clear all data and start new evaluation

## Customization

### Adjusting Evaluation Weights
On Page 1, use sliders to adjust the percentage weight for each criterion. The AI will immediately re-score when evaluations are performed.

### Sample Data
Edit `utils/ai_engine.py`:
- `generate_sample_tender_data()` - Modify tender details and criteria
- `generate_sample_supplier_evaluations()` - Change supplier profiles and scores

### Styling
Edit `app.py` custom CSS to adjust colors, fonts, or layout:
```python
<style>
:root {
    --primary-color: #E63028;      # Airo red
    --secondary-color: #1A1A1A;    # Airo black
    --background-color: #F5F5F5;   # Light grey
}
</style>
```

### Report Templates
Edit `utils/report_gen.py` to customize PDF report layouts, fonts, or content structure.

## 🚀 Cloud Deployment

The application is ready for production deployment to major cloud platforms.

### Supported Platforms

1. **Streamlit Cloud** (Easiest) - Free tier available
   - 5-minute setup
   - Automatic GitHub integration
   - Built-in secret management

2. **Heroku** - Docker-based
   - 15-minute setup
   - Standard deployment workflow

3. **Google Cloud Run** - Serverless
   - 20-minute setup
   - Auto-scaling

4. **AWS EC2** - Full control
   - 30-minute setup
   - Custom configuration

5. **Microsoft Azure** - Full-featured
   - 20-minute setup
   - Free tier available

### Quick Deploy

See **[CLOUD_QUICK_START.md](CLOUD_QUICK_START.md)** for 3-step deployment to any platform.

### Full Documentation

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive deployment guide with:
- Detailed step-by-step instructions
- Security best practices
- Monitoring and logging setup
- CI/CD pipeline configuration
- Troubleshooting guide

### Prerequisites for Deployment

- ✅ Python 3.10+
- ✅ Git
- ✅ Anthropic API key
- ✅ Cloud platform account (Streamlit Cloud, Heroku, AWS, etc.)

### Included Files

```
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Local development with Docker
├── Procfile                # Heroku deployment config
├── runtime.txt             # Python version for Heroku
├── .streamlit/
│   ├── config.toml         # Streamlit production config
│   └── secrets.toml.example # Secrets template
├── DEPLOYMENT.md           # Full deployment guide
└── CLOUD_QUICK_START.md    # Quick start for all platforms
```

## Security

- **API Key**: Stored in session memory only, not persisted to disk
- **Data Privacy**: All uploaded documents are processed in-memory
- **No Data Logging**: Evaluation data is not logged or sent anywhere except Claude API
- **Session Isolation**: Each user session is independent
- **Production Ready**: Includes CORS, CSRF protection, and secure defaults

## Troubleshooting

### "No API key detected"
- Set `ANTHROPIC_API_KEY` environment variable, or
- Enter API key in the Streamlit sidebar, or
- Create `.env` file with your API key

### "Error extracting text from PDF"
- Ensure PDF is valid and not password-protected
- Try copying text manually and using a TXT file instead
- Supported formats: PDF, DOCX, TXT

### "Claude API error"
- Check your API key is valid
- Verify internet connection
- Check Anthropic API status at console.anthropic.com
- Retry after a few seconds (automatic retry logic included)

### "Layout looks strange"
- Ensure you're using the latest version of Streamlit: `pip install --upgrade streamlit`
- Try clearing browser cache and reloading
- Ensure browser window is at least 800px wide

## Performance

- **Tender Upload**: ~2-5 seconds depending on document size
- **Bid Evaluation**: ~10-30 seconds per bid (parallel processing possible with multi-threading)
- **Dashboard Load**: ~1 second (all local rendering)
- **PDF Generation**: ~2-5 seconds per report
- **Chat Response**: ~5-10 seconds depending on question complexity

## Limitations

- Maximum file upload: 100MB (Streamlit limitation)
- Maximum 10 bids per evaluation session (configurable)
- Chat history persists only within session (not saved between sessions)
- PDF reports are generated in memory (large evaluations may be slow)

## Future Enhancements

Potential improvements for production deployment:

- Database storage for persistent project history
- Multi-user support with role-based access
- Supplier document versioning and audit trail
- Custom evaluation frameworks (not just sample)
- Bulk bid import from email or file sharing services
- Real-time collaboration with multiple evaluators
- Advanced analytics and trend analysis
- Integration with procurement systems (Coupa, Ariba, etc.)

## Support & Feedback

Built by **Airo Digital Labs** using [Anthropic Claude API](https://www.anthropic.com/)

For issues, questions, or feedback:
- Review this README for troubleshooting
- Check Streamlit documentation: https://docs.streamlit.io/
- Contact Anthropic support for API issues

## License

This demo application is provided as-is for demonstration purposes.

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Model**: Claude Sonnet 4.5 (claude-sonnet-4-20250514)
