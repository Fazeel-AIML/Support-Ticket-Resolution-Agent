import argparse
from src.core import SupportAgent
from src.core.schemas import Ticket
import json

def main():
    parser = argparse.ArgumentParser(description="Support Ticket Resolution Agent")
    parser.add_argument('--subject', required=True, help='Ticket subject')
    parser.add_argument('--description', required=True, help='Ticket description')
    parser.add_argument('--output', default='response.json', help='Output file path')
    
    args = parser.parse_args()
    
    ticket_data = {
        "subject": args.subject,
        "description": args.description
    }
    
    agent = SupportAgent()
    result = agent.process_ticket(ticket_data)
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Processing complete. Result saved to {args.output}")

if __name__ == "__main__":
    main()