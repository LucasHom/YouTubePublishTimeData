# YouTubePublishTimeData
Determines the best time to publish a video based off of recent trends in a YouTubers publish times. 

Generate an API key: [Google Cloud Projects](https://console.cloud.google.com/projectcreate)
Create .env file for API key and add: API_KEY="YOUR API KEY HERE"

To find a channel's ID, view page source on the channel's page then CTRL+F "channel-id="
In scraper.py add a custom channel id to line 18: channel_id = ["YOUR CHANNEL ID HERE"]

Run the program in your preferred IDE
