import React from 'react';

import Button from '@material-ui/core/Button';

import {withProfile} from "../providers/ProfileProvider";

/**
 * A button which allows sign in if the current user is anonymous or presents their username.
 */
const ProfileButton = ({ profile, ...otherProps }) => {
  if(!profile) { return null; }

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

export default withProfile(ProfileButton);
