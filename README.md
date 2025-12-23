# Hometown Hero Banner Management System

A comprehensive system for managing the Millcreek Kiwanis Hometown Hero banner program. This system processes CSV files from Wix, verifies banner information completeness, tracks payments, manages client notifications, and handles the signoff process for banner printing.

## 🎉 NEW: Graphical User Interface

**No more confusing command-line scripts!** We now offer a user-friendly web-based GUI:

```bash
streamlit run gui_app.py
```

👉 **See [GUI_README.md](GUI_README.md) for the complete GUI guide**

The GUI provides:
- 📊 Visual dashboard with statistics and charts
- 📥 Drag-and-drop CSV file upload
- 📋 Searchable, filterable banner list
- ✏️ Point-and-click banner updates
- 📧 Email management interface
- 🎨 Mobile-friendly responsive design

**Both the GUI and CLI work with the same database**, so you can use whichever interface you prefer!

---

## Features

- **CSV Import**: Automatically process hero information and payment data from Wix CSV exports
- **Data Validation**: Verify that all required banner information is present
- **Payment Verification**: Match and verify payment records against hero records
- **Persistent Storage**: SQLite database stores pole locations and notes that persist across CSV imports
- **Notification System**: Generate client notifications when proofs are ready
- **Email Automation** ⭐: Automated email notifications via Microsoft 365 with approval tracking
- **Signoff Workflow**: Track proof approval and print approval status
- **Status Tracking**: Monitor banners through their complete lifecycle
- **GUI & CLI** ⭐ NEW: Choose between graphical or command-line interface

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your interface**:
   - **GUI (Recommended for most users)**: `streamlit run gui_app.py`
   - **CLI (For advanced users)**: `python banner_manager.py --help`

## Usage

### Option 1: Graphical User Interface (Recommended)

Launch the web-based GUI:

```bash
streamlit run gui_app.py
```

The application will open in your browser. See [GUI_README.md](GUI_README.md) for detailed instructions.

### Option 2: Command Line Interface

#### Import CSV Files

When you download new CSV files from Wix, import them to update the database:

```bash
python banner_manager.py import --hero "Final+Attempt+CMS+11_3.csv" --payment "MILITARY+BANNER+2026+-+Payment.csv"
```

This will:
- Parse both CSV files
- Check for complete banner information
- Verify payment status
- Update the database with current status

### List All Banners

View all banners and their current status:

```bash
python banner_manager.py list
```

### Filter by Status

View banners with a specific status:

```bash
python banner_manager.py list --status "ready for proof"
python banner_manager.py list --status "incomplete"
python banner_manager.py list --status "paid"
```

### Send Notifications

Generate notifications for clients whose proofs are ready:

```bash
python banner_manager.py notify --status "ready for proof"
```

This will:
- Find all banners with complete info and verified payment
- Generate notification messages
- Save notifications to `notifications.txt`
- Mark banners as "proof sent"

### Email Automation (Optional)

**Create draft emails for client notifications using your Microsoft 365 account:**

1. **Setup** (one-time):
   ```bash
   python banner_manager.py email-setup
   ```
   Then edit `m365_config.json` with your Azure AD app credentials. See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed setup instructions.

2. **Create draft emails**:
   ```bash
   python banner_manager.py email-send
   ```
   Creates professional HTML draft emails in your Drafts folder for all sponsors whose banners are ready. Review and send them manually from Outlook.

3. **Check for approval responses**:
   ```bash
   python banner_manager.py email-check
   ```
   Automatically reads your inbox for approval emails and updates the database.

**Benefits:**
- ✅ Professional HTML emails with approval instructions
- ✅ Draft emails for your review before sending
- ✅ Automatic database updates from email responses
- ✅ No duplicate notifications
- ✅ Complete audit trail

See [EMAIL_SETUP.md](EMAIL_SETUP.md) for complete setup guide.

### Update Banner Information

Set the pole location for a banner:

```bash
python banner_manager.py update "John Smith" pole_location "Main St & 1st Ave"
```

Add notes about a banner:

```bash
python banner_manager.py update "John Smith" notes "Family requested corner location"
```

Mark proof as approved by client:

```bash
python banner_manager.py update "John Smith" proof_approved yes
```

Mark banner as approved for printing:

```bash
python banner_manager.py update "John Smith" print_approved yes
```

### View Summary Statistics

Get a quick overview of all banner statuses:

```bash
python banner_manager.py summary
```

## Banner Status Workflow

The system tracks banners through the following statuses based on the complete verification and approval workflow:

1. **Incomplete** - Missing required information or payment
2. **Info Complete - Payment Pending** - All info present, waiting for payment
3. **Paid - Info Incomplete** - Payment received, missing some information  
4. **Paid - Awaiting Verification** - Payment received and info complete, ready for staff review
5. **Documents Verified - Photo Pending** - Documents checked, waiting for photo verification
6. **Ready to Send Proof** - All verification complete (documents and photo), ready to create draft email
7. **Awaiting Customer Approval** - Proof email sent, waiting for customer to approve
8. **Proof Approved by Customer** - Customer approved the proof
9. **Approved for Printing** - Staff final signoff given
10. **Submitted to Printer** - Banner sent to materialpromotions.com for printing
11. **Complete - Thank You Sent** - Banner displayed on assigned pole, thank you sent to sponsor

## Complete Workflow Steps

### Initial Setup (Customer Actions)
1. Customer enters hero data on Wix website
2. Customer submits payment (online or mails check)

### Staff Verification Process
3. **Import CSV files** to get latest data from Wix
4. **Verify payment received** - Ensure banner is paid for
5. **Verify documents** - Check uploaded documents for quality and requirements:
   ```bash
   python banner_manager.py update "Hero Name" documents_verified yes
   ```
6. **Verify photo** - Ensure customer photo meets all requirements:
   ```bash
   python banner_manager.py update "Hero Name" photo_verified yes
   ```

### Customer Approval
7. **Create draft email** with link to Banner list webpage:
   ```bash
   python banner_manager.py email-send
   ```
8. Review drafts in Outlook and send to customers
9. **Check for customer approval** responses:
   ```bash
   python banner_manager.py email-check
   ```
10. **Correct any errors** reported by customer and repeat steps 7-9 if needed

### Print and Display
11. **Final approval for printing**:
    ```bash
    python banner_manager.py update "Hero Name" print_approved yes
    ```
12. **Submit to printer** (materialpromotions.com):
    ```bash
    python banner_manager.py update "Hero Name" submitted_to_printer yes
    ```
13. **Assign pole location**:
    ```bash
    python banner_manager.py update "Hero Name" pole_location "Main St & 5th Ave"
    ```
14. **Send thank you** to sponsor:
    ```bash
    python banner_manager.py update "Hero Name" thank_you_sent yes
    ```

## Required Banner Information

Each banner must have:
- Hero name
- Service branch
- Photo/image
- Sponsor name
- Sponsor email

## Persistent Data

The following information is stored in the database and persists across CSV imports:
- Pole location assignments
- Notes about each banner
- Proof sent/approved status
- Print approval status
- All timestamp information

## CSV File Formats

### Hero Information CSV

The system will automatically detect columns with these names (case-insensitive):
- Name (hero name)
- Branch/Service (service branch)
- Rank
- Years Served
- Hometown/City
- Photo/Image (photo path)
- Sponsor Name
- Email
- Phone

### Payment CSV

The system will automatically detect columns with these names (case-insensitive):
- Name (sponsor name)
- Amount/Paid/Price (amount paid)
- Date (payment date)
- Method/Type (payment method)
- Transaction/ID (transaction ID)

## Database

All data is stored in `hometown_hero.db` (SQLite database). This file contains:
- Banner records with all status information
- Pole location assignments
- Notes
- Timestamps

**Important**: Do not delete this file! It contains persistent data that is not in the CSV files.

## Workflow Example

1. **Download CSV files from Wix**:
   - Export hero information CSV
   - Export payment CSV

2. **Import the files**:
   ```bash
   python banner_manager.py import --hero heroes.csv --payment payments.csv
   ```

3. **Review status**:
   ```bash
   python banner_manager.py list
   ```

4. **Send notifications for ready proofs**:
   ```bash
   python banner_manager.py notify --status "ready for proof"
   ```

5. **Assign pole locations** (as needed):
   ```bash
   python banner_manager.py update "John Smith" pole_location "5th Ave & Pine St"
   ```

6. **Record client approval** (when received):
   ```bash
   python banner_manager.py update "John Smith" proof_approved yes
   ```

7. **Final signoff for printing**:
   ```bash
   python banner_manager.py update "John Smith" print_approved yes
   ```

8. **Check what's ready to print**:
   ```bash
   python banner_manager.py list --status "printing"
   ```

## Troubleshooting

### Column Not Found Errors

If the CSV column names are different than expected, the system will try to match them automatically. Check the console output during import to see which columns were detected.

### Sponsor Name Mismatch

Payment matching is done by exact sponsor name match (case-insensitive). If a payment isn't matched, verify the sponsor name is spelled identically in both CSV files.

### Database Issues

If you encounter database errors:
1. Make sure `hometown_hero.db` is not open in another program
2. Check file permissions
3. If needed, you can delete the database file to start fresh (but you'll lose pole locations and notes)

## Support

For issues or questions, please refer to the Millcreek Kiwanis organization.

## License

This software is provided for use by the Millcreek Kiwanis organization.