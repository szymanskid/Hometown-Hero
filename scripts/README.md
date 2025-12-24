# Deployment Scripts

This directory contains helper scripts for deploying and running the Hometown Hero Banner Management System on Windows.

## Scripts

### update_code.bat

**Purpose**: Safely update code from GitHub without affecting data or configuration files.

**Usage**:
```batch
cd Q:\HHBanners2026\Hometown-Hero
scripts\update_code.bat
```

**What it does**:
1. Checks Git availability
2. Shows current repository status
3. Fetches latest code from GitHub
4. Displays available updates
5. Asks for confirmation before applying updates
6. Uses `git pull --ff-only` to safely update (fast-forward only)
7. Provides clear error messages if update fails

**Safety features**:
- Never touches your data files (hometown_hero.db)
- Never modifies configuration (m365_config.json, .env)
- Shows changes before applying them
- Uses fast-forward-only merge (no complex merges)
- Clear rollback instructions if something goes wrong

### run_app.bat

**Purpose**: Run the GUI application with proper virtual environment and external data configuration.

**Configuration** (edit the script to customize):
```batch
REM Path to your Python virtual environment
SET VENV_PATH=C:\venvs\hometown-hero

REM Path to external data folder
SET DATA_DIR=Q:\HHBanners2026-data
```

**Usage**:
```batch
cd Q:\HHBanners2026\Hometown-Hero
scripts\run_app.bat
```

**What it does**:
1. Activates your Python virtual environment
2. Sets environment variables for data paths (HH_DB_PATH, HH_M365_CONFIG, HH_EXPORT_DIR)
3. Creates data directory if it doesn't exist
4. Verifies Python and Streamlit are installed
5. Launches the Streamlit GUI application

**Benefits**:
- Each computer can use its own Python environment
- Data stays on shared drive, accessible to all
- Simple double-click to run the application
- Automatic error checking and helpful messages

## Setup Instructions

### Initial Setup

1. **Clone repository** (one time, on shared drive):
   ```batch
   cd Q:\HHBanners2026
   git clone https://github.com/szymanskid/Hometown-Hero.git
   ```

2. **Create data directory** (one time):
   ```batch
   mkdir Q:\HHBanners2026-data
   ```

3. **Set up Python environment** (on each computer that will run the app):
   ```batch
   python -m venv C:\venvs\hometown-hero
   C:\venvs\hometown-hero\Scripts\activate
   pip install -r Q:\HHBanners2026\Hometown-Hero\requirements.txt
   ```

4. **Configure run_app.bat**:
   - Open `scripts\run_app.bat` in a text editor
   - Set `VENV_PATH=C:\venvs\hometown-hero`
   - Set `DATA_DIR=Q:\HHBanners2026-data`
   - Save the file

### Daily Use

**To run the application**:
```batch
cd Q:\HHBanners2026\Hometown-Hero
scripts\run_app.bat
```

**To update code** (when new features are released):
```batch
cd Q:\HHBanners2026\Hometown-Hero
scripts\update_code.bat
```

After updating code, if new dependencies were added:
```batch
C:\venvs\hometown-hero\Scripts\activate
pip install -r requirements.txt
```

## Troubleshooting

### "Git is not installed"
- Download and install Git from https://git-scm.com/
- Make sure to select "Add Git to PATH" during installation

### "Python is not installed"
- Download and install Python 3.8+ from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### "Virtual environment not found"
- Check that `VENV_PATH` in `run_app.bat` points to the correct location
- Recreate the virtual environment if needed

### "Database locked error"
- Make sure no other user is currently writing to the database
- Close any other instances of the application
- Database is safe for multiple readers, but only one writer at a time

### Update fails with "merge conflicts"
- This usually means code files were modified directly
- Contact support for help resolving conflicts
- Your data files are always safe during updates

## Multi-User Considerations

When multiple people use the system:

1. **Database writes**: Only one person should modify data (add/update records) at a time
2. **Read-only access**: Multiple people can safely view/browse data simultaneously
3. **Code updates**: Coordinate updates so everyone knows when to restart their app
4. **Central deployment**: Consider running Streamlit on a server with:
   ```batch
   streamlit run gui_app.py --server.address 0.0.0.0 --server.port 8501
   ```
   Then users access via browser: `http://server-name:8501`

## Alternative: Manual Commands

If you prefer not to use the scripts, here are the manual commands:

**Update code**:
```batch
cd Q:\HHBanners2026\Hometown-Hero
git fetch origin main
git switch main
git pull --ff-only origin main
```

**Run application**:
```batch
cd Q:\HHBanners2026\Hometown-Hero
C:\venvs\hometown-hero\Scripts\activate
set HH_DB_PATH=Q:\HHBanners2026-data\hometown_hero.db
set HH_M365_CONFIG=Q:\HHBanners2026-data\m365_config.json
set HH_EXPORT_DIR=Q:\HHBanners2026-data\exports
streamlit run gui_app.py
```
