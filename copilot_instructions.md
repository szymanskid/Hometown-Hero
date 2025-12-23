# Copilot Instructions for Hometown Hero Banner Management System

## Project Overview

This is a banner management system for the Millcreek Kiwanis Hometown Hero program. It processes CSV files from Wix, verifies banner information completeness, tracks payments, manages client notifications, and handles the signoff process for banner printing.

## Architecture

### Dual Interface System
The project provides **two interfaces** that share the same SQLite database:

1. **CLI Interface** (`banner_manager.py`) - Command-line interface for scripting and automation
2. **GUI Interface** (`gui_app.py`) - Streamlit web-based interface for visual interaction

Both interfaces are **equally important** and must remain functional. Changes to one should not break the other.

## Core Components

### Database Layer
- **File**: `database.py`
- **Purpose**: SQLite database operations via `BannerDatabase` class
- **Database**: `hometown_hero.db` (auto-created, gitignored)
- **Important**: All data operations go through this layer to ensure consistency

### Data Models
- **File**: `models.py`
- **Classes**:
  - `HeroInfo` - Hero information from CMS CSV
  - `PaymentInfo` - Payment information from payment CSV
  - `BannerRecord` - Complete banner record with persistent data
- **Key Method**: `BannerRecord.get_status()` - Returns human-readable status based on flags

### CSV Processing
- **File**: `csv_processor.py`
- **Purpose**: Parse hero and payment CSV files from Wix
- **Methods**:
  - `parse_hero_csv()` - Parses hero information
  - `parse_payment_csv()` - Parses payment records
  - `match_hero_to_payment()` - Matches payment to hero by sponsor name

### Notifications
- **File**: `notifications.py`
- **Purpose**: Generate text-based notifications for clients
- **Output**: `notifications.txt` (gitignored)

### Email Service (Optional)
- **File**: `email_service.py`
- **Purpose**: Microsoft 365 email integration for automated notifications
- **Config**: `m365_config.json` (gitignored)
- **Requires**: `O365` package (optional dependency)

## Workflow & Status System

### Banner Status Flow
Banners progress through these statuses (defined in `BannerRecord.get_status()`):

1. **Incomplete** - Missing required information or payment
2. **Info Complete - Payment Pending** - All info present, waiting for payment
3. **Paid - Info Incomplete** - Payment received, missing information
4. **Paid - Awaiting Verification** - Ready for staff to verify documents/photo
5. **Documents Verified - Photo Pending** - Documents checked, photo verification needed
6. **Ready to Send Proof** - All verification complete, ready to email customer
7. **Awaiting Customer Approval** - Proof sent, waiting for customer
8. **Proof Approved by Customer** - Customer approved the proof
9. **Approved for Printing** - Staff final signoff given
10. **Submitted to Printer** - Sent to materialpromotions.com
11. **Complete - Thank You Sent** - Banner displayed, thank you sent

### Persistent Data
The following data persists across CSV imports (stored in database):
- Pole location assignments
- Notes about each banner
- All verification flags (documents_verified, photo_verified, etc.)
- Proof sent/approved status
- Print approval status
- All timestamps

## Development Guidelines

### When Adding Features

1. **Database Changes**: Always modify `database.py` first, then update `models.py` if needed
2. **CLI Interface**: Update `banner_manager.py` to add new commands
3. **GUI Interface**: Update `gui_app.py` to add new UI sections
4. **Keep in Sync**: Ensure both interfaces can access the same functionality

### Testing Approach

```bash
# Test CLI
python banner_manager.py import --hero sample_hero_cms.csv --payment sample_payment.csv
python banner_manager.py list
python banner_manager.py summary

# Test GUI
streamlit run gui_app.py
# Then manually test in browser at http://localhost:8501
```

### Important Files to Preserve

**Never delete or gitignore:**
- `hometown_hero.db` - Contains all persistent data (already gitignored)
- Sample CSV files - Used for testing

**Already gitignored:**
- `hometown_hero.db`, `*.db` - Database files
- `notifications.txt` - Generated notifications
- `m365_config.json` - Email configuration
- `o365_token.txt` - OAuth token
- `streamlit.log` - Streamlit logs
- `.streamlit/` - Streamlit config directory

### Code Style & Standards

1. **Error Handling**: Use specific exceptions (e.g., `OSError`, `FileNotFoundError`) not bare `except:`
2. **Temporary Files**: Use `tempfile` module for cross-platform compatibility
3. **Null Checks**: Always check if config/data exists before accessing properties
4. **Documentation**: Keep README.md, GUI_README.md, and QUICKSTART.md in sync with features
5. **Backward Compatibility**: Never break existing CLI commands or database schema without migration

### Common Pitfalls to Avoid

1. **Don't hardcode paths** - Use `tempfile` for temp files, `Path` for file operations
2. **Don't assume OS** - Code must work on Windows, Mac, and Linux
3. **Don't break CLI** - GUI is an addition, not a replacement
4. **Don't modify database schema** - Without careful migration planning
5. **Don't commit sensitive data** - Check `.gitignore` before committing

## Building & Running

### Dependencies
```bash
pip install -r requirements.txt
```

**Core dependencies:**
- `pandas>=2.0.0` - CSV processing
- `python-dateutil>=2.8.2` - Date parsing
- `streamlit>=1.28.0` - GUI framework

**Optional dependencies:**
- `O365>=2.0.27` - Email automation (only needed if using email features)

### Launch Methods

**CLI:**
```bash
python banner_manager.py --help
```

**GUI:**
```bash
streamlit run gui_app.py
# Or use convenience scripts:
./start_gui.sh        # Unix/Linux/Mac
start_gui.bat         # Windows
```

## Common Tasks for Copilot

### Adding a New Field to Banners

1. Update `models.py` - Add field to `BannerRecord` dataclass
2. Update `database.py` - Add column in schema and CRUD operations
3. Update `banner_manager.py` - Add CLI command/option to update the field
4. Update `gui_app.py` - Add UI control to update the field
5. Test both interfaces

### Adding a New Status

1. Update `BannerRecord.get_status()` in `models.py`
2. Update documentation in README.md and QUICKSTART.md
3. Test status transitions in both CLI and GUI

### Fixing Bugs

1. **Identify scope** - Does it affect CLI, GUI, or both?
2. **Check database layer** - Most bugs originate from data operations
3. **Test both interfaces** - Even if bug is in one, verify the other still works
4. **Run validation** - Use sample CSVs to ensure no regression

### Security Considerations

1. **Input Validation** - Always validate CSV data before processing
2. **File Operations** - Use safe file handling (tempfile, proper cleanup)
3. **Email Credentials** - Never commit `m365_config.json`
4. **SQL Injection** - Use parameterized queries (already done in database.py)
5. **Run CodeQL** - Before finalizing changes

## Documentation Structure

- **README.md** - Main documentation, includes both CLI and GUI
- **GUI_README.md** - Detailed GUI-specific guide
- **QUICKSTART.md** - Quick start for CLI workflow
- **EMAIL_SETUP.md** - Microsoft 365 email setup guide
- **copilot_instructions.md** (this file) - Development guide for AI assistants

## Questions to Ask Users

When unclear about requirements:

1. "Should this feature work in CLI, GUI, or both?"
2. "Do we need to preserve backward compatibility?"
3. "Should existing data be migrated or is fresh start OK?"
4. "Is this for the current year's banners or future years too?"

## Useful Commands for Development

```bash
# Check database contents
sqlite3 hometown_hero.db "SELECT * FROM banners;"

# Run CLI in debug mode
python -u banner_manager.py <command>

# Check what files would be committed
git status
git diff

# Validate Python syntax
python -m py_compile gui_app.py
python -m py_compile banner_manager.py

# Test imports
python -c "from gui_app import *; print('OK')"
python -c "from banner_manager import *; print('OK')"
```

## Repository Best Practices

1. **Commit frequently** - Small, focused commits with clear messages
2. **Test before committing** - Verify both CLI and GUI work
3. **Update documentation** - Keep docs in sync with code changes
4. **Use .gitignore** - Don't commit generated files, databases, or configs
5. **Security scan** - Run CodeQL before completing work

## Getting Help

If you need to understand the codebase better:

1. Start with `models.py` - Understand the data structures
2. Read `database.py` - Understand data operations
3. Check `banner_manager.py` - See CLI commands and logic
4. Review `gui_app.py` - See GUI implementation
5. Look at sample CSV files - Understand input format

## Current State (as of Dec 2025)

- ✅ CLI fully functional with all features
- ✅ GUI fully functional with 6 sections
- ✅ Both interfaces share same database
- ✅ Email integration optional but working
- ✅ Documentation comprehensive and up-to-date
- ✅ Cross-platform compatible (Windows/Mac/Linux)
- ✅ Security scan passed (CodeQL)
- ✅ Code quality reviewed and improved

## Future Enhancement Ideas

Ideas for future Copilot sessions (not yet implemented):

- Bulk operations in GUI (update multiple banners at once)
- Export functionality (generate reports, CSV exports)
- Photo management (upload/view photos directly in GUI)
- Pole location mapping (visual map of pole assignments)
- Year-over-year comparison (track banners across years)
- Automated backup system
- Multi-user support with authentication
- Print queue management
- Integration with printer API

Remember: Always maintain backward compatibility and keep both CLI and GUI functional!
