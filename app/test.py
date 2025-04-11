import requests
from pydantic import BaseModel


class TicketCreate(BaseModel):
    title: str
    description: str
    status: str


def create_ticket(title, description, status):
    data = {"title": title, "description": description, "status": status}
    response = requests.post("http://localhost:8000/tickets/", json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
    return response.json()


def create_faq(question, answer, category):
    data = {"question": question, "answer": answer, "category": category}
    response = requests.post("http://localhost:8000/faqs/", json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
    return response.json()


def query(text, top_k):
    data = {"text": text, "top_k": top_k}
    response = requests.post("http://localhost:8000/query/", json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
    return response.json()


# Create a TicketCreate object
# ticket = TicketCreate(title="Example Ticket", description="This is an example ticket", status="open")

# Convert the TicketCreate object to JSON
# ticket_json = ticket.dict()

# Set the API endpoint URL
# url = "http://localhost:8000/tickets/"

# # Send a POST request to the API endpoint
# response = requests.post(url, json=ticket_json)

# Check if the request was successful


def create_tickets(issues):
    # Sample production issues and their resolutions
    issues = [
        (
            "Database Connection Timeout",
            "Users report intermittent database connection failures. Increased connection pool size and optimized queries. Issue resolved.",
            "Resolved",
        ),
        (
            "High CPU Usage on API Server",
            "API server experiencing high CPU usage due to inefficient loop. Optimized code and added caching. Issue resolved.",
            "Resolved",
        ),
        (
            "Memory Leak in Background Job",
            "Background job causing memory leak due to unclosed file handles. Fixed by ensuring proper resource cleanup. Issue resolved.",
            "Resolved",
        ),
        (
            "Slow Response Time on Login",
            "Users experiencing slow login times. Optimized authentication query and added indexing. Issue resolved.",
            "Resolved",
        ),
        (
            "500 Errors on Checkout Page",
            "Checkout page throwing 500 errors due to missing validation check. Fixed by adding proper error handling. Issue resolved.",
            "Resolved",
        ),
        (
            "Email Notifications Not Sending",
            "Email service was misconfigured after a recent update. Reconfigured SMTP settings and emails are now sending. Issue resolved.",
            "Resolved",
        ),
        (
            "Data Loss in Order Processing",
            "Orders were not being saved due to a race condition. Implemented transaction locking and issue resolved.",
            "Resolved",
        ),
        (
            "Mobile App Crashing on Startup",
            "Crash due to incorrect API response handling. Fixed by updating error handling mechanism. Issue resolved.",
            "Resolved",
        ),
        (
            "Security Vulnerability in Authentication",
            "Detected a security flaw in the authentication system. Patched the vulnerability and updated security policies. Issue resolved.",
            "Resolved",
        ),
        (
            "Unexpected Downtime Due to Server Crash",
            "A sudden server crash caused downtime. Recovered from backup and added monitoring for early detection. Issue resolved.",
            "Resolved",
        ),
    ]
    for issue in issues:
        create_ticket(issue[0], issue[1], issue[2])


def create_faqs():
    # Sample production issues and their resolutions
    faq_data = [
        (
            "how to deal with database connection timeout?",
            "create work order for database team to optimize query performance.",
            "Account Management",
        ),
        # (
        #     "How do I reset my password?",
        #     "To reset your password, click on the 'Forgot Password' link on the login page, enter your email address, and follow the instructions sent to your email.",
        #     "Account Management",
        # ),
        # (
        #     "Why can't I log in to my account?",
        #     "If you're unable to log in, ensure you're using the correct email and password. If the issue persists, try clearing your browser cache or resetting your password.",
        #     "Account Access",
        # ),
        # (
        #     "How can I update my profile information?",
        #     "Log in to your account, navigate to the 'Profile' or 'Settings' section, and click on 'Edit Profile'. Make your changes and save them.",
        #     "Account Management",
        # ),
        # (
        #     "What should I do if I encounter a bug in the application?",
        #     "If you encounter a bug, please report it by going to the 'Help' section and clicking on 'Report a Bug'. Provide as much detail as possible, including steps to reproduce the issue.",
        #     "Technical Support",
        # ),
        # (
        #     "How do I cancel my subscription?",
        #     "To cancel your subscription, go to 'Account Settings', select 'Subscription', and click on 'Cancel Subscription'. Follow the prompts to complete the cancellation process.",
        #     "Billing",
        # ),
        # (
        #     "Is my data secure?",
        #     "Yes, we take data security seriously. We use industry-standard encryption protocols and regularly update our security measures to protect your information.",
        #     "Security",
        # ),
        # (
        #     "How can I export my data?",
        #     "To export your data, go to 'Account Settings', select 'Data', and click on 'Export Data'. Choose the format you prefer and follow the instructions to download your data.",
        #     "Data Management",
        # ),
        # (
        #     "What payment methods do you accept?",
        #     "We accept major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for certain regions.",
        #     "Billing",
        # ),
        # (
        #     "How do I contact customer support?",
        #     "You can contact our customer support team through the 'Help' section in the app, by emailing support@example.com, or by calling our toll-free number during business hours.",
        #     "Customer Support",
        # ),
        # (
        #     "Can I use the application on multiple devices?",
        #     "Yes, you can use the application on multiple devices. Simply log in with your account credentials on each device to access your data and settings.",
        #     "Account Access",
        # ),
    ]

    # Print the list to verify
    for question, answer, category in faq_data:
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print(f"Category: {category}")
        print()

        create_faq(question, answer, category)


if __name__ == "__main__":

    # Create tickets
    # create_tickets(title, description, status)
    # create_faqs()
    query(text="what to do in case of a database connection timeout", top_k=1)
