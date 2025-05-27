// src/store/placeStore.ts
import { defineStore } from 'pinia'
import type { PlaceDetail } from '@/types/api'

export const usePlaceStore = defineStore('place', {
    state: () => ({
        details: {} as Record<string, PlaceDetail>,
    }),
    getters: {
        getDetail: state => (name: string) => state.details[name] ?? null,
    },
    actions: {
        addDetail(detail: PlaceDetail) {
            this.details[detail.name] = detail
        },
        removeDetail(name: string) {
            delete this.details[name]
        },
    },
})
