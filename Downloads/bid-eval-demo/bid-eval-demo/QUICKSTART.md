# Airo Bid Evaluation Platform - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd "D:\Projects\bid-eval-demo"
pip install -r requirements.txt
```

### Step 2: Set Your API Key
Choose one method:

**Option A: Create .env file**
```bash
copy .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: Set environment variable**
```bash
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option C: Use Streamlit UI**
- No setup needed, just paste key in sidebar when app launches

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open at: http://localhost:8501

---

## 📊 Try the Demo in 5 Minutes

1. **Page 1: Load Sample Tender**
   - Click the "Load Sample Tender" button
   - See extracted evaluation criteria

2. **Page 2: Load Sample Bids**
   - Click the "Load Sample Bids" button
   - Watch 5 suppliers get evaluated automatically

3. **Page 3: View Dashboard**
   - See comparative scoring
   - Explore interactive charts
   - Review compliance matrix

4. **Page 4: Download Reports**
   - Generate Executive Summary PDF
   - Export data as CSV/JSON

5. **Page 5: Chat with Assistant**
   - Ask "Compare the top 2 suppliers"
   - Try quick action buttons

---

## 📁 Project Structure

```
bid-eval-demo/
├── app.py                  ← Main app launcher
├── pages/
│   ├── 1_Upload_Tender.py
│   ├── 2_Upload_Bids.py
│   ├── 3_Dashboard.py
│   ├── 4_Reports.py
│   └── 5_Chat.py
├── utils/
│   ├── state.py            ← Session management
│   ├── pdf_parser.py       ← Document extraction
│   ├── ai_engine.py        ← Claude API calls
│   └── report_gen.py       ← PDF generation
├── requirements.txt
├── .env.example
├── README.md
└── SETUP_GUIDE.md
```

---

## 🎯 What You Can Do

### Upload & Analyze
- ✅ Upload tender documents (PDF, DOCX, TXT)
- ✅ Upload supplier bids (multiple files)
- ✅ AI extracts and structures data automatically

### Evaluate
- ✅ Automatic scoring by Claude API
- ✅ Technical, commercial, compliance dimensions
- ✅ Compliance tracking (HSE, ESG, ISO)
- ✅ Risk identification

### Compare
- ✅ Interactive dashboard with charts
- ✅ Supplier ranking table
- ✅ Compliance matrix
- ✅ Trade-off analysis

### Report
- ✅ Professional PDF reports
- ✅ Executive summary
- ✅ Comparative analysis
- ✅ Individual supplier reports
- ✅ CSV/JSON data export

### Ask Questions
- ✅ Chat with evaluation data
- ✅ Compare suppliers
- ✅ Check compliance status
- ✅ Get management summaries

---

## 📝 Sample Data Included

The platform comes with realistic sample data:

**Tender**: RFQ for Industrial Valves at Borouge Polyolefin Plant, UAE

**5 Sample Suppliers**:
1. ValveTech Industries (Germany) - Premium
2. PetroFlow Solutions (UAE) - Local, competitive
3. Shanghai Industrial Valves (China) - Lowest cost
4. Flowserve Middle East (USA/UAE) - Global leader
5. Al Mansoori Valve Systems (UAE) - Local partnership

**6 Evaluation Criteria**:
- Technical Capability (25%)
- Delivery & Logistics (15%)
- Commercial Terms (25%)
- HSE Compliance (15%)
- ESG & Sustainability (10%)
- Past Performance (10%)

---

## ⚙️ Configuration Options

### API Key
Set `ANTHROPIC_API_KEY` in .env, environment, or Streamlit sidebar

### Model
Currently uses: `claude-sonnet-4-20250514`

To change, edit `utils/ai_engine.py`:
```python
model="claude-sonnet-4-20250514",  # Change this line
```

### Max Tokens
- Tender extraction: 4096
- Bid evaluation: 4096
- Chat: 2048
- Trade-off: 2048

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'streamlit'" | `pip install -r requirements.txt` |
| "ANTHROPIC_API_KEY not found" | Set API key in .env or sidebar |
| Port 8501 in use | `streamlit run app.py --server.port 8502` |
| PDF extraction fails | Use TXT or DOCX format instead |
| Charts not showing | Clear browser cache, try different browser |

---

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Setup Details**: See `SETUP_GUIDE.md`
- **Streamlit Docs**: https://docs.streamlit.io/
- **Claude API Docs**: https://docs.anthropic.com/

---

## ✨ Features Highlights

### Smart AI Analysis
- Extracts structured data from unstructured documents
- Generates consistent scoring across suppliers
- Identifies compliance gaps automatically
- Creates narrative trade-off analysis

### Professional UI
- Enterprise-grade design for C-level presentations
- Interactive charts and visualizations
- Responsive layout (desktop & tablet)
- Airo brand styling throughout

### Complete Workflow
- 5-step process from upload to decision
- Session state persistence
- Data export in multiple formats
- PDF report generation

### Intelligent Assistant
- Contextual answers about evaluations
- Compares suppliers with evidence
- Tracks compliance status
- Suggests adjustments to criteria

---

## 🎓 Use Cases

### Procurement Teams
- Evaluate RFPs efficiently
- Score proposals consistently
- Generate documentation
- Support decision-making

### Procurement Leadership
- View comparative dashboards
- Download executive summaries
- Ask questions about evaluations
- Make data-driven decisions

### Finance & Operations
- Review commercial terms
- Track compliance status
- Export data for systems
- Audit evaluation process

### Suppliers (Demo View)
- See evaluation criteria
- Understand scoring approach
- Review feedback summaries
- Get recommendations

---

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Set API key
3. ✅ Run the app
4. ✅ Try sample data
5. ✅ Upload your own documents
6. ✅ Share reports with stakeholders

**Ready?** Run: `streamlit run app.py`

---

**Built with Anthropic Claude API** 🤖
