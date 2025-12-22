# ALLOTMENT DASHBOARD - The Dental Bond

A **Streamlit-based real-time scheduling dashboard** for managing dental allotments and procedures.

## Features

✨ **Real-time Scheduling**
- Live updates with auto-refresh every 60 seconds
- Status tracking (WAITING, ARRIVED, ON GOING, CANCELLED)
- Doctor and staff assignments
- Operation theater management

🎨 **Premium UI Design**
- Beautiful gradient interfaces
- Smooth animations and transitions
- Professional table styling
- Responsive layout
- Loading screen with animated spinner

📊 **Data Management**
- Excel integration (Putt Allotment.xlsx)
- Live data editing
- Automatic save functionality
- Change detection with notifications
- Toast notifications for status updates

## Installation

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
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
