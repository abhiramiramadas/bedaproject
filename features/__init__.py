# Features package initialization
# Import each module individually to handle missing dependencies

__all__ = []

try:
    from .video_clip import VideoClipSaver, clip_saver, save_accident_clip, add_frame_to_buffer
    __all__.extend(['VideoClipSaver', 'clip_saver', 'save_accident_clip', 'add_frame_to_buffer'])
except ImportError as e:
    print(f"Video clip module not available: {e}")

try:
    from .audio_alert import AudioAlertSystem, audio_alert, alert_accident, play_sound, speak_alert
    __all__.extend(['AudioAlertSystem', 'audio_alert', 'alert_accident', 'play_sound', 'speak_alert'])
except ImportError as e:
    print(f"Audio alert module not available: {e}")

try:
    from .pdf_report import AccidentReportGenerator, report_generator, generate_accident_report
    __all__.extend(['AccidentReportGenerator', 'report_generator', 'generate_accident_report'])
except ImportError as e:
    print(f"PDF report module not available: {e}")

try:
    from .database import AccidentDatabase, accident_db, save_to_database, get_accidents_from_db, get_stats
    __all__.extend(['AccidentDatabase', 'accident_db', 'save_to_database', 'get_accidents_from_db', 'get_stats'])
except ImportError as e:
    print(f"Database module not available: {e}")

try:
    from .excel_export import ExcelExporter, excel_exporter, export_to_excel, export_accidents_to_excel
    __all__.extend(['ExcelExporter', 'excel_exporter', 'export_to_excel', 'export_accidents_to_excel'])
except ImportError as e:
    print(f"Excel export module not available: {e}")

try:
    from .map_generator import AccidentMapGenerator, map_generator, generate_accident_map, get_map_html
    __all__.extend(['AccidentMapGenerator', 'map_generator', 'generate_accident_map', 'get_map_html'])
except ImportError as e:
    print(f"Map generator module not available: {e}")
