import os
from openai import OpenAI
import requests

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Get environment variables passed by the GitHub Action
pr_title = os.environ.get('PR_TITLE', 'Untitled Pull Request')
pr_number = os.environ.get('PR_NUMBER')  # PR number for API updates
repo = os.environ.get('GITHUB_REPOSITORY')  # e.g., owner/repo

# Construct the diff URL
pr_diff_url = f"https://github.com/{repo}/pull/{pr_number}.diff"

def fetch_diff(repo, pr_number):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        'Authorization': f'token {os.environ["GITHUB_TOKEN"]}',
        'Accept': 'application/vnd.github.v3.diff',
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching diff from {url}: {e}")
        return ""

def generate_pr_description(title, diff):
    """
    Use OpenAI API to generate a pull request description.
    """
    prompt = f"""Generate a professional pull request description in Markdown format with
sections '## Summary' and '## Files changed' (do not add level 1 title) for the following title and diff:
Title: {title}
Diff: {diff[:1000]}  # Truncated diff for context (API limits)

Output only the PR description in Markdown.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates professional pull request descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating PR description: {e}")
        return "Error generating PR description."

def update_pr_description(repo, pr_number, new_description):
    """
    Update the pull request description using the GitHub API.
    """
    headers = {
        'Authorization': f'token {os.environ["GITHUB_TOKEN"]}',
        'Accept': 'application/vnd.github.v3+json',
    }

    # Fetch the existing PR details
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        pr_data = response.json()
        existing_body = pr_data.get('body', '')

        # Insert the generated description after the marker
        if "# Auto-generated description" in existing_body:
            updated_body = existing_body.split("# Auto-generated description")[0] + \
                           "# Auto-generated description\n\n" + \
                           new_description
        else:
            updated_body = existing_body + "\n\n# Auto-generated description\n\n" + new_description

        # Send the updated description back to GitHub
        update_response = requests.patch(
            url,
            headers=headers,
            json={"body": updated_body}
        )
        update_response.raise_for_status()
        print("Successfully updated PR description.")
    except requests.RequestException as e:
        print(f"Error updating PR description: {e}")

# Main logic -
if pr_number and repo:
    pr_diff = fetch_diff(repo, pr_number)
    if pr_diff:
        generated_description = generate_pr_description(pr_title, pr_diff)
        update_pr_description(repo, pr_number, generated_description)
    else:
        print("Failed to fetch PR diff.")
else:
    print("Missing required environment variables (PR_NUMBER, GITHUB_REPOSITORY).")
