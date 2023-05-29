from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound,Http404,HttpResponseRedirect
from django.shortcuts import redirect,reverse
from django.contrib.sessions.backends.db import SessionStore

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


from rest_framework.response import Response
from rest_framework.decorators import api_view

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events.readonly']

CLIENT_SECRETS_FILE = "client_secret.json"



# REDIRECT_URL = 'http://127.0.0.1:8000/rest/v1/calendar/redirect/'
REDIRECT_URL='https://4d10-122-50-209-48.ngrok-free.app/rest/v1/calendar/redirect/'

# REDIRECT_URL=''

API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
state=''
@api_view(['GET'])
def GoogleCalendarInitView(request):
    print('view 1')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URL

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        prompt='consent')
    # Store the state so the callback can verify the auth server response.
    print( '------session'+state)
    request.session['state'] = state
   
    print('-state--------'+request.session['state'])
    # print(Response({"authorization_url": authorization_url}))
    # return Response({"authorization_url": authorization_url})#from github code
    # return redirect(authorization_url)#working with error
    # return HttpResponse({"authorization_url": authorization_url})
    # return redirect(reverse('my_app:v2'))
    print('end of view 1')
    print(authorization_url)
    return HttpResponseRedirect(authorization_url)#working

@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    print('view 2')
    print('-----redirect page')
    # Specify the state when creating the flow in the callback so that it can
    # verify in the authorization server response.
    # print('---session check in redirect'+request.session['state'])
    # state = request.session['state']
    # if state is None:
    #     return Response({"error": "State parameter missing."})
    
    state=request.GET.get('state','')
    print(state)
    
    
    print('------')

    if state is None:
        return Response({"error": "State parameter missing."})

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    print('check2')
    print(flow)
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #      CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = 'https://4d10-122-50-209-48.ngrok-free.app/rest/v1/calendar/redirect/'
    print('check3')

      # Use the authorization server's response to fetch the OAuth 2.0 tokens.
   
    authorization_response = request.get_full_path()
    print('check4')
    print(request.get_full_path())
    print(authorization_response)
    authorization_response='https://4d10-122-50-209-48.ngrok-free.app'+authorization_response
    flow.fetch_token(authorization_response=authorization_response)
    print('check5')
   
    credentials = flow.credentials
    print('check A')
    request.session['credentials'] = credentials_to_dict(credentials)
    print('check6')
    # Check if credentials are in session
    # if 'credentials' not in request.session:
    #     return redirect('rest/v1/calendar/init/')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials'])
    print('check7')
     # Use the Google API Discovery Service to build client libraries, IDE plugins,
    # and other tools that interact with Google APIs.
    # The Discovery API provides a list of Google APIs and a machine-readable "Discovery Document" for each API
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    print('check8')
    # Returns the calendars on the user's calendar list
    calendar_list = service.calendarList().list().execute()
    # Getting user ID which is his/her email address
    # calendar_id = calendar_list['items'][0]['id']
    print(calendar_list['items'][0]['id'])
    # calender_id='ravikumarab24@gmail.com'

    # Getting all events associated with a user ID (email address)
    # events = service.events().list(calendarId=calendar_id).execute()
    events = service.events().list(calendarId='primary').execute()

    events_list_append = []
    if not events['items']:
        print('No data found.')
        return Response({"message": "No data found or user credentials invalid."})
    else:
        for events_list in events['items']:
            events_list_append.append(events_list)

    # return Response({"error": "calendar event aren't here"})
    return Response({"events": events_list_append})
    # return Response({"events": events})
    # return Response('abc')
    
    # return HttpResponse('second view')

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}





