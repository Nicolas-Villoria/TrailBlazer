"""
Segment service - handles trail segment operations
Port of skeleton/segments.py to web backend
"""
import requests
import gpxpy
from sklearn.cluster import KMeans
import staticmap
from haversine import haversine
import json
import os
from datetime import datetime
from typing import List, Tuple, Set
from pathlib import Path

from models import PointModel, BoxModel
from core.utils import get_logger
from core.config import STATIC_DIR

logger = get_logger("segment_service")


class SegmentService:
    """Service for segment operations"""
    
    def __init__(self, settings_path: str = "settings_file.json"):
        """Initialize segment service with settings"""
        self.settings_path = settings_path
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            # Try to load from backend directory
            backend_dir = Path(__file__).parent.parent
            settings_file = backend_dir / self.settings_path
            
            if not settings_file.exists():
                # Try skeleton directory
                settings_file = backend_dir.parent.parent / "skeleton" / self.settings_path
            
            if not settings_file.exists():
                # Use defaults
                logger.warning("Settings file not found, using defaults")
                self.time_delta = 300
                self.distance_delta = 0.1
                self.n_clusters = 500
                return
            
            with open(settings_file, "r") as f:
                data = json.load(f)
                self.time_delta = data.get("time_delta", 300)
                self.distance_delta = data.get("distance_delta", 0.1)
                self.n_clusters = data.get("n_clusters", 500)
                
            logger.info(f"Loaded settings: time_delta={self.time_delta}, "
                       f"distance_delta={self.distance_delta}, n_clusters={self.n_clusters}")
        except Exception as e:
            logger.error(f"Error loading settings: {e}", exc_info=True)
            # Use defaults
            self.time_delta = 300
            self.distance_delta = 0.1
            self.n_clusters = 500
    
    def _get_directory_name(self, box: BoxModel) -> str:
        """Get directory name for a bounding box"""
        return f"{box.bottom_left.lat}_{box.bottom_left.lon}_{box.top_right.lat}_{box.top_right.lon}"
    
    def _download_points(self, box: BoxModel, filename: str) -> None:
        """Download all GPS points in the bounding box from OpenStreetMap"""
        box_str = f"{box.bottom_left.lon},{box.bottom_left.lat},{box.top_right.lon},{box.top_right.lat}"
        page = 0
        count = 0
        
        # Create directory in static files
        dir_name = self._get_directory_name(box)
        dir_path = Path(STATIC_DIR) / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        file_path = dir_path / filename
        
        logger.info(f"Downloading points for box {box_str}")
        
        with open(file_path, "w") as file:
            while True:
                url = f"https://api.openstreetmap.org/api/0.6/trackpoints?bbox={box_str}&page={page}"
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    gpx_content = response.content.decode("utf-8")
                    gpx = gpxpy.parse(gpx_content)
                    
                    if len(gpx.tracks) == 0:
                        break
                    
                    for t, track in enumerate(gpx.tracks):
                        for segment in track.segments:
                            if all(point.time is not None for point in segment.points):
                                segment.points.sort(key=lambda p: p.time)  # type: ignore
                                for p in segment.points:
                                    file.write(
                                        f"{p.latitude},{p.longitude},{p.time},{t},{page}\n"
                                    )
                                    count += 1
                    page += 1
                    
                except requests.RequestException as e:
                    logger.error(f"Error downloading page {page}: {e}")
                    break
        
        logger.info(f"Downloaded {count} points to {file_path}")
    
    def _load_points(self, box: BoxModel, filename: str) -> List[Tuple[float, float, datetime, int, int]]:
        """Load points from file, downloading if necessary"""
        points = []
        dir_name = self._get_directory_name(box)
        file_path = Path(STATIC_DIR) / dir_name / filename
        
        if not file_path.exists():
            logger.info(f"Points file not found, downloading...")
            self._download_points(box, filename)
        
        try:
            with open(file_path, "r") as file:
                for line in file:
                    lat, lon, time, track, page = line.strip().split(",")
                    t = datetime.strptime(time.split("+")[0], "%Y-%m-%d %H:%M:%S")
                    points.append((float(lat), float(lon), t, int(track), int(page)))
            
            logger.info(f"Loaded {len(points)} points from {file_path}")
            return points
            
        except Exception as e:
            logger.error(f"Error loading points: {e}", exc_info=True)
            return []
    
    def download_segments(self, box: BoxModel, filename: str = "segments.txt") -> int:
        """
        Download and process segments for a bounding box.
        
        Returns:
            Number of segments created
        """
        logger.info(f"Processing segments for box {self._get_directory_name(box)}")
        
        # Load all points
        all_points = self._load_points(box, "pointinfo.txt")
        
        if len(all_points) < 2:
            logger.warning("Not enough points to create segments")
            return 0
        
        # Perform K-means clustering
        logger.info(f"Clustering {len(all_points)} points into {self.n_clusters} clusters")
        
        kmeans = KMeans(n_clusters=min(self.n_clusters, len(all_points)), 
                       random_state=0, n_init=10).fit(
            [(lat, lon) for lat, lon, _, _, _ in all_points]
        )
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Find segments
        segments: Set[Tuple[Tuple[float, float], Tuple[float, float]]] = set()
        
        for i in range(1, len(all_points)):
            _, _, time1, track1, page1 = all_points[i - 1]
            _, _, time2, track2, page2 = all_points[i]
            lat1, lon1 = centers[labels[i - 1]]
            lat2, lon2 = centers[labels[i]]
            
            # Check if points form a valid segment
            if (
                abs(time2 - time1).total_seconds() < self.time_delta
                and haversine((lat1, lon1), (lat2, lon2)) < self.distance_delta
                and labels[i - 1] != labels[i]
                and track1 == track2
                and page1 == page2
            ):
                # Ensure consistent ordering
                if i + 1 < len(all_points) and labels[i + 1] < labels[i]:
                    segments.add(((lat1, lon1), (lat2, lon2)))
                else:
                    segments.add(((lat2, lon2), (lat1, lon1)))
        
        # Save segments to file
        dir_name = self._get_directory_name(box)
        dir_path = Path(STATIC_DIR) / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        file_path = dir_path / filename
        
        with open(file_path, "w") as f:
            for (lat1, lon1), (lat2, lon2) in segments:
                f.write(f"{lat1},{lon1},{lat2},{lon2}\n")
        
        logger.info(f"Saved {len(segments)} segments to {file_path}")
        return len(segments)
    
    def load_segments(self, box: BoxModel, filename: str = "segments.txt") -> List[Tuple[PointModel, PointModel]]:
        """Load segments from file"""
        segments = []
        dir_name = self._get_directory_name(box)
        file_path = Path(STATIC_DIR) / dir_name / filename
        
        if not file_path.exists():
            logger.warning(f"Segments file not found: {file_path}")
            return []
        
        try:
            with open(file_path, "r") as f:
                for line in f:
                    lat1, lon1, lat2, lon2 = line.strip().split(",")
                    start = PointModel(lat=float(lat1), lon=float(lon1))
                    end = PointModel(lat=float(lat2), lon=float(lon2))
                    segments.append((start, end))
            
            logger.info(f"Loaded {len(segments)} segments from {file_path}")
            return segments
            
        except Exception as e:
            logger.error(f"Error loading segments: {e}", exc_info=True)
            return []
    
    def get_segments(self, box: BoxModel, filename: str = "segments.txt") -> List[Tuple[PointModel, PointModel]]:
        """
        Get segments for a bounding box, downloading if necessary.
        
        Args:
            box: Geographic bounding box
            filename: Name of segments file
            
        Returns:
            List of segment tuples (start_point, end_point)
        """
        # Check if segments file exists
        dir_name = self._get_directory_name(box)
        file_path = Path(STATIC_DIR) / dir_name / filename
        
        if not file_path.exists():
            logger.info("Segments file not found, downloading and processing...")
            self.download_segments(box, filename)
        
        return self.load_segments(box, filename)
    
    def create_segment_preview_image(
        self, 
        segments: List[Tuple[PointModel, PointModel]], 
        filename: str
    ) -> str:
        """
        Create a PNG preview image of segments.
        
        Args:
            segments: List of segment tuples
            filename: Output filename (will be saved in static directory)
            
        Returns:
            Path to saved image file
        """
        try:
            map_obj = staticmap.StaticMap(800, 800)
            
            for start, end in segments:
                map_obj.add_line(
                    staticmap.Line(
                        [
                            (start.lon, start.lat),
                            (end.lon, end.lat),
                        ],
                        "blue",
                        2,
                    )
                )
            
            image = map_obj.render()
            output_path = Path(STATIC_DIR) / filename
            image.save(str(output_path))
            
            logger.info(f"Created segment preview image: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating preview image: {e}", exc_info=True)
            raise
