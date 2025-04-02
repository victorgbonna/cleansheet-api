from urllib.parse import quote
from bs4 import BeautifulSoup as bs
import requests as req
import re 
import traceback
import sys
import csv
import json
import os
# from django.core.mail import send_mail,EmailMultiAlternatives
import time

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cloudinary.uploader
import cloudinary.api
import json,os

# Replace these variables with your Gmail account details
EMAIL = 'victorgbonna@gmail.com'
PASSWORD = 'fake ass fake'

def send_email(subject, message, to_email="victorgbonna8@gmail.com"):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def modify_csv(data, csv_file_path):
    # data = json.loads(json_data)

    # Append the data to CSV
    # with open(csv_file_path, 'a', newline='') as csvfile:
    #     fieldnames = data[0].keys() if data else []
    #     csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #     # Write headers if the file is empty
    #     if csvfile.tell() == 0:
    #         csv_writer.writeheader()

    #     # Write data to CSV
    #     for row in data:
    #         csv_writer.writerow(row)
    # return
    current_directory = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    csv_file_parent_path= os.path.join('csv', csv_file_path)
    csv_file_path = os.path.join(current_directory, csv_file_parent_path)  # Path to your CSV file

    fieldnames = data[0].keys() if data else []

    try:
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()

            # Write rows
            writer.writerows(data)
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def read_csv(csv_file):
    current_directory = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    
    csv_file_parent_path= os.path.join('csv', csv_file)

    csv_file_path = os.path.join(current_directory, csv_file_parent_path)  # Path to your CSV file
    try:
        list_of_dicts = []
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row= str(file.readline().strip())  # Read the first line and remove leading/trailing whitespace
            row_headers=first_row.split(',') 
            row_count=0
            for row in csv_reader:
                if(row_count==0):
                    row_count+=1
                    continue
                # print(row)
                # print('\n')
                match_dict={}
                for index,entry in enumerate(row):
                    value= int(entry.strip()) if entry.strip().isdigit() else entry.strip().replace('â€“','–')  
                    match_dict[row_headers[index]]=value
                list_of_dicts.append(match_dict)
        return list_of_dicts
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)
def update_file_in_cloudinary(public_id, updated_season_data):
    updated_data = json.dumps(updated_season_data)
    upload_result = cloudinary.uploader.upload(updated_data, resource_type="raw", public_id=public_id)
    return upload_result
    
def read_from_cloudinary(public_id):
    json_response = cloudinary.api.resource(public_id, resource_type="raw")
    season_data_in_json = json_response['content']
    season_data = json.loads(season_data_in_json)
    return season_data

def save_to_cloudinary(data):
    # json_string = json.dumps(data)

    json_string = {"key1": "value1", "key2": 3.14}
    json_data_string = json.dumps('./csv/epl_2022–23.csv')     
    print('in this')

    upload_result = cloudinary.uploader.upload(
        # data
        'csv/epl_2022–23.csv'
    )
    print(upload_result)
    cloud_file_name = upload_result['url']
    return [cloud_file_name, upload_result['public_id']]
def convert_to_csv(csv_name, comp):
    folder_name = 'csv'
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_directory, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    csv_filename = os.path.join(csv_name)
    
    # Writing to a CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Define CSV writer
        writer = csv.DictWriter(csvfile, fieldnames=comp[0].keys())

        # Write header
        writer.writeheader()

        # Write rows
        writer.writerows(comp)
    return csv_filename

def get_teams_for_that_season(season_input, comp):
    # https://en.wikipedia.org/wiki/2011%E2%80%9312_La_Liga
    season_url='https://en.wikipedia.org/wiki/'
    
    if comp.lower()=="epl":
        year_season_ended=int(season_input.split('–')[1].strip())
        # year_season_begun, year_season_ended = [l.strip() for l in season_input.split('–')]
        # slash_year_ended= year_season_ended[2:]        
        
        # check if it has an FA(before 2007) in its url or not
        if year_season_ended<7:
            season_url+=quote(season_input)+'_FA_Premier_League'
        else:
            season_url+=quote(season_input)+'_Premier_League'
    
    if comp.lower()=="la liga":
        year_season_ended=int(season_input.split('–')[1].strip())
        season_url+=quote(season_input)+'_La_Liga'
    
    if comp.lower()=="serie a":
        year_season_ended=int(season_input.split('–')[1].strip())
        season_url+=quote(season_input)+'_Serie_A'
    # visit the site and extract the teams and their URL
    try:

        # print(season_url)
        # https://en.wikipedia.org/wiki/2011%E2%80%9312_Premier_League
        season_page=req.get(season_url)
        # print(season_url, year_season_ended)
        season_page_to_soup= bs(season_page.text,'html.parser')


        table_section= season_page_to_soup.find('h2', attrs={"id":"League_table"}).find_next('table')
        teams_table_data = [th for th in season_page_to_soup.find_all('th') if len(th.contents) and len(th.contents)!=0 and th.find('a') == th.contents[0]]
        # teams_table_data = [th for th in season_page_to_soup.find_all('th')]
        # print(teams_table_data[0])
        # teams_table_data= season_page_to_soup.find_all('th', lambda tag: tag.findChild('a') == tag.contents[0])
        # print(teams_table_data)
        participating_teams=[]
        for team_table in teams_table_data:
            try:
                if team_table['style'] == None or 'text-align: left; white-space:nowrap;font-weight: normal;' not in team_table['style']:
                    continue
                club_link_tag=team_table.find('a')
                if club_link_tag.has_attr('title') == None:
                    continue
                team_name=club_link_tag.text
                team_url_link='https://en.wikipedia.org'+club_link_tag['href']
                team_url_season_link=team_url_link.replace('org/wiki/', 'org/wiki/'+season_input+'_')
                team_url_season_link+='_season'
                participating_teams.append({
                    'team_name':team_name, 'team_url_link':team_url_link, 
                    'team_title':club_link_tag['title'],
                    'team_url_season_link':team_url_season_link
                })
            except Exception as e:
                continue
        return {'teams':participating_teams}
    except Exception as E:
        print(E)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno  # Get the line number where the exception occurred
        print("An error occurred on line:", line_number)
        traceback.print_exc()  # Print the traceback information
        # return return_dict
        return {'teams':[]}

def run_expression_as_function(expression, variable=None, line_number="0", return_on_error="N/A"):
    try:
        result = eval(expression, variable)
        return result
    except Exception as e:
        # print(f"Error: {e}")
        # print("An error occurred on line:", line_number)
        traceback.print_exc()  # Print the traceback iformation
        return return_on_error

def get_participating_team_scores(participating_team_dict,teams_in_fixtures_for_duplicates, league):
    team_name=participating_team_dict['team_name']        
    league_name="Premier_League"
    if league=="la liga":
        league_name=="La_Liga"
    elif league=="serie a":
        league_name=="Serie_A"    
    season_url=participating_team_dict['team_url_season_link']
    # # check for fixtures to avoid duplicates
    # h2h=home_team['title']+' vs '+away_team_title
    # print('participating_team_dict', participating_team_dict)
    # if(h2h in teams_in_fixtures_for_duplicates):
    #     continue
    # team_matches=[fixture for fixture in fixtures if ((fixture['home_team_title']==team_name or fixture['away_team_title']==team_name) and fixture['home_team_title']+fixture['away_team_title'] not in teams_in_fixtures_for_duplicates)]
    return_dict={"non_wiki_team":None,  "fixture_in_duplicates":None, "match_summary":None}
    # print('return - ', return_dict)
    try:
        print(season_url)
        participating_team_soup=bs(req.get(season_url).text, 'html.parser')
        [code_with_headXscript.extract() for code_with_headXscript in participating_team_soup.find_all(['head', 'script', 'footer'])]
        # print(participating_team_soup)
        # print('\n')
        # pattern = re.compile(r'The league fixtures were announced on', re.IGNORECASE)
        try:
            announcement_collection=participating_team_soup.find_all(lambda tag: tag.name == 'p' and 'league fixtures' in tag.text.lower())
            print(announcement_collection)
            print([len(tag) for tag in announcement_collection])
            announcement=[]
            announcement_alt= participating_team_soup.find('span',attrs={'class':'mw-headline', 'id':league_name})
            announcement=announcement_alt.parent
            # if len(announcement_collection)>1:
            #     announcement=[tag for tag in announcement_collection if len(tag.text)<300]
            #     # epl 2018 19 needed len adjustments, from 80 to 90 both 2017 18
            print('tag length ', len(announcement))
            print('tag', announcement)

            # if len(announcement)==0:
            #     print('no announcement')
            #     # print('is none')
            #     announcement_alt= participating_team_soup.find('span',id="Results_by_round")
            #     if announcement_alt:
            #         announcement=announcement_alt.parent
            #     else:
            #         announcement_alt= participating_team_soup.find('span',id="Results_by_matchday")
            #         if announcement_alt:
            #             announcement=announcement_alt.parent
            #         else:
            #             # for 2010 2011 Premier League campaign resumed and it is so bad
            #             # <span class="mw-headline" id="La_Liga">La Liga</span>
            #             announcement_alt= participating_team_soup.find('span',attrs={'class':'mw-headline', 'id':league_name})
            #             announcement=announcement_alt.parent
            # else:
            #     announcement=announcement[0]
            tags_after_announcement= announcement.find_next_siblings('div', class_="vevent")
            # print('return - ', return_dict)
            
            # print(tags_after_announcement)
        except Exception as e:
            print(e)
            print('error here')
            return_dict={**return_dict, "non_wiki_team":participating_team_dict['team_name']}
            # non_wiki_teams.append(participating_team_dict['team_name'])
            print(participating_team_dict['team_name']+' non wiki team')
            # print('return - ', return_dict)
            
            return return_dict
        if len(tags_after_announcement)==0:
            print('length of tag is 0')
            return_dict={**return_dict, "non_wiki_team":participating_team_dict['team_name']}
            return return_dict
            print('return - ', return_dict)
        
        match_summary_for_team=[]
        fixtures_for_duplicates_for_team=[]
        for event in tags_after_announcement[:38]:
            event_table=event.find('table')

            h2h= [team.find('b').text.strip() for team in event_table.find_all('td', attrs={'class':'vcard attendee'})]
            h2h_to_string=' vs '.join(h2h)
            print(h2h)

            if(h2h_to_string in teams_in_fixtures_for_duplicates):
                continue
            # first td is the match date and time
            # return_dict={**return_dict, "fixture_in_duplicates":h2h_to_string}
            # teams_in_fixtures_for_duplicates.append(h2h_to_string)
            match_date_time_tag= run_expression_as_function('''event_table.find('tr').find('td', attrs={'style':"width:19%"})''', {"event_table":event_table}, 1)
            # print('return except- ', return_dict)
            
            match_date= run_expression_as_function('''match_date_time_tag.find('span').text.split('(')[0].replace('&nbsp;', ' ').replace('\xa0',' ').strip()''', {"match_date_time_tag":match_date_time_tag}, 2)
            game_week= run_expression_as_function('''match_date_time_tag.find('small').text''', {"match_date_time_tag":match_date_time_tag},3)
            stadium= run_expression_as_function('''event_table.find('span', class_='location').text''', {"event_table":event_table}, 4)
                
            referee= run_expression_as_function('''event_table.find('span', class_="location").parent.text.split('Referee: ')[-1]''', {"event_table":event_table},5)
            # print(stadium)
            
            match_time_tr= event_table.find_all('tr', limit=2)
            match_time= match_time_tr[1].find('td').text
            
            match_time= run_expression_as_function('''match_time_tr[1].find('td').text.strip()''', {"match_time_tr":match_time_tr},6)
            start_time= run_expression_as_function('''int(match_time.split(':')[0])''', {"match_time":match_time},7, 0)
            # print('start_time', start_time)
            # match_period="N/A"
            match_period='N/A' if int(start_time)==0 else 'early kick-off' if int(start_time)<15 else 'standard kick-off' if int(start_time)<19 else 'late kick-off'
            score_line= run_expression_as_function('''event_table.find("td", attrs={'class':'vcard attendee'}).find_next_sibling('td', attrs={"style":"width:12%;text-align:center"}).text.strip()''',{"event_table":event_table},9)
            
            # print('score line - '+score_line)
            home_team, away_team= h2h
            # print(home_team)
            # print(score_line)
            home_goals, away_goals= score_line.strip().split('–')

            # min home 31-45+ goals
            # for the goals now 
            goals_capture= match_time_tr[1].find_all('span', class_="fb-goal")
            match_goals_collection={
                'min 1-15 goals':0,'min 16-30 goals':0,'min 31-45+ goals':0,
                'min 46-60 goals':0,'min 61-75 goals':0,
                'min 76-90+ goals':0,
                '45+ goals':0,'90+ goals':0,'1st_half goals':0,'2nd_half goals':0,'stoppage_time goals':0,
                'normal_time goals':0
            }

            for key in list(match_goals_collection.keys()):
                split_key=key.rsplit(' ', 1)
                for side in [' home ', ' away ']:
                    match_goals_collection[side.join(split_key)]=0
            # print(match_goals_collection)
            for goal in goals_capture:
                goal_periods= goal.find_all('span')[2:]
                td_parent=goal_periods[0].find_parent('td')
                home_scored=td_parent.has_attr('style')
                who_scored=' home ' if home_scored else ' away '
                
                for goal_period in goal_periods:
                    # print(goal_period)
                    goal_time=goal_period.text
                    goal_time_int=int(('').join(list(filter(str.isdigit,goal_time.split('+')[0]))))   
                    if '+' in goal_time:
                        match_goals_collection['stoppage_time'+who_scored+'goals']+=1
                        match_goals_collection['stoppage_time goals']+=1
                        if goal_time_int==45:
                            match_goals_collection['45+'+who_scored+'goals']+=1                             
                            match_goals_collection['45+ goals']+=1                             
                        else: 
                            match_goals_collection['90+'+who_scored+'goals']+=1                             
                            match_goals_collection['90+ goals']+=1
                    else:
                        match_goals_collection['normal_time'+who_scored+'goals']+=1                             
                        match_goals_collection['normal_time goals']+=1
                        
                    if goal_time_int<16:
                        match_goals_collection['1st_half'+who_scored+'goals']+=1
                        match_goals_collection['1st_half goals']+=1                             

                        match_goals_collection['min 1-15'+who_scored+'goals']+=1                             
                        match_goals_collection['min 1-15 goals']+=1
                    elif goal_time_int<31:
                        match_goals_collection['1st_half'+who_scored+'goals']+=1
                        match_goals_collection['1st_half goals']+=1

                        match_goals_collection['min 16-30'+who_scored+'goals']+=1
                        match_goals_collection['min 16-30 goals']+=1
                    elif goal_time_int<46:
                        match_goals_collection['1st_half'+who_scored+'goals']+=1
                        match_goals_collection['1st_half goals']+=1

                        match_goals_collection['min 31-45+'+who_scored+'goals']+=1
                        match_goals_collection['min 31-45+ goals']+=1
                    
                    elif goal_time_int<61:
                        match_goals_collection['2nd_half'+who_scored+'goals']+=1
                        match_goals_collection['2nd_half goals']+=1

                        match_goals_collection['min 46-60'+who_scored+'goals']+=1
                        match_goals_collection['min 46-60 goals']+=1
                    elif goal_time_int<76:
                        match_goals_collection['2nd_half'+who_scored+'goals']+=1
                        match_goals_collection['2nd_half goals']+=1
                        
                        match_goals_collection['min 61-75'+who_scored+'goals']+=1
                        match_goals_collection['min 61-75 goals']+=1
                    elif goal_time_int<91:
                        match_goals_collection['2nd_half'+who_scored+'goals']+=1
                        match_goals_collection['2nd_half goals']+=1

                        match_goals_collection['min 76-90+'+who_scored+'goals']+=1
                        match_goals_collection['min 76-90+ goals']+=1
                    
                    # some gameweeks are faulty, so I want to select just 1
            match_summary={
                'home_team':home_team.strip(),'away_team':away_team, 'match_period':match_period,
                'game_week':game_week,'match_date':match_date,'match_time':match_time,
                'stadium':stadium,'score_line':score_line,'total_goals':int(home_goals)+ int(away_goals),
                'away_goals':away_goals, 'home_goals':home_goals, 'referee': referee,
                **match_goals_collection
            }
            match_summary_for_team.append(match_summary)
            fixtures_for_duplicates_for_team.append(h2h_to_string)
            # print(match_summary)
            # clean_sheet_data.append(match_summary)
            # match_summary={}
            # print('\n')
        # print('\n')
        return_dict={**return_dict, "match_summary":match_summary_for_team, "fixture_in_duplicates":fixtures_for_duplicates_for_team}
        return return_dict
    except Exception as E:
        # clean_sheet_data.append({**})
        print(E)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno  # Get the line number where the exception occurred
        print("An error occurred on line:", line_number)
        traceback.print_exc()  # Print the traceback information
        return return_dict

def get_non_wiki_teams_versus(non_wiki_teams):
    assemble_matches=[]
    if(len(non_wiki_teams)>1):
        for i in range(len(non_wiki_teams)):
            the_team= non_wiki_teams[i]
            other_teams=non_wiki_teams[:i]+non_wiki_teams[i+1:]
            for other_team in other_teams:
                assemble_matches.append({'home_team':the_team, 'away_team':other_team})
    return assemble_matches
def get_cleansheets(season, comp, id):
    # print('id is ', id)
    # consumer = MyConsumer({"type": "websocket.connect"})
    season_input=season.replace('-', '–')

    room_name=(season_input.replace('–', '')+comp+id).replace(' ', '')
    # print('reached here')
    # print(room_name)
    
    # consumer.start_fetch({"room":room_name, "channel_name":id})
    # return

    teamsXfixtures=get_teams_for_that_season(season_input, comp)

    participating_teams= teamsXfixtures['teams']
    # fixtures= teamsXfixtures['fixtures']
    
    teams_in_fixtures_for_duplicates=[]
    clean_sheet_data=[]
    non_wiki_teams=[]
    
    team_no=len(participating_teams)
    length_per_team= 100/len(participating_teams[:3])
    for index,participating_team_dict in enumerate(participating_teams):
        team_name=participating_team_dict['team_name']        

        season_url=participating_team_dict['team_url_season_link']
        # # check for fixtures to avoid duplicates
        # h2h=home_team['title']+' vs '+away_team_title
        # print('participating_team_dict', participating_team_dict)
        # if(h2h in teams_in_fixtures_for_duplicates):
        #     continue
        # team_matches=[fixture for fixture in fixtures if ((fixture['home_team_title']==team_name or fixture['away_team_title']==team_name) and fixture['home_team_title']+fixture['away_team_title'] not in teams_in_fixtures_for_duplicates)]
        
        try:
            participating_team_soup=bs(req.get(season_url).text, 'html.parser')
            [code_with_headXscript.extract() for code_with_headXscript in participating_team_soup.find_all(['head', 'script', 'footer'])]
            # print(participating_team_soup)
            # print('\n')
            # pattern = re.compile(r'The league fixtures were announced on', re.IGNORECASE)
            try:
                announcement=participating_team_soup.find(lambda tag: tag.name == 'p' and 'league fixtures' in tag.text.lower())
                if announcement is None:
                    # print('is none')
                    
                    announcement= participating_team_soup.find('span',id="Results_by_round").parent
                    # if announcement is None:
                    #     announcement
                tags_after_announcement= announcement.find_next_siblings('div', class_="vevent")
                # print(tags_after_announcement)
            except:
                non_wiki_teams.append(participating_team_dict['team_name'])
                # print(participating_team_dict['team_name']+' non wiki team')
                continue
            if len(tags_after_announcement)==0:
                non_wiki_teams.append(participating_team_dict['team_name'])
                # print(participating_team_dict['team_name']+' non wiki team')
                continue
                
            for event in tags_after_announcement[:38]:
                event_table=event.find('table')

                h2h= [team.find('b').text.strip() for team in event_table.find_all('td', attrs={'class':'vcard attendee'})]
                h2h_to_string=' vs '.join(h2h)
                # print(h2h)
                if(h2h_to_string in teams_in_fixtures_for_duplicates):
                    continue
                # first td is the match date and time
                teams_in_fixtures_for_duplicates.append(h2h_to_string)
                match_date_time_tag= run_expression_as_function('''event_table.find('tr').find('td', attrs={'style':"width:19%"})''', {"event_table":event_table}, 1)
                
                match_date= run_expression_as_function('''match_date_time_tag.find('span').text.split('(')[0].replace('&nbsp;', ' ').replace('\xa0',' ').strip()''', {"match_date_time_tag":match_date_time_tag}, 2)
                game_week= run_expression_as_function('''match_date_time_tag.find('small').text''', {"match_date_time_tag":match_date_time_tag},3)
                stadium= run_expression_as_function('''event_table.find('span', class_='location').text''', {"event_table":event_table}, 4)
                    
                referee= run_expression_as_function('''event_table.find('span', class_="location").parent.text.split('Referee: ')[-1]''', {"event_table":event_table},5)
                # print(stadium)
                
                match_time_tr= event_table.find_all('tr', limit=2)
                match_time= match_time_tr[1].find('td').text
                
                match_time= run_expression_as_function('''match_time_tr[1].find('td').text.strip()''', {"match_time_tr":match_time_tr},6)
                start_time= run_expression_as_function('''int(match_time.split(':')[0])''', {"match_time":match_time},7, 0)
                # print('start_time', start_time)
                # match_period="N/A"
                match_period='N/A' if int(start_time)==0 else 'early kick-off' if int(start_time)<15 else 'standard kick-off' if int(start_time)<19 else 'late kick-off'
                score_line= run_expression_as_function('''event_table.find("td", attrs={'class':'vcard attendee'}).find_next_sibling('td', attrs={"style":"width:12%;text-align:center"}).text.strip()''',{"event_table":event_table},9)
                
                
                home_team, away_team= h2h
                print(score_line)
                home_goals, away_goals= score_line.strip().split('–')

# min home 31-45+ goals
                # for the goals now 
                goals_capture= match_time_tr[1].find_all('span', class_="fb-goal")
                match_goals_collection={
                    'min 1-15 goals':0,'min 16-30 goals':0,'min 31-45+ goals':0,
                    'min 46-60 goals':0,'min 61-75 goals':0,
                    'min 76-90+ goals':0,
                    '45+ goals':0,'90+ goals':0,'1st_half goals':0,'2nd_half goals':0,'stoppage_time goals':0,
                    'normal_time goals':0
                }

                for key in list(match_goals_collection.keys()):
                    split_key=key.rsplit(' ', 1)
                    for side in [' home ', ' away ']:
                        match_goals_collection[side.join(split_key)]=0
                # print(match_goals_collection)
                for goal in goals_capture:
                    goal_periods= goal.find_all('span')[2:]
                    td_parent=goal_periods[0].find_parent('td')
                    home_scored=td_parent.has_attr('style')
                    who_scored=' home ' if home_scored else ' away '
                    
                    for goal_period in goal_periods:
                        # print(goal_period)
                        goal_time=goal_period.text
                        goal_time_int=int(('').join(list(filter(str.isdigit,goal_time.split('+')[0]))))   
                        if '+' in goal_time:
                            match_goals_collection['stoppage_time'+who_scored+'goals']+=1
                            match_goals_collection['stoppage_time goals']+=1
                            if goal_time_int==45:
                                match_goals_collection['45+'+who_scored+'goals']+=1                             
                                match_goals_collection['45+ goals']+=1                             
                            else: 
                                match_goals_collection['90+'+who_scored+'goals']+=1                             
                                match_goals_collection['90+ goals']+=1
                        else:
                            match_goals_collection['normal_time'+who_scored+'goals']+=1                             
                            match_goals_collection['normal_time goals']+=1
                            
                        if goal_time_int<16:
                            match_goals_collection['1st_half'+who_scored+'goals']+=1
                            match_goals_collection['1st_half goals']+=1                             
 
                            match_goals_collection['min 1-15'+who_scored+'goals']+=1                             
                            match_goals_collection['min 1-15 goals']+=1
                        elif goal_time_int<31:
                            match_goals_collection['1st_half'+who_scored+'goals']+=1
                            match_goals_collection['1st_half goals']+=1

                            match_goals_collection['min 16-30'+who_scored+'goals']+=1
                            match_goals_collection['min 16-30 goals']+=1
                        elif goal_time_int<46:
                            match_goals_collection['1st_half'+who_scored+'goals']+=1
                            match_goals_collection['1st_half goals']+=1

                            match_goals_collection['min 31-45+'+who_scored+'goals']+=1
                            match_goals_collection['min 31-45+ goals']+=1
                        
                        elif goal_time_int<61:
                            match_goals_collection['2nd_half'+who_scored+'goals']+=1
                            match_goals_collection['2nd_half goals']+=1

                            match_goals_collection['min 46-60'+who_scored+'goals']+=1
                            match_goals_collection['min 46-60 goals']+=1
                        elif goal_time_int<76:
                            match_goals_collection['2nd_half'+who_scored+'goals']+=1
                            match_goals_collection['2nd_half goals']+=1
                            
                            match_goals_collection['min 61-75'+who_scored+'goals']+=1
                            match_goals_collection['min 61-75 goals']+=1
                        elif goal_time_int<91:
                            match_goals_collection['2nd_half'+who_scored+'goals']+=1
                            match_goals_collection['2nd_half goals']+=1

                            match_goals_collection['min 76-90+'+who_scored+'goals']+=1
                            match_goals_collection['min 76-90+ goals']+=1
                        
                match_summary={
                    'home_team':home_team.strip(),'away_team':away_team, 'match_period':match_period,
                    'game_week':game_week,'match_date':match_date,'match_time':match_time,
                    'stadium':stadium,'score_line':score_line,'total_goals':int(home_goals)+ int(away_goals),
                    'away_goals':away_goals, 'home_goals':home_goals, 'referee': referee,
                    **match_goals_collection
                }
                # print(match_summary)
                clean_sheet_data.append(match_summary)
                match_summary={}
                # print('\n')
            # print('\n')
        
        except Exception as E:
            # clean_sheet_data.append({**})
            print(E)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_number = exc_tb.tb_lineno  # Get the line number where the exception occurred
            print("An error occurred on line:", line_number)
            traceback.print_exc()  # Print the traceback information
            continue
    
    # {'home_team_title':home_team['title'], 'away_team_title': away_team_title, 'matchday_home_goals':matchday_home_goals, 
    # matchday_away_goals':matchday_away_goals,'away_team_shortcut': away_team_shortcut ,'matchday_score':matchday_score
    # }
    
    assemble_matches=[]
    
    if(len(non_wiki_teams)>1):
        # consumer.change_loading_percent({"room":room_name, "label":'Getting missing matches..', "percent":98})
        for i in range(len(non_wiki_teams)):
            the_team= non_wiki_teams[i]
            other_teams=non_wiki_teams[:i]+non_wiki_teams[i+1:]
            for other_team in other_teams:
                assemble_matches.append({'home_team':the_team, 'away_team':other_team})

    # consumer.change_loading_percent({"room":room_name, "label":'Finalizing..', "percent":99})
    return {'clean_sheet_data':clean_sheet_data, 'non_wiki_teams':assemble_matches}
    # assemble_matches=[]    
    # clean_sheet_add_for_non_wiki_team=[]
    # if(len(non_wiki_teams)>1):
    #     for i in range(len(non_wiki_teams)):
    #         the_team= non_wiki_teams[i]
    #         other_teams=non_wiki_teams[:i]+non_wiki_teams[i+1:]
    #         for other_team in other_teams:
    #             assemble_matches.append({'home_team':the_team, 'away_team':other_team})
        # for non_wiki_team in non_wiki_teams
        # print('assembles', assemble_matches)
        # for assemble_match in assemble_matches:
        #     # print(fixture['home_team'], fixture['away_team'], assemble_match)
        #     # if assemble_match['home_team'] in fixture['home_team'] and assemble_match['away_team'] in fixture['away_team']:
        #     #     print(fixture['home_team'], fixture['away_team'])
                
        #     assemble_fixture=[fixture for fixture in fixtures if assemble_match['home_team'] in fixture['home_team'] and assemble_match['away_team'] in fixture['away_team']]
        #     # print('assemble', assemble_fixture)            
        #     assemble_fixture=assemble_fixture[0]
        #     clean_sheet_add_for_non_wiki_team.append({
        #         **assemble_fixture, 'home_team':assemble_match['home_team'] ,'away_team':assemble_match['away_team']
        #     })

    #rough here
        # for fixture in fixtures:
        #     for assemble_match in assemble_matches:
        #         if
        #         print(fixture['home_team'],fixture['away_team'], non_wiki_team)
        #         if(non_wiki_team in fixture['home_team']):
        #         if(non_wiki_team in fixture['away_team']):
                
        #     # if any(team in fixture['home_team'] for team in non_wiki_teams):
        #     # and any(team in fixture['away_team'] for team in non_wiki_teams):
        #         print(fixture+' in no wiki')
        #         clean_sheet_add_for_non_wiki_team.append({**fixture, 'home_team'::})

    # clean_sheet_add_for_non_wiki_team=[fixture for fixture in fixtures if any(team in fixture['home_team'] for team in non_wiki_teams) and any(team in fixture['away_team'] for team in non_wiki_teams)]     
    # print(clean_sheet_add_for_non_wiki_team, non_wiki_teams)
    #rough there
    
    # clean_sheet_data=[*clean_sheet_data, *clean_sheet_add_for_non_wiki_team]

    # for item in clean_sheet_data:
    #     for key in item:
    #         if item[key] is None or item[key] != item[key]:
    #             item[key] = ""
# time to carry it and get the actual score timelime

