// src/store/userStore.ts
import { defineStore } from 'pinia'
import type { UserPreferences } from '@/types/api'
import type { Hashtag, Viewport } from '@/types/common'

export const useUserStore = defineStore('user', {
    state: () => ({
        area: '' as string,
        startDate: '' as string,
        endDate: '' as string,
        tripDays: 0,
        startPlace: '' as string,
        startTime: '' as string,
        selectedDates: [] as string[],
        endPlace: '' as string,
        endTime: '' as string,
        accommodationName: '' as string,
        accommodationDay: null as number | null,
        tags: [] as Hashtag[],
        category: '' as string,
        viewport: null as Viewport | null,
        preferences: null as UserPreferences | null,
    }),
    getters: {
        hasArea: state => state.area !== '',
        hasTags: state => state.tags.length > 0,
        hasCategory: state => state.category !== '',
        hasPreferences: state => state.preferences !== null,
    },
    actions: {
        setArea(a: string) {
            this.area = a
        },
        setTags(t: Hashtag[]) {
            this.tags = t
        },
        setCategory(c: string) {
            this.category = c
        },
        setViewport(v: Viewport) {
            this.viewport = v
        },
        setPreferences(p: UserPreferences) {
            this.preferences = p
        },
        setStartDate(date: string) {
            this.startDate = date
        },
        setSelectedDates(dates: string[]) {
            this.selectedDates = dates
        },
        setEndDate(date: string) {
            this.endDate = date
        },
        setTripDays(days: number) {
            this.tripDays = days
        },
        setStartPlace(place: string) {
            this.startPlace = place
        },
        setStartTime(time: string) {
            this.startTime = time
        },
        setEndPlace(place: string) {
            this.endPlace = place
        },
        setEndTime(time: string) {
            this.endTime = time
        },
        setAccommodation(name: string, day: number | null) {
            this.accommodationName = name
            this.accommodationDay = day
        },
        resetAll() {
            this.area = ''
            this.tags = []
            this.category = ''
            this.viewport = null
            this.preferences = null
        },
        printDebug() {
            console.log('🧾 사용자 입력 요약 ------------------')
            console.table({
                지역: this.area,
                시작일: this.startDate,
                종료일: this.endDate,
                여행일수: this.tripDays,
                시작장소: this.startPlace,
                시작시간: this.startTime,
                종료장소: this.endPlace,
                종료시간: this.endTime,
                숙소명: this.accommodationName,
                숙박일차: this.accommodationDay,
                해시태그: this.tags.map(tag => tag.hashtag_name).join(', '),
                카테고리: this.category,
            })
            console.log('선호정보:', this.preferences)
            console.log('지도 뷰포트:', this.viewport)
            console.log('--------------------------------------')
        }
    },
})
