import pyqtgraph.exporters

class ExportService:
    @staticmethod
    def export_image(plot_widget, file_path: str):
        # pyqtgraph 提供了内置的 exporter
        exporter = pyqtgraph.exporters.ImageExporter(plot_widget.plotItem)
        # 可以设置一些导出参数，比如分辨率
        exporter.parameters()['width'] = 1920
        exporter.export(file_path)
