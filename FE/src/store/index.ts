import { createPinia } from 'pinia';
import { useUserStore } from '@/store/userStore';
import { useItineraryStore } from '@/store/itineraryStore';
import { usePlaceStore } from '@/store/placeStore';

export const pinia = createPinia();

export const useRootStore = () => ({
  user: useUserStore(),
  itin: useItineraryStore(),
  place: usePlaceStore(),
});
