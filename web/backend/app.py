#!/usr/bin/env python3
"""
Web Backend for TrailBlazer Application

This backend provides REST API endpoints for the TrailBlazer application,
allowing users to find routes to historical monuments through a web interface.
"""

import sys
import os
from pathlib import Path

# Add the skeleton directory to the Python path
SKELETON_DIR = Path(__file__).parent.parent.parent / "skeleton"
sys.path.insert(0, str(SKELETON_DIR))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import traceback

# Import our existing modules
try:
    from segments import get_segments, Box, Point, Segment, Segments
    from graphmaker import make_graph, simplify_graph
    from monuments import get_monuments, Monument, Monuments
    from routes import find_routes, export_PNG_routes, export_KML_routes
    from viewer import export_PNG, export_KML
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Make sure the skeleton directory exists at: {SKELETON_DIR}")
    sys.exit(1)

app = FastAPI(
    title="TrailBlazer API", 
    version="1.0.0",
    description="API for finding routes to historical monuments in Catalunya"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Serve static files (for generated maps and exports)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Pydantic models for API
class PointModel(BaseModel):
    lat: float
    lon: float

class BoxModel(BaseModel):
    bottom_left: PointModel
    top_right: PointModel

class MonumentModel(BaseModel):
    name: str
    location: PointModel

class RouteRequest(BaseModel):
    start_point: PointModel
    monument_type: str
    search_box: BoxModel
    settings: Optional[Dict[str, Any]] = None

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory job storage (in production, use Redis or similar)
jobs: Dict[str, JobStatus] = {}

# Default Catalunya box
DEFAULT_BOX = Box(Point(40.475518, 0.055361), Point(42.903476, 3.494081))

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "TrailBlazer API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/monument-types")
async def get_monument_types():
    """Get available monument types"""
    return {
        "types": [
            {
                "id": "militars", 
                "name": "Military Buildings", 
                "description": "Castles, towers, fortifications",
                "icon": "🏰"
            },
            {
                "id": "religiosos", 
                "name": "Religious Buildings", 
                "description": "Churches, monasteries, chapels",
                "icon": "⛪"
            },
            {
                "id": "civils", 
                "name": "Civil Buildings", 
                "description": "Houses, palaces, civil architecture",
                "icon": "🏛️"
            }
        ]
    }

@app.post("/monuments/{monument_type}")
async def get_monuments_by_type(monument_type: str, box: Optional[BoxModel] = None):
    """Get monuments of a specific type in the given area"""
    original_cwd = os.getcwd()
    try:
        # Change to skeleton directory for file operations
        os.chdir(str(SKELETON_DIR))
        # Convert Pydantic models to our data classes
        search_box = DEFAULT_BOX
        if box:
            search_box = Box(
                Point(box.bottom_left.lat, box.bottom_left.lon),
                Point(box.top_right.lat, box.top_right.lon)
            )
        
        # Map short monument type to full URL path (which is also used as filename)
        monument_type_mapping = {
            "militars": "edificacions-de-caracter-militar",
            "religiosos": "edificacions-de-caracter-religios", 
            "civils": "edificacions-de-caracter-civil"
        }
        
        full_monument_type = monument_type_mapping.get(monument_type, monument_type)
        
        print(f"Fetching monuments of type: {monument_type} -> {full_monument_type}")
        monuments = get_monuments(full_monument_type)
        print(f"Found {len(monuments)} total monuments")
        
        # Filter monuments in the box
        filtered_monuments = []
        for monument in monuments:
            if (monument.location.lat >= search_box.bottom_left.lat and
                monument.location.lat <= search_box.top_right.lat and
                monument.location.lon >= search_box.bottom_left.lon and
                monument.location.lon <= search_box.top_right.lon):
                
                filtered_monuments.append({
                    "name": monument.name,
                    "location": {
                        "lat": monument.location.lat,
                        "lon": monument.location.lon
                    }
                })
        
        print(f"Filtered to {len(filtered_monuments)} monuments in search area")
        return {"monuments": filtered_monuments, "count": len(filtered_monuments)}
    
    except Exception as e:
        print(f"Error in get_monuments_by_type: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass

@app.post("/routes/calculate")
async def calculate_routes(route_request: RouteRequest, background_tasks: BackgroundTasks):
    """Start route calculation (async job)"""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = JobStatus(
        job_id=job_id,
        status="pending",
        progress=0.0
    )
    
    # Start background task
    background_tasks.add_task(process_route_calculation, job_id, route_request)
    
    return {"job_id": job_id, "status": "started"}

@app.get("/routes/status/{job_id}")
async def get_route_status(job_id: str):
    """Get the status of a route calculation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/segments/preview")
async def preview_segments(
    bottom_left_lat: float,
    bottom_left_lon: float,
    top_right_lat: float,
    top_right_lon: float
):
    """Get a preview of segments in the area"""
    original_cwd = os.getcwd()
    try:
        # Change to skeleton directory for file operations
        os.chdir(str(SKELETON_DIR))
        box = Box(
            Point(bottom_left_lat, bottom_left_lon),
            Point(top_right_lat, top_right_lon)
        )
        
        # Use standard filename
        filename = "segments.dat"
        
        print(f"Getting segments for box: {box}")
        segments = get_segments(box, filename)
        print(f"Found {len(segments)} segments")
        
        # Convert to JSON-serializable format (limit for preview)
        segments_data = []
        for segment in segments[:100]:  # Limit to first 100 for preview
            segments_data.append({
                "start": {"lat": segment.start.lat, "lon": segment.start.lon},
                "end": {"lat": segment.end.lat, "lon": segment.end.lon}
            })
        
        return {
            "segments": segments_data,
            "total_count": len(segments),
            "preview_count": len(segments_data)
        }
    
    except Exception as e:
        print(f"Error in preview_segments: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass

async def process_route_calculation(job_id: str, route_request: RouteRequest):
    """Background task to process route calculation"""
    try:
        print(f"🚀 Starting route calculation for job {job_id}")
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10.0
        print(f"📊 Progress: 10% - Initializing calculation")
        
        # Change to skeleton directory to find settings_file.json
        original_cwd = os.getcwd()
        os.chdir(str(SKELETON_DIR))
        
        # Convert request to our data classes
        start_point = Point(route_request.start_point.lat, route_request.start_point.lon)
        box = Box(
            Point(route_request.search_box.bottom_left.lat, route_request.search_box.bottom_left.lon),
            Point(route_request.search_box.top_right.lat, route_request.search_box.top_right.lon)
        )
        
        print(f"Start point: {start_point}, Box: {box}")
        
        # Get segments
        jobs[job_id].progress = 30.0
        print(f"📊 Progress: 30% - Loading trail segments")
        filename = "segments.dat"
        segments = get_segments(box, filename)
        print(f"🗺️ Retrieved {len(segments)} segments from OpenStreetMap")
        
        # Create graph
        jobs[job_id].progress = 50.0
        print(f"📊 Progress: 50% - Building navigation graph")
        graph = make_graph(segments)
        print(f"🔗 Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        simplified_graph = simplify_graph(graph, 10.0)  # Default angle threshold
        print(f"⚡ Simplified graph to {simplified_graph.number_of_nodes()} nodes and {simplified_graph.number_of_edges()} edges")
        
        # Find the closest node in the simplified graph to the start point
        from haversine import haversine
        min_dist = float('inf')
        closest_node = None
        for node in simplified_graph.nodes:
            dist = haversine((start_point.lat, start_point.lon), (node.lat, node.lon))
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        
        if closest_node:
            print(f"📍 Start point adjusted to nearest graph node ({min_dist:.3f} km away)")
            start_point = closest_node
        else:
            raise Exception("No nodes found in graph")
        
        # Get monuments
        jobs[job_id].progress = 70.0
        print(f"📊 Progress: 70% - Loading monuments")
        monument_type_mapping = {
            "militars": "edificacions-de-caracter-militar",
            "religiosos": "edificacions-de-caracter-religios", 
            "civils": "edificacions-de-caracter-civil"
        }
        full_monument_type = monument_type_mapping.get(route_request.monument_type, route_request.monument_type)
        monuments = get_monuments(full_monument_type)
        print(f"🏰 Retrieved {len(monuments)} monuments from Catalunya Medieval")
        
        # Filter monuments in box
        filtered_monuments = []
        for monument in monuments:
            if (monument.location.lat >= box.bottom_left.lat and
                monument.location.lat <= box.top_right.lat and
                monument.location.lon >= box.bottom_left.lon and
                monument.location.lon <= box.top_right.lon):
                filtered_monuments.append(monument)
        
        print(f"📍 Filtered to {len(filtered_monuments)} monuments in search area")
        
        if not filtered_monuments:
            print("⚠️ No monuments found in the specified area")
            jobs[job_id].status = "completed"
            jobs[job_id].progress = 100.0
            jobs[job_id].result = {
                "routes_count": 0,
                "monuments": [],
                "message": "No monuments found in the specified area"
            }
            return
        
        # Connect monuments to the simplified graph by finding nearest nodes
        jobs[job_id].progress = 85.0
        print(f"📊 Progress: 85% - Connecting monuments to trail network")
        for monument in filtered_monuments:
            min_dist = float('inf')
            closest_node = None
            for node in simplified_graph.nodes:
                dist = haversine((monument.location.lat, monument.location.lon), (node.lat, node.lon))
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node
            
            if closest_node and min_dist < 10.0:  # Only connect if within 10 km
                # Add the monument location to the graph and connect it to the nearest node
                simplified_graph.add_edge(monument.location, closest_node, weight=min_dist)
                print(f"  ✓ Connected {monument.name} to graph ({min_dist:.2f} km)")
            else:
                print(f"  ✗ {monument.name} is too far from any trail ({min_dist:.2f} km)")
        
        # Calculate routes
        jobs[job_id].progress = 90.0
        print(f"📊 Progress: 90% - Calculating optimal routes")
        routes = find_routes(simplified_graph, start_point, filtered_monuments)
        print(f"🧮 Route calculation completed")
        
        # Generate visualizations
        png_filename = str(STATIC_DIR / f"routes_{job_id}.png")
        kml_filename = str(STATIC_DIR / f"routes_{job_id}.kml")
        
        export_PNG_routes(box, routes, png_filename)
        export_KML_routes(box, routes, kml_filename)
        print(f"🎨 Generated visualizations: {png_filename}, {kml_filename}")
        
        # Calculate distances for each monument
        monument_results = []
        for monument in filtered_monuments:
            try:
                distance = routes.dist(monument)
                monument_results.append({
                    "name": monument.name,
                    "location": {"lat": monument.location.lat, "lon": monument.location.lon},
                    "distance": distance
                })
                print(f"  ✓ {monument.name}: {distance:.2f} km")
            except Exception as e:
                # If route calculation fails for this monument, still include it
                monument_results.append({
                    "name": monument.name,
                    "location": {"lat": monument.location.lat, "lon": monument.location.lon},
                    "distance": None,
                    "error": "No path available"
                })
                print(f"  ✗ {monument.name}: No route found")
        
        # Complete job
        jobs[job_id].status = "completed"
        jobs[job_id].progress = 100.0
        jobs[job_id].result = {
            "routes_count": len([m for m in monument_results if m.get("distance") is not None]),
            "png_url": f"/static/routes_{job_id}.png",
            "kml_url": f"/static/routes_{job_id}.kml",
            "monuments": monument_results
        }
        
        print(f"✅ Job {job_id} completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in job {job_id}: {e}")
        traceback.print_exc()
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
    finally:
        # Always restore the original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print("Starting TrailBlazer API server...")
    print(f"Skeleton directory: {SKELETON_DIR}")
    print("API will be available at http://localhost:8000")
    print("Interactive docs at http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False  # Set to True for development
    )