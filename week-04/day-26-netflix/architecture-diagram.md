# Netflix Architecture Diagram

## Content Ingestion Pipeline

```
Studio delivers master video file
         │
    ┌────▼────────────────────────────────────────────┐
    │              Transcoding Pipeline                │
    │                                                  │
    │  Master file → Encoding workers (thousands)      │
    │                                                  │
    │  Output per title:                               │
    │    - 4K HDR (HEVC)                               │
    │    - 1080p (H.264, HEVC)                         │
    │    - 720p, 480p, 360p, 240p                      │
    │    - Multiple audio tracks (5.1, stereo)         │
    │    - Subtitles (40+ languages)                   │
    │    - Each resolution split into 2-10 sec chunks  │
    │                                                  │
    │  Total: ~1,200 files per title                   │
    └────┬────────────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────────────────┐
    │              S3 (Origin Storage)                 │
    │  All encoded files stored here                   │
    └────┬────────────────────────────────────────────┘
         │
    ┌────▼────────────────────────────────────────────┐
    │              Open Connect CDN                    │
    │  Netflix's own CDN, deployed in ISP data centers │
    │  15,000+ servers in 1,000+ locations             │
    └─────────────────────────────────────────────────┘
```

## Streaming Architecture

```
User opens Netflix
         │
    ┌────▼────────────────────────────────────────────┐
    │              API Gateway                         │
    └──┬──────┬──────┬──────┬──────────────────────────┘
       │      │      │      │
    ┌──▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──────────────────────┐
    │User │ │Ctlg│ │Rec │ │    Playback Service     │
    │ Svc │ │ Svc│ │ Svc│ │                         │
    └─────┘ └────┘ └────┘ │  1. Verify entitlement  │
                           │  2. Get CDN URL         │
                           │  3. Return manifest     │
                           └─────────────────────────┘
                                        │
                           ┌────────────▼────────────┐
                           │    Open Connect CDN      │
                           │  (Nearest edge server)   │
                           │                          │
                           │  Serves video chunks     │
                           │  Adaptive bitrate        │
                           └──────────────────────────┘
```

## Adaptive Bitrate Streaming (ABR)

```
Video is split into 2-second chunks at multiple quality levels:

Manifest file (m3u8):
  #EXTM3U
  #EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
  360p/segment_001.ts
  #EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1280x720
  720p/segment_001.ts
  #EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1920x1080
  1080p/segment_001.ts

Player algorithm:
  1. Measure available bandwidth
  2. Choose quality level that fits in bandwidth buffer
  3. Download next chunk
  4. If bandwidth drops: switch to lower quality
  5. If bandwidth improves: switch to higher quality
```

## Recommendation System

```
Data sources:
  - Watch history (what you watched, how long)
  - Ratings (explicit: stars; implicit: completion rate)
  - Search queries
  - Browse behavior (what you hovered over)
  - Time of day, device type

Algorithms:
  - Collaborative filtering (users like you watched X)
  - Content-based filtering (you liked action movies, here's another)
  - Deep learning models (Netflix uses neural networks)

Pipeline:
  User events → Kafka → Spark Streaming → Feature store
                                        → Model training (daily)
                                        → Recommendation cache (Redis)
                                        → Served via API
```
