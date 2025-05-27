<template>
  <div class="time-section">
    <div class="section-title center-text">
      <p>어디서 여행을 시작하시나요? 숙소도 예약하셨다구요?</p>
      <h3>🏕️ 여행 장소와 숙소를 입력해주세요</h3>
    </div>

    <div class="section-content">
      <!-- 출발 정보 -->
      <div class="input-card">
        <h3>✈️ 출발 장소 및 시간 입력</h3>
        <p>{{ startDay }}</p>
        <form class="radio-group">
          <label><input v-model="startPlace" type="radio" value="제주국제공항" /> 제주국제공항</label>
          <label><input v-model="startPlace" type="radio" value="제주국제여객터미널" /> 제주국제여객터미널</label>
        </form>
        <input v-model="startTime" type="time" class="text-input" />
      </div>

      <!-- 도착 정보 -->
      <div class="input-card">
        <h3>✈️ 마지막 장소 및 시간 입력</h3>
        <p>{{ endDay }}</p>
        <form class="radio-group">
          <label><input v-model="endPlace" type="radio" value="제주국제공항" /> 제주국제공항</label>
          <label><input v-model="endPlace" type="radio" value="제주국제여객터미널" /> 제주국제여객터미널</label>
        </form>
        <input v-model="endTime" type="time" class="text-input" />
      </div>

      <!-- 숙소 정보 -->
      <!--
      <div class="input-card">
        <h3>🏠 숙소 정보 및 숙박 일차 입력</h3>
        <label class="label-title">✅ 숙소명</label>
        <input class="text-input" placeholder="숙박하실 숙소의 상호를 입력해주세요" v-model="accommodationName" />
        <label class="label-title">✅ 숙박 일차</label>
        <div class="radio-group day-select">
          <label v-for="n in tripday" :key="n">
            <input v-model="selectedDay" type="radio" :value="n" /> Day {{ n }}
          </label>
        </div>
      </div>
      -->
    </div>

    <footer class="section-footer flex-between">
      <button class="button-base button-prev" @click="emit('prev')">이전</button>
      <button class="button-base button-next" @click="handleConfirm">확인</button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { v4 as uuidv4 } from 'uuid'
import { useUserStore } from '@/store/userStore'
import { useItineraryStore } from '@/store/itineraryStore'
import { init as mockInitResponse } from '@/utils/mock'
import type { ItineraryPostBody } from '@/types/api'

const emit = defineEmits<{
  (e: 'prev'): void
}>()

const router = useRouter()
const userStore = useUserStore()
const itineraryStore = useItineraryStore()

const startDay = userStore.startDate
const endDay = userStore.endDate

const startPlace = ref(userStore.startPlace || '')
const startTime = ref(userStore.startTime || '')
const endPlace = ref(userStore.endPlace || '')
const endTime = ref(userStore.endTime || '')
const accommodationName = ref(userStore.accommodationName || '')
const selectedDay = ref<number | null>(userStore.accommodationDay ?? null)

function saveToUserStore() {
  userStore.setStartPlace(startPlace.value)
  userStore.setStartTime(startTime.value)
  userStore.setEndPlace(endPlace.value)
  userStore.setEndTime(endTime.value)
  userStore.setAccommodation(accommodationName.value, selectedDay.value)
}

async function handleConfirm() {
  saveToUserStore()

  const places_by_day: Record<string, { name: string }[]> = {}
  places_by_day["1"] = [{ name: userStore.startPlace }]

  if (userStore.accommodationDay && userStore.accommodationName) {
    const day = userStore.accommodationDay.toString()
    if (!places_by_day[day]) places_by_day[day] = []
    places_by_day[day].push({ name: userStore.accommodationName })
  }

  const lastDay = userStore.tripDays.toString()
  if (!places_by_day[lastDay]) places_by_day[lastDay] = []
  places_by_day[lastDay].push({ name: userStore.endPlace })

  const payload: ItineraryPostBody = {
    date: {
      user_id: uuidv4(),
      start_date: startDay,
      end_date: endDay,
      arrival_time: userStore.startTime,
      departure_time: userStore.endTime,
    },
    user: {
      start_time: "08:00",
      end_time: "20:00",
      travel_style: 'relaxing',
      meal_time_preferences: {
        breakfast: ['08:00'],
        lunch: ['12:00'],
        dinner: ['18:00'],
      },
    },
    places_by_day,
  }

  console.log('📦 전송될 payload:', payload)

  const res = mockInitResponse

  const internalItinerary = {
    places_by_day: Object.fromEntries(
      Object.entries(res.places_by_day).map(([day, places]) => [
        day,
        places.map(place => ({
          ...place,
          address: '',
          open_time: '00:00',
          close_time: '23:59',
          convenience: '',
          image_urls: [],
          arrival_str: '10:00',
          departure_str: '11:00',
          service_time: 60,
        }))
      ])
    )
  }

  const itineraryId = uuidv4()
  itineraryStore.addItinerary(itineraryId, internalItinerary)
  itineraryStore.selectItinerary(itineraryId)
  userStore.printDebug()

  if (res && res.places_by_day && Object.keys(res.places_by_day).length > 0) {
    console.log('✅ 일정 생성 성공 (mock):', res)
    itineraryStore.printDebug()
    router.push('/map')
  } else {
    console.error('❌ 일정 생성 실패 (mock):', res)
    alert('일정 생성에 실패했습니다. 입력값을 다시 확인해주세요.')
  }
}
</script>

<style scoped>
.time-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.section-title {
  padding: 1rem 0;
  flex-shrink: 0;
}

.section-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-card {
  padding: 1.5rem;
  border: 1px solid #e0f0f5;
  border-radius: 12px;
  background-color: #f9fcff;
  box-shadow: 0 2px 8px rgba(0, 188, 212, 0.15);
}

.radio-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1rem 0;
}

.day-select {
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
