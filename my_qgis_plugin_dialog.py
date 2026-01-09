"""
Dialog implementation for DEM Downscaling plugin
"""
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.core import QgsRasterLayer, QgsProject, QgsMessageLog
from qgis.utils import iface
from .dem_downscaling_algorithm import downscale_dem, estimate_memory_usage, get_raster_info, estimate_runtime, GPU_AVAILABLE, SCIPY_AVAILABLE
import os
import subprocess
import sys

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'my_qgis_plugin_dialog_base.ui'))


class DownscalingWorker(QThread):
    """Worker thread for DEM downscaling to keep UI responsive"""
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(dict)  # result dictionary
    error = pyqtSignal(str)  # error message
    
    def __init__(self, input_file, output_file, zoom_factor, rsme):
        QThread.__init__(self)
        self.input_file = input_file
        self.output_file = output_file
        self.zoom_factor = zoom_factor
        self.rsme = rsme
        self.is_cancelled = False
    
    def run(self):
        """Run the downscaling process"""
        try:
            def progress_callback(message, percentage):
                if not self.is_cancelled:
                    self.progress.emit(message, percentage)
            
            result = downscale_dem(
                input_file=self.input_file,
                output_file=self.output_file,
                zoom_factor=self.zoom_factor,
                rsme=self.rsme,
                threshold=0.001,
                progress_callback=progress_callback
            )
            
            if not self.is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """Cancel the processing"""
        self.is_cancelled = True


class MyQGISPluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MyQGISPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        
        # Connect button signals
        self.btnBrowseInput.clicked.connect(self.browse_input_file)
        self.btnBrowseOutput.clicked.connect(self.browse_output_file)
        self.mInputFile.textChanged.connect(self.on_input_changed)
        self.btnInstallLibraries.clicked.connect(self.show_installation_guide)
        
        # Connect OK button - prevent auto-accept, we'll handle it manually
        self.button_box.accepted.disconnect()  # Disconnect default accept
        self.button_box.accepted.connect(self.process)  # Connect to our process method
        self.button_box.rejected.connect(self.reject)  # Default reject (will be changed during processing)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Process")
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Cancel")
        
        # Prevent dialog from closing on Enter key or OK button
        self.setModal(True)
        
        # Initialize worker
        self.worker = None
        self.is_processing = False
        
        # Initialize progress bar
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 100)
        self.progressBar.setVisible(True)
        self.progressBar.setFormat("%p%")  # Show percentage in progress bar
        
        # Worker thread
        self.worker = None
        
        # Check and display library status
        self.check_library_status()
        
    def browse_input_file(self):
        """Open dialog to select input DEM file"""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Input DEM File",
            "",
            "Raster Files (*.tif *.tiff *.img *.bil);;All Files (*.*)"
        )
        if filename:
            self.mInputFile.setText(filename)
            # Automatically suggest output filename
            if not self.mOutputFile.text():
                base_name = os.path.splitext(filename)[0]
                output_name = f"{base_name}_downscaled.tif"
                self.mOutputFile.setText(output_name)
    
    def browse_output_file(self):
        """Open dialog to select output DEM file"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select Output DEM File",
            "",
            "GeoTIFF Files (*.tif);;All Files (*.*)"
        )
        if filename:
            if not filename.endswith('.tif'):
                filename += '.tif'
            self.mOutputFile.setText(filename)
    
    def on_input_changed(self):
        """Update memory estimate when input file changes"""
        if self.mInputFile.text() and os.path.exists(self.mInputFile.text()):
            try:
                info = get_raster_info(self.mInputFile.text())
                zoom = self.mZoomFactor.value()
                mem_est = estimate_memory_usage(info['width'], info['height'], zoom)
                
                # Estimate runtime
                runtime_est = estimate_runtime(
                    info['width'], 
                    info['height'], 
                    zoom,
                    use_gpu=GPU_AVAILABLE,
                    use_vectorized=SCIPY_AVAILABLE
                )
                
                if PSUTIL_AVAILABLE:
                    available_mb = psutil.virtual_memory().available / (1024 * 1024)
                else:
                    available_mb = 4096  # Default 4GB if psutil not available
                
                status_text = (
                    f"Input: {info['width']}x{info['height']} px | "
                    f"Output: {mem_est['output_size'][0]}x{mem_est['output_size'][1]} px | "
                    f"Memory: {mem_est['total_mb']:.1f} MB | "
                    f"Est. time: {runtime_est['formatted_time']} ({runtime_est['processing_mode']})"
                )
                
                if mem_est['total_mb'] > available_mb * 0.8:
                    status_text += " ⚠️ HIGH MEMORY"
                    self.label_status.setStyleSheet("color: orange;")
                else:
                    self.label_status.setStyleSheet("")
                
                self.label_status.setText(status_text)
            except Exception as e:
                self.label_status.setText(f"Ready (Error reading file info: {str(e)})")
        else:
            self.check_library_status()  # Show library status when no file selected
    
    def check_library_status(self):
        """Check and display status of optional libraries"""
        from .dem_downscaling_algorithm import GPU_AVAILABLE, GPU_ERROR_MSG, SCIPY_AVAILABLE
        
        status_parts = []
        
        if GPU_AVAILABLE:
            try:
                import cupy as cp
                compute_cap = cp.cuda.Device(0).compute_capability
                status_parts.append(f"✅ GPU available (Compute {compute_cap[0]}.{compute_cap[1]})")
            except:
                status_parts.append("✅ GPU available")
        elif SCIPY_AVAILABLE:
            status_parts.append("✅ CPU vectorized")
            if GPU_ERROR_MSG:
                status_parts.append(f"⚠️ GPU: {GPU_ERROR_MSG}")
        else:
            status_parts.append("⚠️ Slow mode (install SciPy for speed)")
            if GPU_ERROR_MSG:
                status_parts.append(f"⚠️ GPU: {GPU_ERROR_MSG}")
        
        # Update status label with library info
        current_status = self.label_status.text()
        if current_status and current_status != "Ready" and "Input:" in current_status:
            # Append to existing status if it has file info
            lib_status = " | " + " | ".join(status_parts)
            self.label_status.setText(current_status + lib_status)
        else:
            self.label_status.setText(" | ".join(status_parts) if status_parts else "Ready")
    
    def show_installation_guide(self):
        """Show dialog with installation instructions"""
        import os
        import subprocess
        import platform
        from .dem_downscaling_algorithm import GPU_AVAILABLE, GPU_ERROR_MSG, SCIPY_AVAILABLE
        
        # Create custom dialog with scrollable content
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Install Performance Libraries")
        dialog.setMinimumSize(600, 500)
        dialog.setMaximumSize(800, 700)
        
        # Create main layout
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Create scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        
        # Get path to INSTALLATION_GUIDE.md and CUDA_TOOLKIT_INSTALL.md
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        guide_path = os.path.join(plugin_dir, "INSTALLATION_GUIDE.md")
        cuda_guide_path = os.path.join(plugin_dir, "CUDA_TOOLKIT_INSTALL.md")
        
        # Determine Python executable
        python_exe = sys.executable
        
        # Get Python executable - check if it's actually Python or QGIS executable
        python_exe_for_install = python_exe
        if 'qgis-ltr-bin.exe' in python_exe or 'qgis-bin.exe' in python_exe:
            # This is QGIS executable, not Python - try to find Python in same directory
            bin_dir = os.path.dirname(python_exe)
            # Try common Python executable names
            possible_python = [
                os.path.join(bin_dir, 'python-qgis-ltr.bat'),
                os.path.join(bin_dir, 'python3.exe'),
                os.path.join(bin_dir, 'python.exe'),
            ]
            # Use first that exists, or fall back to original
            for py_exe in possible_python:
                if os.path.exists(py_exe):
                    python_exe_for_install = py_exe
                    break
        
        # Format Python path with quotes if it contains spaces (use corrected Python executable)
        if ' ' in python_exe_for_install:
            python_exe_quoted = f'"{python_exe_for_install}"'
        else:
            python_exe_quoted = python_exe_for_install
        
        # Show current status first
        status_html = "<h3>Current Status:</h3>"
        if GPU_AVAILABLE:
            try:
                import cupy as cp
                device_name = "GPU"
                try:
                    props = cp.cuda.runtime.getDeviceProperties(0)
                    device_name = props['name'].decode('utf-8') if 'name' in props else "GPU"
                    compute_cap = cp.cuda.Device(0).compute_capability
                    status_html += f"<p>✅ <b>GPU Available:</b> {device_name} (Compute {compute_cap[0]}.{compute_cap[1]})</p>"
                except:
                    status_html += "<p>✅ <b>GPU Available</b></p>"
            except:
                status_html += "<p>✅ <b>GPU Available</b></p>"
        else:
            if GPU_ERROR_MSG:
                if "CuPy is not installed" in GPU_ERROR_MSG:
                    status_html += f"<p>❌ <b>GPU Not Available:</b> CuPy is not installed in QGIS Python</p>"
                elif "CUDA Toolkit not installed" in GPU_ERROR_MSG or "nvrtc" in GPU_ERROR_MSG.lower():
                    from .dem_downscaling_algorithm import CUDA_TOOLKIT_INSTALLED
                    if not CUDA_TOOLKIT_INSTALLED:
                        status_html += f"<p>❌ <b>GPU Not Available:</b> CUDA Toolkit not installed</p>"
                        status_html += "<p style='color: orange;'><b>Solution:</b> Install CUDA Toolkit from NVIDIA</p>"
                    else:
                        status_html += f"<p>❌ <b>GPU Not Available:</b> {GPU_ERROR_MSG}</p>"
                else:
                    status_html += f"<p>❌ <b>GPU Not Available:</b> {GPU_ERROR_MSG}</p>"
            else:
                status_html += "<p>❌ <b>GPU Not Available</b></p>"
        
        if SCIPY_AVAILABLE:
            status_html += "<p>✅ <b>CPU Vectorized Available</b> (SciPy installed)</p>"
        else:
            status_html += "<p>⚠️ <b>CPU Vectorized Not Available</b> (SciPy not installed)</p>"
        
        status_label = QtWidgets.QLabel()
        status_label.setText(status_html)
        status_label.setTextFormat(Qt.RichText)
        content_layout.addWidget(status_label)
        
        # Add separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        content_layout.addWidget(separator)
        
        # Create installation instructions (simplified)
        instructions_html = ""
        
        # Add installation instructions (simplified)
        if not SCIPY_AVAILABLE or not GPU_AVAILABLE:
            instructions_html += "<h3>Installation Commands:</h3>"
            
            if not SCIPY_AVAILABLE:
                instructions_html += "<h4>1. Install SciPy (Recommended - 10-100x faster on CPU):</h4>"
                instructions_html += f"<pre style='background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;'>{python_exe_quoted} -m pip install scipy</pre>"
            
            if not GPU_AVAILABLE:
                instructions_html += "<h4>2. Install CuPy (For GPU - 8x faster):</h4>"
                if 'qgis-ltr-bin.exe' in python_exe or 'qgis-bin.exe' in python_exe:
                    instructions_html += "<p><b>⚠️ CRITICAL:</b> Use Python executable (not QGIS executable)!</p>"
                
                instructions_html += "<p><b>For CUDA 11.x (most common):</b></p>"
                instructions_html += f"<pre style='background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;'>{python_exe_quoted} -m pip install cupy-cuda11x</pre>"
                
                instructions_html += "<p><b>For CUDA 12.x:</b></p>"
                instructions_html += f"<pre style='background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;'>{python_exe_quoted} -m pip install cupy-cuda12x</pre>"
        
        instructions_html += "<h3>How to Install:</h3>"
        instructions_html += "<ol>"
        instructions_html += "<li>Open <b>Command Prompt</b> (NOT QGIS Python Console!)</li>"
        instructions_html += "<li>Click the buttons below to copy the command</li>"
        instructions_html += "<li>Paste the command in Command Prompt and press Enter</li>"
        instructions_html += "<li>Wait for installation to complete (may take several minutes)</li>"
        instructions_html += "<li><b>Restart QGIS</b> completely</li>"
        instructions_html += "</ol>"
        instructions_html += "<p><b>⚠️ Important:</b> If you see 'Invalid Data Source' error, you're using the wrong executable. Use Python executable, not QGIS executable!</p>"
        
        # Add fix script info
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        fix_script_path = os.path.join(plugin_dir, 'fix_cuda_dll.bat')
        if os.path.exists(fix_script_path):
            instructions_html += "<hr>"
            instructions_html += "<h3>Auto-Fix CUDA DLL Issues:</h3>"
            instructions_html += f"<p>If you're having CUDA DLL errors, try running:</p>"
            instructions_html += f"<pre style='background-color: #e8f4f8; padding: 10px; border: 1px solid #ccc;'>{fix_script_path}</pre>"
            instructions_html += "<p>This script will automatically detect and fix CUDA PATH issues.</p>"
        
        instructions_label = QtWidgets.QLabel()
        instructions_label.setText(instructions_html)
        instructions_label.setTextFormat(Qt.RichText)
        instructions_label.setWordWrap(True)
        content_layout.addWidget(instructions_label)
        
        # Add links to guides
        guide_link = QtWidgets.QLabel()
        guide_links_html = "<p><b>📖 Guides:</b><br>"
        if os.path.exists(guide_path):
            guide_links_html += f"• <a href='file:///{guide_path.replace(os.sep, '/')}'>Full Installation Guide</a><br>"
        if os.path.exists(cuda_guide_path):
            guide_links_html += f"• <a href='file:///{cuda_guide_path.replace(os.sep, '/')}'>CUDA Toolkit Installation (for GPU errors)</a>"
        guide_links_html += "</p>"
        guide_link.setText(guide_links_html)
        guide_link.setTextFormat(Qt.RichText)
        guide_link.setOpenExternalLinks(True)
        content_layout.addWidget(guide_link)
        
        # Add warning about CUDA Toolkit if GPU not available
        if not GPU_AVAILABLE and GPU_ERROR_MSG and ("nvrtc" in GPU_ERROR_MSG.lower() or "dll" in GPU_ERROR_MSG.lower()):
            cuda_warning = QtWidgets.QLabel()
            cuda_warning.setText(
                "<p><b>⚠️ CUDA Toolkit Required:</b><br>"
                f"Error: {GPU_ERROR_MSG}<br>"
                "You need to install <b>CUDA Toolkit</b> from NVIDIA.<br>"
                f"See: <a href='file:///{cuda_guide_path.replace(os.sep, '/')}'>CUDA Toolkit Installation Guide</a></p>"
            )
            cuda_warning.setTextFormat(Qt.RichText)
            cuda_warning.setOpenExternalLinks(True)
            cuda_warning.setStyleSheet("color: orange; font-weight: bold;")
            content_layout.addWidget(cuda_warning)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set content widget to scroll area
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Create button layout (always visible at bottom)
        button_layout = QtWidgets.QHBoxLayout()
        
        buttons_to_add = []
        if not SCIPY_AVAILABLE:
            scipy_button = QtWidgets.QPushButton("📋 Copy SciPy Command")
            scipy_button.clicked.connect(lambda: self._copy_command(f"{python_exe_quoted} -m pip install scipy", "SciPy"))
            button_layout.addWidget(scipy_button)
            buttons_to_add.append(scipy_button)
        
        if not GPU_AVAILABLE:
            cupy11_button = QtWidgets.QPushButton("📋 Copy CuPy (CUDA 11)")
            cupy11_button.clicked.connect(lambda: self._copy_command(f"{python_exe_quoted} -m pip install cupy-cuda11x", "CuPy (CUDA 11)"))
            button_layout.addWidget(cupy11_button)
            buttons_to_add.append(cupy11_button)
            
            cupy12_button = QtWidgets.QPushButton("📋 Copy CuPy (CUDA 12)")
            cupy12_button.clicked.connect(lambda: self._copy_command(f"{python_exe_quoted} -m pip install cupy-cuda12x", "CuPy (CUDA 12)"))
            button_layout.addWidget(cupy12_button)
            buttons_to_add.append(cupy12_button)
        
        if os.path.exists(guide_path):
            view_guide_button = QtWidgets.QPushButton("📖 Open Full Guide")
            view_guide_button.clicked.connect(lambda: self._open_guide_file(guide_path, platform))
            button_layout.addWidget(view_guide_button)
        
        button_layout.addStretch()
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.exec_()
    
    def _copy_command(self, command, library_name):
        """Copy command to clipboard and show confirmation"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(command)
        QtWidgets.QMessageBox.information(self, "Copied!", 
            f"{library_name} command copied to clipboard:\n\n{command}\n\n"
            f"<b>⚠️ IMPORTANT:</b>\n"
            f"1. Open <b>Command Prompt</b> (NOT QGIS Python Console!)\n"
            f"2. Paste the command and press Enter\n"
            f"3. Wait for installation to complete\n"
            f"4. <b>Restart QGIS</b> completely after installation")
    
    def _open_guide_file(self, guide_path, platform):
        """Open the installation guide file"""
        import os
        import subprocess
        try:
            if platform.system() == 'Windows':
                os.startfile(guide_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', guide_path])
            else:  # Linux
                subprocess.call(['xdg-open', guide_path])
        except Exception as e:
            QtWidgets.QMessageBox.information(self, "Open Guide", 
                f"Could not open guide automatically.\n\n"
                f"Please open manually:\n{guide_path}")
    
    def validate_inputs(self):
        """Validate input values"""
        if not self.mInputFile.text():
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an input DEM file!")
            return False
        
        if not os.path.exists(self.mInputFile.text()):
            QtWidgets.QMessageBox.warning(self, "Error", "Input DEM file does not exist!")
            return False
        
        if not self.mOutputFile.text():
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an output DEM file!")
            return False
        
        output_dir = os.path.dirname(self.mOutputFile.text())
        if output_dir and not os.path.exists(output_dir):
            QtWidgets.QMessageBox.warning(self, "Error", "Output directory does not exist!")
            return False
        
        # Check memory requirements
        try:
            info = get_raster_info(self.mInputFile.text())
            zoom = self.mZoomFactor.value()
            mem_est = estimate_memory_usage(info['width'], info['height'], zoom)
            available_mb = psutil.virtual_memory().available / (1024 * 1024)
            
            if mem_est['total_mb'] > available_mb * 0.9:
                reply = QtWidgets.QMessageBox.warning(
                    self,
                    "High Memory Usage Warning",
                    f"Estimated memory usage ({mem_est['total_mb']:.1f} MB) is very high.\n"
                    f"Available memory: {available_mb:.1f} MB\n\n"
                    f"Processing may fail or be very slow.\n\n"
                    f"Do you want to continue?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if reply == QtWidgets.QMessageBox.No:
                    return False
        except Exception as e:
            QgsMessageLog.logMessage(f"Error estimating memory: {str(e)}", "DEM Downscaling")
        
        return True
    
    def update_progress(self, message, percentage):
        """Update progress bar and status label with percentage"""
        # Ensure percentage is within valid range
        percentage = max(0, min(100, int(percentage)))
        
        # Update status label with message and percentage
        status_text = f"{message}"
        if percentage > 0:
            status_text += f" ({percentage}%)"
        self.label_status.setText(status_text)
        
        # Update progress bar
        self.progressBar.setValue(percentage)
        self.progressBar.update()  # Force update
        
        # Process events to keep UI responsive
        QtWidgets.QApplication.processEvents()
    
    def process(self):
        """Process DEM downscaling - dialog stays open during processing"""
        if not self.validate_inputs():
            return
        
        # Prevent dialog from closing - block the default accept behavior
        # Check if already processing
        if self.is_processing or (self.worker and self.worker.isRunning()):
            # Already processing, do nothing
            return
        
        # Mark as processing
        self.is_processing = True
        
        # Disable OK button and change Cancel to Stop
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Stop")
        self.button_box.rejected.disconnect()  # Disconnect default reject
        self.button_box.rejected.connect(self.cancel_processing)
        
        # Disable input fields during processing
        self.mInputFile.setEnabled(False)
        self.mOutputFile.setEnabled(False)
        self.mZoomFactor.setEnabled(False)
        self.mRsme.setEnabled(False)
        self.btnBrowseInput.setEnabled(False)
        self.btnBrowseOutput.setEnabled(False)
        
        input_file = self.mInputFile.text()
        output_file = self.mOutputFile.text()
        zoom_factor = self.mZoomFactor.value()
        rsme = self.mRsme.value()
        
        # Get runtime estimate before starting
        try:
            info = get_raster_info(input_file)
            runtime_est = estimate_runtime(
                info['width'],
                info['height'],
                zoom_factor,
                use_gpu=GPU_AVAILABLE,
                use_vectorized=SCIPY_AVAILABLE
            )
            self.label_status.setText(
                f"Starting processing... Estimated time: {runtime_est['formatted_time']} "
                f"({runtime_est['processing_mode']})"
            )
        except:
            self.label_status.setText("Starting processing...")
        
        self.progressBar.setRange(0, 100)  # Set range 0-100%
        self.progressBar.setValue(0)

        # Create and start worker thread
        self.worker = DownscalingWorker(input_file, output_file, zoom_factor, rsme)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()
        
        # IMPORTANT: Do NOT call accept() or close() - keep dialog open!
    
    def cancel_processing(self):
        """Cancel processing if running"""
        if self.worker and self.worker.isRunning():
            reply = QtWidgets.QMessageBox.question(
                self,
                "Cancel Processing",
                "Are you sure you want to cancel the processing?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.worker.cancel()
                self.worker.wait(5000)  # Wait up to 5 seconds
                self.is_processing = False
                
                # Re-enable UI
                self.mInputFile.setEnabled(True)
                self.mOutputFile.setEnabled(True)
                self.mZoomFactor.setEnabled(True)
                self.mRsme.setEnabled(True)
                self.btnBrowseInput.setEnabled(True)
                self.btnBrowseOutput.setEnabled(True)
                
                self.label_status.setText("Processing cancelled")
                self.progressBar.setValue(0)
                self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
                self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Process")
                self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
                self.button_box.rejected.disconnect()
                self.button_box.rejected.connect(self.reject)
        else:
            # Not processing, just close dialog
            self.reject()
    
    def on_processing_finished(self, result):
        """Handle processing completion - dialog stays open"""
        # Mark as not processing
        self.is_processing = False
        
        # Set progress to 100%
        self.progressBar.setValue(100)
        self.update_progress("Processing completed!", 100)
        
        # Re-enable UI elements
        self.mInputFile.setEnabled(True)
        self.mOutputFile.setEnabled(True)
        self.mZoomFactor.setEnabled(True)
        self.mRsme.setEnabled(True)
        self.btnBrowseInput.setEnabled(True)
        self.btnBrowseOutput.setEnabled(True)
        
        # Re-enable buttons
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Process")
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
        self.button_box.rejected.disconnect()  # Disconnect stop handler
        self.button_box.rejected.connect(self.reject)  # Reconnect default reject to close dialog
        
        # Show success message
        msg = (
            f"Downscaling completed successfully!\n\n"
            f"Iterations: {result['iterations']}\n"
            f"Final energy: {result['final_energy']:.6f}\n"
            f"Converged: {'Yes' if result.get('converged', True) else 'No'}\n"
            f"Memory used: ~{result.get('memory_estimate_mb', 0):.1f} MB\n"
            f"Output size: {result['output_size'][0]}x{result['output_size'][1]} pixels\n\n"
            f"Output file: {result['output_file']}"
        )
        
        QtWidgets.QMessageBox.information(self, "Success", msg)
        
        # Load result into QGIS
        if os.path.exists(result['output_file']):
            layer = QgsRasterLayer(result['output_file'], os.path.basename(result['output_file']))
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                iface.messageBar().pushSuccess(
                    "DEM Downscaling",
                    f"Layer loaded: {os.path.basename(result['output_file'])}"
                )
            else:
                iface.messageBar().pushWarning(
                    "DEM Downscaling",
                    "File created but could not be loaded into QGIS"
                )
        
        # Update status - dialog remains open, user can close manually
        self.label_status.setText(f"✓ Completed! ({result['iterations']} iterations) - Click Close to exit")
    
    def on_processing_error(self, error_msg):
        """Handle processing errors - dialog stays open"""
        self.is_processing = False
        
        self.progressBar.setValue(0)
        QtWidgets.QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during processing:\n{error_msg}"
        )
        self.label_status.setText(f"Error: {error_msg}")
        
        # Re-enable UI elements
        self.mInputFile.setEnabled(True)
        self.mOutputFile.setEnabled(True)
        self.mZoomFactor.setEnabled(True)
        self.mRsme.setEnabled(True)
        self.btnBrowseInput.setEnabled(True)
        self.btnBrowseOutput.setEnabled(True)
        
        # Re-enable buttons
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Process")
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
        self.button_box.rejected.disconnect()
        self.button_box.rejected.connect(self.reject)
