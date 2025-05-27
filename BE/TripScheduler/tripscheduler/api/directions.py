import requests
import time
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def get_route_duration_and_path(
    route_entry: Dict
) -> Tuple[int, Optional[List[Dict]]]:
    """
    단일 응답(route_entry)에서 duration(분)과 path(좌표 리스트)를 추출
    """
    optimal = (
        route_entry.get("route", {}).get("traoptimal")
        or route_entry.get("route", {}).get("trafast")
        or []
    )
    if not optimal:
        return -1, None

    ms = optimal[0].get("summary", {}).get("duration", 0)
    minutes = int(round(ms / 60000))
    return minutes, optimal[0].get("path")

def fetch_route(
    start: str, goal: str, headers: Dict[str, str], timeout: float = 5
) -> Dict:
    """
    실제 API 호출을 수행하고 JSON 응답을 반환.
    실패 시 빈 dict 반환.
    """
    url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    params = {"start": start, "goal": goal, "lang": "ko"}

    #백앤드 api 테스트
    logger.debug("🚀 호출 URL: %s", url)
    logger.debug("📌 요청 파라미터: %s", params)
    logger.debug("🔑 요청 헤더: %s", headers)

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)

        logger.debug("📥 응답 코드: %s", resp.status_code)
        if resp.status_code == 401:
            logger.error("❌ 401 Unauthorized: 인증 실패! 키를 확인하세요.")
        elif resp.status_code != 200:
            logger.warning("⚠️ API 비정상 응답: %s - %s", resp.status_code, resp.text)

        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error("API 호출 실패 %s → %s: %s", start, goal, e)
        return {}

def update_direction_matrices(
    i: int,
    j: int,
    dur_mat: List[List[int]],
    path_mat: List[List[Optional[List[float]]]],
    entry: Dict
):
    """
    dur_mat, path_mat의 [i][j]와 [j][i]를 업데이트
    장소별 dur, path를 entry에서 추출
    """
    minutes, path = get_route_duration_and_path(entry)
    dur_mat[i][j] = dur_mat[j][i] = minutes
    path_mat[i][j] = path_mat[j][i] = path

def create_matrices(
    places: List[Dict],
    api_key_id: str,
    api_key: str,
    is_mock_enabled: bool = False,
    mock_api_response: Optional[List[List[Dict]]] = None
) -> Tuple[List[List[int]], List[List[Dict]], List[List[Optional[List[float]]]]]:
    length = len(places)
    duration_matrix = [[0]*length for _ in range(length)]
    raw_api_response = [[None]*length for _ in range(length)]
    path_matrix = [[None]*length for _ in range(length)]

    def process_pair(i: int, j: int, entry: Dict):
        raw_api_response[i][j] = raw_api_response[j][i] = entry
        update_direction_matrices(i, j, duration_matrix, path_matrix, entry)

    if is_mock_enabled:
        if mock_api_response is None:
            raise ValueError("mock=True일 때는 raw_matrix를 반드시 제공해야 합니다.")
        logger.info("Mock 모드: raw_matrix 기반 처리 시작")
        for i in range(length):
            for j in range(i+1, length):
                entry = mock_api_response[i][j] or {}
                process_pair(i, j, entry)
        return duration_matrix, mock_api_response, path_matrix

    headers = {
        "X-NCP-APIGW-API-KEY-ID": api_key_id,
        "X-NCP-APIGW-API-KEY": api_key
    }
    logger.info("API 모드: %d개 지점에 대해 처리 시작", length)
    for i in range(length):
        for j in range(i+1, length):
            start = f"{places[i]['x_cord']},{places[i]['y_cord']}"
            goal  = f"{places[j]['x_cord']},{places[j]['y_cord']}"
            entry = fetch_route(start, goal, headers)
            if not entry.get("route"):
                logger.warning("유효 경로 없음: %s → %s", start, goal)
            process_pair(i, j, entry)
            time.sleep(0.1) 

    logger.info("거리·경로 매트릭스 생성 완료")
    return duration_matrix, raw_api_response, path_matrix
