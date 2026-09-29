<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">写入时口径已固化：改默认出血不会重算此单，列表与本页同源同值。</p>
      <ul class="item-list">
        <li><span>礼盒</span><span class="meta">{{ run.box_name }}</span></li>
        <li><span>出血 bleed_mm</span><span class="meta">{{ run.bleed_mm }} mm</span></li>
        <li>
          <span>加边后三边</span>
          <span class="meta">{{ run.eff_length }} × {{ run.eff_width }} × {{ run.eff_height }} m</span>
        </li>
        <li><span>用纸 paper_m2</span><span class="meta">{{ run.paper_m2 }} m²</span></li>
        <li><span>折边系数</span><span class="meta">× {{ run.overlap }}</span></li>
        <li><span>口径</span><span class="meta">{{ run.result?.formula ?? '—' }}</span></li>
        <li><span>写入时间</span><span class="meta">{{ run.created_at }}</span></li>
      </ul>
      <BoxUnfold
        :l="run.eff_length ?? run.result?.eff_length ?? 0"
        :w="run.eff_width ?? run.result?.eff_width ?? 0"
        :h="run.eff_height ?? run.result?.eff_height ?? 0"
        :bleed-mm="run.bleed_mm ?? 0"
        :paper-m2="run.paper_m2 ?? run.result?.paper_m2 ?? null"
      />
      <div class="row" style="margin-top: 1.25rem">
        <router-link
          class="btn"
          :to="`/bench?box=${run.box_id}&bleed=${run.bleed_mm ?? 0}&overlap=${run.overlap}`"
        >
          按写入口径去算纸台复算
        </router-link>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
