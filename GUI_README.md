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

3. **View your banners**:
   - Go to "Dashboard" to see overall statistics
   - Go to "Banner List" to see individual banners

### Daily Workflow

1. **Import Latest Data**:
   - Navigate to "Import CSV"
   - Upload fresh CSV exports from Wix
   - System preserves your notes and pole locations

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
- Database file remains on your local system
- Email credentials are stored in `m365_config.json` locally
- When running on a network, ensure your network is trusted

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
