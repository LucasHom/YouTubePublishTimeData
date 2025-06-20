from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from isodate import parse_duration
from datetime import datetime, time
import statistics
from collections import defaultdict

load_dotenv() #get the .env from dir

api_key = os.getenv("API_KEY") #use the loaded .env to retrieve key

if api_key is None:
    raise Exception("API_KEY not found. Check .env file formatting and location.\n")
else:
    print("Successfully loaded API key\n")

channel_id = "UCdisIt9G75xRwoHPwCnNNTQ" #ADD YOUR CHANNEL ID HERE (for github users)

# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Make a request to get the most recent 50 videos from the channel
response = youtube.search().list(
    part="snippet", # We want the title, description, etc.
    channelId=channel_id, # Filter to this channel
    maxResults=50, # Up to 50 results (API max)
    order="date", # Sort by newest first
    type="video" # Only return videos (no playlists or channels)
).execute()

video_ids = [item["id"]["videoId"] for item in response["items"]]

# Get video details including duration
video_response = youtube.videos().list(
    part="snippet,contentDetails,statistics",
    id=",".join(video_ids)
).execute()

videos_found = 0
videos_filtered = []
lowest_date = None
highest_date = None

# Filter shorts
for item in video_response["items"]:
    # duration = parse_duration(item["contentDetails"]["duration"]).total_seconds()
    content = item.get("contentDetails", {})
    duration_str = content.get("duration")

    if duration_str:
        duration = parse_duration(duration_str).total_seconds()
    else:
        print(f"Skipping video ID {item.get('id')} — no duration info.")
        continue  # or set duration = 0 or handle another way

    if duration <= 60: # if its a short
        videos_found += 1
        title = item["snippet"]["title"]
        video_id = item["id"]
        views = int(item["statistics"].get("viewCount", "0"))

        # format time to AM PM simple
        publish_time_ISO = item["snippet"]["publishedAt"]
        dt_utc = datetime.strptime(publish_time_ISO, "%Y-%m-%dT%H:%M:%SZ")
        # set date of last and most recent videos
        if lowest_date is None or dt_utc < lowest_date:
            lowest_date = dt_utc
        if highest_date is None or dt_utc > highest_date:
            highest_date = dt_utc

        publish_time = dt_utc.strftime("%#I:%M %p")

        videos_filtered.append({
            "title": title,
            "video_id": video_id,
            "views": views,
            "publishtime": publish_time
        })

videos_filtered.sort(key=lambda x: x["views"], reverse=True)

views_by_hour = defaultdict(list)

for video in videos_filtered:
    time_obj = datetime.strptime(video["publishtime"], "%I:%M %p").time()
    rounded_hour = time(time_obj.hour, 0)
    rounded_str = rounded_hour.strftime("%#I:00 %p") 
    views_by_hour[rounded_str].append(video["views"])


median_views_by_hour = { # Compute median views per hour
    hour: int(statistics.median(views)) for hour, views in views_by_hour.items()
}

sorted_medians = sorted(median_views_by_hour.items(), key=lambda x: x[1], reverse=True)

print(f"\033[1mRetrieved {videos_found} videos\033[0m")
print(f"\033[1mTimeframe: {lowest_date.strftime("%B %d")} - {highest_date.strftime("%B %d")} \n\033[0m")

print("\033[1mMedian Views by Publish Time:\033[0m")

for hour, median in sorted_medians:
    print(f"{hour:>7} → {median:,} median views")

if sorted_medians:
    best_hour, best_median = sorted_medians[0]
    print(f"\n\033[1mSuggested time to post: {best_hour} ({best_median:,} median views)\n\033[0m")

print("---------------------------------------------------------------------\n")

for video in videos_filtered:
    print(f"{video["title"]}: {video["views"]} views - https://youtube.com/shorts/{video["video_id"]} ----- {video["publishtime"]}\n")