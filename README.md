# Support Ticket Resolution Agent

![LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)

An AI-powered support ticket resolution system built with LangGraph that automatically classifies, processes, and responds to customer support tickets with a multi-step review loop.

## Features

- **Automatic Ticket Classification**: Categorizes tickets into Billing, Technical, Security, or General
- **Context-Aware Responses**: Retrieves relevant information using RAG (Retrieval-Augmented Generation)
- **Quality Assurance**: Automated draft review with policy compliance checking
- **Self-Correcting**: Up to 2 automatic retries with feedback incorporation
- **Escalation Handling**: Logs failed tickets for human review

## Prerequisites

- Python 3.9+
- [Groq](https://console.groq.com/) or OpenAI API key
- (Optional) Poetry for dependency management

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/support-ticket-agent.git
cd support-ticket-agent
```

### 2. Set up virtual environment
```bash
python -m venv ass_venv
# Windows:
ass_venv\Scripts\activate
# Mac/Linux:
source ass_venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the root directory:

```ini
# For Groq (recommended):
GROQ_API_KEY=your_api_key_here

# OR for OpenAI:
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Running the Agent (Command Line Interface)
```bash
python src/main.py '{"subject":"Login issue","description":"I cant access my account"}'

# Or using a JSON file:
python src/main.py ticket.json
```

### Expected Output
The agent will generate a `response.json` file containing:

- Original ticket
- Classification
- Retrieved context
- Generated draft
- Review results
- Attempt count
- Escalation status


## Sample Workflow

1. The agent receives a ticket
2. Classifies it into a category
3. Retrieves relevant documentation
4. Generates a draft response
5. Reviews the draft for quality
6. Either:
   - Approves and returns the response, or
   - Retries up to 2 times, or
   - Escalates to human support

## Project Structure

```
support-ticket-agent/
├── src/
│   ├── config/       # Configuration settings
│   ├── core/         # Core agent logic and schemas
│   ├── services/     # Individual processing components
│   ├── __init__.py
│   └── main.py       # Entry point
├── tests/            # Unit tests
├── .....             # Test Files
├── requirements.txt  # Dependencies
└── README.md         # This file
```