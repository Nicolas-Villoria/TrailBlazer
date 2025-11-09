# 🚀 TrailBlazer - Quick Start Guide

## ✅ Project Status: COMPLETE & READY TO USE!

All components have been implemented and the application is fully functional.

---

## 🏃 Quick Start (30 seconds)

### 1. Start the API Server

```bash
cd /Users/nicolasvilloria/Desktop/DATOS/projects/TrailBlazer/web/backend
python3 app.py
```

You should see:
```
2025-11-07 XX:XX:XX - trailblazer.monument_service - INFO - Database already contains 3220 monuments
2025-11-07 XX:XX:XX - trailblazer.main - INFO - Starting TrailBlazer API server
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Open API Documentation

Visit in your browser:
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **Health Check**: http://localhost:8000/health

### 3. Test the API

Run the test script:
```bash
cd /Users/nicolasvilloria/Desktop/DATOS/projects/TrailBlazer/web/backend
python3 test_api.py
```

---

## 📚 What's Available

### API Endpoints

**Monuments**:
- `GET /monument-types` - List all monument types with counts
- `GET /monuments` - Get monuments in a geographic area

**Segments** (Trail Data):
- `POST /segments/download` - Download trail segments from OpenStreetMap
- `GET /segments` - Retrieve cached segments
- `POST /segments/preview` - Generate preview of trail network
- `GET /segments/stats` - Get segment statistics

**Routes** (Route Calculation):
- `POST /routes/calculate` - Calculate routes to monuments (async job)
- `GET /routes/job/{job_id}` - Check calculation progress
- `GET /routes/download/{job_id}/png` - Download PNG map
- `GET /routes/download/{job_id}/kml` - Download KML for GPS

**System**:
- `GET /` - API information
- `GET /health` - Health check

---

## 🧪 Example Usage

### 1. Get Monument Types
```bash
curl http://localhost:8000/monument-types
```

### 2. Get Monuments in Barcelona Area
```bash
curl "http://localhost:8000/monuments?monument_type=militars&bottom_left_lat=41.3&bottom_left_lon=2.0&top_right_lat=41.5&top_right_lon=2.3"
```

### 3. Calculate Routes

```bash
# Start route calculation
curl -X POST http://localhost:8000/routes/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start_point": {"lat": 41.35, "lon": 2.05},
    "monument_type": "militars",
    "search_box": {
      "bottom_left": {"lat": 41.3, "lon": 2.0},
      "top_right": {"lat": 41.4, "lon": 2.1}
    }
  }'

# Returns: {"job_id": "abc-123-def", "status": "pending", "message": "..."}

# Check progress (replace JOB_ID with actual ID)
curl http://localhost:8000/routes/job/JOB_ID

# When completed, download files
curl -O http://localhost:8000/routes/download/JOB_ID/png
curl -O http://localhost:8000/routes/download/JOB_ID/kml
```

---

## 📂 Project Structure

```
TrailBlazer/
├── README.md                   # Main documentation
├── PROJECT_OVERVIEW.md         # Development guide
├── COMPLETION_REPORT.md        # What was completed
├── QUICK_START.md             # This file
│
├── skeleton/                   # Original CLI (complete)
│   ├── main.py
│   ├── segments.py
│   ├── monuments.py
│   ├── graphmaker.py
│   ├── routes.py
│   └── viewer.py
│
└── web/
    ├── backend/               # ✅ API Server (COMPLETE)
    │   ├── app.py            # FastAPI application
    │   ├── test_api.py       # Test script
    │   │
    │   ├── services/         # Business logic
    │   │   ├── graph.py           # ✅ NEW
    │   │   ├── segment_service.py # ✅ NEW
    │   │   ├── route_service.py   # ✅ NEW
    │   │   └── monument_service.py
    │   │
    │   ├── routers/          # API endpoints
    │   │   ├── routes.py          # ✅ NEW
    │   │   ├── segments.py        # ✅ NEW
    │   │   └── monuments.py
    │   │
    │   ├── models/           # Pydantic models
    │   ├── database/         # SQLite operations
    │   └── core/             # Config & utilities
    │
    └── frontend/
        └── index.html        # Web interface
```

---

## 🎯 What Was Implemented

### Services (3 new files - ~740 lines)
✅ **graph.py**: Graph creation, simplification, shortest paths  
✅ **segment_service.py**: Segment download, K-means clustering, caching  
✅ **route_service.py**: Route calculation, PNG/KML export  

### Routers (2 new files - ~530 lines)
✅ **routes.py**: 5 endpoints for route calculation & download  
✅ **segments.py**: 4 endpoints for segment operations  

### Features
✅ Segment downloading from OpenStreetMap  
✅ K-means point clustering  
✅ Graph network building & simplification  
✅ Dijkstra's shortest path algorithm  
✅ PNG map generation  
✅ KML file export for GPS  
✅ Async job processing with progress tracking  
✅ File download endpoints  
✅ Comprehensive error handling  

---

## 🔍 Typical Workflow

1. **Choose Area**: Define bounding box (lat/lon coordinates)
2. **Get Monuments**: Query monuments in that area
3. **Download Segments**: Get trail data (one-time, cached)
4. **Select Start Point**: Where you want to start hiking
5. **Calculate Routes**: Start async job to find optimal paths
6. **Monitor Progress**: Poll job status endpoint
7. **Download Results**: Get PNG map and KML file
8. **Use on GPS**: Load KML into Garmin, phone, etc.

---

## 📊 Performance Notes

- **Segment Download**: 2-10 minutes (depends on area size, cached after first download)
- **Graph Building**: 5-30 seconds (depends on segment count)
- **Route Calculation**: 10-60 seconds (depends on monuments and graph size)
- **File Generation**: 2-5 seconds

**Tip**: Start with small areas (0.1° x 0.1°) for testing, then expand.

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
cd web/backend
# Edit app.py line ~77, change port to 8001
python3 app.py
```

### "No monuments found"
- Check monument type spelling: "militars", "religiosos", "civils"
- Verify coordinates are in Catalunya (lat: 40-43, lon: 0-4)
- Run `python3 init_db.py` to initialize monument database

### "No segments found"
- Segments download can take time for large areas
- Check OpenStreetMap API is accessible
- Try smaller area first
- Check `web/backend/static/` for cached files

### Jobs stuck in "processing"
- Check server logs for errors
- Segments might be downloading (first time is slow)
- Try smaller area or fewer monuments

---

## 📚 Documentation

- **README.md**: Complete project documentation
- **PROJECT_OVERVIEW.md**: Architecture and development details
- **COMPLETION_REPORT.md**: What was implemented
- **API Docs**: http://localhost:8000/docs (when server running)

---

## 🎉 You're Ready!

The TrailBlazer project is **100% complete** and ready to use.

Start the server, open the API docs, and start discovering optimal routes to Catalunya's historical monuments!

**Happy Trail Blazing!** 🥾⛰️🏰
