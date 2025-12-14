# Quick Start Guide

## Initial Setup

1. **Install Python 3.8 or higher** if not already installed

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
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

### Step 3: Send Proof Ready Notifications

```bash
python banner_manager.py notify --status "ready for proof"
```

This generates notifications for all banners that:
- Have complete information
- Have verified payment (Status = CONFIRMED)
- Haven't been sent notifications yet

Notifications are saved to `notifications.txt`

### Step 4: Track Banner Progress

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

### Step 5: Check What's Ready to Print

```bash
python banner_manager.py list --status "printing"
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

To backup your data, simply copy the `hometown_hero.db` file to a safe location. This file contains all your pole locations, notes, and tracking information.

## Questions?

Refer to the full README.md for detailed documentation.
