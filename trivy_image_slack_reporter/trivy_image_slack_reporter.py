"""
This script takes a Trivy scan JSON file and sends the results to a Slack channel.
"""

import json
import os
from typing import Final

import slack_sdk
from ca_slack_block_kit import Block, Divider, Header, MarkdownSection


def main() -> None:
    # Optional environment variables
    severity: Final[list[str]] = os.environ.get("SEVERITY", "HIGH,CRITICAL").split(",")
    artifact_url = os.environ.get("ARTIFACT_URL", None)

    # Required environment variables
    try:
        results = json.load(open(os.environ["RESULTS_FILE"]))
    except KeyError as e:
        raise Exception("RESULTS_FILE environment variable is not set") from e
    except FileNotFoundError as e:
        raise Exception("RESULTS_FILE environment variable is not set to a valid file") from e

    try:
        image_title = os.environ["IMAGE_TITLE"]
    except KeyError as e:
        raise Exception("IMAGE_TITLE environment variable is not set") from e

    try:
        slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    except KeyError as e:
        raise Exception("SLACK_BOT_TOKEN environment variable is not set") from e

    try:
        slack_channel_id = os.environ["SLACK_CHANNEL_ID"]
    except KeyError as e:
        raise Exception("SLACK_CHANNEL_ID environment variable is not set") from e

    title = f"🛡️ {image_title} Security Scan 🛡️"

    blocks: list[Block] = [
        Header(title),
        Divider(),
        MarkdownSection(
            f"This scan shows {', '.join(severity)} severity vulnerabilities found in the following image:\n\n`{results['Metadata']['RepoDigests'][0]}`\n"
        ),
        Divider(),
    ]

    # Filter out vulnerabilities that don't match the specified severity levels
    targets = {
        str(result["Target"] + " - " + result["Type"]): [
            v for v in result["Vulnerabilities"] if v["Severity"] in severity
        ]
        for result in results["Results"]
        if "Vulnerabilities" in result.keys()
    }

    vulnerabilities_count = 0

    for target, vulnerabilities in targets.items():
        output = ""
        if vulnerabilities == []:
            # Skip results that don't have vulnerabilities
            continue
        blocks.append(Header(target))
        for v in vulnerabilities:
            output += f"• *{v['Title']}*\n"
            output += f"   <{v['PrimaryURL']}|{v['VulnerabilityID']}>\n"
            output += f"   Severity: {v['Severity']}\n"
            output += f"   Package: {v['PkgName']}\n"
            output += f"   Installed Version: {v['InstalledVersion']}\n"
            output += f"   Fixed Version: {v['FixedVersion']}\n"
            output += "\n"

            vulnerabilities_count += 1

        blocks.append(MarkdownSection(output))
        blocks.append(Divider())

    if artifact_url:
        blocks.append(
            MarkdownSection(
                f"For more details, please check the <{artifact_url}|full scan result>."
            )
        )

    # Truncate sections that are too long
    for i, block in enumerate(blocks):
        if isinstance(block, MarkdownSection):
            if len(block.text) >= 3000:
                # Split the text into individual vulnerabilities
                items: list[str] = block.text.split("• ")

                # Remove vulnerabilities until the text is less than 2900 characters
                while len("• ".join(items)) > 2900:
                    items.pop()

                # Reconstruct the text with the truncated vulnerabilities
                block.text = (
                    "• ".join(items)
                    + f"*The vulnerabilities in this section are truncated. {'See the full scan result for more details.' if artifact_url else ''}*"
                )

                # Update the blocks list
                blocks[i] = block

    blocks_dict_list = [b.render() for b in blocks]
    print("Message blocks:")
    print(json.dumps(blocks_dict_list, indent=2))

    if not vulnerabilities_count:
        print("No vulnerabilities found. Skipping sending Slack message.")
    elif os.environ.get("DRY_RUN"):
        print("Dry run enabled. Skipping sending Slack message.")
    else:
        print(f"Sending results to channel {slack_channel_id}...")

        try:
            client = slack_sdk.WebClient(token=slack_bot_token)
            client.chat_postMessage(
                channel=slack_channel_id,
                text=title,
                blocks=blocks_dict_list,
                unfurl_links=False,
                unfurl_media=False,
            )
        except Exception as e:
            raise Exception(f"Error sending results to Slack: {e}") from e

    print("Done.")


if __name__ == "__main__":
    main()
