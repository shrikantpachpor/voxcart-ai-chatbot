import React, { useEffect } from "react";
import { chatApi } from "../../services/api";

interface ProfileData {
  phone_number?: string;
  user?: {
    email: string;
  };
  saved_addresses?: Array<{
    street?: string;
    city?: string;
  }>;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = React.useState<ProfileData | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const { data } = await chatApi.getProfile();
        setProfile(data);
      } catch (error) {
        // Error loading profile
      }
    };
    loadProfile();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Your Profile</h2>
      {profile && (
        <div className="space-y-4">
          <div className="p-4 bg-white rounded shadow">
            <h3 className="font-bold mb-2">Contact Info</h3>
            <p>Phone: {profile.phone_number || "Not provided"}</p>
            <p>Email: {profile.user?.email || "Not available"}</p>
          </div>
          <div className="p-4 bg-white rounded shadow">
            <h3 className="font-bold mb-2">Saved Addresses</h3>
            {profile.saved_addresses?.map((addr, index) => (
              <div key={index} className="border-b py-2">
                {addr.street}, {addr.city}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;