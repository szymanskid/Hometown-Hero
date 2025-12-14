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

### Step 3: Verify Documents and Photos

Before sending proofs to customers, verify the quality of uploaded materials:

**Verify documents:**
```bash
python banner_manager.py update "John Smith" documents_verified yes
```

**Verify photo meets requirements:**
```bash
python banner_manager.py update "John Smith" photo_verified yes
```

### Step 4: Send Proof Notifications

**Option A: Text File Notifications**
```bash
python banner_manager.py notify --status "ready for proof"
```

**Option B: Email Drafts (Recommended)**
```bash
python banner_manager.py email-send
```

This creates professional HTML draft emails in your M365 Drafts folder for all sponsors whose banners are ready (documents and photos verified). Review and send them manually from Outlook. Requires one-time M365 setup (see EMAIL_SETUP.md).

### Step 5: Check for Customer Approvals (Email Only)

```bash
python banner_manager.py email-check
```

Automatically reads inbox for approval responses and updates the database.

### Step 6: Finalize and Print

**Final approval for printing:**
```bash
python banner_manager.py update "John Smith" print_approved yes
```

**Submit to printer:**
```bash
python banner_manager.py update "John Smith" submitted_to_printer yes
```

**Assign pole location:**
```bash
python banner_manager.py update "John Smith" pole_location "Main St & 5th Ave"
```

**Add notes:**
```bash
python banner_manager.py update "John Smith" notes "Family prefers corner location"
```

**Send thank you:**
```bash
python banner_manager.py update "John Smith" thank_you_sent yes
```

### Step 7: Check Status at Any Point

Check what's ready at different stages:

```bash
python banner_manager.py list --status "awaiting verification"
python banner_manager.py list --status "ready to send"
python banner_manager.py list --status "submitted to printer"
python banner_manager.py list --status "complete"
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
4. **Paid - Awaiting Verification** - Ready for staff to verify documents and photo
5. **Documents Verified - Photo Pending** - Documents checked, photo verification needed
6. **Ready to Send Proof** - All verification complete, ready to email customer
7. **Awaiting Customer Approval** - Proof sent, waiting for customer
8. **Proof Approved by Customer** - Customer approved the proof
9. **Approved for Printing** - Staff final signoff given
10. **Submitted to Printer** - Sent to materialpromotions.com
11. **Complete - Thank You Sent** - Banner displayed, thank you sent

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
