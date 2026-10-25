/**
 * South Lhonak GLOF InSAR Measurability Atlas
 * Client-Side Interactive Logic: Radar Canvas Simulation, Segmented Thresholds, and Scrollytelling
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ==========================================================================
     01. Interactive Radar Physics Canvas Simulator
     ========================================================================== */
  const canvas = document.getElementById('radarCanvas');
  const ctx = canvas ? canvas.getContext('2d') : null;

  const btnDesc = document.getElementById('btn-track-desc');
  const btnAsc = document.getElementById('btn-track-asc');

  const telemAzimuth = document.getElementById('telemAzimuth');
  const telemElev = document.getElementById('telemElev');
  const telemProj = document.getElementById('telemProj');
  const telemSens = document.getElementById('telemSens');

  let currentTrack = 'desc'; // 'desc' (Track 048) or 'asc' (Track 012)
  let waveOffset = 0;
  let animFrameId = null;

  const trackData = {
    desc: {
      azimuth: '-10.4° (ESE)',
      elevation: '50.8°',
      projection: '-0.276',
      sensitivity: '0.309',
      heading: '190.4°',
      sensorXRatio: 0.85,
      sensorYRatio: 0.14,
      name: 'DESCENDING TRACK 048 (LOOKING WEST)'
    },
    asc: {
      azimuth: '-169.6° (WSW)',
      elevation: '50.9°',
      projection: '-0.366',
      sensitivity: '0.449',
      heading: '349.6°',
      sensorXRatio: 0.15,
      sensorYRatio: 0.14,
      name: 'ASCENDING TRACK 012 (LOOKING EAST)'
    }
  };

  function updateTelemetry(track) {
    const data = trackData[track];
    if (telemAzimuth) telemAzimuth.textContent = data.azimuth;
    if (telemElev) telemElev.textContent = data.elevation;
    if (telemProj) telemProj.textContent = data.projection;
    if (telemSens) telemSens.textContent = data.sensitivity;
  }

  // Utility to render protected badges behind text so lines never clash with text
  function drawBadge(ctx, text, x, y, textColor, bgColor, borderColor, font) {
    ctx.save();
    ctx.font = font || '10px "JetBrains Mono", monospace';
    const paddingX = 8;
    const paddingY = 4;
    const textWidth = ctx.measureText(text).width;
    const boxHeight = 18;

    ctx.fillStyle = bgColor || 'rgba(8, 11, 15, 0.9)';
    ctx.fillRect(x - paddingX, y - boxHeight + 4, textWidth + paddingX * 2, boxHeight);

    ctx.strokeStyle = borderColor || 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x - paddingX, y - boxHeight + 4, textWidth + paddingX * 2, boxHeight);

    ctx.fillStyle = textColor || '#FFFFFF';
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  function drawRadarScene() {
    if (!ctx || !canvas) return;
    const w = canvas.width;
    const h = canvas.height;

    // Clear background
    ctx.fillStyle = '#080B0F';
    ctx.fillRect(0, 0, w, h);

    // Altitude Grid Lines (4,800m to 6,800m asl)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    for (let y = 50; y < h - 50; y += 45) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      const altMeters = Math.round(6800 - (y / (h - 90)) * 2000);
      ctx.fillStyle = '#475569';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText(`${altMeters}m ASL`, 8, y - 4);
    }

    // Topographic Cross-Section Profile (West to East)
    // Left: Valley floor and Lake (5,200m)
    // Center: Active Moraine Scarp (5,350m, ~33° slope)
    // Right: High Glacial Ridge Crest (6,200m)
    const pts = [
      { x: 0, y: h - 60 },
      { x: w * 0.18, y: h - 60 }, // Lake basin start
      { x: w * 0.42, y: h - 60 }, // Lake surface end
      { x: w * 0.52, y: h - 140 }, // Lateral moraine scarp base
      { x: w * 0.62, y: h - 230 }, // Lateral moraine scarp crest (Steep face ~33°)
      { x: w * 0.74, y: h - 260 }, // Flatter upper bench (<15°)
      { x: w * 0.88, y: h - 320 }, // Moraine ridge peak (6,200m)
      { x: w, y: h - 290 }
    ];

    // Mountain Body
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) {
      ctx.lineTo(pts[i].x, pts[i].y);
    }
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();

    ctx.fillStyle = '#10151E';
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Bottom Geographic Orientation Axis
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(20, h - 18);
    ctx.lineTo(w - 20, h - 18);
    ctx.stroke();

    drawBadge(ctx, 'WEST // PROGLACIAL LAKE BASIN (5,200M)', 25, h - 12, '#94A3B8', '#080B0F', '#242E3D');
    drawBadge(ctx, 'EAST // MORAINE RIDGE (6,200M)', w - 240, h - 12, '#94A3B8', '#080B0F', '#242E3D');

    // South Lhonak Lake Water Body (Elevation 5,200m)
    const lakeStartX = w * 0.18;
    const lakeEndX = w * 0.44;
    const lakeY = h - 60;
    ctx.fillStyle = 'rgba(0, 240, 255, 0.18)';
    ctx.fillRect(lakeStartX, lakeY - 6, lakeEndX - lakeStartX, 20);
    ctx.strokeStyle = '#00F0FF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(lakeStartX, lakeY - 6);
    ctx.lineTo(lakeEndX, lakeY - 6);
    ctx.stroke();

    drawBadge(ctx, 'SOUTH LHONAK LAKE (5,200m)', lakeStartX + 12, lakeY + 28, '#00F0FF', 'rgba(8,11,15,0.92)', 'rgba(0,240,255,0.4)', '11px "Space Grotesk", sans-serif');

    // Active Moraine Failure Scarp Face (Slope ~33°, Elevation 5,350m)
    const scarpP1 = pts[3];
    const scarpP2 = pts[4];
    ctx.strokeStyle = '#FF4757';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(scarpP1.x, scarpP1.y);
    ctx.lineTo(scarpP2.x, scarpP2.y);
    ctx.stroke();

    // 1. Scarp Label Badge (Positioned high above the scarp crest with generous vertical clearance)
    drawBadge(ctx, 'LATERAL MORAINE FAILURE SCARP (~33°)', scarpP1.x - 30, scarpP2.y - 45, '#FF4757', 'rgba(16,21,30,0.95)', '#FF4757', '11px "Space Grotesk", sans-serif');

    // Vector Calculations at Scarp Centroid
    const midX = (scarpP1.x + scarpP2.x) / 2;
    const midY = (scarpP1.y + scarpP2.y) / 2;

    // 2. Downslope Motion Vector d (Points DOWN and LEFT into lake)
    const slopeAngle = Math.atan2(scarpP1.y - scarpP2.y, scarpP1.x - scarpP2.x);
    const dLen = 70;
    const dEndX = midX + Math.cos(slopeAngle) * dLen;
    const dEndY = midY + Math.sin(slopeAngle) * dLen;

    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(midX, midY);
    ctx.lineTo(dEndX, dEndY);
    ctx.stroke();

    // Arrowhead for d
    const arrowHeadLen = 10;
    ctx.fillStyle = '#F59E0B';
    ctx.beginPath();
    ctx.moveTo(dEndX, dEndY);
    ctx.lineTo(dEndX - arrowHeadLen * Math.cos(slopeAngle - Math.PI / 6), dEndY - arrowHeadLen * Math.sin(slopeAngle - Math.PI / 6));
    ctx.lineTo(dEndX - arrowHeadLen * Math.cos(slopeAngle + Math.PI / 6), dEndY - arrowHeadLen * Math.sin(slopeAngle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    // Dedicated badge for d (down near lake shore, clear of any other text)
    drawBadge(ctx, 'd (Downslope Vector)', dEndX - 80, dEndY + 24, '#F59E0B', 'rgba(8,11,15,0.95)', '#F59E0B', '10px "JetBrains Mono", monospace');

    // Satellite Position & Radar Wavefronts
    const satData = trackData[currentTrack];
    const satX = w * satData.sensorXRatio;
    const satY = h * satData.sensorYRatio;

    // 3. Ground-to-Sensor Look Vector s (Points from Scarp UP to Satellite)
    const sAngle = Math.atan2(satY - midY, satX - midX);
    const sLen = 110;
    const sEndX = midX + Math.cos(sAngle) * sLen;
    const sEndY = midY + Math.sin(sAngle) * sLen;

    ctx.strokeStyle = '#00F0FF';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(midX, midY);
    ctx.lineTo(sEndX, sEndY);
    ctx.stroke();

    // Arrowhead for s
    ctx.fillStyle = '#00F0FF';
    ctx.beginPath();
    ctx.moveTo(sEndX, sEndY);
    ctx.lineTo(sEndX - arrowHeadLen * Math.cos(sAngle - Math.PI / 6), sEndY - arrowHeadLen * Math.sin(sAngle - Math.PI / 6));
    ctx.lineTo(sEndX - arrowHeadLen * Math.cos(sAngle + Math.PI / 6), sEndY - arrowHeadLen * Math.sin(sAngle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    // Dedicated badge for s (Positioned high along the beam line in open sky, far from the scarp)
    const sBadgeX = currentTrack === 'desc' ? satX - 170 : satX + 35;
    const sBadgeY = satY + 45;
    drawBadge(ctx, 's (Look Vector to Satellite)', sBadgeX, sBadgeY, '#00F0FF', 'rgba(8,11,15,0.95)', '#00F0FF', '10px "JetBrains Mono", monospace');

    // Angle Arc between d and s (Demonstrating why P = d • s < 0)
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.arc(midX, midY, 32, Math.min(slopeAngle, sAngle), Math.max(slopeAngle, sAngle));
    ctx.stroke();
    ctx.restore();

    // 4. Obtuse Angle Explanation Badge (Positioned inside the mountain bedrock, safely below scarp)
    drawBadge(ctx, 'Angle γ > 90° (Obtuse) ⇒ P = d • s < 0', midX + 25, midY + 40, '#E2E8F0', 'rgba(16,21,30,0.95)', 'rgba(255,255,255,0.2)', '10px "JetBrains Mono", monospace');

    // Animate Propagating Radar Waves (from Satellite down toward Scarp)
    const distToScarp = Math.hypot(midX - satX, midY - satY);
    const beamAngle = Math.atan2(midY - satY, midX - satX);

    ctx.save();
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
    ctx.lineWidth = 1.5;

    // Full beam guideline
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(satX, satY);
    ctx.lineTo(midX, midY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Expanding wavefront arcs
    waveOffset = (waveOffset + 0.75) % 45;
    for (let r = waveOffset + 30; r < distToScarp; r += 45) {
      ctx.beginPath();
      ctx.arc(satX, satY, r, beamAngle - 0.14, beamAngle + 0.14);
      ctx.stroke();
    }
    ctx.restore();

    // Satellite Platform Body
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(satX - 14, satY - 7, 28, 14);
    // Solar Panel Arrays
    ctx.fillStyle = '#00E599';
    ctx.fillRect(satX - 38, satY - 4, 20, 8);
    ctx.fillRect(satX + 18, satY - 4, 20, 8);

    drawBadge(ctx, `SENTINEL-1 C-BAND // ${satData.name}`, satX - 110, satY - 18, '#00E599', 'rgba(8,11,15,0.95)', '#00E599', '10px "JetBrains Mono", monospace');
  }

  function startAnimation() {
    function loop() {
      drawRadarScene();
      animFrameId = requestAnimationFrame(loop);
    }
    loop();
  }

  if (btnDesc && btnAsc) {
    btnDesc.addEventListener('click', () => {
      currentTrack = 'desc';
      btnDesc.classList.add('active');
      btnAsc.classList.remove('active');
      updateTelemetry('desc');
    });

    btnAsc.addEventListener('click', () => {
      currentTrack = 'asc';
      btnAsc.classList.add('active');
      btnDesc.classList.remove('active');
      updateTelemetry('asc');
    });
  }

  if (canvas) {
    startAnimation();
    updateTelemetry('desc');
  }


  /* ==========================================================================
     02. Observability Sensitivity Threshold Controller (Tactile 3-State Mode)
     ========================================================================== */
  const rDisplay = document.getElementById('r-val-display');

  const barDesc = document.getElementById('bar-desc');
  const barAsc = document.getElementById('bar-asc');
  const barComb = document.getElementById('bar-comb');

  const statDesc = document.getElementById('stat-desc');
  const statAsc = document.getElementById('stat-asc');
  const statComb = document.getElementById('stat-comb');

  const threshBtns = document.querySelectorAll('.thresh-btn');

  const thresholdMetrics = {
    20: {
      label: 'R ≥ 0.20 (LENIENT)',
      descPct: 78.0,
      ascPct: 89.1,
      combPct: 95.0
    },
    30: {
      label: 'R ≥ 0.30 (STANDARD)',
      descPct: 51.8,
      ascPct: 76.3,
      combPct: 87.0
    },
    50: {
      label: 'R ≥ 0.50 (STRICT)',
      descPct: 12.4,
      ascPct: 35.4,
      combPct: 37.9
    }
  };

  if (threshBtns.length > 0) {
    threshBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        threshBtns.forEach(b => {
          b.classList.remove('active');
          const tag = b.querySelector('.thresh-tag');
          const sub = b.querySelector('.thresh-sub');
          if (tag) tag.classList.remove('text-cyan');
          if (sub) sub.classList.remove('text-cyan');
        });

        btn.classList.add('active');
        const activeTag = btn.querySelector('.thresh-tag');
        const activeSub = btn.querySelector('.thresh-sub');
        if (activeTag) activeTag.classList.add('text-cyan');
        if (activeSub) activeSub.classList.add('text-cyan');

        const rVal = parseInt(btn.getAttribute('data-r'), 10);
        const data = thresholdMetrics[rVal] || thresholdMetrics[30];

        if (rDisplay) rDisplay.textContent = data.label;

        if (barDesc) barDesc.style.width = `${data.descPct}%`;
        if (barAsc) barAsc.style.width = `${data.ascPct}%`;
        if (barComb) barComb.style.width = `${data.combPct}%`;

        if (statDesc) statDesc.textContent = `${data.descPct}% COVERAGE`;
        if (statAsc) statAsc.textContent = `${data.ascPct}% COVERAGE`;
        if (statComb) statComb.textContent = `${data.combPct}% OBSERVABLE`;
      });
    });
  }


  /* ==========================================================================
     03. Sticky Sub-Nav Active State On Scroll
     ========================================================================== */
  const sections = document.querySelectorAll('.section');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let currentId = '';
    const scrollPos = window.scrollY + 140;

    sections.forEach((sec) => {
      const top = sec.offsetTop;
      const height = sec.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        currentId = sec.getAttribute('id');
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${currentId}`) {
        link.classList.add('active');
      }
    });
  });

});
