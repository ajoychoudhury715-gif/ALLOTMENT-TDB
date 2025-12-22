# ALLOTMENT DASHBOARD - The Dental Bond

A **Streamlit-based real-time scheduling dashboard** for managing dental allotments and procedures.

## Features

✨ **Real-time Scheduling**
- Live updates with auto-refresh every 60 seconds
- Status tracking (WAITING, ARRIVED, ON GOING, CANCELLED)
- Doctor and staff assignments
- Operation theater management
- 🔔 **15-minute reminder notifications** before patient appointments

🎨 **Premium UI Design**
- Beautiful gradient interfaces
- Smooth animations and transitions
- Professional table styling
- Responsive layout
- Loading screen with animated spinner

☁️ **Cloud-Ready**
- **Supabase (Postgres) integration** for persistent cloud storage (recommended)
- Optional **Google Sheets integration** (fallback)
- Works on Streamlit Cloud without data loss
- Falls back to local Excel file for development
- Real-time sync across all users

📊 **Data Management**
- Excel integration (local development)
- Google Sheets integration (production)
- Live data editing
- Automatic save functionality
- Change detection with notifications
- Toast notifications for status updates

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Production)

#### Option 1A (Recommended): Supabase (No Google Sheets)

1. **Create a Supabase project**
   - Go to https://supabase.com and create a new project
   - In the Supabase dashboard → **SQL Editor**, run:

```sql
create table if not exists tdb_allotment_state (
  id text primary key,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);
```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io and deploy this repo
   - In app settings → **Secrets**, add:

```toml
supabase_url = "https://YOUR_PROJECT_REF.supabase.co"
supabase_key = "YOUR_SUPABASE_ANON_KEY"

# Optional (recommended): avoids Row Level Security (RLS) blocking reads/writes
# supabase_service_role_key = "YOUR_SUPABASE_SERVICE_ROLE_KEY"

# Optional overrides:
# supabase_table = "tdb_allotment_state"
# supabase_row_id = "main"
```

The app will store the whole schedule in a single row (`id = "main"`) as JSON.

#### Option 1B: Google Sheets (Alternative)

1. **Create a Google Sheet**
   - Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
   - Add these column headers in row 1:
     `Patient Name, In Time, Out Time, Procedure, DR., FIRST, SECOND, Third, CASE PAPER, OP, SUCTION, CLEANING, STATUS`
   - Copy the spreadsheet URL

2. **Set up Google Cloud Service Account**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable **Google Sheets API** and **Google Drive API**
   - Go to *APIs & Services > Credentials > Create Credentials > Service Account*
   - Create a key for the service account (JSON format)
   - **Important**: Share your Google Sheet with the service account email (with Editor access)

3. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in
   - Click "New app" and select this repository
   - In app settings, go to **Secrets** and add:
   ```toml
   spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
   
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   ```
   - Click Deploy!

### Option 2: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/ajoychoudhury715-gif/ALLOTMENT-TDB.git
cd ALLOTMENT-TDB
```

2. **Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add your Excel file**
- Place `Putt Allotment.xlsx` in the project root directory
- Required sheet: "Sheet1"
- Required columns: Patient Name, In Time, Out Time, Procedure, DR., OP, FIRST, SECOND, Third, CASE PAPER, SUCTION, CLEANING, STATUS

## Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
ALLOTMENT-TDB/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── Putt Allotment.xlsx            # Excel data file
├── The Dental Bond LOGO_page-0001.jpg  # Company logo
└── .github/                        # GitHub configurations
```

## Dependencies

- **streamlit**: Web framework
- **pandas**: Data manipulation
- **openpyxl**: Excel handling
- **streamlit-autorefresh**: Auto-refresh functionality

See `requirements.txt` for full list.

## Features Overview

### Dashboard Sections
1. **Header** - Logo, title, and real-time date/time display
2. **Full Today's Schedule** - Comprehensive table with all procedures
3. **Status Tracking** - Color-coded status indicators
4. **Data Editing** - Inline editing with instant saves

### Status Colors
- 🔵 **WAITING** - Patient waiting for procedure
- 🟢 **ON GOING** - Procedure in progress
- 🟡 **ARRIVED** - Patient has arrived
- 🔴 **CANCELLED** - Procedure cancelled

### Time Format
- Input: HH:MM (12-hour with AM/PM)
- Storage: Decimal format in Excel (9.30 = 09:30)

## Configuration

### Color Theme
Edit the `COLORS` dictionary in `app.py` to customize:
- Background colors
- Text colors
- Accent colors
- Status indicators

### Auto-Refresh Interval
Change the interval in the `st_autorefresh()` call:
```python
st_autorefresh(interval=60000, debounce=True, key="autorefresh")  # 60 seconds
```

## Usage Tips

1. **Adding Patients** - Click "➕ Add Patient" button
2. **Saving Changes** - Click "💾 Save" button (changes auto-save after edits)
3. **Status Updates** - Use dropdown in STATUS column
4. **Real-time Updates** - Dashboard refreshes automatically every 60 seconds

## Troubleshooting

### Excel File Not Found
- Ensure `Putt Allotment.xlsx` is in the same directory as `app.py`
- Check that the filename matches exactly (case-sensitive)

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Auto-refresh Not Working
Install the missing package:
```bash
pip install streamlit-autorefresh
```

## Development

### Code Structure
- **Imports & Config** - Lines 1-30
- **Color Customization** - Lines 26-36
- **CSS Styling** - Lines 45-430
- **Header Section** - Lines 440-490
- **Data Loading** - Lines 500-570
- **Data Processing** - Lines 580-700
- **UI Components** - Lines 800+

### Adding Features
1. Create a new function in the appropriate section
2. Update the CSS if adding new UI elements
3. Test with sample data
4. Document changes in this README

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit changes (`git commit -m 'Add amazing feature'`)
3. Push to branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is proprietary software for The Dental Bond.

## Support

For issues or questions, please contact the development team.

## Version History

### v1.0.0 (Current)
- Initial release
- Premium UI design
- Real-time scheduling
- Excel integration
- Auto-refresh functionality

---

**Made with ❤️ for The Dental Bond**
