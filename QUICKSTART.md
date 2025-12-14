# Quick Start Guide

## Initial Setup

1. **Install Python 3.8 or higher** if not already installed

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   For email automation (optional):
   ```bash
   pip install O365
   ```

3. **Place your CSV files** in the project directory:
   - `Final+Attempt+CMS+11_3.csv` (hero information from Wix)
   - `MILITARY+BANNER+2026+-+Payment.csv` (payment information from Wix)

## Daily Workflow

### Step 1: Import Latest CSV Files from Wix

```bash
python banner_manager.py import --hero "Final+Attempt+CMS+11_3.csv" --payment "MILITARY+BANNER+2026+-+Payment.csv"
```

This will:
- Import all PUBLISHED hero records (DRAFT entries are skipped)
- Match payments with CONFIRMED status
- Update banner information while preserving your notes and pole locations

### Step 2: Review Current Status

```bash
python banner_manager.py list
```

Or filter by specific status:
```bash
python banner_manager.py list --status "ready for proof"
python banner_manager.py list --status "incomplete"
python banner_manager.py list --status "payment pending"
```

### Step 3: Send Notifications

**Option A: Text File Notifications**
```bash
python banner_manager.py notify --status "ready for proof"
```

**Option B: Email Drafts (Recommended)**
```bash
python banner_manager.py email-send
```

This creates professional HTML draft emails in your M365 Drafts folder for all sponsors whose banners are ready. Review and send them manually from Outlook. Requires one-time M365 setup (see EMAIL_SETUP.md).

### Step 4: Check for Approvals (Email Only)

```bash
python banner_manager.py email-check
```

Automatically reads inbox for approval responses and updates the database.

### Step 5: Track Banner Progress

**Assign pole location:**
```bash
python banner_manager.py update "John Smith" pole_location "Main St & 5th Ave"
```

**Add notes:**
```bash
python banner_manager.py update "John Smith" notes "Family prefers corner location"
```

**Mark proof as approved:**
```bash
python banner_manager.py update "John Smith" proof_approved yes
```

**Final signoff for printing:**
```bash
python banner_manager.py update "John Smith" print_approved yes
```

### Step 6: Check What's Ready to Print

```bash
python banner_manager.py list --status "printing"
```

## Email Automation Setup (One-Time)

For automated email notifications and approval tracking:

1. **Create config template:**
   ```bash
   python banner_manager.py email-setup
   ```

2. **Follow setup guide:** See `EMAIL_SETUP.md` for complete Azure AD configuration

3. **Test it:**
   ```bash
   python banner_manager.py email-send
   python banner_manager.py email-check
   ```

## Banner Status Flow

1. **Incomplete** - Missing information or payment
2. **Info Complete - Payment Pending** - All info present, waiting for payment
3. **Paid - Info Incomplete** - Payment received, missing information
4. **Ready for Proof** - Ready to notify client
5. **Awaiting Proof Approval** - Notification sent, waiting for client
6. **Proof Approved** - Client approved
7. **Ready for Printing** - Final signoff, ready to print

## Tips

- **Re-import CSVs often** - Your notes and pole locations are preserved in the database
- **Use the summary command** to get a quick overview: `python banner_manager.py summary`
- **Filter by status** to focus on specific stages of the workflow
- **Keep the database file** (`hometown_hero.db`) - it contains your pole locations and notes
- **Email automation saves time** - Set up once, then fully automated notifications

## Common Scenarios

### Sponsor name doesn't match
If a payment isn't matching, check that the "Your Name" in the payment CSV exactly matches the "Name of Buyer" in the hero CSV. The system does a case-insensitive match but the names must be identical.

### Re-importing updates
When you re-import CSVs:
- Hero info and payment status are updated from the CSVs
- Your pole locations and notes are preserved
- Status flags (proof_sent, proof_approved, print_approved) are preserved

### Finding specific banners
Use partial name matching:
```bash
python banner_manager.py update "Smith" pole_location "Main St"
```

If multiple matches are found, you'll be asked to be more specific.

## Backup

To backup your data, simply copy these files to a safe location:
- `hometown_hero.db` - All banner data, pole locations, and notes
- `m365_config.json` - Email configuration (if using email automation)

## Questions?

- **General usage**: See `README.md` for detailed documentation
- **Email setup**: See `EMAIL_SETUP.md` for step-by-step Azure AD configuration
- **Troubleshooting**: Check documentation or contact support
