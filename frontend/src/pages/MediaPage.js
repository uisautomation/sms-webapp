import React, { Component } from 'react';
import PropTypes from 'prop-types';

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
        <Typography component='div' paragraph style={{padding:'0px 200px',}}>
          <div style={{position:'relative', paddingBottom:'56.25%', overflow:'hidden'}}>
            <iframe src={window.media_item.player_url} width="100%" height="100%" frameborder="0" allowfullscreen style={{position:'absolute'}}>
            </iframe>
          </div>
        </Typography>
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
  videoWrapper: {
    backgroundColor: 'black',
    position: 'absolute',
    left: 0, top: 0, right: 0, bottom: 0,
    display: 'flex', flexDirection: 'column', justifyContent: 'center'
  },
  page: {
    minHeight: '100vh',
    paddingTop: theme.spacing.unit * 8,
    width: '100%',
  },

});
/* tslint:enable */

export default withRoot(withStyles(styles)(MediaPage));
