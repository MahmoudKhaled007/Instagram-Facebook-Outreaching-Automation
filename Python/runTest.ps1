$imagePath = "./Instgram Images/image1.jpg"
$prompt = @"
Generate ONE casual social media comment using these rules:
1. Tone: Human-like (use contractions, fragments, conversational flow)
2. Structure:
   - Start with compliment/observation/personal connection
   - Include 1 industry-specific insight
   - Optional: Add a question OR quick tip
   - End with DM teaser (e.g., 'Sent you something cool in DMs!')
3. Format:
   - 50-260 characters
   - No emojis/hashtags
   - No direct names ('you' instead of '@username')
   - Output ONLY the final comment
"@

# Start Ollama and send prompt
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "ollama"
$processInfo.Arguments = "run gemma3:12b --image `"$imagePath`""
$processInfo.RedirectStandardInput = $true
$processInfo.RedirectStandardOutput = $true
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null

$process.StandardInput.WriteLine($prompt)
$process.StandardInput.Close()

$response = $process.StandardOutput.ReadToEnd()
$process.WaitForExit()

return $response
