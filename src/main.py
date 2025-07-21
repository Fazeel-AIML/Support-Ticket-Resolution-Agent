import argparse
import json
import os
from src.core import SupportAgent
from src.core.schemas import Ticket

def main():
    parser = argparse.ArgumentParser(description="Support Ticket Resolution Agent")
    parser.add_argument('--subject', help='Ticket subject')
    parser.add_argument('--description', help='Ticket description')
    parser.add_argument('--input', help='Path to input JSON file')
    parser.add_argument('--output', default='response.json', help='Output file path')

    args = parser.parse_args()

    ticket_data = None

    if args.input:
        # First priority: load from --input JSON file
        if not os.path.exists(args.input):
            print(f"❌ Input file '{args.input}' does not exist.")
            return
        try:
            with open(args.input, 'r') as f:
                ticket_data = json.load(f)
            if 'subject' not in ticket_data or 'description' not in ticket_data:
                print("❌ Input JSON must contain 'subject' and 'description' fields.")
                return
        except Exception as e:
            print(f"❌ Failed to load or parse input file: {e}")
            return
    elif args.subject and args.description:
        # Second priority: both CLI args are given
        ticket_data = {
            "subject": args.subject,
            "description": args.description
        }
    elif args.description:
        # Fallback: Only description given
        ticket_data = {
            "subject": "INVALID INPUT",
            "description": args.description
        }
    else:
        print("❌ Please provide either --input OR both --subject and --description OR at least --description.")
        return

    # Process the ticket
    agent = SupportAgent()
    result = agent.process_ticket(ticket_data)

    # Save result only if not escalated or has retry attempts
    if not result.get('escalated') or result.get('attempt', 0) > 0:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Processing complete. Result saved to {args.output}")
    else:
        print("⚠️ Ticket escalated - see data/escalation.csv")

if __name__ == "__main__":
    main()
