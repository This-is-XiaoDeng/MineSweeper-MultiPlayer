<script setup>
import { removeListener, bindListener, getName } from '@/scripts/server';
import MatchButton from '@/components/MatchButton.vue';
import { ref, onMounted, onUnmounted } from 'vue';
import ReadyButton from '@/components/ReadyButton.vue';
import router from '@/router';


const matchSuccessful = ref(false)
const players = ref([])
const isPlayerReady = ref(false)

let matchResultListenerID = null
onMounted(async () => {matchResultListenerID = bindListener("session.matched", (message) => {
  matchSuccessful.value = true;
  removeListener(matchResultListenerID);
  matchResultListenerID = null;
  players.value = [];
  message['players'].forEach(player => {
    players.value.push({ name: player, ready: false });
  });
})});
onUnmounted(() => {removeListener(matchResultListenerID)});

let getReadyListenerID = null
onMounted(async () => {getReadyListenerID = bindListener("player.ready", (message) => {
  removeListener(getReadyListenerID);
  getReadyListenerID = null;
  players.value.forEach(player => {
    if (player['name'] === message['name']) {
      player['ready'] = message['ready'];
    }
  });
  if (message['name'] === getName()) {
    isPlayerReady.value = message['ready'];
  }
})});
onUnmounted(() => {removeListener(getReadyListenerID)});

let counterListenerID = null
const counter = ref(null)
onMounted(async () => {counterListenerID = bindListener("counter.count", (message) => {
  counter.value = message['second'];
})});
onUnmounted(() => {removeListener(counterListenerID)});

let counterStartListenerID = null
onMounted(async () => {counterStartListenerID = bindListener("counter.start", (_) => {
  removeListener(counterStartListenerID);
  removeListener(counterListenerID);
  counterStartListenerID = null;
  counter.value = null;
  router.push("/game");
})});
onUnmounted(() => {removeListener(counterStartListenerID)});

</script>

<template>
  <MatchButton v-if="!matchSuccessful" />
  <div v-else>
    <h3>匹配成功！</h3>
    <p>玩家列表：</p>
    <ol>
      <li v-for="player in players" :key="player">
        {{ player['name'] }}
        <span class="badge bg-success" v-if="player['ready']">已准备</span>
      </li>
    </ol>
    <ReadyButton v-if="!isPlayerReady" />
    <p v-if="counter !== null">请等待... {{ counter }}</p>
  </div>
</template>
