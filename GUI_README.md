# Hometown Hero Banner Management - GUI Application

## 🚀 Quick Start

The Hometown Hero Banner Management System now includes a user-friendly graphical interface built with Streamlit!

### Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the GUI**:
   ```bash
   streamlit run gui_app.py
   ```

The application will automatically open in your default web browser at `http://localhost:8501`

## 📦 Deployment on Shared Drive

For teams working from a shared network drive (e.g., `Q:\HHBanners2026`), the system supports external data storage for safe code updates and per-machine Python environments.

### Quick Setup for Shared Deployment

1. **Clone repository to shared drive**:
   ```bash
   cd Q:\HHBanners2026
   git clone https://github.com/szymanskid/Hometown-Hero.git
   ```

2. **Create external data folder**:
   ```bash
   mkdir Q:\HHBanners2026-data
   ```

3. **Configure paths** in `Q:\HHBanners2026-data\.env`:
   ```
   HH_DB_PATH=Q:\HHBanners2026-data\hometown_hero.db
   HH_M365_CONFIG=Q:\HHBanners2026-data\m365_config.json
   HH_EXPORT_DIR=Q:\HHBanners2026-data\exports
   ```

4. **Set up per-machine Python** (each computer):
   ```bash
   python -m venv C:\venvs\hometown-hero
   C:\venvs\hometown-hero\Scripts\activate
   pip install -r Q:\HHBanners2026\Hometown-Hero\requirements.txt
   ```

5. **Run using the helper script**:
   - Edit `scripts\run_app.bat`:
     - Set `VENV_PATH=C:\venvs\hometown-hero`
     - Set `DATA_DIR=Q:\HHBanners2026-data`
   - Double-click `scripts\run_app.bat` to launch

### Updating Code

When updates are available, use the update script:
```bash
cd Q:\HHBanners2026\Hometown-Hero
scripts\update_code.bat
```

This safely updates code without touching your data files.

### Configuration Status Panel

The Dashboard now includes a "Configuration Status" panel that shows:
- **Database Path**: Current database location and accessibility
- **M365 Config Path**: Email configuration location
- **Network Storage Warning**: Alert if database is on network drive (important for concurrent access)
- **Configuration Warnings**: Any issues with paths or permissions

Click the panel to expand and view details.

### Environment Variables

You can configure paths using environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `HH_DB_PATH` | `./hometown_hero.db` | Path to SQLite database |
| `HH_M365_CONFIG` | `./m365_config.json` | Path to M365 config |
| `HH_EXPORT_DIR` | `./exports` | Directory for exports |
| `HH_CONFIG_DIR` | (none) | External config directory |

**Using .env file** (recommended for shared deployment):
```bash
# Create Q:\HHBanners2026-data\.env
HH_DB_PATH=Q:\HHBanners2026-data\hometown_hero.db
HH_M365_CONFIG=Q:\HHBanners2026-data\m365_config.json
HH_EXPORT_DIR=Q:\HHBanners2026-data\exports

# Set environment variable to use external config
set HH_CONFIG_DIR=Q:\HHBanners2026-data
```

### Multi-User Access

**Important considerations for shared deployment:**
- Only one user should write to the database at a time
- Multiple users can safely browse/view data
- Consider running Streamlit centrally on a server for browser-only access:
  ```bash
  streamlit run gui_app.py --server.address 0.0.0.0 --server.port 8501
  ```
- Check the Configuration Status panel for network storage warnings

## 🎯 Features

The GUI provides a streamlined interface for all banner management tasks:

### 📊 Dashboard
- View summary statistics at a glance
- See banner counts by status
- Visual status breakdown with charts

### 📥 Import CSV
- Upload hero information and payment CSV files
- Drag-and-drop file upload interface
- Automatic processing and database updates
- **NEW**: Comprehensive import diagnostics report showing:
  - Total heroes and payments imported
  - Match statistics (heroes with/without payments)
  - Detailed tables of unmatched records
  - Downloadable mismatch CSV files for analysis
  - Duplicate payment detection

### 📋 Banner List
- View all banners in an organized list
- Filter by status
- Search by hero or sponsor name
- Expandable cards showing full banner details

### ✏️ Update Banner
- Select any banner from a dropdown
- Update verification flags with checkboxes
- Set pole locations and add notes
- Real-time status updates

### 📧 Notifications
- See which banners are ready for notification
- Generate text notifications with one click
- Automatic status updates

### 📧 Email Management
- **Setup**: Configure Microsoft 365 email integration
- **Send Emails**: Create draft emails in your Outlook Drafts folder
- **Check Responses**: Automatically process approval responses from inbox

## 🖥️ Using the GUI

### First Time Setup

1. **Launch the application**:
   ```bash
   streamlit run gui_app.py
   ```

2. **Import your CSV files**:
   - Go to "Import CSV" in the sidebar
   - Upload your hero information CSV
   - Upload your payment CSV
   - Click "Import CSV Files"
   - **Review the import summary report** to see:
     - How many heroes and payments were imported
     - Which heroes don't have matching payments
     - Which payments don't have matching heroes
     - Any duplicate payment records detected
   - Download mismatch CSV files if you need to investigate further

3. **View your banners**:
   - Go to "Dashboard" to see overall statistics
   - Go to "Banner List" to see individual banners

### Daily Workflow

1. **Import Latest Data**:
   - Navigate to "Import CSV"
   - Upload fresh CSV exports from Wix
   - Review the import summary to see match statistics
   - System preserves your notes and pole locations
   - All heroes are imported, even without payments

2. **Verify Documents and Photos**:
   - Go to "Update Banner"
   - Select a banner from the dropdown
   - Check "Documents Verified" and "Photo Verified"
   - Click "Update Banner"

3. **Send Notifications**:
   - Go to "Email Management" → "Send Emails"
   - Click "Create Draft Emails in Outlook"
   - Review and send from Outlook

4. **Check for Approvals**:
   - Go to "Email Management" → "Check Responses"
   - Click "Check Inbox for Approvals"
   - System automatically updates banner statuses

5. **Finalize Banners**:
   - Go to "Update Banner"
   - Mark as "Approved for Printing"
   - Add pole location
   - Mark as "Submitted to Printer"
   - Eventually mark as "Thank You Sent"

## 📖 Comparison: CLI vs GUI

Both interfaces access the same database and can be used interchangeably:

| Feature | CLI Command | GUI Location |
|---------|-------------|--------------|
| Import CSV | `python banner_manager.py import --hero file1.csv --payment file2.csv` | Import CSV page |
| List banners | `python banner_manager.py list` | Banner List page |
| Update banner | `python banner_manager.py update "John Smith" pole_location "Main St"` | Update Banner page |
| Send notifications | `python banner_manager.py notify --status "ready for proof"` | Notifications page |
| Email setup | `python banner_manager.py email-setup` | Email Management → Setup |
| Send emails | `python banner_manager.py email-send` | Email Management → Send Emails |
| Check emails | `python banner_manager.py email-check` | Email Management → Check Responses |
| View summary | `python banner_manager.py summary` | Dashboard |

## 🔧 Advanced Options

### Running on a Different Port

```bash
streamlit run gui_app.py --server.port 8502
```

### Running on Network (accessible from other computers)

```bash
streamlit run gui_app.py --server.address 0.0.0.0
```

### Configuration

Streamlit configuration can be customized in `.streamlit/config.toml`. Create this file for advanced settings like:
- Theme customization
- Server settings
- Browser behavior

## 📱 Mobile Access

The Streamlit interface is responsive and works on tablets and mobile devices. Simply access the URL from any device on your network.

## 🔒 Security Notes

- The GUI runs locally on your computer by default
- Database and configuration files can be stored externally (e.g., on a shared drive)
- Email credentials in `m365_config.json` should be protected with appropriate file permissions
- When running on a network, ensure your network is trusted
- The Configuration Status panel warns when database is on network storage
- Use `.gitignore` to prevent committing sensitive data (database, config files already ignored)

## 🐛 Troubleshooting

### GUI won't start
```bash
# Check if streamlit is installed
pip show streamlit

# Reinstall if needed
pip install --upgrade streamlit
```

### Port already in use
```bash
# Use a different port
streamlit run gui_app.py --server.port 8502
```

### Database locked error
- Close any other instances of the application
- Make sure the CLI isn't running simultaneously
- Check that `hometown_hero.db` isn't open in another program

### Import CSV fails
- Ensure CSV files are properly formatted
- Check that files contain the expected columns
- See README.md for CSV format details

### Import shows fewer heroes than expected
**The import diagnostics will help you troubleshoot this!**

After import, check the **Import Summary Report** that appears:
1. **Total Heroes** - Should match the number of PUBLISHED entries in your hero CSV
2. **Heroes without Payment** - Shows how many heroes don't have matching payments
3. **Unmatched Heroes table** - Lists specific heroes and why they're unmatched

**Common reasons for mismatches:**
- Sponsor names spelled differently in hero vs payment CSV
- Extra whitespace or capitalization differences (system auto-normalizes these)
- Payment status is not "CONFIRMED" in the payment CSV
- Missing sponsor name in hero CSV

**Important:** All heroes are still imported into the database, even without payments. They'll show status "Info Complete - Payment Pending" until a payment is matched.

### Viewing detailed mismatch information
1. After import, scroll down to see the unmatched tables
2. Click "Download Unmatched Heroes CSV" to save a detailed report
3. Open the CSV in Excel to review which heroes are missing payments and why
4. Compare sponsor names between your two CSV files to find spelling differences

### Example scenario: 56 heroes, 40 payments
- ✅ All 56 heroes will be imported
- ✅ Dashboard will show "Total Banners: 56"
- ✅ Import report will show "Heroes with Payment: 40"
- ✅ Import report will show "Heroes without Payment: 16"
- ✅ The 16 unmatched heroes will be listed in a table with reasons

## 📚 Additional Resources

- **Full Documentation**: See [README.md](README.md) for complete system documentation
- **Email Setup**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for Microsoft 365 configuration
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for workflow examples

## 🆘 Support

For issues or questions, please refer to the Millcreek Kiwanis organization.

## 💡 Tips

- **Refresh Data**: Click the refresh button (⟳) in the top-right corner to reload data
- **Keyboard Shortcuts**: Press `Ctrl+R` or `Cmd+R` to refresh the page
- **Multiple Tabs**: Open multiple browser tabs to view different sections simultaneously
- **Export Data**: Use "Banner List" to view and copy data for external use
- **Both Interfaces**: The CLI and GUI can be used together - they share the same database

## 🎨 Features Comparison

**GUI Advantages:**
- ✅ Visual interface - no command memorization needed
- ✅ File upload with drag-and-drop
- ✅ Real-time statistics and charts
- ✅ Point-and-click updates
- ✅ Form validation
- ✅ Better for occasional users
- ✅ Accessible from any device with a browser

**CLI Advantages:**
- ✅ Faster for experienced users
- ✅ Can be automated with scripts
- ✅ Works over SSH
- ✅ Better for batch operations
- ✅ Lower resource usage

Choose the interface that best suits your workflow!
