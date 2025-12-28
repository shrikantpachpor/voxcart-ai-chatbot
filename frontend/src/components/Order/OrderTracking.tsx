import React, { useEffect } from "react";
import { chatApi } from "../../services/api";

interface TrackingData {
  geolocation_history?: Array<{ lat: number; lng: number }>;
  tracking_numbers?: string[];
}

const OrderTracking: React.FC<{ orderId: string }> = ({ orderId }) => {
  const [trackingData, setTrackingData] = React.useState<TrackingData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data } = await chatApi.getOrderStatus(orderId);
        setTrackingData(data);
      } catch (error) {
        // Error fetching order status
      }
    };
    fetchData();
  }, [orderId]);

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-xl font-bold mb-4">Order #{orderId}</h3>
      {trackingData?.geolocation_history && (
        <div className="h-64 bg-gray-100 rounded-lg mb-4">
          {/* Map integration would go here */}
          <div className="p-4 text-gray-500">
            Map component placeholder
            {trackingData.geolocation_history.map((loc, index) => (
              <div key={index}>
                Lat: {loc.lat}, Lng: {loc.lng}
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="space-y-2">
        {trackingData?.tracking_numbers?.map((num, index) => (
          <div key={index} className="flex items-center justify-between">
            <span>{num}</span>
            <button 
              onClick={() => navigator.clipboard.writeText(num)}
              className="p-2 hover:bg-gray-100 rounded"
            >
              📋
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderTracking;