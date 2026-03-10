# ==========================================================
# PDF Report Generator - Generates accident reports
# ==========================================================

import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white, red, orange, yellow, green
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available. PDF reports disabled.")


class AccidentReportGenerator:
    """Generates professional PDF reports for accidents"""
    
    def __init__(self, output_dir="uploads/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a2e'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#16213e'),
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=5
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#333333'),
            spaceBefore=5,
            spaceAfter=5
        ))
        
        # Severity styles
        self.severity_colors = {
            'CRITICAL': HexColor('#ff0000'),
            'HIGH': HexColor('#ff6600'),
            'MEDIUM': HexColor('#ffaa00'),
            'LOW': HexColor('#ffcc00')
        }
    
    def generate_report(self, accident_data, image_path=None, video_clip_path=None):
        """
        Generate a PDF accident report
        
        Args:
            accident_data: Dictionary with accident information
            image_path: Path to accident screenshot
            video_clip_path: Path to video clip (for reference)
            
        Returns:
            Path to generated PDF
        """
        if not REPORTLAB_AVAILABLE:
            return None
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        severity = accident_data.get('severity', 'UNKNOWN')
        filename = f"Accident_Report_{severity}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Build content
        elements = []
        
        # Header/Title
        elements.append(Paragraph(
            "ACCIDENT DETECTION REPORT",
            self.styles['ReportTitle']
        ))
        
        # Report metadata
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(
            f"Generated: {report_time}",
            ParagraphStyle('Center', parent=self.styles['Normal'], alignment=TA_CENTER)
        ))
        elements.append(Spacer(1, 20))
        
        # Severity Banner
        severity_color = self.severity_colors.get(severity, HexColor('#666666'))
        severity_table = Table([[f"SEVERITY: {severity}"]], colWidths=[18*cm])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), severity_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('PADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(severity_table)
        elements.append(Spacer(1, 20))
        
        # Accident Image
        if image_path and os.path.exists(image_path):
            try:
                img = Image(image_path, width=16*cm, height=9*cm)
                elements.append(img)
                elements.append(Paragraph(
                    "Accident Scene Capture",
                    ParagraphStyle('Caption', parent=self.styles['Normal'], 
                                 alignment=TA_CENTER, fontSize=9, textColor=HexColor('#666666'))
                ))
                elements.append(Spacer(1, 15))
            except:
                pass
        
        # Accident Details Section
        elements.append(Paragraph("ACCIDENT DETAILS", self.styles['SectionHeader']))
        
        accident_time = accident_data.get('timestamp', datetime.now().isoformat())
        impact_score = accident_data.get('impact_score', 0)
        iou = accident_data.get('iou', 0)
        vehicles = accident_data.get('vehicle_types', [])
        speeds = accident_data.get('speeds', [0, 0])
        
        details_data = [
            ["Detection Time", accident_time],
            ["Severity Level", severity],
            ["Impact Score", f"{impact_score:.1f} / 100"],
            ["Collision Overlap (IoU)", f"{iou:.1%}"],
            ["Vehicles Involved", ", ".join(vehicles) if vehicles else "Unknown"],
            ["Estimated Speeds", f"{speeds[0]:.1f} px/f, {speeds[1]:.1f} px/f" if len(speeds) >= 2 else "N/A"]
        ]
        
        details_table = Table(details_data, colWidths=[6*cm, 12*cm])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 15))
        
        # Location Section
        elements.append(Paragraph("LOCATION INFORMATION", self.styles['SectionHeader']))
        
        lat = accident_data.get('latitude', 0)
        lon = accident_data.get('longitude', 0)
        address = accident_data.get('address', 'Location data not available')
        
        location_data = [
            ["GPS Coordinates", f"{lat:.6f}, {lon:.6f}"],
            ["Address", address[:60] + "..." if len(str(address)) > 60 else address],
            ["Google Maps", f"https://maps.google.com/?q={lat},{lon}"]
        ]
        
        location_table = Table(location_data, colWidths=[6*cm, 12*cm])
        location_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f4ea')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ]))
        elements.append(location_table)
        elements.append(Spacer(1, 15))
        
        # Emergency Services Section
        elements.append(Paragraph("EMERGENCY SERVICES", self.styles['SectionHeader']))
        
        hospital = accident_data.get('nearest_hospital', 'N/A')
        hospital_dist = accident_data.get('hospital_distance', 'N/A')
        police = accident_data.get('nearest_police', 'N/A')
        police_dist = accident_data.get('police_distance', 'N/A')
        
        emergency_data = [
            ["Nearest Hospital", f"{hospital} ({hospital_dist} km)" if hospital != 'N/A' else 'N/A'],
            ["Nearest Police Station", f"{police} ({police_dist} km)" if police != 'N/A' else 'N/A'],
        ]
        
        emergency_table = Table(emergency_data, colWidths=[6*cm, 12*cm])
        emergency_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#fff3e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ]))
        elements.append(emergency_table)
        elements.append(Spacer(1, 15))
        
        # Weather Section
        weather = accident_data.get('weather', 'N/A')
        temp = accident_data.get('temperature', 'N/A')
        visibility = accident_data.get('visibility', 'N/A')
        
        if weather != 'N/A':
            elements.append(Paragraph("WEATHER CONDITIONS", self.styles['SectionHeader']))
            
            weather_data = [
                ["Weather", weather],
                ["Temperature", f"{temp}°C" if temp != 'N/A' else 'N/A'],
                ["Visibility", f"{visibility} km" if visibility != 'N/A' else 'N/A'],
            ]
            
            weather_table = Table(weather_data, colWidths=[6*cm, 12*cm])
            weather_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f0ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ]))
            elements.append(weather_table)
            elements.append(Spacer(1, 15))
        
        # Damage Assessment Section
        damage = accident_data.get('damage_assessment', {})
        if damage:
            elements.append(Paragraph("DAMAGE ASSESSMENT (Insurance)", self.styles['SectionHeader']))
            
            damage_data = [
                ["Estimated Cost", f"${damage.get('estimated_cost', 0):,}"],
                ["Repair Duration", f"{damage.get('repair_days', 'N/A')} days"],
                ["Total Loss", "Yes" if damage.get('total_loss', False) else "No"],
            ]
            
            damage_table = Table(damage_data, colWidths=[6*cm, 12*cm])
            damage_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#ffe8e8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ]))
            elements.append(damage_table)
            elements.append(Spacer(1, 15))
        
        # Video Clip Reference
        if video_clip_path:
            elements.append(Paragraph("VIDEO EVIDENCE", self.styles['SectionHeader']))
            elements.append(Paragraph(
                f"Video clip saved: {video_clip_path}",
                self.styles['InfoText']
            ))
            elements.append(Spacer(1, 15))
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = """
        <i>This report was automatically generated by the AI-Based Real-Time Accident Detection System.
        All data is captured automatically using computer vision and may require manual verification.</i>
        """
        elements.append(Paragraph(
            footer_text,
            ParagraphStyle('Footer', parent=self.styles['Normal'], 
                          fontSize=8, textColor=HexColor('#888888'), alignment=TA_CENTER)
        ))
        
        # Build PDF
        try:
            doc.build(elements)
            print(f"PDF Report generated: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None


# Global instance
report_generator = AccidentReportGenerator()


def generate_accident_report(accident_data, image_path=None, video_clip_path=None):
    """
    Convenience function to generate accident report
    
    Args:
        accident_data: Accident information dictionary
        image_path: Path to accident screenshot
        video_clip_path: Path to video clip
        
    Returns:
        Path to generated PDF or None
    """
    return report_generator.generate_report(accident_data, image_path, video_clip_path)


# Test when run directly
if __name__ == "__main__":
    # Test data
    test_accident = {
        "timestamp": datetime.now().isoformat(),
        "severity": "HIGH",
        "impact_score": 65.5,
        "iou": 0.45,
        "vehicle_types": ["Car", "Motorcycle"],
        "speeds": [25.3, 18.7],
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "123 Test Street, Chennai, Tamil Nadu, India",
        "nearest_hospital": "Government General Hospital",
        "hospital_distance": 2.5,
        "nearest_police": "Chennai Central Police Station",
        "police_distance": 1.8,
        "weather": "Clear",
        "temperature": 32,
        "visibility": 10,
        "damage_assessment": {
            "estimated_cost": 12500,
            "repair_days": "15-20",
            "total_loss": False
        }
    }
    
    print("Generating test report...")
    path = generate_accident_report(test_accident)
    if path:
        print(f"Report saved to: {path}")
