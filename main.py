# This file contains the script to use the Jira rest api to get information from tickets.
# the goal is that this script can be ran to grant users access to databases when their tickets have been approved
from jira import JIRA
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.cloud import storage
from google.cloud import kms_v1
import json


'''
Custom fields for Jira DB tickets:
    - user to get access:   13741
    - database:     13740   [string]
    - access types: 13742   [list]
    - status.name           [string]
    - description           [String
'''
class JiraInteract:

    def __init__(self):
        """constructor method"""
        encrypted_string = read_file_as_string("prod-jira-mail-function", "secrets/approved-ticket-mail-keys.enc")
        decrypted_byte_string = decrypt_symmetric("ri-platform-prod",
                                                  "europe-west2",
                                                  "platform-prod-keyring",
                                                  "jira-email-function",
                                                  encrypted_string)
        decrypted_string = decrypted_byte_string.decode("utf-8")
        dict = json.loads(decrypted_string)

        self.username = dict["jira-user"]
        self.password = dict["jira-api-token"]
        self.sendgrid_api_key = dict["sendgrid-api-token"]
        # self.to_email = dict["emails"]


    def connect_api(self):
        """connection method returning an object that can be interacted with to make api calls"""
        # creating the connection with the Jira API
        jira = JIRA(
            basic_auth=(self.username, self.password),
            options={
                'server': 'https://retailinsightltd.atlassian.net/'
            }
        )
        return jira

    def get_resolved_issues(self):
        """
        this function gets all the approved issues in the provided project and returns a list of
        issue objects.
        """
        project_name = "DSD"

        # creating the connection with the Jira API
        jira = self.connect_api()

        # getting all issues in the provided project that were resolved in the last day or less
        issues_in_project =  jira.search_issues('project={} and resolutiondate >=-24h'.format(project_name))

        out_list = list()
        # getting the issue name and the summary and storing them in a dict. this dict then gets appended to a list
        for issue in issues_in_project:
            if issue.fields.status.id == "5" and str(issue.fields.issuetype) == "Equipment":
                issue_dict = {"id": str(issue), "summary": issue.fields.summary}
                out_list.append(issue_dict)

        return out_list

    def get_resolved_tickets_history(self):
        """
        Method that retrieves the ticket's changelogs and returns for each ticket a list of changes
        :return: list of lists containing the ticket info and their changelogs
        """
        # print("getting history")
        jira = self.connect_api()

        resolved_issues = self.get_resolved_issues()
        out_list = list()
        for issue in resolved_issues:
            issue_id = issue["id"]
            issue_summary = issue["summary"]

            issue = jira.issue(issue_id, expand='changelog')
            changelog = issue.changelog

            # get change history with author and add it to list
            sub_list = list()

            for history in changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        string = "{} on: {} changed {} from '{}' To '{}'".\
                            format(history.author, history.created, issue_id, item.fromString, item.toString)
                        sub_list.append(string)
            sub_list.append("<br />Approval History:")
            sub_list.append("<br />Ticket description: <br /> {} <br />".format(issue.fields.description))
            sub_list.append("Ticket Details:<br /> Ticket-id: {}<br /> Ticket-title: {} <br />".format(issue_id, issue_summary))
            sub_list.append("Subject: Approval history for ticket: {}  ".format(issue_id))

            # reverse list to have it show in chronological order
            sub_list.reverse()
            out_list.append(sub_list)

        return out_list

    def send_emails(self, emails_list):
        """Method that sends out the emails stored in the list using Sendgrid"""
        # print("sending emails")
        for email in emails_list:
            message = Mail(
                from_email='platform.notifications@ri-team.com',
                to_emails='finance-team@ri-team.com',
                subject=email[:48],
                html_content=email[48:])
            try:
                sg = SendGridAPIClient(self.sendgrid_api_key)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e.message)

def read_file_as_string(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_string()


def create_emails(list_of_lists):
    """Method that creates lists with strings that can be sent as an email"""
    # print("creating emails")
    emails_list = list()
    for sublist in list_of_lists:
        email_string = ""
        for item in sublist:
            email_string += item + "<br />"
        emails_list.append(email_string)

    return emails_list

def decrypt_symmetric(project_id, location_id, key_ring_id, crypto_key_id,
                      ciphertext):
    """Decrypts input ciphertext using the provided symmetric CryptoKey."""


    # Creates an API client for the KMS API.
    client = kms_v1.KeyManagementServiceClient()

    # The resource name of the CryptoKey.
    name = client.crypto_key_path_path(project_id, location_id, key_ring_id,
                                       crypto_key_id)
    # Use the KMS API to decrypt the data.
    response = client.decrypt(name, ciphertext)
    return response.plaintext

def run_jira_approval_history_emails(*args):
    jira_interact = JiraInteract()
    # print("created obj")
    ticket_history = jira_interact.get_resolved_tickets_history()
    # print("fetched history")
    emails = create_emails(ticket_history)
    # print("created emails")
    jira_interact.send_emails(emails)
    # print("Sent emails")
