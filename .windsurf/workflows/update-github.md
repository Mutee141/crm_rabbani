---
description: Update project and push changes to GitHub automatically
---

# Update GitHub Repository Workflow

This workflow helps you automatically commit and push changes to your GitHub repository when you update your project.

## Steps to Update GitHub

1. **Run the auto-update script**
   ```bash
   python update_github.py
   ```

2. **Alternative: Manual Git commands**
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin master
   ```

## What the Script Does

- **Checks for changes**: Detects if any files have been modified
- **Stages all changes**: Adds all modified files to git staging area
- **Commits with timestamp**: Creates an automatic commit with timestamp
- **Pushes to GitHub**: Uploads changes to your GitHub repository

## Usage Examples

### Quick Update
```bash
python update_github.py
```

### Manual Update with Custom Message
```bash
git add .
git commit -m "Fixed bug in user authentication"
git push origin master
```

### Check Status Before Update
```bash
git status
```

## Important Notes

- Make sure you're connected to internet
- The script uses the configured Git credentials (Mutee141)
- All changes are automatically committed with timestamps
- The script will tell you if there are no changes to push

## Troubleshooting

If the update fails:
1. Check your internet connection
2. Verify GitHub repository access
3. Run `git status` to see what's happening
4. Make sure you have the latest changes: `git pull origin master`
