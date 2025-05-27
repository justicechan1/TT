export {}; 

declare global {
  interface Window {
    naver: typeof naver;
  }

  namespace naver.maps {
    class LatLng {
      constructor(lat: number, lng: number);
      lat(): number;
      lng(): number;
    }

    class Map {
      constructor(container: string | HTMLElement, options: any);
      setCenter(latlng: LatLng): void;
      setZoom(zoom: number): void;
      getBounds(): any;
      getProjection(): any;
      addListener(event: string, handler: Function): void;
    }

    class Marker {
      constructor(options: { position: LatLng; map: Map });
      setMap(map: Map | null): void;
    }

    class Size {
      constructor(width: number, height: number);
    }

    class Point {
      constructor(x: number, y: number);
    }

    class Polyline {
      constructor(options: any);
      setMap(map: Map | null): void;
    }

    const Event: {
      addListener: (target: any, eventName: string, handler: Function) => void;
    };
  }
}
