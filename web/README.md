# TrailBlazer Web Application

A modern web interface for the TrailBlazer route-finding application that helps users discover the shortest routes to historical monuments in Catalunya.

## 🌟 Features

- **Interactive Map**: Click to set your starting point and explore monuments
- **Real-time Route Calculation**: Asynchronous processing with progress tracking
- **Multiple Monument Types**: Military, religious, and civil buildings
- **Visual Exports**: Download route maps as PNG or KML files
- **Responsive Design**: Works on desktop and mobile devices
- **RESTful API**: Clean API for integration with other applications

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Internet connection (for downloading OpenStreetMap data and monument information)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/ap2-rutes-i-monuments-2024
   ```

2. **Install dependencies**
   ```bash
   # Install original project dependencies
   pip3 install -r requirements.txt
   
   # Install additional web dependencies
   pip3 install fastapi uvicorn python-multipart pydantic
   ```

3. **Start the web application**
   ```bash
   ./start_web.sh
   ```

   This will:
   - Install all dependencies
   - Start the backend API server on http://localhost:8000
   - Start a simple frontend server on http://localhost:3000
   - Open your browser automatically

### Manual Startup

If the automatic script doesn't work, you can start the components manually:

1. **Start the Backend**
   ```bash
   cd web/backend
   python3 app.py
   ```

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd web/frontend
   python3 -m http.server 3000
   ```

3. **Open your browser**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 🗺️ How to Use

1. **Set Starting Point**: 
   - Click anywhere on the map, or
   - Use "Use My Location" button, or
   - Enter coordinates manually

2. **Choose Monument Type**:
   - 🏰 Military Buildings (castles, towers, fortifications)
   - ⛪ Religious Buildings (churches, monasteries)  
   - 🏛️ Civil Buildings (palaces, houses)

3. **Preview Monuments**: Click "Preview Monuments" to see available monuments in the current map view

4. **Calculate Routes**: Click "Calculate Routes" to find optimal paths to all monuments

5. **Download Results**: Get PNG maps and KML files for GPS devices

## 🏗️ Architecture

### Backend (FastAPI)
- **Location**: `web/backend/app.py`
- **Port**: 8000
- **Features**: RESTful API, async processing, file generation

### Frontend (HTML/JavaScript)
- **Location**: `web/frontend/index.html`
- **Port**: 3000 (development server)
- **Features**: Interactive Leaflet maps, responsive UI

### Original Modules
The web application reuses all the existing logic from the skeleton directory:
- `segments.py` - Trail segment discovery
- `monuments.py` - Monument data retrieval
- `graphmaker.py` - Route graph construction
- `routes.py` - Path finding algorithms
- `viewer.py` - Visualization generation

## 📡 API Endpoints

### Monument Operations
- `GET /monument-types` - Get available monument categories
- `POST /monuments/{type}` - Get monuments of specific type in area

### Route Operations  
- `POST /routes/calculate` - Start route calculation (async)
- `GET /routes/status/{job_id}` - Check calculation progress

### Utility
- `GET /segments/preview` - Preview trail segments in area
- `GET /health` - API health check

## 🔧 Configuration

The web application uses the same settings as the original project:

- **settings_file.json**: Algorithm parameters
- **Data caching**: Segments and monuments are cached to improve performance
- **File storage**: Generated maps and routes are stored in `web/backend/static/`

## 🚧 Development

### Adding Features

1. **New API Endpoints**: Add to `web/backend/app.py`
2. **Frontend Features**: Modify `web/frontend/index.html`
3. **Algorithm Changes**: Update the original skeleton modules

### Testing

```bash
# Test the API directly
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

## 📱 Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox  
- ✅ Safari
- ✅ Edge
- 📱 Mobile browsers

## 🤝 Contributing

The web interface is built on top of the existing TrailBlazer logic. To contribute:

1. Test the original terminal application first
2. Understand the API endpoints in `app.py`
3. Make changes to either backend or frontend
4. Test with different monument types and locations

## 📄 License

Same license as the original TrailBlazer project.

---

**Happy Trail Blazing! 🥾🗺️**