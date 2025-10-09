"""
Monument service - handles monument data operations
Bridges current file-based system to future database implementation
"""
from typing import List, Optional
from core.utils import skeleton_working_directory, get_logger
from core.config import MONUMENT_TYPE_MAPPING, DefaultBox, SKELETON_DIR
from models import MonumentResponse, PointModel

logger = get_logger("monument_service")


class MonumentService:
    """Service for monument operations"""
    
    def __init__(self):
        # Future: will initialize database connection
        pass
    
    def get_monument_types(self) -> List[dict]:
        """Get available monument types"""
        from core.config import MONUMENT_TYPES
        return MONUMENT_TYPES
    
    def get_monuments_by_type_and_area(
        self,
        monument_type: str,
        bottom_left_lat: Optional[float] = None,
        bottom_left_lon: Optional[float] = None,
        top_right_lat: Optional[float] = None,
        top_right_lon: Optional[float] = None
    ) -> List[MonumentResponse]:
        """
        Get monuments by type and optionally filter by area
        Currently uses skeleton functions, will transition to database
        """
        try:
            # Import skeleton functions
            from monuments import get_monuments
            from segments import Point, Box
            
            # Set up search area
            if all([bottom_left_lat, bottom_left_lon, top_right_lat, top_right_lon]):
                search_box = Box(
                    Point(bottom_left_lat, bottom_left_lon),
                    Point(top_right_lat, top_right_lon)
                )
            else:
                search_box = Box(
                    Point(DefaultBox.BOTTOM_LEFT_LAT, DefaultBox.BOTTOM_LEFT_LON),
                    Point(DefaultBox.TOP_RIGHT_LAT, DefaultBox.TOP_RIGHT_LON)
                )
            
            # Map monument type
            full_monument_type = MONUMENT_TYPE_MAPPING.get(monument_type, monument_type)
            
            logger.info("Fetching monuments", extra={
                "monument_type": monument_type, 
                "full_monument_type": full_monument_type
            })
            
            # Get monuments using skeleton functions
            with skeleton_working_directory():
                monuments = get_monuments(full_monument_type)
            
            logger.info("Retrieved monuments", extra={"count": len(monuments)})
            
            # Filter monuments in the search area
            filtered_monuments = []
            for monument in monuments:
                if (monument.location.lat >= search_box.bottom_left.lat and
                    monument.location.lat <= search_box.top_right.lat and
                    monument.location.lon >= search_box.bottom_left.lon and
                    monument.location.lon <= search_box.top_right.lon):
                    
                    filtered_monuments.append(MonumentResponse(
                        name=monument.name,
                        location=PointModel(
                            lat=monument.location.lat,
                            lon=monument.location.lon
                        )
                    ))
            
            logger.info("Filtered monuments", extra={
                "total_monuments": len(monuments),
                "filtered_count": len(filtered_monuments),
                "search_box": {
                    "lat_range": [search_box.bottom_left.lat, search_box.top_right.lat],
                    "lon_range": [search_box.bottom_left.lon, search_box.top_right.lon]
                }
            })
            
            return filtered_monuments
            
        except Exception as e:
            logger.error("Error in monument service", extra={
                "monument_type": monument_type,
                "error": str(e)
            }, exc_info=True)
            raise