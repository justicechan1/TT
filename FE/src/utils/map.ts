import type { Viewport } from "@/types/common";

// map 객체에서 bounds를 가져오는 함수
export function getMapBounds(map: naver.maps.Map): Viewport {
    if (!map || typeof map.getBounds !== "function") {
        throw new Error("유효한 Naver Map 객체를 전달하세요.");
    }

    const bounds = map.getBounds();
    const ne = bounds.getNE();
    const sw = bounds.getSW();

    // Viewport 형식으로 변환해서 반환
    return {
        min_x: sw.lng(),
        min_y: sw.lat(),
        max_x: ne.lng(),
        max_y: ne.lat(),
    };
}