# Requirement Copilot

A simple Claude-powered web app that turns messy product ideas, client requests, or meeting notes into structured requirement analysis.

## Overview

Requirement Copilot is a lightweight Streamlit app built with the Claude API.  
Users can paste a block of unstructured requirement text, then get a structured result including:

- One-line summary
- Core requirements
- Potential risks
- Questions to confirm
- Suggested next steps

This project is designed as a small human-in-the-loop productivity tool for early-stage requirement clarification.

## Features

- Simple single-page web interface
- Claude-powered requirement analysis
- Structured JSON output
- Prompt caching support
- Token usage display
- Lightweight and easy to run locally

## Tech Stack

- Python
- Streamlit
- Anthropic Claude API

## Project Structure

```text
app.py
claude_client.py
requirements.txt
Setup
Install dependencies:


pip install -r requirements.txt
Set your API key:


export ANTHROPIC_API_KEY=your_api_key
On Windows PowerShell:


$env:ANTHROPIC_API_KEY="your_api_key"
Run
Start the app with:


streamlit run app.py
Then open the local URL shown in your terminal.

Example Use Case
Input:

A client wants an internal knowledge base for sales and customer support.

They need search, permission control, FAQ organization, and possible future integration with enterprise messaging tools.

Their current problem is that documents are scattered and outdated versions are often used.

Output:

concise summary of the goal
key functional requirements
implementation risks
clarification questions
next-step suggestions
Notes
This project is intended as a first-pass requirement analysis assistant, not a full replacement for product managers or business analysts.
Outputs should still be reviewed by a human before execution.
The app uses Claude structured output to make frontend rendering more stable and consistent.
Why I Built This
I built this tool to make early requirement整理 and clarification faster and more structured.

Instead of manually turning raw conversations or notes into actionable requirement points, this app helps generate a usable first draft within seconds.



如果你想更自然一点，我建议你把最后一段这句：

`I built this tool to make early requirement整理 and clarification faster and more structured.`

改成纯英文版：

`I built this tool to make early-stage requirement clarification faster and more structured.`

也就是最后 README 里更推荐用这个版本：

```md
## Why I Built This

I built this tool to make early-stage requirement clarification faster and more structured.  
Instead of manually turning raw conversations or notes into actionable requirement points, this app helps generate a usable first draft within seconds.
