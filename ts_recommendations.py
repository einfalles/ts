import httplib2
import sys
from apiclient.discovery import build

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
# youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

class Recommender():
    def __init__(self,credentials):
        self.youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,http=credentials)

    def get_watch_history(self):
        count = 0
        watch_history = []
        channels_response = self.youtube.channels().list(mine=True,part="contentDetails").execute()
        for channel in channels_response["items"]:
            uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]

        playlistitems_list_request = self.youtube.playlistItems().list(playlistId=uploads_list_id,part="snippet",maxResults=50)

        while len(watch_history) < 5:
            playlistitems_list_response = playlistitems_list_request.execute()
            for playlist_item in playlistitems_list_response["items"]:
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                video_req = self.youtube.videos().list(part="snippet",id=video_id)
                video_res = video_req.execute()
                for video_item in video_res["items"]:
                    video_cat_id = video_item["snippet"]["categoryId"]
                    if video_cat_id == '10':
                        video_title = video_item["snippet"]["title"]
                        history_temp = video_title.encode('utf8').rsplit('-',1)
                        if len(history_temp) > 1:
                            watch_history.append(history_temp)
                        else:
                            print history_temp
            playlistitems_list_request = self.youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)
            count = count + 1
        return watch_history
