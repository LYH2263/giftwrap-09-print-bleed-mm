<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const bleedMm = ref(0)
const err = ref('')

onMounted(async () => {
  try {
    const [b, s] = await Promise.all([getJSON(`/api/boxes/${props.id}`), getJSON('/api/settings')])
    box.value = b
    bleedMm.value = Number(s.bleed_mm ?? 0)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

const bleedOk = computed(() => Number(bleedMm.value) >= 0)
const eff = computed(() => {
  if (!box.value) return { l: 0, w: 0, h: 0 }
  const b = bleedOk.value ? Number(bleedMm.value) / 1000 : 0
  return {
    l: box.value.length + 2 * b,
    w: box.value.width + 2 * b,
    h: box.value.height + 2 * b,
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="box">
      <h1>{{ box.name }}</h1>
      <p class="lede">
        {{ box.length }} × {{ box.width }} × {{ box.height }} m
        <span class="pill" :class="{ warn: box.data_quality === 'dirty' }">
          {{ box.data_quality === 'dirty' ? '脏数据' : '可用' }}
        </span>
      </p>
      <p v-if="box.data_quality === 'dirty'" class="bad">{{ box.note }}</p>
      <div class="row">
        <label class="field">
          出血 mm
          <input v-model.number="bleedMm" class="num" type="number" min="0" step="0.5" />
        </label>
        <span v-if="bleedOk && Number(bleedMm) > 0" class="meta">
          加边后 {{ eff.l.toFixed(3) }} × {{ eff.w.toFixed(3) }} × {{ eff.h.toFixed(3) }} m
        </span>
      </div>
      <p v-if="!bleedOk" class="bad">出血不能为负</p>
      <BoxUnfold :l="eff.l" :w="eff.w" :h="eff.h" :bleed-mm="bleedOk ? Number(bleedMm) : 0" />
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" :to="`/bench?box=${box.id}&bleed=${bleedOk ? bleedMm : 0}`">
          用此盒去算纸
        </router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
  </div>
</template>
