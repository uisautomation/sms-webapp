import React from 'react';

import Button from '@material-ui/core/Button';

import {withProfile} from "../providers/ProfileProvider";

/**
 * A button which allows sign in if the current user is anonymous or presents their username. Properties
 * appropriate to the material-ui Button component (apart from ``component`` and ``href``) can be used.
 *
 * In addition to the basic component, ``ProfileButtonWithProfile`` is exported which is ``ProfileButton``
 * already wired to the profile provider.
 */
const ProfileButton = ({ profile, ...otherProps }) => {
  if(!profile) {
    return (
      <Button {...otherProps}>Sign in</Button>
    );
  }

  if(profile.is_anonymous) {
    return (
      <Button component='a' href={profile.urls.login} {...otherProps}>
        Sign in
      </Button>
    );
  }

  return (
    <Button {...otherProps}>
      { profile.username }
    </Button>
  );
};

const ProfileButtonWithProfile = withProfile(ProfileButton);

export { ProfileButtonWithProfile };
export default ProfileButton;
