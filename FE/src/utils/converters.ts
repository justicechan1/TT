import type { PlaceSummary, ItineraryPlace } from '@/types/api';

export function convertPlaceSummaryToItineraryPlace(summary: PlaceSummary): ItineraryPlace {
  return {
    name: summary.name,
    x_cord: summary.x_cord,
    y_cord: summary.y_cord,
    address: '',
    category: summary.category,
    open_time: '',
    close_time: '',
    convenience: '',
    image_urls: [],
    arrival_str: '00:00',
    departure_str: '00:00',
    service_time: 0,
  };
}
