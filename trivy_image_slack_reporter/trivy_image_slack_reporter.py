"""
This script takes a Trivy scan JSON file and sends the results to a Slack channel.
"""

import json
import os
import slack_sdk

# Optional environment variables
SEVERITY = os.environ.get("SEVERITY", "HIGH,CRITICAL").split(",")
ARTIFACT_URL = os.environ.get("ARTIFACT_URL", None)

# Required environment variables
try:
    results = json.load(open(os.environ["RESULTS_FILE"]))
except KeyError:
    raise Exception("RESULTS_FILE environment variable is not set")
except FileNotFoundError:
    raise Exception("RESULTS_FILE environment variable is not set to a valid file")

try:
    IMAGE_TITLE = os.environ["IMAGE_TITLE"]
except KeyError:
    raise Exception("IMAGE_TITLE environment variable is not set")

try:
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
except KeyError:
    raise Exception("SLACK_BOT_TOKEN environment variable is not set")

try:
    SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
except KeyError:
    raise Exception("SLACK_CHANNEL_ID environment variable is not set")


TITLE = f"🛡️ {IMAGE_TITLE} Security Scan 🛡️"

blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": TITLE,
            "emoji": True,
        },
    },
    {"type": "divider"},
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"This scan shows {', '.join(SEVERITY)} severity vulnerabilities found in the following image:\n\n`{ results['Metadata']['RepoDigests'][0] }`\n",
        },
    },
    {"type": "divider"},
]


# Filter out vulnerabilities that don't match the specified severity levels
targets = {
    str(result["Target"] + " - " + result["Type"]): [
        v for v in result["Vulnerabilities"] if v["Severity"] in SEVERITY
    ]
    for result in results["Results"]
    if "Vulnerabilities" in result.keys()
}


for target, vulnerabilities in targets.items():
    output = str()
    if vulnerabilities == []:
        # Skip results that don't have vulnerabilities
        continue
    blocks.append(
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": target,
            },
        }
    )
    for v in vulnerabilities:
        output += f"• *{v['Title']}*\n"
        output += f"   <{v['PrimaryURL']}|{v['VulnerabilityID']}>\n"
        output += f"   Severity: {v['Severity']}\n"
        output += f"   Package: {v['PkgName']}\n"
        output += f"   Installed Version: {v['InstalledVersion']}\n"
        output += f"   Fixed Version: {v['FixedVersion']}\n"
        output += "\n"

    blocks.append(
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": output},
        }
    )
    blocks.append({"type": "divider"})

if ARTIFACT_URL:
    blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"For more details, please check the <{ ARTIFACT_URL }|full scan result>.",
            },
        }
    )


# Truncate sections that are too long
for block in blocks:
    if block["type"] == "section":
        if len(block["text"]["text"]) > 3000:
            # Split the text into individual vulnerabilities
            items: list[str] = block["text"]["text"].split("• ")

            # Remove vulnerabilities until the text is less than 2900 characters
            while len("• ".join(items)) > 2900:
                items.pop()

            # Reconstruct the text with the truncated vulnerabilities
            block["text"]["text"] = (
                "• ".join(items)
                + f"*The vulnerabilities in this section are truncated. {'See the full scan result for more details.' if ARTIFACT_URL else ''}*"
            )

print(f"Sending results to channel {SLACK_CHANNEL_ID}:")
print(json.dumps(blocks, indent=2))

client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)

try:
    client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=TITLE,
        blocks=blocks,
        unfurl_links=False,
        unfurl_media=False,
    )
except Exception as e:
    raise Exception(f"Error sending results to Slack: {e}")

print("Done.")
