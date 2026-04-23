#!/usr/bin/env python3
"""
Automatic GitHub Update Script
This script helps automatically commit and push changes to GitHub
"""

import subprocess
import sys
from datetime import datetime

def run_command(command, cwd=None):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_changes():
    """Check if there are any changes to commit"""
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print(f"Error checking git status: {stderr}")
        return False
    
    return len(stdout.strip()) > 0

def auto_commit_and_push():
    """Automatically commit and push changes to GitHub"""
    
    print("🔍 Checking for changes...")
    
    # Check if there are changes
    if not check_changes():
        print("✅ No changes to commit. Repository is up to date.")
        return True
    
    print("📝 Changes detected. Starting automatic update...")
    
    # Add all changes
    print("➕ Adding all changes...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Error adding files: {stderr}")
        return False
    
    # Commit with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-update: {timestamp}"
    
    print(f"💾 Committing changes: {commit_message}")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Error committing: {stderr}")
        return False
    
    # Push to GitHub
    print("🚀 Pushing to GitHub...")
    success, stdout, stderr = run_command("git push origin master")
    if not success:
        print(f"❌ Error pushing to GitHub: {stderr}")
        return False
    
    print("✅ Successfully updated GitHub repository!")
    return True

def main():
    """Main function"""
    print("🔄 GitHub Auto-Update Tool")
    print("=" * 40)
    
    try:
        if auto_commit_and_push():
            print("\n🎉 Update completed successfully!")
        else:
            print("\n❌ Update failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Update cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
