# TrailBlazer 🗺️

> Discover the shortest routes to Catalunya's historical monuments

**TrailBlazer** is a route-finding application that helps you explore Catalunya's historical treasures by calculating optimal paths through real trail networks. Whether you're a tourist, historian, or adventurer, TrailBlazer combines OpenStreetMap trail data with monument locations to plan your perfect journey.

## ✨ Features

- 🏰 **Monument Discovery**: Browse military, religious, and civil historical buildings across Catalunya
- 🛤️ **Real Trail Networks**: Uses actual hiking trails from OpenStreetMap data
- 📍 **Smart Routing**: Calculates shortest paths using Dijkstra's algorithm
- 🗺️ **Visual Exports**: Download route maps as PNG images or KML files for GPS devices
- 🌐 **Web Interface**: Interactive map-based UI (in development)
- 💻 **CLI Tool**: Full-featured command-line interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for downloading trail and monument data)

### Installation

1. **Clone or download the repository**
   ```bash
   cd TrailBlazer
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

### Usage

#### Web Application (Recommended - In Development)

```bash
cd web/backend
python3 app.py
```

Then open your browser to:
- **Frontend**: http://localhost:3000 (serve `web/frontend/index.html`)
- **API Docs**: http://localhost:8000/docs

#### Command-Line Interface

```bash
cd skeleton
python3 main.py
```

Follow the interactive prompts to:
1. Select a geographic area
2. Choose monument type (military, religious, civil)
3. Set your starting point
4. Generate routes and export maps

## 📦 Dependencies

All required libraries are listed in `requirements.txt`:

- **Data Collection**: `requests`, `gpxpy`, `beautifulsoup4`
- **Geospatial**: `haversine`, `turfpy`, `geojson`
- **Graph Algorithms**: `networkx`, `scikit-learn`
- **Visualization**: `staticmap`, `simplekml`
- **CLI Interface**: `rich`
- **Web API** (backend only): `fastapi`, `uvicorn`, `pydantic`

## 🏗️ Architecture

TrailBlazer consists of two main components:

### 1. Core Engine (`skeleton/`)

The original command-line implementation with complete functionality:

- **`segments.py`**: Downloads and processes trail segments from OpenStreetMap
  - Fetches GPS track points in a geographic area
  - Performs K-means clustering to identify representative trail points
  - Creates segments between nearby points on the same trail
  - Caches data locally to avoid re-downloading

- **`monuments.py`**: Retrieves monument data from Catalunya's heritage database
  - Supports three monument types: military, religious, and civil
  - Parses HTML pages to extract monument names and locations
  - Returns structured monument data

- **`graphmaker.py`**: Builds and optimizes graph networks
  - Creates NetworkX graph from trail segments
  - Calculates edge weights using haversine distance
  - Simplifies graph by removing redundant collinear nodes
  - Optimizes for efficient pathfinding

- **`routes.py`**: Finds optimal routes using graph algorithms
  - Implements Dijkstra's shortest path algorithm
  - Calculates routes from starting point to all monuments
  - Handles unreachable monuments gracefully
  - Exports results to PNG maps and KML files

- **`viewer.py`**: Generates visual outputs
  - Creates PNG maps using staticmap library
  - Generates KML files for GPS devices
  - Color-codes start points, routes, and monuments

- **`main.py`**: Interactive command-line interface
  - Rich terminal formatting for user-friendly experience
  - Step-by-step workflow guidance
  - Configuration management via `settings_file.json`

### 2. Web Application (`web/`)

Modern REST API with interactive frontend (in development):

**Backend** (`web/backend/`):
- **FastAPI** framework for async REST API
- **SQLite** databases for job tracking and monument storage
- **Modular architecture**:
  - `models/`: Pydantic models for request/response validation
  - `routers/`: API endpoints for monuments, routes, segments
  - `services/`: Business logic layer
  - `database/`: Data persistence layer
  - `core/`: Configuration and utilities

**Frontend** (`web/frontend/`):
- **Interactive Leaflet map** for point selection
- **Bootstrap 5** UI components
- **Async job tracking** for long-running calculations
- **File downloads** for PNG/KML exports

### Data Flow

```
User Input → Segment Download → Graph Building → Route Calculation → Export
    ↓              ↓                  ↓                 ↓              ↓
  Coords     OpenStreetMap      NetworkX Graph     Dijkstra      PNG/KML
   Point         (GPX)          (clustering)      Algorithm      Files
```

## 🔧 Configuration

Settings are configured in `settings_file.json`:

```json
{
  "time_delta": 300,        // Max seconds between trail points (5 min)
  "distance_delta": 0.1,    // Max km between trail points (100m)
  "n_clusters": 500,        // Number of clusters for K-means
  "angle": 5                // Max angle deviation for node removal (degrees)
}
```

**Tuning Guidelines**:
- **Increase `n_clusters`** for more detailed trails (slower, more accurate)
- **Decrease `distance_delta`** for tighter trail connections
- **Adjust `angle`** to control graph simplification (lower = more simplification)

## 📊 Project Structure

```
TrailBlazer/
├── README.md                    # This file
├── PROJECT_OVERVIEW.md          # Detailed development guide
├── requirements.txt             # Python dependencies
├── settings_file.json           # Configuration
├── todo                         # Development tasks
│
├── skeleton/                    # ✅ Core CLI application (Complete)
│   ├── main.py                  # CLI interface
│   ├── segments.py              # Trail segment processing
│   ├── monuments.py             # Monument data fetching
│   ├── graphmaker.py            # Graph algorithms
│   ├── routes.py                # Route finding
│   ├── viewer.py                # Export visualization
│   └── settings_file.json       # CLI configuration
│
└── web/                         # 🚧 Web application (In Progress)
    ├── backend/
    │   ├── app.py               # FastAPI main application
    │   ├── requirements.txt     # Backend dependencies
    │   ├── models/              # ✅ Pydantic data models
    │   ├── routers/             # ⚠️ API endpoints (partial)
    │   ├── services/            # ⚠️ Business logic (partial)
    │   ├── database/            # ✅ SQLite storage
    │   └── core/                # ✅ Config & utilities
    │
    └── frontend/
        ├── index.html           # ✅ Interactive web UI
        └── README.md            # Frontend documentation
```

## 🔬 How It Works

### 1. Trail Segment Discovery

1. **Download GPS Tracks**: Fetches GPX files from OpenStreetMap for a geographic area
2. **Extract Points**: Parses GPX data to get timestamped coordinates
3. **Cluster Points**: Uses K-means to identify representative trail locations
4. **Create Segments**: Connects nearby clustered points that:
   - Are on the same trail
   - Are within time/distance thresholds
   - Belong to different clusters (to avoid tiny segments)

### 2. Graph Construction

1. **Build Network**: Creates graph with trail points as nodes and segments as edges
2. **Calculate Weights**: Edge weights = haversine distance between points
3. **Simplify Graph**: Removes nodes with degree 2 that are nearly collinear
   - Reduces graph size by 30-50%
   - Maintains path accuracy
   - Speeds up pathfinding

### 3. Route Calculation

1. **Find Monuments**: Retrieves all monuments of selected type in area
2. **Identify Start Node**: Finds closest graph node to user's starting point
3. **Run Dijkstra**: Calculates shortest path to each monument
4. **Build Route Graph**: Combines all paths into single route network
5. **Calculate Distances**: Computes total distance to each monument

### 4. Export & Visualization

**PNG Export**:
- Renders static map image
- Yellow marker: Starting point
- Red markers: Monuments
- Blue lines: Trail routes
- Black dots: Trail intersections

**KML Export**:
- GPS-compatible format
- Importable to Google Earth, Garmin, etc.
- Includes monument names and distances
- Color-coded routes

## 🚧 Current Development Status

### ✅ Completed
- Core CLI application (100%)
- Web frontend UI (100%)
- Backend infrastructure (models, database, config)
- Monument endpoints (GET /monuments, GET /monument-types)

### 🚧 In Progress
- Route service implementation
- Segment service implementation
- Graph service implementation
- Routes API endpoints
- Segments API endpoints

### 📋 To Do
- Complete service layer porting from skeleton
- Implement async job processing for route calculation
- Add file download endpoints
- End-to-end testing
- Performance optimization

**See `PROJECT_OVERVIEW.md` for detailed completion plan.**

## 🧪 Testing

### CLI Testing
```bash
cd skeleton
python3 main.py
# Follow prompts to test full workflow
```

### Web API Testing
```bash
cd web/backend
python3 app.py
# Visit http://localhost:8000/docs for Swagger UI
```

### Example API Calls
```bash
# Get monument types
curl http://localhost:8000/monument-types

# Get monuments in area
curl "http://localhost:8000/monuments?monument_type=militars&bottom_left_lat=41.0&bottom_left_lon=1.0&top_right_lat=42.0&top_right_lon=2.0"

# Health check
curl http://localhost:8000/health
```

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints (Current)

**Monuments**:
- `GET /monument-types` - List available monument types with counts
- `GET /monuments` - Get monuments by type and area

**System**:
- `GET /` - API information
- `GET /health` - Health check

**Coming Soon**:
- `POST /segments/download` - Download trail segments
- `POST /routes/calculate` - Calculate routes (async job)
- `GET /routes/job/{job_id}` - Check route calculation status
- `GET /routes/download/{job_id}/png` - Download PNG map
- `GET /routes/download/{job_id}/kml` - Download KML file

## 🤝 Contributing

This is an educational project for learning Python, web development, and graph algorithms.

**Development Workflow**:
1. Read `PROJECT_OVERVIEW.md` for architecture details
2. Implement missing services in `web/backend/services/`
3. Create API endpoints in `web/backend/routers/`
4. Test with Swagger UI at http://localhost:8000/docs
5. Update documentation

## 📄 License

Educational project - Catalunya Monuments data sourced from public databases.

## 🙏 Acknowledgments

- **OpenStreetMap** contributors for trail data
- **Generalitat de Catalunya** for monument databases
- Python community for excellent geospatial libraries

## 📧 Support

For questions or issues:
1. Check `PROJECT_OVERVIEW.md` for detailed documentation
2. Review API docs at http://localhost:8000/docs
3. Examine skeleton code for reference implementations

---

**Happy Trail Blazing!** 🥾⛰️🏰
