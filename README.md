# imdb-to-video

AI-powered pipeline that converts any IMDb movie page into a 
ready-to-upload 2-minute short video.

## Workflow

![Workflow](assets/workflow.png)

## Pipeline

1. Input IMDb URL
2. Scrape metadata, plot & cast
3. Generate AI script (~280 words)
4. Create AI voiceover
5. Gather visual assets
6. Add background music
7. Assemble video
8. QA & export MP4

## Tech Stack

Python · OpenAI · ElevenLabs · TMDB API · FFmpeg

## Author

Muheet Mehraj