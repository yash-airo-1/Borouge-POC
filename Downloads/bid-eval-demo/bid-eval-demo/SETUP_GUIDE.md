# Airo Bid Evaluation Platform - Setup & Testing Guide

## Project Status

✅ **Complete** - All files created and ready to run

## Files Created

### Core Application
- ✅ `app.py` - Main Streamlit app with navigation and sidebar
- ✅ `requirements.txt` - All Python dependencies
- ✅ `.env.example` - Environment variable template
- ✅ `README.md` - Comprehensive documentation

### Utility Modules (`utils/`)
- ✅ `state.py` - Session state management (16 functions)
- ✅ `pdf_parser.py` - PDF/DOCX/TXT text extraction
- ✅ `ai_engine.py` - Claude API integration with sample data generation
- ✅ `report_gen.py` - Professional PDF report generation with ReportLab

### Pages (`pages/`)
- ✅ `1_Upload_Tender.py` - Tender document upload and parsing
- ✅ `2_Upload_Bids.py` - Multi-file bid upload and evaluation
- ✅ `3_Dashboard.py` - Interactive dashboard with 6 analysis sections
- ✅ `4_Reports.py` - PDF report generation and data export
- ✅ `5_Chat.py` - Bid Intelligence Chatbot with quick actions

## Prerequisites

### System Requirements
- Python 3.10 or higher
- 200MB+ free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

### API Requirements
- Anthropic API key (free or paid)
- Internet connection for Claude API calls

## Installation Steps

### Step 1: Verify Python Installation
```bash
python --version
# Should show Python 3.10+

pip --version
# Should work without errors
```

### Step 2: Navigate to Project Directory
```bash
cd "D:\Projects\bid-eval-demo"
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed anthropic streamlit PyMuPDF reportlab plotly pandas python-dotenv
```

### Step 5: Configure API Key

**Option A: Environment File** (Recommended)
```bash
# Copy the example
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env with your API key
# Add: ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**Option B: Environment Variable**
```bash
# Windows Command Prompt
set ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

**Option C: Streamlit Sidebar**
- Launch the app (see Step 6)
- Paste your API key in the sidebar input field
- Stored in session memory only (cleared on refresh)

### Step 6: Run the Application
```bash
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501

  Press CTRL+C to stop
```

### Step 7: Open in Browser
- Automatically opens at http://localhost:8501
- Or manually navigate to the URL shown

## Testing Guide

### Phase 1: Quick Demo (5 minutes)

1. **Start Page 1: Upload Tender**
   - Click "Load Sample Tender" button
   - ✅ Should show tender details and evaluation criteria
   - ✅ Criteria sliders should work
   - ✅ Category breakdown should display

2. **Go to Page 2: Upload Bids**
   - Click "Load Sample Bids" button
   - ✅ Should show 5 supplier evaluation cards
   - ✅ Each card should display scores and details
   - ✅ Expanders should show supplier information

3. **Go to Page 3: Dashboard**
   - ✅ Ranking table should show all 5 suppliers sorted by score
   - ✅ Radar chart should display (Technical, Commercial, Compliance)
   - ✅ Bar charts should render interactively
   - ✅ Compliance matrix should show ✓, ✗, ◐ symbols

4. **Go to Page 4: Reports**
   - Click "Generate Executive Summary"
   - ✅ PDF should be generated and downloadable
   - Click "Generate Comparative Analysis"
   - ✅ Second PDF should be generated

5. **Go to Page 5: Chat**
   - Ask: "Compare the top 2 suppliers"
   - ✅ Should get a response about ValveTech vs PetroFlow
   - Click a quick action button
   - ✅ Should get a relevant response

### Phase 2: PDF Upload Test (10 minutes)

1. **Create Test Documents**
   - Download sample PDF files or use existing ones
   - Ensure PDFs contain business content (not just images)

2. **Test Page 1: Upload PDF**
   - Upload a PDF document
   - ✅ Should show "Analyzing tender document..." spinner
   - ✅ Should extract tender data successfully
   - ✅ Should show "Tender parsed successfully"

3. **Test Page 2: Upload Bids**
   - Upload 2-3 supplier PDF documents
   - ✅ Should show progress bar
   - ✅ Each should be evaluated and show scores
   - ✅ Cards should display evaluation results

### Phase 3: Feature Verification

#### State Management
- Reset Demo button should clear all data
- Navigation between pages should preserve data
- API key should persist in session

#### API Integration
- Tender extraction should succeed (requires API key)
- Bid evaluation should work for all uploaded files
- Chat responses should be contextual and accurate
- Trade-off analysis should generate meaningful narrative

#### Charts & Visualizations
- All Plotly charts should be interactive (hover, zoom, pan)
- Chart colors should match Airo branding
- Charts should display correctly on different screen sizes

#### PDF Generation
- Reports should be downloadable as PDFs
- PDFs should have Airo branding at top
- PDFs should be readable and well-formatted
- CSVs should export correctly

#### Chat Functionality
- Quick action buttons should populate input field
- Chat history should accumulate during session
- Clear Chat button should remove history
- Chat should cite specific supplier data

### Phase 4: Error Handling

1. **Invalid File**
   - Upload a non-PDF file as tender
   - ✅ Should show error message
   - ✅ Should not crash app

2. **No API Key**
   - Don't set API key, try to upload tender
   - ✅ Should show API key warning in sidebar

3. **Large File**
   - Upload a >50MB file
   - ✅ Should handle gracefully

4. **Internet Disconnection**
   - Simulate offline mode
   - ✅ Should show API error message

## Sample Data Reference

### Tender
- **Title**: RFQ-2026-BRG-001: Supply and Maintenance of Industrial Control Valves
- **Organization**: Borouge PLC, Ruwais, UAE
- **Criteria**: 6 evaluation criteria with 100% total weight

### Suppliers
1. **ValveTech Industries** (Germany) - Score: 87/100
2. **PetroFlow Solutions** (UAE) - Score: 84/100
3. **Shanghai Industrial Valves** (China) - Score: 71/100
4. **Flowserve Middle East** (USA/UAE) - Score: 86/100
5. **Al Mansoori Valve Systems** (UAE) - Score: 79/100

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Load app | 3-5 sec | First launch takes longer |
| Load sample tender | 1 sec | Instant |
| Load sample bids | 1 sec | Instant |
| Upload & parse PDF | 5-10 sec | Depends on file size |
| Evaluate bid | 15-30 sec | Claude API call |
| Show dashboard | <1 sec | All local rendering |
| Generate PDF | 2-5 sec | Report generation |
| Chat response | 10-15 sec | Claude API call |

## Troubleshooting

### Issue: "No module named 'streamlit'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Solution: Set API key (see Step 5 above)
# Or enter in sidebar input field
```

### Issue: Port 8501 already in use
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502
```

### Issue: PDF extraction fails
- Ensure PDF is not password-protected
- Try text-based PDF (not scanned image)
- Convert to TXT or DOCX and upload instead

### Issue: Chat not responding
- Check internet connection
- Verify API key is correct
- Check Anthropic API status
- Try reloading the page

### Issue: Charts not displaying
- Ensure browser supports WebGL (older browsers may have issues)
- Try a different browser
- Clear browser cache

## Development Notes

### Code Structure
- **State Management**: Centralized in `utils/state.py`
- **API Calls**: Abstracted in `utils/ai_engine.py`
- **PDF Operations**: Split between parser and generator
- **UI Components**: Clean, reusable Streamlit components

### Adding New Features
1. Add state variables in `utils/state.py`
2. Add AI functions in `utils/ai_engine.py`
3. Add UI in appropriate page file
4. Use existing patterns for consistency

### Modifying Sample Data
Edit `utils/ai_engine.py`:
- `generate_sample_tender_data()` - Change tender details
- `generate_sample_supplier_evaluations()` - Change supplier scores

### Customizing Styling
Edit `app.py`:
- CSS in `st.markdown()` for global styles
- Individual page styles in their respective files
- Color scheme: red (#E63028), black (#1A1A1A), grey (#F5F5F5)

## Deployment Considerations

### For Production Use

1. **Database**
   - Add persistent storage (PostgreSQL, MongoDB)
   - Store project history and user evaluations
   - Track audit trail

2. **Authentication**
   - Add user login (Auth0, OAuth2)
   - Role-based access control
   - API key encryption

3. **Scaling**
   - Use Streamlit Cloud or custom server
   - Implement caching layer
   - Consider async processing for large batches

4. **Security**
   - HTTPS/TLS encryption
   - API rate limiting
   - Input validation and sanitization
   - Data encryption at rest

### Deployment to Streamlit Cloud

```bash
# Push code to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# Go to https://streamlit.io/cloud
# Connect GitHub repository
# Add ANTHROPIC_API_KEY as secret
# Deploy
```

## Next Steps

1. ✅ All files are created and ready
2. Install dependencies: `pip install -r requirements.txt`
3. Set API key: Edit `.env` or set environment variable
4. Run app: `streamlit run app.py`
5. Test with sample data
6. Upload your own tender and bids
7. Export reports and use in presentations

## Success Criteria

Your installation is successful when:
- ✅ App launches without errors
- ✅ Sidebar shows API key input
- ✅ Sample tender loads on Page 1
- ✅ Sample bids load on Page 2
- ✅ Dashboard displays all charts
- ✅ Reports can be generated and downloaded
- ✅ Chat responds to questions

## Support

For issues:
1. Check this guide's Troubleshooting section
2. Review README.md for feature documentation
3. Check Streamlit docs: https://docs.streamlit.io/
4. Check Anthropic API docs: https://docs.anthropic.com/

---

**Ready to launch!** 🚀

Next step: `pip install -r requirements.txt`
