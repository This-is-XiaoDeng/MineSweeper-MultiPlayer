<script setup>
import { ref, onMounted } from 'vue'
import { getServerStatus, createWebSocketConnection, setName } from '../scripts/server.js';
import router from '@/router/index.js';

const stat_text = ref('等待中 ...')
const ready_to_join = ref(false)
const name = ref(null)

function updateServerStatus() {
  return new Promise(async () => {
    try {
      const data = await getServerStatus();
      if (data['code'] === 200) {
        stat_text.value = `成功与服务器通信，在线人数: ${data['data']['online']}`;
        ready_to_join.value = true;
      } else {
        stat_text.value = '服务器异常';
      }
    } catch (error) {
      stat_text.value = String(error)
    }
  });
}
onMounted(() => {
  updateServerStatus();
  ready_to_join.value = false;
  name.value = null;
});

async function join(name) {
  if (!name) {
    alert("请输入你的名字！");
    return;
  }
  await createWebSocketConnection();
  if ((await setName(name))["code"] === 200) {
    router.push("/prepare");
    return;
  }
  alert("设置名字失败，可能是和在线玩家重复！");
}

</script>

<template>
  <span class="h1">Mine Sweeper</span>
  <span class="badge">
    <span class="bg-success">MultiPlayer</span>
    <span class="bg-secondary">V1</span>
  </span>
  <div style="height: 15px;"></div>
  <div style="text-align: center;">
    <div class="card shadown">
      <div class="card-body">
        <div v-if="ready_to_join">
          <p>输入你的名字，然后点击“加入游戏”：</p>
          <div class="input-group mb-3">
            <input v-model="name" type="text" class="form-control" aria-describedby="button-addon2" id="name">
            <button class="btn btn-primary" type="button" @click="join(name)" id="button-addon2">加入游戏</button>
          </div>
        </div>
        <p>{{ stat_text }} <a v-if="!ready_to_join" href="javascript:location.reload()">刷新</a></p>
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped></style>
