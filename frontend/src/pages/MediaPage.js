import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';

import AppBar from '../components/AppBar';
import { withProfile } from '../providers/ProfileProvider';
import withRoot from './withRoot';

/**
 * The index page for the FIXME
 */
const MediaPage = ({ classes }) => (
  <div className={ classes.page }>
    <AppBar position="fixed">
      <ProfileButton variant="flat" color="inherit" />
    </AppBar>

    <div className={ classes.body }>
      Some Media
    </div>
  </div>
);

MediaPage.propTypes = {
  classes: PropTypes.object.isRequired,
};

/** A button which allows sign in if the current user is anonymous or presents their username. */
// FIXME move this
const ProfileButton = withProfile(({ profile, ...otherProps }) => {
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
});

const styles = theme => ({
  body: {
    margin: [[0, 'auto']],
    paddingLeft: theme.spacing.unit * 2,
    paddingRight: theme.spacing.unit * 2,
    paddingTop: theme.spacing.unit * 3,

    [theme.breakpoints.up('sm')]: {
      paddingLeft: theme.spacing.unit * 3,
      paddingRight: theme.spacing.unit * 3,
    },
  },
  page: {
    minHeight: '100vh',
    paddingTop: theme.spacing.unit * 8,
    width: '100%',
  }
});

export default withRoot(withStyles(styles)(MediaPage));
