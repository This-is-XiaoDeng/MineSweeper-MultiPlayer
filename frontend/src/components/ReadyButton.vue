<script lang="js" setup>
import { getReady } from "../scripts/server.js"

async function ready() {
    if ((await getReady(true))['code'] !== 200) {
        alert("出现未知错误，请检查网页控制台！");
        return;
    }
}
</script>

<template>
    <button class="btn btn-primary" @click="ready()">确认准备</button>
</template>
