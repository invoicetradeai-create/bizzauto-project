import React from 'react';

interface UserAvatarProps {
  userName?: string;
  profilePictureUrl?: string;
}

const UserAvatar: React.FC<UserAvatarProps> = ({
  userName,
  profilePictureUrl,
}) => {
  const getInitials = (name?: string) => {
    if (!name) return '';
    const parts = name.split(' ');
    if (parts.length === 1) {
      return parts[0].charAt(0).toUpperCase();
    }
    return (
      parts[0].charAt(0) + parts[parts.length - 1].charAt(0)
    ).toUpperCase();
  };

  const initials = getInitials(userName);

  return (
    <div
      className={`relative flex items-center justify-center rounded-full bg-gray-700 text-white font-semibold shadow-md
                  w-8 h-8 text-xs sm:w-10 sm:h-10 sm:text-sm md:w-12 md:h-12 md:text-base
                  flex-shrink-0`} // flex-shrink-0 to prevent shrinking in flex containers
      aria-label={userName ? `${userName}'s avatar` : 'User avatar'}
    >
      {profilePictureUrl ? (
        <img
          src={profilePictureUrl}
          alt={userName ? `${userName}'s profile` : 'User profile'}
          className="w-full h-full rounded-full object-cover"
        />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
};

export default UserAvatar;
