<script setup>
import router from '@/router';
import { removeListener, bindListener, getGameMap, getName, mineBlock } from '@/scripts/server';
import { ref, onMounted, onUnmounted } from 'vue';

const selfMap = ref([])
const otherMap = ref([])

onMounted(async () => {
  const gameMap = (await getGameMap())["data"]
  selfMap.value = gameMap['my_map']
  otherMap.value = gameMap['other_map']
});

let otherMapListenerID = null
onMounted(async () => {otherMapListenerID = bindListener("map.updated", (message) => {
  if (message['name'] !== getName()) {
    otherMap.value = message['game_map']
  }
})});
onUnmounted(() => {removeListener(otherMapListenerID)});

async function requestMineBlock(y, x) {
  selfMap.value = (await mineBlock([x, y]))["data"]["game_map"]
}

const winner = ref(null)

let playerWinListener = null
onMounted(async () => {playerWinListener = bindListener("player.win", (message) => {
  removeListener(playerWinListener)
  playerWinListener = null
  winner.value = message['name']
})});
onUnmounted(() => {removeListener(playerWinListener)});

</script>

<template>
    <div class="row">
      <div class="col-6">
        <h1>Your Map</h1>
        <table>
          <tr v-for="(row, i) in selfMap" :key="i">
            <td v-for="(col, j) in row" :key="j">
              <div v-if="col === -1" class="white-block block block-my" @click="requestMineBlock(i, j)"></div>
              <div v-else-if="col === 0" class="block block-my"></div>
              <div v-else-if="col === 10" class="block boom-block block-my">💣</div>
              <div class="block block-my" v-else>{{ col }}</div>
            </td>
          </tr>
        </table>
      </div>
      <div class="col-6">
        <h1>Enemy Map</h1>

        <table>
          <tr v-for="(row, i) in otherMap" :key="i">
            <td v-for="(col, j) in row" :key="j">
              <div v-if="col === -1" class="white-block block block-enemy"></div>
              <div v-else-if="col === 0" class="block block-enemy"></div>
              <div v-else-if="col === 10" class="block boom-block block-enemy">💣</div>

              <div class="block block-enemy" v-else>{{ col }}</div>
            </td>
          </tr>
        </table>
      </div>
    </div>
    <p v-if="winner">赢家：{{ winner }}</p>
    <button v-if="winner" class="btn btn-primary" @click="router.push('/prepare')">返回</button>
</template>

<style lang="css" scoped>

.block-my:hover {
  border: 2px solid #000;
}

.white-block.block-enemy {
  background-color: #AAA;
}

.white-block.block-my {
  background-color: #999;
}

.boom-block {
  background-color: #F00;
}

.block {
  margin: 1px;
  width: 30px;
  height: 30px;
  text-align: center;  
}


</style>
