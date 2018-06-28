import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import AppBar from '../components/AppBar';
import withRoot from './withRoot';
import ProfileButton from "../components/ProfileButton";

/**
 * The media item page
 */
const MediaPage = ({ mediaItem, classes }) => (
  <div className={ classes.page }>
    <AppBar position="fixed">
      <ProfileButton variant="flat" color="inherit" />
    </AppBar>
    <div className={ classes.body }>
      <section>
        <Grid container spacing={16} className={ classes.gridContainer }>
          <Grid item xs={12} className={ classes.playerWrapper } style={{paddingBottom:'56.25%'}}>
            <iframe src={mediaItem.player_url} className={ classes.player } width="100%" height="100%" frameBorder="0" allowFullScreen>
            </iframe>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subheading" gutterBottom>
              <a target='_blank' href={mediaItem.bestSource.url} download>
                Download media
              </a>
            </Typography>
          </Grid>
        </Grid>
      </section>
    </div>
  </div>
);

MediaPage.propTypes = {
  classes: PropTypes.object.isRequired,
};

/**
 * A higher-order component wrapper which passes the media item to its child. At the moment the
 * media item is simply resolved from global data. The wrapper also en-riches the item by selecting
 * the best download source to use.
 */
const withMediaItem = WrappedComponent => props => {

  const mediaItem = window.mediaItem;

  mediaItem.bestSource = null;

  for (let i = 0; i < mediaItem.sources.length; i++) {

    if (!mediaItem.bestSource) {
      mediaItem.bestSource = mediaItem.sources[i];
    }

    if (mediaItem.sources[i].type === "video/mp4") {
      if (mediaItem.bestSource.type !== mediaItem.sources[i].type) {
        mediaItem.bestSource = mediaItem.sources[i];
      }
      if (mediaItem.bestSource.height < mediaItem.sources[i].height) {
        mediaItem.bestSource = mediaItem.sources[i];
      }
    }
  }

  return (<WrappedComponent mediaItem={mediaItem} {...props} />);
};

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
  playerWrapper: {
    position:'relative',
    overflow:'hidden'
  },
  player: {
    position:'absolute'
  },
});
/* tslint:enable */

export default withMediaItem(withRoot(withStyles(styles)(MediaPage)));
