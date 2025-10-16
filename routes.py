import os
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from models import db, User, Poster, Subscription
from forms import LoginForm, RegistrationForm, ProfileSetupForm, PosterGenerationForm, ProfileEditForm
from gemini_service import generate_poster_image, validate_prompt
from image_service import add_watermark, add_profile_overlay, save_uploaded_file, generate_filename, add_logo_to_poster_top
from razorpay_service import RazorpayService

def render_standalone_editor(poster, width, height, current_user):
    """
    Render standalone poster editor without Bootstrap interference
    """
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Poster - {poster.title} - Postasy</title>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Fabric.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js"></script>
    <!-- jsPDF for PDF export -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

    <style>
        :root {{
            --primary-color: #3a6baf; /* Postasy primary */
            --primary-hover: #184280; /* deep */
            --secondary-color: #56D1C1; /* subtle accent */
            --background-dark: #0f1116;
            --panel-dark: #1a2230;
            --text-light: #ecf0f1;
            --border-color: rgba(58, 107, 175, 0.35);
            --success-color: #27ae60;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --shadow: 0 4px 14px rgba(24, 66, 128, 0.25);
            --shadow-lg: 0 12px 30px rgba(24, 66, 128, 0.35);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #184280 0%, #3a6baf 60%, #184280 100%);
            color: var(--text-light);
            overflow: auto;
        }}

        .editor-container {{ display: flex; height: 100vh; background: rgba(0,0,0,0.25); }}

        /* Left Panel Styling */
        .left-panel {{
            width: 220px;
            background-color: rgba(26, 34, 48, 0.95);
            padding: 16px;
            display: flex;
            flex-direction: column;
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            max-height: 100vh;
            backdrop-filter: blur(8px);
        }}

        .logo-header {{
            display: flex;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }}

        .logo-header i {{ font-size: 20px; color: var(--primary-color); margin-right: 8px; }}
        .logo-header h2 {{ margin: 0; color: white; font-size: 18px; font-weight: 600; }}

        /* Main Tools */
        .main-tools {{ margin-bottom: 30px; }}

        .tool-btn {{
            display: flex;
            align-items: center;
            width: 100%;
            padding: 12px 16px;
            background: none;
            border: none;
            color: #a0aec0;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 6px;
            margin-bottom: 4px;
        }}

        .tool-btn:hover {{ background-color: rgba(58, 107, 175, 0.12); color: #dfe7f5; }}

        /* Right Work Area */
        .work-area {{ flex: 1; display: flex; flex-direction: column; }}
        .top-bar {{ height: 56px; background: rgba(26,34,48,0.8); border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; backdrop-filter: blur(6px); }}
        .top-actions .btn {{ background: var(--primary-color); color: #fff; border: none; padding: 8px 12px; border-radius: 8px; box-shadow: var(--shadow); }}
        .top-actions .btn:hover {{ background: var(--primary-hover); box-shadow: var(--shadow-lg); }}
    </style>
</head>
<body>
    <div class="editor-container">
        <!-- Left Panel: Tools & Controls -->
        <aside class="left-panel">
            <div class="logo-header">
                <i class="fas fa-palette"></i>
                <h2>Postasy</h2>
            </div>

            <div class="main-tools">
                <!-- Basic Tools -->
                <button class="tool-btn active" id="selectTool" onclick="setTool('select')">
                    <i class="fas fa-mouse-pointer"></i><span>Select</span>
                </button>
                <button class="tool-btn" id="textTool" onclick="setTool('text')">
                    <i class="fas fa-font"></i><span>Add Text</span>
                </button>
                <button class="tool-btn" onclick="showShapesMenu(this)">
                    <i class="fas fa-shapes"></i><span>Add Shape</span>
                </button>
                
                <div class="tool-separator"></div>
                
                <button class="tool-btn" onclick="undoAction()">
                    <i class="fas fa-undo"></i><span>Undo</span>
                </button>
                <button class="tool-btn" onclick="redoAction()">
                    <i class="fas fa-redo"></i><span>Redo</span>
                </button>
                <button class="tool-btn" onclick="deleteSelected()">
                    <i class="fas fa-trash"></i><span>Delete</span>
                </button>
            </div>

            <!-- Collapsible Panels -->
            <div class="panel-group">
                <div class="panel">
                    <button class="panel-header" onclick="togglePanel(this)">
                        <span><i class="fas fa-layer-group"></i> Layers</span>
                        <i class="fas fa-chevron-down toggle-icon"></i>
                    </button>
                    <div class="panel-content" id="layersPanel">
                        <!-- Layer items will be dynamically added here -->
                        <p style="color: var(--text-light); opacity: 0.7; font-size: 14px;">Your layers will appear here.</p>
                    </div>
                </div>

                <div class="panel">
                    <button class="panel-header" onclick="togglePanel(this)">
                        <span><i class="fas fa-sliders-h"></i> Properties</span>
                        <i class="fas fa-chevron-down toggle-icon"></i>
                    </button>
                    <div class="panel-content" id="propertiesPanel">
                        <p style="color: var(--text-light); opacity: 0.7; font-size: 14px;">Select an object to edit its properties.</p>
                    </div>
                </div>

                <div class="panel">
                    <button class="panel-header" onclick="togglePanel(this)">
                        <span><i class="fas fa-file-export"></i> Export</span>
                        <i class="fas fa-chevron-down toggle-icon"></i>
                    </button>
                    <div class="panel-content">
                        <button class="export-btn" onclick="exportAs('png')">
                            <i class="fas fa-file-image"></i>Export as PNG
                        </button>
                        <button class="export-btn" onclick="exportAs('jpg')">
                            <i class="fas fa-file-image"></i>Export as JPG
                        </button>
                        <button class="export-btn" onclick="exportAs('pdf')">
                            <i class="fas fa-file-pdf"></i>Export as PDF
                        </button>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Right Panel: Main Area -->
        <main class="main-area">
            <header class="main-header">
                <div class="poster-title-container">
                    <i class="fas fa-image"></i>
                    <input type="text" value="{poster.title}" class="poster-title" id="posterTitle">
                </div>
                <div class="header-actions">
                    <button class="btn btn-secondary" onclick="previewPoster()">
                        <i class="fas fa-eye"></i>Preview
                    </button>
                    <button class="btn btn-success" id="saveBtn" onclick="savePoster()">
                        <i class="fas fa-save"></i>Save Changes
                    </button>
                    <a href="/poster/gallery" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i>Back to Gallery
                    </a>
                </div>
            </header>

            <div class="canvas-container">
                <div class="canvas-wrapper">
                    <!-- Poster Loading Overlay -->
                    <div class="loading-overlay" id="loadingOverlay">
                        <div class="spinner"></div>
                        <p class="loading-text">Loading your poster...</p>
                    </div>

                    <!-- The Actual Poster Canvas -->
                    <canvas id="posterCanvas"></canvas>
                </div>

                <!-- Canvas Controls -->
                <div class="canvas-controls">
                    <button class="control-btn" onclick="zoomOut()" title="Zoom Out">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="control-btn" onclick="fitToScreen()" title="Fit to Screen">
                        <i class="fas fa-expand-arrows-alt"></i>
                    </button>
                    <button class="control-btn" onclick="zoomIn()" title="Zoom In">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        </main>
    </div>

    <!-- Save Form (Hidden) -->
    <form id="saveForm" method="POST" style="display: none;">
        <input type="hidden" name="canvas_data" id="canvasData">
    </form>

    <script>
        console.log('🎨 Starting Postasy Editor Standalone...');

        // Global variables
        let canvas = null;
        let history = [];
        let historyStep = 0;
        let currentTool = 'select';
        let zoomLevel = 1;
        let backgroundImage = null;

        // Poster data
        const posterData = {{
            id: {poster.id},
            title: "{poster.title}",
            filename: "{poster.filename}"
        }};

        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('📐 DOM loaded, initializing standalone editor...');
            initializeEditor();
        }});

        function initializeEditor() {{
            try {{
                console.log('🔧 Setting up standalone canvas...');
                
                // Create canvas with optimal dimensions
                const canvasWidth = {width};
                const canvasHeight = {height};
                
                canvas = new fabric.Canvas('posterCanvas', {{
                    width: canvasWidth,
                    height: canvasHeight,
                    backgroundColor: '#ffffff',
                    preserveObjectStacking: true,
                    selection: true,
                    targetFindTolerance: 5,
                    perPixelTargetFind: true
                }});
                
                console.log('✅ Standalone canvas created:', canvasWidth + 'x' + canvasHeight);
                
                // Setup canvas events
                setupCanvasEvents();
                
                // Load the poster image
                loadPosterImage();
                
                // Initialize UI
                updateToolbar();
                initializePanels();
                
                console.log('🚀 Standalone editor initialization complete');
                
            }} catch (error) {{
                console.error('❌ Standalone editor initialization failed:', error);
                hideLoading();
                showMessage('Failed to initialize the editor. Please refresh the page.', 'error');
            }}
        }}

        function setupCanvasEvents() {{
            console.log('🔗 Setting up standalone canvas events...');
            
            canvas.on('selection:created', handleSelection);
            canvas.on('selection:updated', handleSelection);
            canvas.on('selection:cleared', clearSelection);
            canvas.on('object:modified', saveState);
            canvas.on('object:added', updateLayers);
            canvas.on('object:removed', updateLayers);
            canvas.on('mouse:down', handleCanvasClick);
            
            console.log('✅ Standalone canvas events configured');
        }}

        function loadPosterImage() {{
            console.log('🖼️ Loading poster image standalone...');
            
            const imageUrl = '/static/uploads/posters/' + posterData.filename;
            console.log('📂 Image URL:', imageUrl);
            
            // Create test image to verify accessibility
            const testImg = new Image();
            
            testImg.onload = function() {{
                console.log('✅ Test image loaded successfully');
                console.log('📏 Image dimensions:', testImg.width + 'x' + testImg.height);
                
                // Load with Fabric.js
                fabric.Image.fromURL(imageUrl, function(fabricImg) {{
                    if (!fabricImg) {{
                        console.error('❌ Failed to create Fabric image');
                        hideLoading();
                        showMessage('Failed to load the poster image.', 'error');
                        return;
                    }}
                    
                    console.log('✅ Fabric image created successfully');
                    
                    try {{
                        // Calculate optimal scaling
                        const canvasWidth = canvas.getWidth();
                        const canvasHeight = canvas.getHeight();
                        const imgWidth = fabricImg.width;
                        const imgHeight = fabricImg.height;
                        
                        const scaleX = canvasWidth / imgWidth;
                        const scaleY = canvasHeight / imgHeight;
                        const scale = Math.min(scaleX, scaleY, 1);
                        
                        console.log('📐 Calculated scale:', scale);
                        
                        // Configure background image
                        fabricImg.set({{
                            scaleX: scale,
                            scaleY: scale,
                            left: (canvasWidth - imgWidth * scale) / 2,
                            top: (canvasHeight - imgHeight * scale) / 2,
                            selectable: false,
                            evented: false,
                            name: 'background-image',
                            lockMovementX: true,
                            lockMovementY: true,
                            lockRotation: true,
                            lockScalingX: true,
                            lockScalingY: true,
                            hoverCursor: 'default',
                            moveCursor: 'default'
                        }});
                        
                        // Clear canvas and add background
                        canvas.clear();
                        canvas.add(fabricImg);
                        canvas.sendToBack(fabricImg);
                        canvas.renderAll();
                        
                        // Store reference
                        backgroundImage = fabricImg;
                        
                        // Save initial state
                        saveState();
                        updateLayers();
                        
                        // Hide loading with smooth animation
                        setTimeout(() => {{
                            hideLoading();
                            showMessage('Poster loaded successfully!', 'success');
                            console.log('🎉 Standalone poster loaded and editor ready!');
                        }}, 500);
                        
                    }} catch (error) {{
                        console.error('❌ Error configuring image:', error);
                        hideLoading();
                        showMessage('Error setting up the poster image.', 'error');
                    }}
                    
                }}, {{
                    crossOrigin: 'anonymous'
                }});
            }};
            
            testImg.onerror = function(e) {{
                console.error('❌ Failed to load test image:', imageUrl, e);
                hideLoading();
                showMessage('The poster image could not be found. Please check if the image exists.', 'error');
            }};
            
            // Set loading timeout
            setTimeout(() => {{
                const overlay = document.getElementById('loadingOverlay');
                if (overlay && !overlay.classList.contains('hidden')) {{
                    console.error('⏰ Image loading timeout');
                    hideLoading();
                    showMessage('Image loading timed out. Please check your connection.', 'error');
                }}
            }}, 15000);
            
            testImg.src = imageUrl;
        }}

        function hideLoading() {{
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {{
                loadingOverlay.classList.add('hidden');
            }}
        }}

        function showMessage(message, type = 'success') {{
            // Remove existing messages
            const existingMessages = document.querySelectorAll('.message');
            existingMessages.forEach(msg => msg.remove());
            
            // Create new message
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{type}}`;
            messageDiv.innerHTML = `
                <i class="fas fa-${{type === 'success' ? 'check' : 'exclamation-triangle'}}"></i>
                ${{message}}
            `;
            
            document.body.appendChild(messageDiv);
            
            // Auto-remove after delay
            setTimeout(() => {{
                messageDiv.remove();
            }}, 5000);
        }}

        // Panel management
        function initializePanels() {{
            // Open the first panel by default
            const firstPanel = document.querySelector('.panel-header');
            if (firstPanel) {{
                togglePanel(firstPanel);
            }}
        }}

        function togglePanel(header) {{
            const content = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            
            // Toggle content
            if (content.classList.contains('active')) {{
                content.classList.remove('active');
                content.style.display = 'none';
                header.classList.remove('active');
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            }} else {{
                content.classList.add('active');
                content.style.display = 'block';
                header.classList.add('active');
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            }}
        }}

        // Tool management
        function setTool(tool) {{
            currentTool = tool;
            updateToolbar();
            
            // Configure canvas for the tool
            switch(tool) {{
                case 'select':
                    canvas.isDrawingMode = false;
                    canvas.selection = true;
                    canvas.defaultCursor = 'default';
                    break;
                case 'text':
                    canvas.isDrawingMode = false;
                    canvas.selection = false;
                    canvas.defaultCursor = 'text';
                    break;
                default:
                    canvas.isDrawingMode = false;
                    canvas.selection = false;
                    canvas.defaultCursor = 'crosshair';
            }}
            
            canvas.renderAll();
        }}

        function updateToolbar() {{
            // Update active tool button
            document.querySelectorAll('.tool-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            const toolBtn = document.getElementById(currentTool + 'Tool');
            if (toolBtn) {{
                toolBtn.classList.add('active');
            }}
        }}

        function handleCanvasClick(options) {{
            if (currentTool === 'text') {{
                const pointer = canvas.getPointer(options.e);
                addText(pointer.x, pointer.y);
            }}
        }}

        // Object creation functions
        function addText(x, y) {{
            const text = new fabric.Textbox('Click to edit text', {{
                left: x - 75,
                top: y - 15,
                width: 200,
                fontSize: 32,
                fill: '#4A90E2',
                fontFamily: 'Arial',
                fontWeight: '600',
                name: 'text-' + Date.now(),
                cornerStyle: 'circle',
                borderColor: '#4A90E2',
                cornerColor: '#4A90E2'
            }});
            
            canvas.add(text);
            canvas.setActiveObject(text);
            setTool('select');
            saveState();
        }}

        function addRectangle() {{
            const rect = new fabric.Rect({{
                left: 100,
                top: 100,
                width: 150,
                height: 100,
                fill: '#4A90E2',
                stroke: '#357ABD',
                strokeWidth: 2,
                rx: 10,
                ry: 10,
                name: 'rectangle-' + Date.now(),
                cornerStyle: 'circle',
                borderColor: '#4A90E2',
                cornerColor: '#4A90E2'
            }});
            
            canvas.add(rect);
            canvas.setActiveObject(rect);
            saveState();
        }}

        function addCircle() {{
            const circle = new fabric.Circle({{
                left: 100,
                top: 100,
                radius: 60,
                fill: '#50E3C2',
                stroke: '#4A90E2',
                strokeWidth: 2,
                name: 'circle-' + Date.now(),
                cornerStyle: 'circle',
                borderColor: '#4A90E2',
                cornerColor: '#4A90E2'
            }});
            
            canvas.add(circle);
            canvas.setActiveObject(circle);
            saveState();
        }}

        // Shape menu
        function showShapesMenu(btn) {{
            const menu = document.createElement('div');
            menu.style.cssText = `
                position: absolute;
                background: var(--panel-dark);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                box-shadow: var(--shadow-lg);
                padding: 12px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 8px;
                min-width: 150px;
            `;
            
            const shapes = [
                {{ icon: 'fas fa-square', action: 'addRectangle', title: 'Rectangle' }},
                {{ icon: 'fas fa-circle', action: 'addCircle', title: 'Circle' }}
            ];
            
            shapes.forEach(shape => {{
                const shapeBtn = document.createElement('button');
                shapeBtn.className = 'tool-btn';
                shapeBtn.innerHTML = `<i class="${{shape.icon}}"></i><span>${{shape.title}}</span>`;
                shapeBtn.onclick = function() {{
                    window[shape.action]();
                    document.body.removeChild(menu);
                }};
                menu.appendChild(shapeBtn);
            }});
            
            const rect = btn.getBoundingClientRect();
            menu.style.left = (rect.right + 10) + 'px';
            menu.style.top = rect.top + 'px';
            
            document.body.appendChild(menu);
            
            // Remove menu when clicking outside
            setTimeout(() => {{
                document.addEventListener('click', function removeMenu(e) {{
                    if (!menu.contains(e.target) && e.target !== btn) {{
                        if (document.body.contains(menu)) {{
                            document.body.removeChild(menu);
                        }}
                        document.removeEventListener('click', removeMenu);
                    }}
                }});
            }}, 10);
        }}

        // Layer management
        function updateLayers() {{
            const layersPanel = document.getElementById('layersPanel');
            const objects = canvas.getObjects().slice().reverse();
            
            let html = '';
            objects.forEach((obj, index) => {{
                const actualIndex = objects.length - index - 1;
                const name = obj.name || obj.type + ' ' + (actualIndex + 1);
                const isSelected = canvas.getActiveObject() === obj;
                const isVisible = obj.visible !== false;
                
                html += `
                    <div class="layer-item ${{isSelected ? 'active' : ''}}" onclick="selectLayer(${{actualIndex}})">
                        <div class="layer-name">${{name}}</div>
                        <div class="layer-controls">
                            <button class="layer-control-btn" onclick="event.stopPropagation(); toggleLayerVisibility(${{actualIndex}})" title="Toggle Visibility">
                                <i class="fas fa-eye${{isVisible ? '' : '-slash'}}"></i>
                            </button>
                            ${{obj.name !== 'background-image' ? `<button class="layer-control-btn" onclick="event.stopPropagation(); deleteLayer(${{actualIndex}})" title="Delete Layer">
                                <i class="fas fa-trash"></i>
                            </button>` : ''}}
                        </div>
                    </div>
                `;
            }});
            
            layersPanel.innerHTML = html || '<p style="color: var(--text-light); opacity: 0.7; font-size: 14px;">No layers</p>';
        }}

        function selectLayer(index) {{
            const objects = canvas.getObjects();
            const obj = objects[index];
            if (obj) {{
                canvas.setActiveObject(obj);
                canvas.renderAll();
            }}
        }}

        function toggleLayerVisibility(index) {{
            const objects = canvas.getObjects();
            const obj = objects[index];
            if (obj) {{
                obj.set('visible', !obj.visible);
                canvas.renderAll();
                updateLayers();
            }}
        }}

        function deleteLayer(index) {{
            const objects = canvas.getObjects();
            const obj = objects[index];
            if (obj && obj.name !== 'background-image') {{
                canvas.remove(obj);
                saveState();
            }}
        }}

        // Selection handling
        function handleSelection() {{
            updatePropertiesPanel();
            updateLayers();
        }}

        function clearSelection() {{
            clearPropertiesPanel();
            updateLayers();
        }}

        // Properties panel
        function updatePropertiesPanel() {{
            const activeObject = canvas.getActiveObject();
            const panel = document.getElementById('propertiesPanel');
            
            if (!activeObject || activeObject.name === 'background-image') {{
                clearPropertiesPanel();
                return;
            }}
            
            let html = '';
            
            // Position properties
            html += `
                <div class="property-group">
                    <label class="property-label">Position</label>
                    <div class="property-row">
                        <input type="number" class="property-input" placeholder="X" value="${{Math.round(activeObject.left)}}" onchange="updateObjectProperty('left', this.value)">
                        <input type="number" class="property-input" placeholder="Y" value="${{Math.round(activeObject.top)}}" onchange="updateObjectProperty('top', this.value)">
                    </div>
                </div>
            `;
            
            // Text-specific properties
            if (activeObject.type === 'textbox' || activeObject.type === 'text') {{
                html += `
                    <div class="property-group">
                        <label class="property-label">Font Size</label>
                        <input type="number" class="property-input" value="${{activeObject.fontSize}}" onchange="updateObjectProperty('fontSize', this.value)">
                    </div>
                    <div class="property-group">
                        <label class="property-label">Text Color</label>
                        <input type="color" class="color-picker" value="${{activeObject.fill}}" onchange="updateObjectProperty('fill', this.value)">
                    </div>
                `;
            }}
            
            // Shape-specific properties
            if (activeObject.type === 'rect' || activeObject.type === 'circle') {{
                html += `
                    <div class="property-group">
                        <label class="property-label">Fill Color</label>
                        <input type="color" class="color-picker" value="${{activeObject.fill}}" onchange="updateObjectProperty('fill', this.value)">
                    </div>
                `;
            }}
            
            panel.innerHTML = html;
        }}

        function clearPropertiesPanel() {{
            document.getElementById('propertiesPanel').innerHTML = '<p style="color: var(--text-light); opacity: 0.7; font-size: 14px;">Select an object to edit its properties.</p>';
        }}

        function updateObjectProperty(property, value) {{
            const activeObject = canvas.getActiveObject();
            if (!activeObject) return;
            
            const numValue = parseFloat(value);
            activeObject.set(property, isNaN(numValue) ? value : numValue);
            canvas.renderAll();
            saveState();
        }}

        // Action functions - ALL DEFINED HERE
        function deleteSelected() {{
            const activeObjects = canvas.getActiveObjects();
            if (activeObjects.length) {{
                const filteredObjects = activeObjects.filter(obj => obj.name !== 'background-image');
                if (filteredObjects.length > 0) {{
                    canvas.remove(...filteredObjects);
                    canvas.discardActiveObject();
                    saveState();
                }}
            }}
        }}

        function duplicateSelected() {{
            const activeObject = canvas.getActiveObject();
            if (activeObject && activeObject.name !== 'background-image') {{
                activeObject.clone(function(cloned) {{
                    cloned.set({{
                        left: cloned.left + 20,
                        top: cloned.top + 20,
                        name: activeObject.name.replace(/\\d+$/, '') + Date.now()
                    }});
                    canvas.add(cloned);
                    canvas.setActiveObject(cloned);
                    saveState();
                }});
            }}
        }}

        // History management
        function saveState() {{
            if (!canvas) return;
            
            if (historyStep < history.length - 1) {{
                history = history.slice(0, historyStep + 1);
            }}
            
            const state = JSON.stringify(canvas.toJSON());
            history.push(state);
            historyStep = history.length - 1;
            
            // Limit history size
            if (history.length > 50) {{
                history.shift();
                historyStep--;
            }}
        }}

        function undoAction() {{
            if (historyStep > 0) {{
                historyStep--;
                const state = history[historyStep];
                canvas.loadFromJSON(state, function() {{
                    canvas.renderAll();
                    updateLayers();
                    updatePropertiesPanel();
                    backgroundImage = canvas.getObjects().find(obj => obj.name === 'background-image');
                }});
            }}
        }}

        function redoAction() {{
            if (historyStep < history.length - 1) {{
                historyStep++;
                const state = history[historyStep];
                canvas.loadFromJSON(state, function() {{
                    canvas.renderAll();
                    updateLayers();
                    updatePropertiesPanel();
                    backgroundImage = canvas.getObjects().find(obj => obj.name === 'background-image');
                }});
            }}
        }}

        // Zoom functions
        function zoomIn() {{
            zoomLevel = Math.min(zoomLevel * 1.2, 5);
            canvas.setZoom(zoomLevel);
        }}

        function zoomOut() {{
            zoomLevel = Math.max(zoomLevel / 1.2, 0.1);
            canvas.setZoom(zoomLevel);
        }}

        function fitToScreen() {{
            zoomLevel = 1;
            canvas.setZoom(zoomLevel);
            canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
        }}

        // Export functions
        function exportAs(format) {{
            try {{
                if (!canvas) {{
                    showMessage('Canvas not initialized', 'error');
                    return;
                }}
                
                const dataURL = canvas.toDataURL({{
                    format: format === 'jpg' ? 'jpeg' : format,
                    quality: 0.95,
                    multiplier: 2
                }});
                
                if (format === 'pdf') {{
                    const {{ jsPDF }} = window.jspdf;
                    const pdf = new jsPDF({{
                        orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
                        unit: 'px',
                        format: [canvas.width, canvas.height]
                    }});
                    
                    pdf.addImage(dataURL, 'PNG', 0, 0, canvas.width, canvas.height);
                    pdf.save(`${{posterData.title || 'poster'}}.pdf`);
                }} else {{
                    const link = document.createElement('a');
                    link.download = `${{posterData.title || 'poster'}}.${{format}}`;
                    link.href = dataURL;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                showMessage(`Successfully exported as ${{format.toUpperCase()}}!`, 'success');
                
            }} catch (error) {{
                console.error('Export error:', error);
                showMessage('Failed to export image. Please try again.', 'error');
            }}
        }}

        // Save poster
        function savePoster() {{
            try {{
                if (!canvas || canvas.getObjects().length === 0) {{
                    showMessage('Canvas is empty. Please add some content before saving.', 'error');
                    return;
                }}
                
                const saveBtn = document.getElementById('saveBtn');
                const originalText = saveBtn.innerHTML;
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>Saving...';
                saveBtn.disabled = true;
                
                const dataURL = canvas.toDataURL('image/png', 1.0);
                
                if (!dataURL || dataURL.length < 100) {{
                    throw new Error('Generated image data is invalid');
                }}
                
                document.getElementById('canvasData').value = dataURL;
                document.getElementById('saveForm').submit();
                
                showMessage('Poster saved successfully!', 'success');
                
            }} catch (error) {{
                console.error('Save error:', error);
                showMessage('Failed to save poster. Please try again.', 'error');
                
                const saveBtn = document.getElementById('saveBtn');
                saveBtn.innerHTML = '<i class="fas fa-save"></i>Save Changes';
                saveBtn.disabled = false;
            }}
        }}

        function previewPoster() {{
            window.open('/poster/{poster.id}', '_blank');
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {{
                return;
            }}
            
            if (e.ctrlKey || e.metaKey) {{
                switch(e.key) {{
                    case 'z':
                        e.preventDefault();
                        if (e.shiftKey) {{
                            redoAction();
                        }} else {{
                            undoAction();
                        }}
                        break;
                    case 's':
                        e.preventDefault();
                        savePoster();
                        break;
                    case 'd':
                        e.preventDefault();
                        duplicateSelected();
                        break;
                }}
            }}
            
            if (e.key === 'Delete' || e.key === 'Backspace') {{
                e.preventDefault();
                deleteSelected();
            }}
        }});

        // Responsive handling
        window.addEventListener('resize', function() {{
            if (canvas) {{
                canvas.renderAll();
            }}
        }});

        console.log('🎨 Postasy Standalone Editor script loaded and ready!');
    </script>
</body>
</html>'''
    
    return Response(html_template, mimetype='text/html')

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
poster_bp = Blueprint('poster', __name__)
profile_bp = Blueprint('profile', __name__)
subscription_bp = Blueprint('subscription', __name__)
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main_bp.route('/landing')
def landing():
    """Redirect from old landing URL to root"""
    return redirect(url_for('main.index'))

# Marketing info pages
@main_bp.route('/pricing')
def pricing_page():
    return render_template('marketing_pricing.html')

@main_bp.route('/privacy')
def privacy_page():
    return render_template('marketing_privacy.html')

@main_bp.route('/terms')
def terms_page():
    return render_template('marketing_terms.html')

@main_bp.route('/about')
def about_page():
    return render_template('marketing_about.html')

@main_bp.route('/robots.txt')
def robots():
    """SEO: Robots.txt file"""
    return render_template('robots.txt'), 200, {'Content-Type': 'text/plain'}

@main_bp.route('/sitemap.xml')
def sitemap():
    """SEO: XML sitemap"""
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic database connectivity check
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

@main_bp.route('/api/analytics', methods=['POST'])
def analytics_endpoint():
    """Receive analytics data"""
    try:
        data = request.get_json()
        # Log analytics data (in production, send to analytics service)
        app.logger.info(f"Analytics: {data}")
        return {'status': 'received'}, 200
    except Exception:
        return {'status': 'error'}, 400

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Master admin bypasses profile completion requirement
    if not current_user.profile_completed and not current_user.is_master_admin:
        flash('Please complete your profile to start generating posters.', 'info')
        return redirect(url_for('profile.setup'))
    
    # Get user's recent posters
    recent_posters = Poster.query.filter_by(user_id=current_user.id)\
                                 .order_by(desc(Poster.created_at))\
                                 .limit(6).all()
    
    # Get poster statistics for current user
    total_posters = Poster.query.filter_by(user_id=current_user.id).count()
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_posters = Poster.query.filter(
        Poster.user_id == current_user.id,
        Poster.created_at >= week_ago
    ).count()
    
    # Admin dashboard features for master admin
    admin_stats = {}
    if current_user.is_master_admin:
        admin_stats = {
            'total_users': User.query.filter_by(is_master_admin=False).count(),
            'total_all_posters': Poster.query.count(),
            'premium_users': User.query.filter_by(is_premium=True, is_master_admin=False).count()
        }
    
    return render_template('dashboard.html', 
                         recent_posters=recent_posters,
                         total_posters=total_posters,
                         weekly_posters=weekly_posters,
                         is_admin=current_user.is_master_admin,
                         admin_stats=admin_stats)

# Authentication routes
def authenticate_master_admin(username, password):
    """
    MASTER ADMIN LOGIN - For internal testing and admin access
    Credentials: admin@postasy.ai / MasterKey#2025
    This bypasses all usage limits and provides unlimited access
    """
    MASTER_EMAIL = "admin@postasy.ai"
    MASTER_USERNAME = "postasy_admin"
    MASTER_PASSWORD = "MasterKey#2025"
    
    # Check if username matches either the email or the username
    return (username == MASTER_EMAIL or username == MASTER_USERNAME) and password == MASTER_PASSWORD

def get_or_create_master_admin():
    """
    Get or create the master admin user in the database
    This user is flagged as is_master_admin=True and has unlimited access
    """
    MASTER_EMAIL = "admin@postasy.ai"
    MASTER_USERNAME = "postasy_admin"
    
    # Check if master admin already exists
    master_user = User.query.filter_by(email=MASTER_EMAIL).first()
    
    if not master_user:
        # Create master admin user
        master_user = User()
        master_user.username = MASTER_USERNAME
        master_user.email = MASTER_EMAIL
        master_user.full_name = "Master Administrator"
        master_user.business_name = "Postasy Internal"
        master_user.is_premium = True
        master_user.is_master_admin = True  # This is the key flag for unlimited access
        master_user.profile_completed = True
        master_user.user_type = "organization"  # Master admin is organization type
        master_user.set_password("MasterKey#2025")
        db.session.add(master_user)
        db.session.commit()
        print("Created master admin user for internal testing")
    
    return master_user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    # For master admin testing, bypass form validation
    if request.method == 'POST':
        print(f"Login attempt: username={request.form.get('username')}, password_present={bool(request.form.get('password'))}")
        
        # Check if this is a master admin login attempt
        username = request.form.get('username') or form.username.data
        password = request.form.get('password') or form.password.data
        
        if authenticate_master_admin(username, password):
            # Get or create master admin user
            user = get_or_create_master_admin()
            login_user(user, remember=True)
            flash(f'Master admin logged in successfully: {user.email}', 'success')
            print(f"Master admin logged in: {user.email}")
            return redirect(url_for('main.dashboard'))
        
        if form.validate_on_submit():
            # Regular user authentication
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                return redirect(next_page)
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Check if username or email already exists
                if User.query.filter_by(username=form.username.data).first():
                    flash('Username already exists. Please choose a different one.', 'danger')
                    return render_template('register.html', form=form)
                
                if User.query.filter_by(email=form.email.data).first():
                    flash('Email already registered. Please use a different email.', 'danger')
                    return render_template('register.html', form=form)
                
                # Create new user
                user = User()
                user.username = form.username.data
                user.email = form.email.data
                user.set_password(form.password.data)
                user.profile_completed = False
                user.is_premium = False
                user.is_master_admin = False
                
                # Classify user based on email domain
                user.user_type = user.classify_user_type()
                
                db.session.add(user)
                db.session.commit()
                
                login_user(user)
                flash('Registration successful! Please complete your profile.', 'success')
                return redirect(url_for('profile.setup'))
            
            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')
                return render_template('register.html', form=form)
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# Profile routes
@profile_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if current_user.profile_completed:
        return redirect(url_for('main.dashboard'))
    
    form = ProfileSetupForm()
    if form.validate_on_submit():
        # Update user profile
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.business_name = form.business_name.data
        current_user.website = form.website.data
        current_user.facebook = form.facebook.data
        current_user.instagram = form.instagram.data
        current_user.twitter = form.twitter.data
        current_user.linkedin = form.linkedin.data
        current_user.profile_completed = True
        
        # Handle logo upload
        if form.logo.data:
            upload_folder = os.path.join('static', 'uploads', 'logos')
            filename = save_uploaded_file(form.logo.data, upload_folder)
            if filename:
                current_user.logo_filename = filename
        
        db.session.commit()
        flash('Profile completed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('profile_setup.html', form=form)

@profile_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    form = ProfileEditForm()
    
    if request.method == 'GET':
        # Pre-populate form with current data
        form.full_name.data = current_user.full_name
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.business_name.data = current_user.business_name
        form.website.data = current_user.website
        form.facebook.data = current_user.facebook
        form.instagram.data = current_user.instagram
        form.twitter.data = current_user.twitter
        form.linkedin.data = current_user.linkedin
    
    if form.validate_on_submit():
        # Update user profile
        current_user.full_name = form.full_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.business_name = form.business_name.data
        current_user.website = form.website.data
        current_user.facebook = form.facebook.data
        current_user.instagram = form.instagram.data
        current_user.twitter = form.twitter.data
        current_user.linkedin = form.linkedin.data
        
        # Handle logo upload
        if form.logo.data:
            upload_folder = os.path.join('static', 'uploads', 'logos')
            filename = save_uploaded_file(form.logo.data, upload_folder)
            if filename:
                current_user.logo_filename = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.manage'))
    
    return render_template('profile_management.html', form=form)

# Poster routes
@poster_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    # Master admin bypasses profile completion requirement
    if not current_user.profile_completed and not current_user.is_master_admin:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('profile.setup'))
    
    # Check daily usage limits
    if not current_user.can_create_poster_today():
        user_type = current_user.user_type.title()
        daily_limit = current_user.get_daily_poster_limit()
        flash(f'You have reached your daily limit of {daily_limit} poster(s) for {user_type} accounts. Please upgrade to Premium for unlimited access.', 'warning')
        return redirect(url_for('payment.plans'))
    
    form = PosterGenerationForm()
    if form.validate_on_submit():
        # Validate prompt
        is_valid, result = validate_prompt(form.prompt.data)
        if not is_valid:
            flash(f'Error: {result}', 'danger')
            return render_template('generate_poster.html', form=form)
        
        sanitized_prompt = result
        
        # Generate poster
        filename = generate_filename('.jpg')
        temp_path = os.path.join('static', 'uploads', 'temp_' + filename)
        final_path = os.path.join('static', 'uploads', 'posters', filename)
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        
        # Generate base image with Gemini
        if not generate_poster_image(sanitized_prompt, temp_path):
            flash('Error generating poster. Please try again.', 'danger')
            return render_template('generate_poster.html', form=form)
        
        # Add profile overlay
        selected_fields = form.get_selected_fields()
        profile_data = current_user.get_profile_fields()
        
        overlay_path = os.path.join('static', 'uploads', 'overlay_' + filename)
        if not add_profile_overlay(temp_path, overlay_path, profile_data, selected_fields):
            flash('Error adding profile information to poster.', 'warning')
            overlay_path = temp_path
        

        
        # Add watermark based on subscription (master admin gets watermark-free)
        if not add_watermark(overlay_path, final_path, current_user.has_unlimited_access()):
            flash('Error processing poster. Please try again.', 'danger')
            return render_template('generate_poster.html', form=form)
        
        # Save poster record
        poster = Poster()
        poster.title = form.title.data
        poster.prompt = sanitized_prompt
        poster.filename = filename
        poster.user_id = current_user.id
        poster.is_public = form.is_public.data
        poster.has_watermark = not current_user.has_unlimited_access()
        poster.set_displayed_fields(selected_fields)
        
        db.session.add(poster)
        db.session.commit()
        
        # Clean up temporary files
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if overlay_path != temp_path and os.path.exists(overlay_path):
                os.remove(overlay_path)
        except:
            pass
        
        flash('Poster generated successfully!', 'success')
        return redirect(url_for('poster.view', poster_id=poster.id))
    
    return render_template('generate_poster.html', form=form)

@poster_bp.route('/gallery')
@login_required
def gallery():
    page = request.args.get('page', 1, type=int)
    posters = Poster.query.filter_by(user_id=current_user.id)\
                          .order_by(desc(Poster.created_at))\
                          .paginate(page=page, per_page=12, error_out=False)
    
    return render_template('poster_gallery.html', posters=posters)

@poster_bp.route('/<int:poster_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(poster_id):
    """
    CRITICAL: Poster editing route - handles canvas operations and prevents crashes
    This route must handle all poster editing operations smoothly for production
    """
    poster = Poster.query.get_or_404(poster_id)
    
    # Check permissions
    if poster.user_id != current_user.id:
        flash('You do not have permission to edit this poster.', 'danger')
        return redirect(url_for('poster.gallery'))
    
    try:
        # Ensure poster file exists and validate
        poster_path = os.path.join('static', 'uploads', 'posters', poster.filename)
        if not os.path.exists(poster_path):
            logging.error(f"Poster file not found: {poster_path}")
            flash('Poster file not found. Please regenerate the poster.', 'danger')
            return redirect(url_for('poster.gallery'))
        
        # Validate that the file is actually an image
        try:
            from PIL import Image
            with Image.open(poster_path) as test_img:
                if test_img.size[0] == 0 or test_img.size[1] == 0:
                    raise ValueError("Invalid image dimensions")
        except Exception as e:
            logging.error(f"Invalid poster image file: {e}")
            flash('Poster file is corrupted. Please regenerate the poster.', 'danger')
            return redirect(url_for('poster.gallery'))
        
        if request.method == 'POST':
            # Handle canvas save operations
            canvas_data = request.form.get('canvas_data')
            if canvas_data and canvas_data.startswith('data:image'):
                try:
                    # Parse base64 image data
                    import base64
                    import io
                    from PIL import Image
                    
                    # Extract base64 data
                    header, data = canvas_data.split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # Create new filename for edited version
                    edited_filename = f"edited_{generate_filename('.png')}"
                    edited_path = os.path.join('static', 'uploads', 'posters', edited_filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(edited_path), exist_ok=True)
                    
                    # Save the edited image
                    with open(edited_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Update poster record with new filename
                    poster.filename = edited_filename
                    poster.updated_at = db.func.now()
                    db.session.commit()
                    
                    flash('Poster saved successfully!', 'success')
                    return redirect(url_for('poster.view', poster_id=poster.id))
                    
                except Exception as e:
                    print(f"Error saving edited poster: {str(e)}")
                    flash('Error saving poster. Please try again.', 'danger')
            else:
                flash('Invalid canvas data received.', 'danger')
        
        # Get poster dimensions for canvas initialization
        try:
            from PIL import Image
            with Image.open(poster_path) as img:
                width, height = img.size
        except:
            width, height = 800, 600  # Default fallback
        
        # Prepare user profile data for the editor
        posterData = {
            'userProfile': current_user.get_profile_fields()
        }
        
        # Create serializable poster data
        posterInfo = {
            'id': poster.id,
            'filename': poster.filename,
            'title': poster.title,
            'prompt': poster.prompt
        }
        

        
        # Use the new Canva-like editor
        return render_template('poster_editor_canva.html', poster=poster, posterInfo=posterInfo, posterData=posterData)
                             
    except Exception as e:
        print(f"Error in poster edit route: {str(e)}")
        flash('An error occurred while loading the editor. Please try again.', 'danger')
        return redirect(url_for('poster.gallery'))

@poster_bp.route('/<int:poster_id>')
@login_required
def view(poster_id):
    poster = Poster.query.get_or_404(poster_id)
    
    # Check permissions
    if poster.user_id != current_user.id and not poster.is_public:
        flash('You do not have permission to view this poster.', 'danger')
        return redirect(url_for('poster.gallery'))
    
    return render_template('poster_view.html', poster=poster)

@poster_bp.route('/<int:poster_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(poster_id):
    print(f"DELETE ROUTE CALLED - poster_id: {poster_id}, user_id: {current_user.id}")
    
    try:
        poster = Poster.query.get_or_404(poster_id)
        print(f"Poster found: {poster.title}, owner: {poster.user_id}")
        
        # Check permissions
        if poster.user_id != current_user.id:
            print(f"PERMISSION DENIED - poster owner: {poster.user_id}, current user: {current_user.id}")
            flash('You do not have permission to delete this poster.', 'danger')
            return redirect(url_for('poster.gallery'))
        
        print("Permission check passed, proceeding with deletion")
        
        # Delete file
        try:
            file_path = os.path.join('static', 'uploads', 'posters', poster.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        # Delete from database
        try:
            db.session.delete(poster)
            db.session.commit()
            print("Poster deleted from database successfully")
            flash('Poster deleted successfully.', 'success')
        except Exception as e:
            print(f"Database error: {e}")
            db.session.rollback()
            flash('Error deleting poster from database.', 'danger')
            return redirect(url_for('poster.gallery'))
        
        print("Delete operation completed successfully")
        return redirect(url_for('poster.gallery'))
        
    except Exception as e:
        print(f"Unexpected error in delete route: {e}")
        flash('An error occurred while deleting the poster.', 'danger')
        return redirect(url_for('poster.gallery'))

@poster_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    poster_ids = request.form.getlist('poster_ids')
    
    if not poster_ids:
        flash('No posters selected for deletion.', 'warning')
        return redirect(url_for('poster.gallery'))
    
    deleted_count = 0
    error_count = 0
    
    for poster_id in poster_ids:
        try:
            poster = Poster.query.get(poster_id)
            
            # Check if poster exists and user has permission
            if poster and poster.user_id == current_user.id:
                # Delete the poster file
                poster_path = os.path.join('static', 'uploads', 'posters', poster.filename)
                if os.path.exists(poster_path):
                    os.remove(poster_path)
                
                # Delete from database
                db.session.delete(poster)
                deleted_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            print(f"Error deleting poster {poster_id}: {str(e)}")
            error_count += 1
    
    # Commit all deletions
    try:
        db.session.commit()
        
        if deleted_count > 0:
            flash(f'{deleted_count} poster(s) deleted successfully!', 'success')
        
        if error_count > 0:
            flash(f'{error_count} poster(s) could not be deleted.', 'warning')
            
    except Exception as e:
        print(f"Error committing bulk delete: {str(e)}")
        flash('Error deleting posters. Please try again.', 'danger')
    
    return redirect(url_for('poster.gallery'))

@poster_bp.route('/<int:poster_id>/make-public', methods=['POST'])
@login_required
def make_public(poster_id):
    poster = Poster.query.get_or_404(poster_id)
    
    # Check permissions
    if poster.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    poster.is_public = True
    db.session.commit()
    
    return jsonify({'success': True})

@poster_bp.route('/<int:poster_id>/make-private', methods=['POST'])
@login_required
def make_private(poster_id):
    poster = Poster.query.get_or_404(poster_id)
    
    # Check permissions
    if poster.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    poster.is_public = False
    db.session.commit()
    
    return jsonify({'success': True})

@poster_bp.route('/public')
def public_gallery():
    page = request.args.get('page', 1, type=int)
    posters = Poster.query.filter_by(is_public=True)\
                          .order_by(desc(Poster.created_at))\
                          .paginate(page=page, per_page=12, error_out=False)
    
    return render_template('poster_gallery.html', posters=posters, public=True)

# Subscription routes


# Payment and Subscription Routes
@payment_bp.route('/plans')
@login_required
def plans():
    """Display subscription plans"""
    plans = RazorpayService.get_plans()
    current_plan = current_user.get_subscription_plan()
    return render_template('subscription_plans.html', plans=plans, current_plan=current_plan)

@payment_bp.route('/checkout/<plan_id>')
@login_required
def checkout(plan_id):
    """Create Razorpay subscription for selected plan"""
    try:
        subscription = RazorpayService.create_subscription(plan_id, current_user.id)
        
        # Return subscription details for frontend integration
        return jsonify({
            'success': True,
            'subscription_id': subscription['id'],
            'short_url': subscription.get('short_url'),
            'status': subscription['status'],
            'plan_id': plan_id
        })
    except Exception as e:
        flash(f'Error creating subscription: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 400

@payment_bp.route('/success')
@login_required
def success():
    """Handle successful payment"""
    payment_id = request.args.get('payment_id')
    subscription_id = request.args.get('subscription_id')
    
    if payment_id and subscription_id:
        # Verify payment signature
        razorpay_signature = request.args.get('razorpay_signature')
        razorpay_order_id = request.args.get('razorpay_order_id')
        
        if RazorpayService.verify_payment_signature(payment_id, razorpay_order_id, razorpay_signature):
            flash('Subscription activated successfully! Welcome to Premium!', 'success')
        else:
            flash('Payment verification failed. Please contact support.', 'danger')
    else:
        flash('Payment details missing. Please contact support.', 'warning')
    
    return redirect(url_for('main.dashboard'))

# Stripe integration removed

@payment_bp.route('/cancel')
@login_required
def cancel():
    """Handle canceled payment"""
    flash('Payment canceled. You can upgrade anytime.', 'info')
    return redirect(url_for('payment.plans'))

# Stripe integration removed

# Stripe integration removed

# Legacy subscription routes (for backward compatibility)
@subscription_bp.route('/plans')
@login_required
def old_plans():
    return redirect(url_for('payment.plans'))

@subscription_bp.route('/checkout')
@login_required
def old_checkout():
    return redirect(url_for('payment.plans'))

# Profile routes
@profile_bp.route('/user/<username>')
def public_profile(username):
    """Display public profile for any user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get public posters only
    public_posters = Poster.query.filter_by(
        user_id=user.id, 
        is_public=True
    ).order_by(desc(Poster.created_at)).all()
    
    return render_template('profile_public.html', 
                         user=user, 
                         public_posters=public_posters)

@profile_bp.route('/settings')
@login_required
def settings():
    """Advanced profile settings page"""
    return render_template('profile_settings.html')

@profile_bp.route('/privacy', methods=['GET', 'POST'])
@login_required
def privacy():
    """Privacy settings for profile"""
    if request.method == 'POST':
        # Handle privacy settings updates
        flash('Privacy settings updated successfully!', 'success')
        return redirect(url_for('profile.privacy'))
    
    return render_template('profile_privacy.html')

# Static file routes
@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

# Modern Editor Route
@poster_bp.route('/modern-editor/<int:poster_id>')
@login_required
def modern_editor(poster_id):
    """Modern Canva-like poster editor with glassmorphism design"""
    poster = Poster.query.get_or_404(poster_id)
    
    # Check ownership or admin access
    if poster.user_id != current_user.id and not current_user.is_master_admin:
        abort(403)
    
    return render_template('poster_editor_modern.html', poster=poster)
