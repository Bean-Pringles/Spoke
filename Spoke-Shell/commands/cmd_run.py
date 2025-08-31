import subprocess
import os

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    DANGEROUS = [
        "rm", "rmdir", "mkfs", "dd", "shutdown", "reboot", "poweroff",
        ":(){:|:&};:", "halt", "init", "chattr", "chmod 777 /", "chown root",
        "mv /", "cp -rf /", "wipe", "fdisk", "parted", "mkfs.ext4", "mkfs.ntfs",
        "mkfs.fat", "mkfs.btrfs", "mkfs.xfs", "mkfs.vfat", "umount", "mount -o remount",
        "killall -9", "rm -rf /", "yes > /dev/sda", "dd if=/dev/zero", "mklabel gpt",
        "del", "erase", "format", "shutdown", "rd", "rmdir", "move *",
        "attrib -s -h", "diskpart", "format C:", "del /S /Q *", "rd /S /Q *",
        "taskkill /F /IM", "takeown", "icacls", "bcdedit", "diskpart /s",
    ]

    requireConfirm = [
        "mv", "cp", "ln", "chmod", "chown", "kill", "pkill",
        "service", "systemctl", "tar", "gzip", "gunzip", "wget", "curl",
        "python", "node", "npm", "pip", "brew", "git", "docker", "docker-compose",
        "rsync", "scp", "ssh", "openssl", "openssl genrsa", "openssl rsa", "iptables",
        "ufw", "journalctl", "systemctl enable", "systemctl disable",
        "move", "copy", "xcopy", "rename", "attrib", "powershell", "taskkill",
        "net stop", "net start", "wscript", "cscript", "reg", "msiexec", "python", "node",
        "robocopy", "schtasks", "takeown", "icacls", "bcdedit", "diskpart",
        "format", "shutdown /s", "shutdown /r", "regedit", "wmic", "PowerShell -Command",
    ]

    # Handle different token structures
    command_str = ""
    is_loud = False

    # Pattern: ['run', '(', '"ls"', ')', 'loud'] or ['run', '(', '"ls"', ')']
    if len(tokens) >= 4 and tokens[1] == "(" and tokens[3] == ")":
        command_str = tokens[2]
        # Remove quotes if present
        if (command_str.startswith('"') and command_str.endswith('"')) or \
           (command_str.startswith("'") and command_str.endswith("'")):
            command_str = command_str[1:-1]
        
        is_loud = len(tokens) == 5 and tokens[4] == "loud"
    
    # Pattern: ['run', 'pwd', 'loud'] or ['run', 'pwd']
    elif len(tokens) >= 2:
        command_str = get_val(tokens[1])
        # Remove quotes if it's a quoted string
        if isinstance(command_str, str):
            if (command_str.startswith('"') and command_str.endswith('"')) or \
               (command_str.startswith("'") and command_str.endswith("'")):
                command_str = command_str[1:-1]
        
        is_loud = len(tokens) == 3 and tokens[2] == "loud"
    
    else:
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False

    # Split command to get first word for safety check
    cmd_parts = command_str.split()
    if not cmd_parts:
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False
    
    cmd_name = cmd_parts[0]
    
    # Safety checks
    if cmd_name in DANGEROUS:
        print("Error: Command blocked for safety.")
        errorLine(lineNum, line)
        return False
    
    elif cmd_name in requireConfirm:
        confirm = input(f"Command '{cmd_name}' can be risky. Proceed? (y/N): ")
        if confirm.lower() != "y":
            print("Command cancelled by user.")
            return True

    # Execute the command
    try:
        if is_loud:
            # Run command and print output
            result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.rstrip())
            if result.stderr:
                print(result.stderr.rstrip())
        else:
            # Run command silently
            subprocess.run(command_str, shell=True, capture_output=True, text=True)
        
        return True
    
    except Exception as e:
        print("Command execution failed")
        errorLine(lineNum, line)
        return False