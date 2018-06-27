import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import AppBar from '../components/AppBar';
import { withProfile } from '../providers/ProfileProvider';
import withRoot from './withRoot';

/**
 * The media item page
 */
const MediaPage = ({ classes }) => (
  <div className={ classes.page }>
    <AppBar position="fixed">
      <ProfileButton variant="flat" color="inherit" />
    </AppBar>
    <div className={ classes.body }>
      <section>
        <Grid container spacing={16} className={ classes.gridContainer }>
          <Grid item xs={12} className={ classes.gridItem } style={{paddingBottom:'56.25%'}}>
            <iframe src={window.media_item.player_url} className={ classes.player } width="100%" height="100%" frameborder="0" allowfullscreen>
            </iframe>
          </Grid>
        </Grid>
      </section>
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

/* tslint:disable object-literal-sort-keys */
var styles = theme => ({
  page: {
    minHeight: '100vh',
    paddingTop: theme.spacing.unit * 8,
    width: '100%',
  },
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
  gridContainer: {
    maxWidth: 1260,
    margin: '0 auto'
  },
  gridItem: {
    position:'relative',
    overflow:'hidden'
  },
  player: {
    position:'absolute'
  },
});
/* tslint:enable */

export default withRoot(withStyles(styles)(MediaPage));
