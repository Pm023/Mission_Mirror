/**
 * Mission Mirror — Starfield Background Canvas
 * Subtle, high-performance ambient deep space starfield with gentle parallax.
 */
const Starfield = {
  canvas: null,
  ctx: null,
  stars: [],
  starCount: 95,
  animId: null,

  init() {
    this.canvas = document.getElementById('space-starfield-canvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.resize();
    this.createStars();
    this.animate();

    window.addEventListener('resize', () => this.resize());
  },

  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  },

  createStars() {
    this.stars = [];
    const w = this.canvas.width || window.innerWidth;
    const h = this.canvas.height || window.innerHeight;
    for (let i = 0; i < this.starCount; i++) {
      this.stars.push({
        x: Math.random() * w,
        y: Math.random() * h,
        radius: Math.random() * 1.4 + 0.3,
        alpha: Math.random() * 0.7 + 0.2,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinkleDir: Math.random() > 0.5 ? 1 : -1,
        vy: Math.random() * 0.12 + 0.03
      });
    }
  },

  animate() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.clearRect(0, 0, w, h);

    for (let i = 0; i < this.stars.length; i++) {
      const s = this.stars[i];

      // Twinkle
      s.alpha += s.twinkleSpeed * s.twinkleDir;
      if (s.alpha > 0.9) { s.alpha = 0.9; s.twinkleDir = -1; }
      if (s.alpha < 0.2) { s.alpha = 0.2; s.twinkleDir = 1; }

      // Drift
      s.y -= s.vy;
      if (s.y < 0) {
        s.y = h;
        s.x = Math.random() * w;
      }

      ctx.beginPath();
      ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(186, 230, 253, ${s.alpha})`;
      ctx.fill();
    }

    this.animId = requestAnimationFrame(() => this.animate());
  }
};

