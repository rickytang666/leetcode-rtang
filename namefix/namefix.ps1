# Script to fix LeetCode problem folder names to use 4-digit padding
# Example: 56-problem-name -> 0056-problem-name

# Set output encoding to UTF-8 to handle special characters like ✓
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$renamedCount = 0
$directories = @("easy", "medium", "hard")

function Pad-FolderName {
    param (
        [string]$FolderPath
    )
    
    $folderName = Split-Path -Path $FolderPath -Leaf
    $parentDir = Split-Path -Path $FolderPath -Parent
    
    # Extract the problem number (digits at the start of the folder name)
    # Matches strings starting with digits, optionally followed by dash and more chars
    if ($folderName -match "^([0-9]+)(-.*)?$") {
        $problemNum = $matches[1]
        $restOfName = $matches[2] # This will be the "-others" part or empty
        if ($null -eq $restOfName) { $restOfName = "" }
        
        # Check if already 4 digits
        if ($problemNum.Length -eq 4) {
            return
        }
        
        # Check if it's 1-3 digits
        if ($problemNum.Length -ge 1 -and $problemNum.Length -le 3) {
            # Pad to 4 digits
            $paddedNum = $problemNum.PadLeft(4, '0')
            $newName = "${paddedNum}${restOfName}"
            $newPath = Join-Path -Path $parentDir -ChildPath $newName
            
            Write-Host "Wrong: $folderName" -ForegroundColor Yellow
            
            # Check if target already exists
            if (Test-Path -Path $newPath) {
                Write-Host "Error: Target already exists: $newPath" -ForegroundColor Red
                return
            }
            
            # Rename the folder
            Rename-Item -Path $FolderPath -NewName $newName
            Write-Host "Fixed: $newName`n" -ForegroundColor Green
            
            $global:renamedCount++
        }
    }
}

# Process each difficulty level
foreach ($difficulty in $directories) {
    if (Test-Path -Path $difficulty) {
        # Find all problem folders (they are at depth 2 within each difficulty folder)
        # Depth 0: ./easy
        # Depth 1: ./easy/0001-0500
        # Depth 2: ./easy/0001-0500/0001-two-sum
        
        $level1Dirs = Get-ChildItem -Path $difficulty -Directory
        foreach ($l1 in $level1Dirs) {
            $level2Dirs = Get-ChildItem -Path $l1.FullName -Directory | Where-Object { $_.Name -match "^[0-9]" }
            foreach ($folder in $level2Dirs) {
                Pad-FolderName -FolderPath $folder.FullName
            }
        }
    }
}

# Summary
if ($renamedCount -eq 0) {
    Write-Host "$([char]0x2713) All folders are already properly formatted!" -ForegroundColor Green
} else {
    Write-Host "$([char]0x2713) Fixed $renamedCount folder(s)" -ForegroundColor Green
}
