import React, { Component } from 'react';
import PropTypes from 'prop-types';

import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import AppBar from '../components/AppBar';
import withRoot from './withRoot';
import ProfileButton from "../components/ProfileButton";

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
            <iframe src={window.media_item.player_url} className={ classes.player } width="100%" height="100%" frameBorder="0" allowFullScreen>
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
