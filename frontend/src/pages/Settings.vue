<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const s = ref({})
const bleed = ref(0)
const err = ref('')
const msg = ref('')

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
    bleed.value = Number(s.value.bleed_mm ?? 0)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function saveBleed() {
  err.value = ''
  msg.value = ''
  if (!(bleed.value >= 0)) {
    err.value = '出血不能为负'
    return
  }
  try {
    s.value = await putJSON('/api/settings', { key: 'bleed_mm', value: bleed.value })
    msg.value = '已保存默认出血；只影响新估算，已写入的用纸档保持原值。'
  } catch (e) {
    err.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">折边系数只读；默认出血可改，仅作用于新估算，不回溯已写入的用纸档。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <ul class="item-list">
      <li>
        <span>折边系数 overlap</span>
        <span class="meta">{{ s.overlap }}</span>
      </li>
      <li>
        <span>默认出血 bleed_mm</span>
        <span class="meta">
          <input v-model.number="bleed" class="num" type="number" min="0" step="0.5" />
          <button style="margin-left: 0.6rem" @click="saveBleed">保存</button>
        </span>
      </li>
    </ul>
    <p v-if="msg" class="stat-line">{{ msg }}</p>
  </div>
</template>
