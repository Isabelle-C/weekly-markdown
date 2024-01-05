from flask import Blueprint, render_template, request, redirect, session

from config import TOKEN_FILEPATH, CREDENTIALS_FILEPATH

import datetime
import dateutil.parser
import pytz
from pytz import timezone
import os.path

from google.auth.transport.requests import Request
from google.auth.credentials import Credentials as AuthCredentials
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


scheduler = Blueprint('scheduler', __name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def parse_date(date, convert_timezone):
    parsed_date = dateutil.parser.isoparse(date)
    
    if convert_timezone!=None:
        return parsed_date.astimezone(timezone(convert_timezone))

    return parsed_date


@scheduler.route('/scheduler_home', methods=['GET'])
def scheduler_home():
    if not os.path.exists(TOKEN_FILEPATH):
        return redirect('/authorize')
    
    else:
        creds= OAuth2Credentials.from_authorized_user_file(TOKEN_FILEPATH, SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        page_token = None
        calendars = []
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendars.append({
                    'id': calendar_list_entry['id'],
                    'summary': calendar_list_entry['summary']
                })
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        timezones = pytz.all_timezones

        return render_template('scheduler.html', calender_ids=calendars, timezones=timezones)

@scheduler.route('/authorize')
def authorize():
    creds = None

    if os.path.exists(TOKEN_FILEPATH):
        creds = OAuth2Credentials.from_authorized_user_file(TOKEN_FILEPATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILEPATH, SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(TOKEN_FILEPATH, 'w') as token:
            token.write(creds.to_json())
    
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILEPATH,
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:5001/oauth2callback')

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)

@scheduler.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILEPATH,
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        state=state,
        redirect_uri='http://localhost:5001/oauth2callback')

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return 'Credentials successfully fetched!'


@scheduler.route('/get_events', methods=['GET'])
def get_events():
    if not os.path.exists(TOKEN_FILEPATH):
        return redirect('/authorize')
    
    else:
        creds= OAuth2Credentials.from_authorized_user_file(TOKEN_FILEPATH, SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        page_token = None
        calendars = []
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendars.append({
                    'id': calendar_list_entry['id'],
                    'summary': calendar_list_entry['summary']
                })
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        timezones = pytz.all_timezones

        calendar_id = request.args.get('cal_id', '')
        event_name = request.args.get('event_name', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        convert_timezone = request.args.get('time_zone', None)
        tz = timezone(convert_timezone)

        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            start_date = tz.localize(start_date)
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            end_date = tz.localize(end_date)

        events_result = service.events().list(calendarId=calendar_id, timeMin=now, singleEvents=True,
        orderBy='startTime').execute()

        events_to_write = []

        events = events_result.get('items', [])
        for event in events:
            if event['summary'] == event_name:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                    
                event_start_date = parse_date(start, convert_timezone)

                if start_date <= event_start_date <= end_date:
                    
                    start_time_day = event_start_date.strftime('%A %m/%d')
                    start_time_time = event_start_date.strftime('%I:%M %p').lstrip("0")

                    event_end_date = parse_date(end, convert_timezone)
                    six_pm = datetime.datetime(event_end_date.year, event_end_date.month, event_end_date.day, 18, 0, 0)
                    
                    if event_end_date.time() > six_pm.time():
                        end_d = '6:00 PM'
                    else:
                        end_d = event_end_date.strftime('%I:%M %p').lstrip("0")

                        events_to_write.append(f"{start_time_day} {start_time_time} - {end_d}")

        return render_template('scheduler.html', events_to_write=events_to_write, calender_ids=calendars, timezones=timezones)
