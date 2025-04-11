Add-Type -AssemblyName PresentationFramework
$result = [System.Windows.MessageBox]::Show("Are you sure you want to sign out?", "Sign Out", "YesNo", "Warning")
if ($result -eq "Yes") { shutdown.exe /l } else { exit }