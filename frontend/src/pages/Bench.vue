<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const route = useRoute()
const boxes = ref([])
const bid = ref(1)
const bleedMm = ref(0)
const overlap = ref(1.15)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    const [boxRes, s] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/settings')])
    boxes.value = boxRes.items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    bleedMm.value = Number(route.query.bleed ?? s.bleed_mm ?? 0)
    overlap.value = Number(route.query.overlap ?? s.overlap ?? 1.15)
    const qbox = Number(route.query.box)
    if (qbox && boxes.value.some((b) => b.id === qbox)) bid.value = qbox
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function go(save) {
  err.value = ''
  if (!(bleedMm.value >= 0)) {
    err.value = '出血不能为负'
    return
  }
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', {
          box_id: bid.value,
          bleed_mm: bleedMm.value,
          overlap: overlap.value,
          save: true,
        })
      : await getJSON(
          `/api/estimate?box_id=${bid.value}&bleed_mm=${bleedMm.value}&overlap=${overlap.value}`,
        )
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。出血按毫米登记，逐边外扩后再乘折边系数。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="field">
        出血 mm
        <input v-model.number="bleedMm" class="num" type="number" min="0" step="0.5" />
      </label>
      <label class="field">
        折边系数
        <input v-model.number="overlap" class="num" type="number" min="0" step="0.01" />
      </label>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        出血 {{ out.bleed_mm }} mm · 加边后三边 {{ out.eff_length }} × {{ out.eff_width }} ×
        {{ out.eff_height }} m · 口径 {{ out.formula }}
      </p>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m
      </p>
      <p v-if="out.run_id" class="stat-line">
        已写入用纸档 #{{ out.run_id }}，
        <router-link :to="`/history/${out.run_id}`">查看留档</router-link>
        （此后改默认出血不影响此单）
      </p>
      <BoxUnfold
        :l="out.eff_length"
        :w="out.eff_width"
        :h="out.eff_height"
        :bleed-mm="out.bleed_mm"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
