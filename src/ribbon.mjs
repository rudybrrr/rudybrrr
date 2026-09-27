// Renders the portfolio's chrome ribbon (rudhresh.com's hero shader) as a seamless loop of
// transparent WebP frames in src/ribbon/, which build.py embeds in the hero.
// Run: npm i && node src/ribbon.mjs   (needs a Chromium; set CHROME to its binary)
import { mkdirSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import puppeteer from 'puppeteer-core';

const FRAMES = 60;
const W = 560;
const H = 600;
const out = new URL('./ribbon/', import.meta.url).pathname;
const chrome = process.env.CHROME ?? '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';

// Same band, studio and tint as the site; time is replaced by a loop phase uS in [0, 1)
// so every motion is a sine of it and frame 60 lands back on frame 0.
const fragment = `
precision highp float;
uniform vec2 uRes;
uniform float uS;
const vec3 uTint = vec3(0.27, 0.35, 0.91);
const float TAU = 6.2831853;

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

float map(vec3 p) {
  float a = uS * TAU;
  p.xz *= rot(1.15 + 0.32 * sin(a));
  p.yz *= rot(0.42 + 0.10 * cos(a));
  p.xy *= rot(0.55 + 0.14 * sin(a + 1.2));
  vec2 q = vec2(length(p.xy) - 0.62, p.z);
  q *= rot(atan(p.y, p.x) * 1.5 + 0.9 + 0.55 * sin(a + 0.6));
  q.x -= clamp(q.x, -0.26, 0.26);
  return length(q) - 0.032;
}

vec3 normal(vec3 p) {
  const vec2 e = vec2(1.0, -1.0) * 0.0015;
  return normalize(e.xyy * map(p + e.xyy) + e.yyx * map(p + e.yyx) + e.yxy * map(p + e.yxy) + e.xxx * map(p + e.xxx));
}

vec3 env(vec3 r) {
  vec3 col = mix(vec3(0.03, 0.032, 0.036), vec3(0.72, 0.74, 0.77), smoothstep(-0.3, 0.75, r.y));
  col += vec3(1.25) * exp(-abs(r.y - 0.05) * 12.0);
  col += vec3(1.3) * smoothstep(0.82, 1.0, sin(r.x * 4.0 + 1.3) * 0.5 + 0.5) * smoothstep(0.1, 0.5, r.y);
  col += uTint * 1.25 * smoothstep(0.3, 1.0, -r.x * 0.8 + r.y * 0.3);
  col += uTint * 0.55 * smoothstep(0.4, 1.0, r.x * 0.7 - r.y * 0.6);
  return col;
}

void main() {
  float scale = min(uRes.x, uRes.y) * 1.22;
  vec2 uv = (gl_FragCoord.xy - 0.5 * uRes) / scale;
  vec3 ro = vec3(0.0, 0.0, 4.9);
  vec3 rd = normalize(vec3(uv, -1.75));
  float t = 0.0, dmin = 1e3, tmin = 0.0;
  for (int i = 0; i < 220; i++) {
    float d = map(ro + rd * t);
    if (d < dmin) { dmin = d; tmin = t; }
    if (d < 0.0004 * t || t > 7.0) break;
    t += d * 0.5;
  }
  float px = 2.0 / scale * tmin / 1.75;
  float alpha = 1.0 - smoothstep(0.0004 * tmin, px * 1.5, dmin);
  if (alpha <= 0.0) { gl_FragColor = vec4(0.0); return; }
  vec3 p = ro + rd * tmin;
  vec3 n = normal(p);
  vec3 r = reflect(rd, n);
  float fres = pow(1.0 - max(dot(n, -rd), 0.0), 4.0);
  vec3 col = env(r) * (0.5 + 0.5 * fres) + fres * (0.12 + uTint * 0.35);
  col = col / (1.0 + col * 0.3);
  gl_FragColor = vec4(col, alpha); // straight alpha: the PNG is not premultiplied
}`;

const page = `<canvas width=${W} height=${H}></canvas><script>
const c = document.querySelector('canvas');
const gl = c.getContext('webgl', { premultipliedAlpha: false, preserveDrawingBuffer: true, antialias: false });
const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); return x; };
const pr = gl.createProgram();
gl.attachShader(pr, sh(gl.VERTEX_SHADER, 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}'));
gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, ${JSON.stringify(fragment)}));
gl.linkProgram(pr); gl.useProgram(pr);
gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,3,-1,-1,3]), gl.STATIC_DRAW);
gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
gl.uniform2f(gl.getUniformLocation(pr, 'uRes'), ${W}, ${H});
const draw = s => { gl.uniform1f(gl.getUniformLocation(pr, 'uS'), s); gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT); gl.drawArrays(gl.TRIANGLES, 0, 3); };
// Union of every frame's opaque pixels, so frames can be cropped to one shared box.
window.bounds = n => {
  const px = new Uint8Array(${W} * ${H} * 4);
  let x0 = ${W}, y0 = ${H}, x1 = 0, y1 = 0;
  for (let i = 0; i < n; i++) {
    draw(i / n); gl.readPixels(0, 0, ${W}, ${H}, gl.RGBA, gl.UNSIGNED_BYTE, px);
    for (let y = 0; y < ${H}; y++) for (let x = 0; x < ${W}; x++) if (px[(y * ${W} + x) * 4 + 3] > 2) {
      x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, ${H} - 1 - y); y1 = Math.max(y1, ${H} - 1 - y);
    }
  }
  return { x: Math.max(0, x0 - 2), y: Math.max(0, y0 - 2), w: Math.min(${W}, x1 + 3) - Math.max(0, x0 - 2), h: Math.min(${H}, y1 + 3) - Math.max(0, y0 - 2) };
};
const out = document.createElement('canvas');
window.frame = (s, b) => { draw(s); out.width = b.w; out.height = b.h; out.getContext('2d').drawImage(c, b.x, b.y, b.w, b.h, 0, 0, b.w, b.h); return out.toDataURL('image/png'); };
</script>`;

mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({ executablePath: chrome, headless: 'new', args: ['--use-gl=angle', '--ignore-gpu-blocklist'] });
const tab = await browser.newPage();
await tab.setContent(page);
const box = await tab.evaluate(n => window.bounds(n), FRAMES);
writeFileSync(`${out}box.json`, JSON.stringify({ ...box, full: [W, H] }));
for (let i = 0; i < FRAMES; i++) {
  const png = await tab.evaluate((s, b) => window.frame(s, b), i / FRAMES, box);
  const name = `${out}${String(i).padStart(2, '0')}`;
  writeFileSync(`${name}.png`, Buffer.from(png.split(',')[1], 'base64'));
  execFileSync('cwebp', ['-quiet', '-q', '68', '-alpha_q', '70', '-m', '6', `${name}.png`, '-o', `${name}.webp`]);
  execFileSync('rm', [`${name}.png`]);
}
await browser.close();
