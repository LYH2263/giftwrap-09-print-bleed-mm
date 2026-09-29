<script setup>
import { computed } from 'vue'

const props = defineProps({
  l: { type: Number, default: 0 },
  w: { type: Number, default: 0 },
  h: { type: Number, default: 0 },
  paperM2: { type: Number, default: null },
  bleedMm: { type: Number, default: 0 },
})

const VW = 280
const VH = 180
const PAD = 16

// 十字展开按传入（当次加边后）尺寸等比绘制：
// 顶/底 L×W，正/背 L×H，左右 W×H；bleedMm>0 时虚线内框标出未加边的原盒面。
const layout = computed(() => {
  const L = Math.max(Number(props.l) || 0, 1e-6)
  const W = Math.max(Number(props.w) || 0, 1e-6)
  const H = Math.max(Number(props.h) || 0, 1e-6)
  const totalW = 2 * (L + W)
  const totalH = H + 2 * W
  const s = Math.min((VW - 2 * PAD) / totalW, (VH - 2 * PAD) / totalH)
  const ox = (VW - totalW * s) / 2
  const oy = (VH - totalH * s) / 2
  const panels = [
    { x: W, y: 0, pw: L, ph: W, label: '顶', top: true },
    { x: 0, y: W, pw: W, ph: H, label: '侧' },
    { x: W, y: W, pw: L, ph: H, label: '正' },
    { x: W + L, y: W, pw: W, ph: H, label: '侧' },
    { x: W + L + W, y: W, pw: L, ph: H, label: '背' },
    { x: W, y: W + H, pw: L, ph: W, label: '底' },
  ].map((p) => ({
    ...p,
    sx: ox + p.x * s,
    sy: oy + p.y * s,
    sw: p.pw * s,
    sh: p.ph * s,
  }))
  const inset = (Math.max(Number(props.bleedMm) || 0, 0) / 1000) * s
  return { panels, inset, L, W, H }
})
</script>

<template>
  <div class="unfold">
    <p class="unfold-title">
      盒体展开示意{{ Number(bleedMm) > 0 ? `（含出血 +${bleedMm}mm/边）` : '' }}
    </p>
    <svg class="unfold-svg" :viewBox="`0 0 ${VW} ${VH}`" aria-hidden="true">
      <g v-for="(p, i) in layout.panels" :key="i">
        <rect
          class="panel"
          :class="{ top: p.top }"
          :x="p.sx"
          :y="p.sy"
          :width="p.sw"
          :height="p.sh"
          rx="2"
        />
        <rect
          v-if="layout.inset > 0.4"
          class="bleed-line"
          :x="p.sx + layout.inset"
          :y="p.sy + layout.inset"
          :width="Math.max(p.sw - 2 * layout.inset, 0)"
          :height="Math.max(p.sh - 2 * layout.inset, 0)"
        />
        <text :x="p.sx + p.sw / 2" :y="p.sy + p.sh / 2 + 3" text-anchor="middle">
          {{ p.label }}
        </text>
      </g>
    </svg>
    <p v-if="Number(bleedMm) > 0" class="stat-line">
      加边后尺寸 {{ layout.L.toFixed(3) }} × {{ layout.W.toFixed(3) }} × {{ layout.H.toFixed(3) }} m
      （每边外扩 {{ bleedMm }} mm 出血，虚线为原盒面）
    </p>
    <p v-else class="stat-line">
      外形 {{ layout.L.toFixed(2) }} × {{ layout.W.toFixed(2) }} × {{ layout.H.toFixed(2) }} m
    </p>
    <p v-if="paperM2 != null" class="stat-line">
      估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²（先加出血扩边，再乘折边系数）
    </p>
  </div>
</template>
