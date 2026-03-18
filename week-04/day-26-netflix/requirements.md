# Netflix System Design — Requirements

## Functional Requirements

1. Users can browse and search the content catalog
2. Users can stream video content
3. Personalized recommendations
4. Continue watching (resume from where you left off)
5. Download for offline viewing
6. Multiple profiles per account
7. Parental controls

## Scale Requirements (Netflix's actual scale)
- 260 million subscribers globally
- 100 million hours of content streamed per day
- 15,000+ titles in catalog
- Peak: 15% of global internet bandwidth
- 190+ countries

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Video start time | < 2 seconds |
| Buffering rate | < 0.1% of playback time |
| Availability | 99.99% |
| CDN cache hit rate | > 95% |
| Recommendation freshness | Updated daily |

## Key Technical Challenges
1. Video encoding (multiple resolutions, codecs)
2. CDN strategy (15% of global internet bandwidth)
3. Adaptive bitrate streaming
4. Personalization at scale (260M users)
5. Global availability with regional content restrictions
