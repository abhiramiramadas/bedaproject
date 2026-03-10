# ==========================================================
# Interactive Map Generator for Accidents
# ==========================================================

import os
from datetime import datetime
from typing import List, Dict

try:
    import folium
    from folium.plugins import MarkerCluster, HeatMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("folium not available. Map generation disabled.")


class AccidentMapGenerator:
    """Generate interactive maps showing accident locations"""
    
    def __init__(self, output_dir="uploads/maps"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Severity colors
        self.severity_colors = {
            'CRITICAL': 'red',
            'HIGH': 'orange',
            'MEDIUM': 'yellow',
            'LOW': 'green'
        }
        
        # Severity icons
        self.severity_icons = {
            'CRITICAL': 'exclamation-triangle',
            'HIGH': 'warning',
            'MEDIUM': 'info-sign',
            'LOW': 'ok-sign'
        }
    
    def generate_map(self, accidents: List[Dict], center_lat: float = None, 
                     center_lon: float = None, filename: str = None) -> str:
        """
        Generate an interactive map with accident markers
        
        Args:
            accidents: List of accident dictionaries
            center_lat: Center latitude (auto-calculated if not provided)
            center_lon: Center longitude (auto-calculated if not provided)
            filename: Output filename
            
        Returns:
            Path to generated HTML map
        """
        if not FOLIUM_AVAILABLE:
            return None
        
        if not accidents:
            # Default to Chennai if no accidents
            center_lat = center_lat or 13.0827
            center_lon = center_lon or 80.2707
        else:
            # Calculate center from accidents
            if center_lat is None:
                center_lat = sum(a.get('latitude', 0) for a in accidents) / len(accidents)
            if center_lon is None:
                center_lon = sum(a.get('longitude', 0) for a in accidents) / len(accidents)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='cartodbdark_matter'  # Dark theme
        )
        
        # Add marker cluster
        marker_cluster = MarkerCluster(name="Accidents").add_to(m)
        
        # Add markers for each accident
        for accident in accidents:
            lat = accident.get('latitude', 0)
            lon = accident.get('longitude', 0)
            
            if lat == 0 and lon == 0:
                continue
            
            severity = accident.get('severity', 'LOW')
            color = self.severity_colors.get(severity, 'blue')
            
            # Create popup content
            popup_html = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="color: {color}; margin: 0;">⚠️ {severity} Accident</h4>
                <hr style="margin: 5px 0;">
                <p><b>Time:</b> {accident.get('timestamp', 'N/A')[:19]}</p>
                <p><b>Vehicles:</b> {', '.join(accident.get('vehicle_types', ['Unknown']))}</p>
                <p><b>Impact Score:</b> {accident.get('impact_score', 0):.1f}</p>
                <p><b>Address:</b> {accident.get('address', 'N/A')[:50]}</p>
                <p><b>Hospital:</b> {accident.get('nearest_hospital', 'N/A')}</p>
                <p><b>Weather:</b> {accident.get('weather', 'N/A')}</p>
            </div>
            """
            
            # Add marker
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{severity} - Click for details",
                icon=folium.Icon(color=color, icon='car', prefix='fa')
            ).add_to(marker_cluster)
        
        # Add heatmap layer if enough data
        if len(accidents) >= 3:
            heat_data = [[a.get('latitude', 0), a.get('longitude', 0), 
                         a.get('impact_score', 50) / 100] 
                        for a in accidents 
                        if a.get('latitude', 0) != 0]
            
            if heat_data:
                HeatMap(
                    heat_data,
                    name="Accident Heatmap",
                    min_opacity=0.3,
                    radius=25,
                    blur=15,
                    gradient={0.4: 'yellow', 0.65: 'orange', 1: 'red'}
                ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                    background-color: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px;
                    font-family: Arial; color: white;">
            <h4 style="margin: 0 0 10px 0;">🚗 Accident Severity</h4>
            <p style="margin: 3px 0;"><span style="color: red;">●</span> Critical</p>
            <p style="margin: 3px 0;"><span style="color: orange;">●</span> High</p>
            <p style="margin: 3px 0;"><span style="color: yellow;">●</span> Medium</p>
            <p style="margin: 3px 0;"><span style="color: green;">●</span> Low</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accident_map_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        m.save(filepath)
        
        print(f"Map generated: {filepath}")
        return filepath
    
    def generate_live_map_html(self, accidents: List[Dict]) -> str:
        """
        Generate map HTML string for embedding in dashboard
        
        Args:
            accidents: List of accident dictionaries
            
        Returns:
            HTML string of the map
        """
        if not FOLIUM_AVAILABLE:
            return "<p>Map not available</p>"
        
        # Default center
        if accidents:
            center_lat = sum(a.get('latitude', 13.0827) for a in accidents) / len(accidents)
            center_lon = sum(a.get('longitude', 80.2707) for a in accidents) / len(accidents)
        else:
            center_lat, center_lon = 13.0827, 80.2707
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='cartodbdark_matter'
        )
        
        # Add markers
        for accident in accidents[-20:]:  # Last 20 accidents
            lat = accident.get('latitude', 0)
            lon = accident.get('longitude', 0)
            if lat == 0 and lon == 0:
                continue
            
            severity = accident.get('severity', 'LOW')
            color = self.severity_colors.get(severity, 'blue')
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"{severity}: {', '.join(accident.get('vehicle_types', ['Vehicle']))}"
            ).add_to(m)
        
        return m._repr_html_()


# Global instance
map_generator = AccidentMapGenerator()


def generate_accident_map(accidents: List[Dict], filename: str = None) -> str:
    """Generate accident map"""
    return map_generator.generate_map(accidents, filename=filename)


def get_map_html(accidents: List[Dict]) -> str:
    """Get embeddable map HTML"""
    return map_generator.generate_live_map_html(accidents)
