# Import required modules
Import-Module Az
Import-Module AzureRM.OperationalInsights

# Define your Azure Data Log Analytics workspace details
$workspaceId = "<Your_Workspace_Id>"
$workspaceKey = "<Your_Workspace_Key>"
$workspaceName = "<Your_Workspace_Name>"
$resourceGroupName = "<Your_Resource_Group_Name>"

# Define the path of the zip file
$zipFilePath = "<Path_to_your_zip_file>"

# Connect to Azure
Connect-AzAccount

# Get the storage account from where you want to extract the zip file
$storageAccount = Get-AzStorageAccount -ResourceGroupName $resourceGroupName

# Get the storage account context
$ctx = $storageAccount.Context

# Extract the zip file
Expand-Archive -Path $zipFilePath -DestinationPath $env:TEMP

# Get the list of files extracted from the zip
$extractedFiles = Get-ChildItem $env:TEMP

# Loop through each file and push it to Azure Data Log Analytics workspace
foreach ($file in $extractedFiles) {
    $content = Get-Content $file.FullName
    $body = @{
        "WorkspaceId" = $workspaceId
        "KeyType" = "SharedKey"
        "LogType" = "MyCustomLogType"  # Define your custom log type here
        "Body" = $content -join "`r`n"
    }
    $bodyJson = $body | ConvertTo-Json

    # Generate authorization header
    $date = Get-Date
    $sharedKey = [System.Convert]::FromBase64String($workspaceKey)
    $hmacSha256 = New-Object System.Security.Cryptography.HMACSHA256
    $hmacSha256.Key = $sharedKey
    $dateString = $date.ToString('r')
    $contentLength = [System.Text.Encoding]::UTF8.GetByteCount($bodyJson)
    $contentType = "application/json"
    $method = "POST"
    $resource = "/api/logs"
    $stringToSign = "$method`n$contentLength`n$contentType`n" + "x-ms-date:$dateString`n" + "$resource"
    $signatureBytes = $hmacSha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($stringToSign))
    $signature = [System.Convert]::ToBase64String($signatureBytes)
    $authorization = "SharedKey $workspaceId:$signature"

    # Send data to Azure Data Log Analytics workspace
    $uri = "https://$workspaceName.ods.opinsights.azure.com$resource?api-version=2016-04-01"
    $headers = @{
        "Authorization" = $authorization
        "Log-Type" = "MyCustomLogType"  # Define your custom log type here
        "x-ms-date" = $dateString
        "time-generated-field" = $dateString
    }
    Invoke-RestMethod -Method $method -Uri $uri -ContentType $contentType -Headers $headers -Body $bodyJson
}

# Clean up temporary files
Remove-Item $env:TEMP\* -Force -Recurse
