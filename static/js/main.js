document.addEventListener('DOMContentLoaded', () => {
    const historyContainer = document.getElementById('history-container');
    const refreshBtn = document.getElementById('refresh-btn');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const closeLightbox = document.querySelector('.close-lightbox');

    // Fetch history
    const fetchHistory = async () => {
        try {
            // Add visual spinning animation
            refreshBtn.classList.add('spinning');
            refreshBtn.style.opacity = '0.7';
            
            const response = await fetch('/api/history');
            const data = await response.json();
            
            historyContainer.innerHTML = ''; // clear loading state
            
            if(data.length === 0) {
                historyContainer.innerHTML = '<div class="loading-state">No intrusions detected yet.</div>';
            } else {
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'history-card';
                    card.innerHTML = `
                        <img src="/static/${item.screenshot_path}" alt="Intrusion at ${item.timestamp}" class="history-thumb">
                        <div class="history-details">
                            <div class="history-time">${item.timestamp}</div>
                            <div><span class="history-badge">Intrusion</span></div>
                        </div>
                    `;
                    
                    // Add click event for lightbox
                    card.addEventListener('click', () => {
                        openLightbox(`/static/${item.screenshot_path}`, `Intrusion Detected at: ${item.timestamp}`);
                    });
                    
                    historyContainer.appendChild(card);
                });
            }
            
            // Restore refresh btn
            setTimeout(() => {
                refreshBtn.classList.remove('spinning');
                refreshBtn.style.opacity = '1';
            }, 300);
            
        } catch (error) {
            console.error('Error fetching history:', error);
            historyContainer.innerHTML = '<div class="loading-state" style="color: var(--danger)">Error loading history.</div>';
            refreshBtn.classList.remove('spinning');
            refreshBtn.style.opacity = '1';
        }
    };

    // Lightbox functions
    const openLightbox = (imgSrc, captionText) => {
        lightbox.style.display = 'block';
        lightboxImg.src = imgSrc;
        lightboxCaption.innerText = captionText;
        // prevent body scroll
        document.body.style.overflow = 'hidden';
    };

    const closeLightboxFunc = () => {
        lightbox.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    closeLightbox.addEventListener('click', closeLightboxFunc);

    // Close when clicking outside the image
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightboxFunc();
        }
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox.style.display === 'block') {
            closeLightboxFunc();
        }
    });

    // Initial fetch
    fetchHistory();

    // Setup polling (every 3 seconds)
    setInterval(fetchHistory, 3000);
    
    // Manual refresh
    refreshBtn.addEventListener('click', fetchHistory);

    // ===================================
    // Settings & Configuration Logic
    // ===================================
    const settingsModal = document.getElementById('settings-modal');
    const navSettings = document.getElementById('nav-settings');
    const closeSettings = document.getElementById('close-settings');
    
    // Toggle modal
    navSettings.addEventListener('click', (e) => {
        e.preventDefault();
        settingsModal.style.display = 'block';
    });
    closeSettings.addEventListener('click', () => settingsModal.style.display = 'none');
    
    // Update Video Source manually
    document.getElementById('btn-update-source').addEventListener('click', async () => {
        const sourceVal = document.getElementById('source-input').value.trim();
        if(!sourceVal) return;
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_source: sourceVal })
            });
            alert('Source updated. Refreshing feed...');
            location.reload();
        } catch(e) { console.error(e); }
    });

    // Upload Video Source
    document.getElementById('btn-upload-video').addEventListener('click', async () => {
        const fileInput = document.getElementById('video-upload');
        if(!fileInput.files.length) return;
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        try {
            const res = await fetch('/api/upload_video', {
                method: 'POST',
                body: formData
            });
            if(res.ok) {
                alert('Upload successful! Refreshing feed...');
                location.reload();
            } else {
                alert('Upload failed.');
            }
        } catch(e) { console.error(e); }
    });

    // ===================================
    // Drawing Polygon Logic
    // ===================================
    const canvas = document.getElementById('drawing-canvas');
    const ctx = canvas.getContext('2d');
    const drawControls = document.getElementById('drawing-controls');
    let points = [];
    let isDrawingMode = false;

    // Start drawing mode
    document.getElementById('btn-draw-poly').addEventListener('click', () => {
        settingsModal.style.display = 'none';
        isDrawingMode = true;
        points = [];
        drawControls.style.display = 'block';
        
        // Sync canvas size to the video stream element
        const videoEl = document.getElementById('video-stream');
        canvas.width = videoEl.clientWidth;
        canvas.height = videoEl.clientHeight;
        canvas.style.pointerEvents = 'auto'; // allow clicks
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        alert("Click on the video feed to map new restricted area points.");
    });

    // Handle canvas clicks
    canvas.addEventListener('click', (e) => {
        if(!isDrawingMode) return;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        points.push({x, y});
        renderPoints();
    });

    function renderPoints() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if(points.length === 0) return;
        
        ctx.strokeStyle = '#ef4444'; // var(--danger)
        ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
        ctx.lineWidth = 3;
        
        // Draw polygon and fill
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for(let i=1; i<points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        if(points.length > 2) {
            ctx.lineTo(points[0].x, points[0].y);
            ctx.fill();
        }
        ctx.stroke();
        
        // Draw circles on points
        ctx.fillStyle = '#ffffff';
        points.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        });
    }

    // Save Polygon
    document.getElementById('btn-save-poly').addEventListener('click', async () => {
        if(points.length < 3) {
            alert('A polygon needs at least 3 points!');
            return;
        }
        
        // Scale points from Canvas size back to original 640x480 for Python Backend
        const scaleX = 640 / canvas.width;
        const scaleY = 480 / canvas.height;
        const scaledPoints = points.map(p => [Math.round(p.x * scaleX), Math.round(p.y * scaleY)]);
        
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ polygon_points: scaledPoints })
            });
            quitDrawingMode();
            alert('Polygon restriction updated successfully!');
        } catch(e) { console.error(e); }
    });

    // Cancel Polygon
    document.getElementById('btn-cancel-poly').addEventListener('click', quitDrawingMode);

    function quitDrawingMode() {
        isDrawingMode = false;
        points = [];
        drawControls.style.display = 'none';
        canvas.style.pointerEvents = 'none';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
});
