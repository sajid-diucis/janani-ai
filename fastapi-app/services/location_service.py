import math
from typing import List, Dict, Any

class LocationService:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians 
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return round(c * r, 2)

    def find_nearest(self, lat: float, lng: float, items: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Find the nearest items from a list based on lat/lng.
        """
        if not lat or not lng:
            return items[:limit]

        results = []
        for item in items:
            dist = self.calculate_distance(lat, lng, item["lat"], item["lng"])
            item_with_dist = item.copy()
            item_with_dist["distance_km"] = dist
            results.append(item_with_dist)

        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

location_service = LocationService()
