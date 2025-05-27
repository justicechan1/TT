import { defineStore } from 'pinia'
import type { InternalItinerary } from '@/types/api'

export const useItineraryStore = defineStore('itinerary', {
    state: () => ({
        items: {} as Record<string, InternalItinerary>,
        currentId: null as string | null,
        selectedDay: 0,  // 선택된 날짜 상태 추가
    }),
    getters: {
        current(state): InternalItinerary | null {
            return state.currentId ? state.items[state.currentId] : null
        },
        totalPlaces(): number {
            return this.current
                ? Object.values(this.current.places_by_day).flat().length
                : 0
        },
    },
    actions: {
        addItinerary(id: string, itinerary: InternalItinerary) {
            this.items[id] = itinerary
            this.currentId = id
        },
        selectItinerary(id: string) {
            if (this.items[id]) this.currentId = id
        },
        removeItinerary(id: string) {
            delete this.items[id]
            if (this.currentId === id) this.currentId = null
        },
        reorderPlaces(day: number, newList: InternalItinerary['places_by_day'][number]) {
            const cur = this.current
            if (cur) cur.places_by_day[day] = newList
        },
        updatePlaceTime(
            day: number,
            name: string,
            arrival: string,
            departure: string,
            serviceTime: number
        ) {
            const cur = this.current
            const list = cur?.places_by_day[day]
            const place = list?.find(p => p.name === name)
            if (place) {
                place.arrival_str = arrival
                place.departure_str = departure
                place.service_time = serviceTime
            }
        },

        // selectedDay 업데이트
        updateSelectedDay(day: number) {
            this.selectedDay = day
        },

        getProcessedPlaces(day: number) {
            const cur = this.current;

            // `places_by_day`에 해당 day에 대한 데이터가 없으면 빈 배열 반환
            if (!cur || !cur.places_by_day[day]) {
                console.log(`Day ${day}에 대한 데이터가 없습니다.`);  // 로그 한 번만 출력
                return { day, places: [] };  // day와 places 배열을 포함하는 객체 반환
            }

            // 해당 day의 장소들을 가공하여 배열로 만들기
            const processedPlaces = cur.places_by_day[day].map((place, idx) => ({
                order: idx + 1,  // 순번
                name: place.name ?? '없음',
                category: place.category ?? '없음',
                arrival_str: place.arrival_str ?? '없음',
                departure_str: place.departure_str ?? '없음',
                service_time: place.service_time ?? '없음',
                x_cord: place.x_cord ?? '없음',
                y_cord: place.y_cord ?? '없음',
            }));

            console.log(`Day ${day}에 대한 가공된 데이터:`, processedPlaces);  // 가공된 데이터 확인
            return { day, places: processedPlaces };  // day와 places 배열을 포함하는 객체 반환
        },

        printDebug() {
            const all = Object.entries(this.items)

            if (all.length === 0) {
                console.log('⛔ 저장된 일정이 없습니다.')
                return
            }

            console.log('📦 저장된 전체 일정 요약 ------------------')

            all.forEach(([id, itinerary], index) => {
                const dayCount = Object.keys(itinerary.places_by_day).length
                const placeCount = Object.values(itinerary.places_by_day).flat().length
                const firstDay = Math.min(...Object.keys(itinerary.places_by_day).map(Number))
                const firstPlace = itinerary.places_by_day[firstDay]?.[0]?.name || '-'

                console.log(`\n🗂️ 일정 ${index + 1} (ID: ${id})`)
                console.log(`🗓️ 여행일 수: ${dayCount}일`)
                console.log(`📍 총 장소 수: ${placeCount}`)
                console.log(`🚩 첫 날 첫 장소: ${firstPlace}`)

                Object.entries(itinerary.places_by_day).forEach(([day, places]) => {
                    console.log(`\n--- Day ${day} (${places.length}개 장소) ---`)
                    const table = places.map((p, idx) => ({
                        순번: idx + 1,
                        이름: p.name ?? '없음',
                        카테고리: p.category ?? '없음',
                        주소: p.address ?? '없음',
                        '오픈 시간': p.open_time ?? '없음',
                        '마감 시간': p.close_time ?? '없음',
                        편의시설: p.convenience ?? '없음',
                        이미지수: Array.isArray(p.image_urls) ? p.image_urls.length : 0,
                        도착: p.arrival_str ?? '없음',
                        출발: p.departure_str ?? '없음',
                        '체류 시간(min)': p.service_time ?? '없음',
                        X좌표: p.x_cord ?? '없음',
                        Y좌표: p.y_cord ?? '없음',
                    }))
                    console.table(table)
                })
            })

            console.log('\n✅ 모든 일정 출력 완료.')
        }
    },
})
