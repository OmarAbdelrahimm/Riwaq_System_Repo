/**
 * Procedural PBR Textures for Bab Zuwayla
 * 100% procedural HTML5 Canvas textures with zero external URL / 404 dependencies
 */

import * as THREE from 'three';

/**
 * Creates aged Cairo Mokattam limestone ashlar block texture
 */
export function createAshlarStoneTexture(warmth = 0.5): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  // Base stone tone (sand/ochre Mokattam limestone)
  const baseR = Math.round(210 + warmth * 15);
  const baseG = Math.round(195 + warmth * 5);
  const baseB = Math.round(170 - warmth * 15);

  ctx.fillStyle = `rgb(${baseR}, ${baseG}, ${baseB})`;
  ctx.fillRect(0, 0, 1024, 1024);

  // Micro-grain pitting & noise
  const imgData = ctx.getImageData(0, 0, 1024, 1024);
  const data = imgData.data;
  for (let i = 0; i < data.length; i += 4) {
    const grain = (Math.random() - 0.5) * 24;
    data[i] = Math.min(255, Math.max(0, data[i] + grain));
    data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + grain * 0.9));
    data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + grain * 0.8));
  }
  ctx.putImageData(imgData, 0, 0);

  // Ashlar course lines (horizontal bedding planes and staggered vertical joints)
  const courseCount = 16;
  const courseHeight = 1024 / courseCount;

  ctx.lineWidth = 2.5;

  for (let c = 0; c < courseCount; c++) {
    const y = c * courseHeight;

    // Subtle individual course tint variation
    const courseTint = (Math.random() - 0.5) * 16;
    ctx.fillStyle = `rgba(${courseTint > 0 ? 230 : 150}, ${courseTint > 0 ? 210 : 140}, ${courseTint > 0 ? 180 : 120}, ${Math.abs(courseTint) / 100})`;
    ctx.fillRect(0, y, 1024, courseHeight);

    // Bed joint shadow & highlight
    ctx.strokeStyle = 'rgba(70, 60, 50, 0.55)';
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 250, 235, 0.35)';
    ctx.beginPath();
    ctx.moveTo(0, y + 2.5);
    ctx.lineTo(1024, y + 2.5);
    ctx.stroke();

    // Vertical joints staggered per course
    const blockWidth = 128 + ((c % 3) * 16);
    const offset = (c % 2 === 0 ? 0 : blockWidth / 2) + (c * 23) % 40;

    for (let x = offset; x < 1024; x += blockWidth) {
      ctx.strokeStyle = 'rgba(65, 55, 45, 0.45)';
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x, y + courseHeight);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(255, 248, 230, 0.25)';
      ctx.beginPath();
      ctx.moveTo(x + 2, y);
      ctx.lineTo(x + 2, y + courseHeight);
      ctx.stroke();
    }
  }

  // Weathering patinas (soot, rain wash streaks, desert sand settling)
  const grad = ctx.createLinearGradient(0, 0, 0, 1024);
  grad.addColorStop(0, 'rgba(80, 70, 60, 0.15)');
  grad.addColorStop(0.5, 'rgba(160, 140, 110, 0.05)');
  grad.addColorStop(1, 'rgba(110, 95, 75, 0.2)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 1024, 1024);

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Creates normal/bump map for stone ashlar blocks
 */
export function createAshlarNormalTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  // Neutral normal map color: RGB(128, 128, 255)
  ctx.fillStyle = '#8080ff';
  ctx.fillRect(0, 0, 512, 512);

  const courseCount = 16;
  const courseHeight = 512 / courseCount;

  ctx.lineWidth = 3;
  for (let c = 0; c < courseCount; c++) {
    const y = c * courseHeight;
    // Horizontal bevel
    ctx.strokeStyle = '#5080c0';
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(512, y);
    ctx.stroke();

    // Vertical joints
    const blockWidth = 64 + ((c % 3) * 8);
    const offset = (c % 2 === 0 ? 0 : blockWidth / 2);
    for (let x = offset; x < 512; x += blockWidth) {
      ctx.strokeStyle = '#8050c0';
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x, y + courseHeight);
      ctx.stroke();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  return texture;
}

/**
 * Creates iron-studded door texture matching reference photograph image_191b72fb.png
 */
export function createIronStuddedDoorTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  // Dark wrought iron / heavy weathered timber base
  ctx.fillStyle = '#322f2b';
  ctx.fillRect(0, 0, 1024, 1024);

  // Iron horizontal bands
  const bandCount = 28;
  const bandHeight = 1024 / bandCount;

  for (let b = 0; b < bandCount; b++) {
    const y = b * bandHeight;
    // Band plate variation
    const bandShade = Math.round(45 + (Math.sin(b * 1.7) * 12));
    ctx.fillStyle = `rgb(${bandShade}, ${bandShade - 3}, ${bandShade - 6})`;
    ctx.fillRect(0, y + 2, 1024, bandHeight - 4);

    // Bevel between iron straps
    ctx.strokeStyle = '#181614';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1024, y);
    ctx.stroke();

    ctx.strokeStyle = '#605850';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, y + 2);
    ctx.lineTo(1024, y + 2);
    ctx.stroke();

    // Dense hemispherical iron rivets / studs across each strap
    const studsPerBand = 18;
    const studSpacing = 1024 / studsPerBand;
    const studRadius = 5.5;

    for (let s = 0; s < studsPerBand; s++) {
      const sx = s * studSpacing + (studSpacing / 2) + ((b % 2) * 4);
      const sy = y + bandHeight / 2;

      // Stud cast shadow
      ctx.fillStyle = 'rgba(10, 10, 10, 0.7)';
      ctx.beginPath();
      ctx.arc(sx + 1.5, sy + 2, studRadius + 1, 0, Math.PI * 2);
      ctx.fill();

      // Stud iron body
      const studGrad = ctx.createRadialGradient(sx - 2, sy - 2, 1, sx, sy, studRadius);
      studGrad.addColorStop(0, '#8c857b');
      studGrad.addColorStop(0.6, '#464038');
      studGrad.addColorStop(1, '#201d1a');
      ctx.fillStyle = studGrad;
      ctx.beginPath();
      ctx.arc(sx, sy, studRadius, 0, Math.PI * 2);
      ctx.fill();

      // Specular highlight on dome
      ctx.fillStyle = 'rgba(220, 215, 205, 0.65)';
      ctx.beginPath();
      ctx.arc(sx - 2, sy - 2, 1.6, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Creates chevron / zigzag stone carved relief pattern for Mamluk minaret shafts
 */
export function createChevronReliefTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  ctx.fillStyle = '#cfc2ac';
  ctx.fillRect(0, 0, 512, 512);

  const rowCount = 16;
  const rowHeight = 512 / rowCount;
  const waveWidth = 32;

  ctx.lineWidth = 3.5;

  for (let r = 0; r < rowCount; r++) {
    const y = r * rowHeight;
    ctx.strokeStyle = 'rgba(80, 68, 54, 0.45)';
    ctx.beginPath();
    for (let x = 0; x <= 512; x += waveWidth) {
      if (x === 0) ctx.moveTo(x, y + rowHeight / 2);
      ctx.lineTo(x + waveWidth / 2, y + 2);
      ctx.lineTo(x + waveWidth, y + rowHeight - 2);
    }
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 250, 240, 0.4)';
    ctx.beginPath();
    for (let x = 0; x <= 512; x += waveWidth) {
      if (x === 0) ctx.moveTo(x, y + rowHeight / 2 + 2);
      ctx.lineTo(x + waveWidth / 2, y + 4);
      ctx.lineTo(x + waveWidth, y + rowHeight);
    }
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Creates radial contact shadow map
 */
export function createContactShadowTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  const grad = ctx.createRadialGradient(256, 256, 40, 256, 256, 240);
  grad.addColorStop(0, 'rgba(28, 25, 20, 0.85)');
  grad.addColorStop(0.4, 'rgba(28, 25, 20, 0.55)');
  grad.addColorStop(0.7, 'rgba(28, 25, 20, 0.2)');
  grad.addColorStop(1, 'rgba(28, 25, 20, 0)');

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 512, 512);

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

/**
 * Creates technical blueprint grid texture
 */
export function createBlueprintGridTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);

  ctx.fillStyle = '#F3EBDB';
  ctx.fillRect(0, 0, 512, 512);

  // Minor grid lines
  ctx.strokeStyle = 'rgba(28, 27, 25, 0.08)';
  ctx.lineWidth = 1;
  const step = 16;
  for (let p = 0; p <= 512; p += step) {
    ctx.beginPath();
    ctx.moveTo(p, 0);
    ctx.lineTo(p, 512);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, p);
    ctx.lineTo(512, p);
    ctx.stroke();
  }

  // Major grid lines
  ctx.strokeStyle = 'rgba(169, 138, 75, 0.25)';
  ctx.lineWidth = 1.5;
  for (let p = 0; p <= 512; p += step * 4) {
    ctx.beginPath();
    ctx.moveTo(p, 0);
    ctx.lineTo(p, 512);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, p);
    ctx.lineTo(512, p);
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(10, 10);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}
