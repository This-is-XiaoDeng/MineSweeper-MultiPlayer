<script lang="js" setup>
import { ref } from 'vue'
import { startMatching } from "../scripts/server.js"

const match_started = ref(false)


async function match() {
    if ((await startMatching())['code'] !== 200) {
        alert("发起匹配时出现未知错误，请检查网页控制台！");
        return;
    }
    match_started.value = true;
}

</script>

<template>
    <div class="match-button" v-if="!match_started">
        <h3>已经准备好了！</h3>
        <button class="btn btn-primary" @click="match()">开始匹配</button>
    </div>
    <div class="match-button" v-else>
        <h3>正在匹配中...</h3>
    </div>
</template>

<style lang="css" scoped>
.match-button {
    align-items: center;
}
</style>