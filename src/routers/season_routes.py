from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import NoResultFound
from ..database import SessionLocal
from .. import crud, utils,schemas
from typing import Optional
import json
from sqlalchemy.orm import Session
import traceback
import sys
import csv
import os
import time

router= APIRouter()

db = SessionLocal()
# def start_fetch(self, text_data):
#     copy_text_data=text_data
#     print('copy', copy_text_data)
#     self.send(text_data=json.dumps({
#         **copy_text_data
#     }))
@router.get("/all")
def read_api(filterBy: str= None):
    try:
        seasons= crud.get_seasons(db=db, filterBy=filterBy)     
        return {
                "message":"Message successful",
                "data":{
                    "seasons":seasons
                }
            }
    except Exception as e:
        print(e)    
        return JSONResponse(
            status_code=400,
            content={"error":{"message": "Something went wrong"}}
        )  

# 7 seconds
@router.post("/search-league-info")
def search_league_info(season_data: schemas.Season):
    try:
        season_data= json.loads(season_data.model_dump_json())
        print('SEASON ',season_data)

        # try:
        possible_leagues=['epl', 'la liga', 'serie a']
        # 2022-23
        possible_years=[str(season)+'–'+str(season+1)[2:] for season in range(2000,2023)]

        print(possible_years,possible_leagues)
        
        if not bool(season_data) or not bool(season_data['league']) or not bool(season_data['year']):
            return JSONResponse(
                status_code=400,
                                content={"error":{"message": "Invalid data"}}
            )    
        if season_data['league'] not in possible_leagues:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )     
            # print('req ',season_data['league'])
                
        if season_data['year'] not in possible_years:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )    
        league_input, year_input= season_data['league'], season_data['year']

        db = SessionLocal()
        season_exists= crud.find_season_by_leagueXyear(db=db, league=league_input, year=year_input)

        print('season_exists ', season_exists)
        if season_exists is not None:
            crud.update_season_visits(db=db, league=league_input, year=year_input)
            return {
                "message":"Message successful",
                "data":{
                    "percent":"40%",
                    "body":season_data,
                    "api_endpoint":"get_existing_league_stats",
                    "label":"Fetching teams and matches"
                }
            }
        else:
            season_input=year_input.replace('-', '–')
            # return
            teamsXfixtures=utils.get_teams_for_that_season(season_input, league_input)
            participating_teams= teamsXfixtures['teams']
            return {
                "message":"Message successful",
                "data":{
                    "percent":"10%",
                    "body":{**season_data, "participating_teams":participating_teams, "len_teams":len(participating_teams)},
                    "api_endpoint":"get_new_league_stats",
                    "label":"Fetching teams and matches"
                }
            }        
    except Exception as e:
        print(e)    
        return JSONResponse(
            status_code=400,
            content={"error":{"message": "Something went wrong"}}
        )  


@router.post("/get-league-info")
def get_league_info(season_data: schemas.Season):
    season_data= json.loads(season_data.model_dump_json())
    try:
        possible_leagues=['epl', 'la liga', 'serie a']
        # 2022-23
        possible_years=[str(season)+'–'+str(season+1)[2:] for season in range(2000,2023)]
        # season_data= json.loads(season_data.model_dump_json())

        # print(possible_years,possible_leagues)
        
        if not bool(season_data) or not bool(season_data['league']) or not bool(season_data['year']):
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid data"}}
            )    
        if season_data['league'] not in possible_leagues:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )     
            # print('req ',season_data['league'])
                
        if season_data['year'] not in possible_years:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid year data"}}
            )    
        league_input, year_input= season_data['league'], season_data['year']

        db = SessionLocal()
        season_exists= crud.find_season_by_leagueXyear(db=db, league=league_input, year=year_input)
        if season_exists is not None:
            csv_data_for_that_season= season_exists.fixtures
            del season_exists.fixtures
            # utils.read_from_cloudinary(season_exists.cloudPublicId)
            
            return {
                "message":"Message successful",
                "data":{
                    "body":season_exists
                    ,"csv_data":csv_data_for_that_season
                }
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"error":{"message": "League info not found"}}
            )    
    except Exception as e:
        print(f"Error: {e}")
        # print("An error occurred on line:", line_number)
        # traceback.print_exc()  # Print the traceback iformation
        # return return_on_error

        return JSONResponse(
            status_code=400,
            error={"message": "Something went wrong"}
        ) 


@router.post("/get-new-league-info")
def get_new_league_info(season_data: schemas.NewSeason):
    season_data= json.loads(season_data.model_dump_json())
    print(season_data.keys())
    try:
        possible_leagues=['epl', 'la liga', 'serie a']
        # 2022-23
        possible_years=[str(season)+'–'+str(season+1)[2:] for season in range(2000,2023)]

        print(possible_years,possible_leagues)
        
        if not bool(season_data) or not bool(season_data['league']) or not bool(season_data['year']):
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid data"}}
            )    
        if season_data['league'] not in possible_leagues:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )         
                
        if season_data['year'] not in possible_years:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid year data"}}
            )    
        # league_input, year_input= season_data['league'], season_data['year']
        participating_teams=season_data["participating_teams"]
        print(participating_teams)
        db = SessionLocal()
        teams_in_fixtures_for_duplicates=[]
        match_summaries=[]
        non_wiki_teams=[]

        for index,participating_team_dict in enumerate(participating_teams[:6]):
            print('pased here-',index)
            # return
            return_dict=utils.get_participating_team_scores(participating_team_dict,teams_in_fixtures_for_duplicates, league=season_data['league'])
            # print('return_dict -', return_dict)
            if return_dict["non_wiki_team"] is not None:
                print('non_wiki_team', return_dict["non_wiki_team"])
                non_wiki_teams.append(return_dict["non_wiki_team"])
            print('passed non_wiki')
            if return_dict["fixture_in_duplicates"] is not None:
                teams_in_fixtures_for_duplicates+=return_dict["fixture_in_duplicates"]
            print('passed dupli')
            if return_dict["match_summary"] is not None:
                match_summaries+=return_dict["match_summary"]
            print('passed match')
        # return {
        #     "data":{
        #         "teams_in_fixtures_for_duplicates":teams_in_fixtures_for_duplicates,
        #         "match_summaries":match_summaries,
        #         "non_wiki_teams":non_wiki_teams,
        #         "league":season_data['league'],
        #         "year": season_data['year']
        #     }
        # }
            
        if(len(match_summaries)<1):
            # utils.send_email()
            html_message = f"<p>There might be duplicates in this data</p><p>ID: <strong>{'2'}</strong></p><p>League: <strong>{str(season_data['league'])}</strong></p><p>Year: <strong>{str(season_data['year'])}</strong></p>"
            # utils.send_email('No data in new cleansheet!!',html_message)
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Something went wrong on our end"}}
            )    
        isComplete=True
        remainingFixtures=[]
        if len(non_wiki_teams)>1:
            isComplete=False
            remainingFixtures=non_wiki_teams
        overFilled=len(match_summaries)-380
        # supposed_total_matches=(len(participating_teams)*(len(participating_teams)-1))/2
        # overFilled=len(match_summaries)-(supposed_total_matches*2)
        
        body={"league":season_data['league'], "year": season_data['year'], "isComplete":isComplete, "remainingFixtures":remainingFixtures, "overFilled":overFilled}
        # csv_name= season_data['league']+'_'+season_data['year']+'.csv'
        
        # season_file_name=utils.convert_to_csv(csv_name,match_summaries)
        # print('seas', season_file_name)
        # cloud_file=utils.save_to_cloudinary(season_file_name)
        
        new_season=crud.save_season(db=db, 
                                    league= body['league'], year=body['year'], isComplete=body['isComplete'], 
                                    overFilled=body['overFilled'], remainingFixtures=body['remainingFixtures'],
                                    fixtures=match_summaries
                                    # cloudPublicId=cloud_file[1], csvFileLink=cloud_file[0]
                                )
        del new_season.fixtures
        # print('new season-', new_season)

        # if not isComplete:
        #     html_message = f"<p>There might be duplicates in this data</p><p>ID: <strong>{'2'}</strong></p><p>League: <strong>{str(body['league'])}</strong></p><p>Year: <strong>{str(body['year'])}</strong></p>"
        #     utils.send_email('Duplicates in new cleansheet!!',html_message)
        # elif overFilled>0:
        #     html_message = f"<p>There might be missing matches in this data</p><p>ID: <strong>{'2'}</strong></p><p>League: <strong>{str(body['league'])}</strong></p><p>Year: <strong>{str(body['year'])}</strong></p>"
        #     utils.send_email('Missing matches in new cleansheet!!',html_message)
        return {
            "message":"Data saved",
            "data":{
                "body": new_season,
                "csv_data":match_summaries  
            }
        }
        # else:
        #     html_alert_message = f"<p>There has been a new fetch</p><p>ID: <strong>{str(serializer.data['id'])}</strong></p><p>League: <strong>{str(league_input)}</strong></p><p>Year: <strong>{str(year_input)}</strong></p>"
        #     send_email('New cleansheet added!!',html_alert_message)    
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=400,
            content={"error":{"message": "Something went wrong"}}
        ) 


# ["seasons/all", "seasons/search-league-info", "seasons/get-league-info", "seasons/new-league-info", "seasons/get-new-league-info"]  
@router.put("/update-league-info")
def update_league_info(season_data: schemas.UpdateSeason):
    # utils.update_file_in_cloudinary(your_public_id, updated_data)
    # instead edit the fixtures
    #then complete the rest
    season_data=json.loads(season_data.model_dump_json())
    try:
        possible_leagues=['epl', 'la liga', 'serie a']
        # 2022-23
        possible_years=[str(season)+'–'+str(season+1)[2:] for season in range(2000,2023)]
        if not bool(season_data) or not bool(season_data['league']) or not bool(season_data['year']):
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid data"}}
            )    
        if season_data['league'] not in possible_leagues:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )     
            # print('req ',season_data['league'])
                
        if season_data['year'] not in possible_years:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid year data"}}
            )    
        # league_input, year_input= season_data['league'], season_data['year']
        # add_csv_file=season_data["add_csv_file"]
        league_input, year_input= season_data['league'], season_data['year']
        
        
        db = SessionLocal()
        csvFileLink=season_data.add_csv_file
        isComplete = season_data.isComplete
        overFilled = season_data.overFilled
        remainingFixtures = season_data.remainingFixtures

        season_exists_updated= crud.update_season(
            db=db, league=league_input, year=year_input, 
            isComplete=isComplete, overFilled=overFilled, 
            remainingFixtures=remainingFixtures, csvFileLink=csvFileLink
        )
        if season_exists_updated is None:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "League not found"}}
            ) 
        return {
            "message":"Data saved",
            "data":{
                "body": season_data
                # ,"csv_data":csv_data_for_that_season
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error":{"message": "Something went wrong"}}
        ) 
    

@router.patch("/update-league-csv")
def update_season_csv_url(season_data: schemas.UpdateSeasonUrl):
    # utils.update_file_in_cloudinary(your_public_id, updated_data)
    season_data=json.loads(season_data.model_dump_json())
    try:
        possible_leagues=['epl', 'la liga', 'serie a']
        # 2022-23
        possible_years=[str(season)+'–'+str(season+1)[2:] for season in range(2000,2023)]
        if not bool(season_data) or not bool(season_data['league']) or not bool(season_data['year']):
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid data"}}
            )    
        if season_data['league'] not in possible_leagues:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid league data"}}
            )     
            # print('req ',season_data['league'])
                
        if season_data['year'] not in possible_years:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "Invalid year data"}}
            )    
        # league_input, year_input= season_data['league'], season_data['year']
        # add_csv_file=season_data["add_csv_file"]
        league_input, year_input= season_data['league'], season_data['year']
        
        
        db = SessionLocal()
        csvFileLink=season_data['add_csv_file']

        season_exists_updated= crud.update_season_url(
            db=db, league=league_input, year=year_input, csvFileLink=csvFileLink
        )
        if season_exists_updated is None:
            return JSONResponse(
                status_code=400,
                content={"error":{"message": "League not found"}}
            ) 
        return {
            "message":"Data saved",
            "data":{
                "body": season_data
                # ,"csv_data":csv_data_for_that_season
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error":{"message": "Something went wrong"}}
        ) 
    
