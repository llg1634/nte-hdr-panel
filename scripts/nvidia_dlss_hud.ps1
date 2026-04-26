param(
  [ValidateSet("on", "off", "status")]
  [string]$Mode = "status"
)

$Path = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\NGXCore"
$Name = "ShowDlssIndicator"

if ($Mode -eq "on") {
  New-Item -Path $Path -Force | Out-Null
  New-ItemProperty -Path $Path -Name $Name -PropertyType DWord -Value 0x400 -Force | Out-Null
}
elseif ($Mode -eq "off") {
  New-Item -Path $Path -Force | Out-Null
  New-ItemProperty -Path $Path -Name $Name -PropertyType DWord -Value 0 -Force | Out-Null
}

try {
  $value = (Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop).$Name
  [pscustomobject]@{
    Path = $Path
    Name = $Name
    Value = $value
    Enabled = ($value -ne 0)
  }
}
catch {
  [pscustomobject]@{
    Path = $Path
    Name = $Name
    Value = $null
    Enabled = $false
  }
}
