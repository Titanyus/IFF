<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type User = { username:string, groups:string[], canManage:boolean, canTrash:boolean }
type Event = { action:string, from:string, to:string, actor:string, at:string }
type Case = { id:number, status:string, requestedOn:string, startedOn:string|null, endedOn:string|null, deleted:boolean, child:{id:number,name:string}, guardians:{id:number,name:string}[], events?:Event[] }
type Guardian = {id:number,name:string}
const user = ref<User|null>(null)
const csrf = ref('')
const ready = ref(false)
const busy = ref(false)
const error = ref('')
const loginName = ref('verwaltung@example.test')
const password = ref('')
const filter = ref('waiting')
const cases = ref<Case[]>([])
const guardians = ref<Guardian[]>([])
const openCase = ref<number|null>(null)
const editorCase = ref<number|null>(null)
const effectiveOn = ref(new Date().toISOString().slice(0,10))
const newOpen = ref(false)
const fresh = ref({firstName:'',lastName:'',guardianId:'',guardianName:'',requestedOn:new Date().toISOString().slice(0,10)})
const statusLabels:Record<string,string> = {waiting:'Wartend',active:'Aktiv',closed:'Abgeschlossen'}
const tabs = computed(()=>[...['waiting','active','closed','all'], ...(user.value?.canTrash?['trashed']:[])])
const tabLabels:Record<string,string> = {waiting:'Warteliste',active:'Aktiv',closed:'Abgeschlossen',all:'Alle Fälle',trashed:'Papierkorb'}

async function api(path:string, method='GET', data?:unknown) {
  const response = await fetch('/api/'+path, {
    method, credentials:'same-origin', cache:'no-store',
    headers:{'Content-Type':'application/json', ...(method==='GET'?{}:{'X-CSRFToken':csrf.value})},
    ...(data===undefined?{}:{body:JSON.stringify(data)})
  })
  const body = await response.json().catch(()=>({error:'Serverantwort ungültig'}))
  if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`)
  return body
}
async function refreshSession() {
  const session = await api('session/')
  user.value = session.user
  csrf.value = session.csrfToken
}
async function load() {
  const data = await api('cases/?status='+encodeURIComponent(filter.value))
  cases.value = data.cases
}
async function initial() {
  try { await refreshSession(); if(user.value) await load() }
  catch(e) { error.value = String(e) }
  finally { ready.value = true }
}
onMounted(initial)
async function doLogin() {
  try { error.value=''; busy.value=true; await api('login/','POST',{username:loginName.value,password:password.value}); password.value=''; await refreshSession(); await load() }
  catch(e) { error.value = (e as Error).message }
  finally { busy.value=false }
}
async function doLogout() {
  try { await api('logout/','POST'); user.value=null; cases.value=[]; await refreshSession() }
  catch(e) { error.value=(e as Error).message }
}
async function selectTab(tab:string) {
  try { filter.value=tab; openCase.value=null; await load() } catch(e){error.value=(e as Error).message}
}
async function detail(item:Case) {
  try {
    if (openCase.value===item.id) {openCase.value=null; return}
    const result = await api('cases/'+item.id+'/')
    Object.assign(item,result.case)
    openCase.value=item.id
  } catch(e){error.value=(e as Error).message}
}
async function startNew() {
  newOpen.value=!newOpen.value
  if (newOpen.value) {
    try { const data=await api('guardians/'); guardians.value=data.guardians } catch(e){error.value=(e as Error).message}
  }
}
async function createCase() {
  try {
    error.value='';busy.value=true
    await api('cases/','POST',{...fresh.value,guardianId:fresh.value.guardianId || null})
    fresh.value={firstName:'',lastName:'',guardianId:'',guardianName:'',requestedOn:new Date().toISOString().slice(0,10)}
    newOpen.value=false; filter.value='waiting'; await load()
  } catch(e) {error.value=(e as Error).message} finally {busy.value=false}
}
async function change(item:Case) {
  try {error.value='';busy.value=true; await api('cases/'+item.id+'/transition/','POST',{to:item.status==='waiting'?'active':'closed',effectiveOn:effectiveOn.value}); editorCase.value=null; await load()}
  catch(e){error.value=(e as Error).message}finally{busy.value=false}
}
async function setTrash(item:Case, restore=false) {
  if(!restore && !confirm('Diesen Fall in den Papierkorb verschieben?'))return
  try{error.value='';await api('cases/'+item.id+'/'+(restore?'restore':'trash')+'/','POST');openCase.value=null;await load()}
  catch(e){error.value=(e as Error).message}
}
</script>

<template>
  <div class="shell">
    <header class="topbar"><div class="brand"><span class="brandmark">✳</span><div><strong>Frühförderung</strong><small>Verwaltung · Django + Vue</small></div></div><div v-if="user" class="user"><span>{{user.username}}</span><button class="subtle" @click="doLogout">Abmelden</button></div></header>
    <main v-if="!ready" class="main">Lade Anwendung ...</main>
    <main v-else-if="!user" class="login">
      <div class="panel"><p class="eyebrow">TECHNISCHER PROTOTYP</p><h1>Willkommen zurück</h1><p class="muted">Mit einem fiktiven Demo-Konto anmelden.</p>
      <form @submit.prevent="doLogin"><label>Benutzername<input type="text" v-model="loginName" autocomplete="username" required></label><label>Passwort<input type="password" v-model="password" autocomplete="current-password" required></label><button class="primary" :disabled="busy">Anmelden</button></form>
      <p class="hint">Demo: verwaltung@example.test · DemoPass-2026!</p></div>
    </main>
    <main v-else class="main">
      <div class="heading"><div><p class="eyebrow">KINDER- UND FÖRDERFALLVERWALTUNG</p><h1>Fallübersicht</h1><p class="muted">Eine Datenbasis, verschiedene berechtigte Ansichten.</p></div><button v-if="user.canManage" class="primary desktop-only" @click="startNew">{{newOpen?'Schließen':'+ Neuen Fall anlegen'}}</button></div>
      <div v-if="error" class="alert" role="alert">{{error}} <button class="close" @click="error=''">×</button></div>
      <section v-if="newOpen && user.canManage" class="panel desktop-only"><h2>Neues Kind mit wartendem Förderfall</h2><form @submit.prevent="createCase" class="form-grid"><label>Vorname<input required maxlength="100" v-model.trim="fresh.firstName"></label><label>Nachname<input required maxlength="100" v-model.trim="fresh.lastName"></label><label>Anmeldedatum<input required type="date" v-model="fresh.requestedOn"></label><label>Vorhandene Bezugsperson (optional)<select v-model="fresh.guardianId"><option value="">– Neue Person –</option><option v-for="g in guardians" :key="g.id" :value="String(g.id)">{{g.name}}</option></select></label><label v-if="!fresh.guardianId">Name der Bezugsperson<input required maxlength="200" v-model.trim="fresh.guardianName"></label><button class="primary" type="submit" :disabled="busy">Anlegen</button></form><p class="hint">Demo-Funktion. Keine echten personenbezogenen Daten verwenden.</p></section>
      <nav class="tabs" aria-label="Fallfilter"><button v-for="tab in tabs" :key="tab" :class="{selected:filter===tab}" @click="selectTab(tab)">{{tabLabels[tab]}}</button></nav>
      <section class="panel list-panel"><div class="list-heading"><h2>{{tabLabels[filter]}}</h2><span class="count">{{cases.length}} Fälle</span></div>
      <p v-if="!cases.length" class="empty">In dieser Ansicht gibt es keine Fälle.</p>
      <div v-for="item in cases" :key="item.id" class="case-item">
        <div class="case-summary"><div><span class="pill" :class="item.status">{{statusLabels[item.status]}}</span><h3>{{item.child.name}}</h3><p class="muted">Anmeldung: {{item.requestedOn}} · {{item.guardians.map(g=>g.name).join(', ')}}</p></div><button class="subtle" @click="detail(item)">{{openCase===item.id?'Schließen':'Details'}}</button></div>
        <div v-if="openCase===item.id" class="details"><p>Beginn: <strong>{{item.startedOn||'–'}}</strong> · Ende: <strong>{{item.endedOn||'–'}}</strong></p>
          <h4>Änderungshistorie</h4><p v-for="event in item.events||[]" :key="event.at" class="event">{{event.at.slice(0,16).replace('T',' ')}} · {{event.actor}} · {{event.action}} <span v-if="event.to">({{event.from||'–'}} → {{event.to}})</span></p>
          <div class="actions desktop-only"><button v-if="user.canManage && !item.deleted && item.status!=='closed'" class="subtle" @click="editorCase=editorCase===item.id?null:item.id">{{item.status==='waiting'?'Förderung starten':'Förderung abschließen'}}</button><button v-if="user.canTrash && !item.deleted" class="danger" @click="setTrash(item)">Papierkorb</button><button v-if="user.canTrash && item.deleted" class="subtle" @click="setTrash(item,true)">Wiederherstellen</button></div>
          <form v-if="editorCase===item.id" class="transition-form desktop-only" @submit.prevent="change(item)"><label>{{item.status==='waiting'?'Förderbeginn':'Förderende'}}<input type="date" v-model="effectiveOn" required></label><button class="primary" :disabled="busy">Bestätigen</button></form>
        </div>
      </div>
      </section>
      <p class="footnote">PoC · fiktive Daten · HTTP nur über localhost · kein Produktivbetrieb</p>
    </main>
  </div>
</template>
