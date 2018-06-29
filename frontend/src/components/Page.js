import React from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';

import withRoot from "../pages/withRoot";
import AppBar from "./AppBar";
import {ProfileButtonWithProfile} from "./ProfileButton";
import MotdBanner from "./MotdBanner";

/**
 * A top level component that wraps all pages to give then elements common to all page, the ``AppBar``
 * etc.
 */
const Page = (
  { defaultSearch, classes, children }
) => (
      <div className={ classes.page }>
        <AppBar position="fixed" defaultSearch={defaultSearch}>
          <ProfileButtonWithProfile variant="flat" color="inherit" />
        </AppBar>

        <div className={classes.body}>
          <MotdBanner />
          { children }
        </div>
      </div>
);

Page.propTypes = {
  /** @ignore */
  classes: PropTypes.object.isRequired,

  /** Default search text to populate the search form with. */
  defaultSearch: PropTypes.string,
};

const styles = theme => ({
  page: {
    minHeight: '100vh',
    paddingTop: theme.spacing.unit * 8,
    width: '100%',
  },

  body: {
    margin: [[0, 'auto']],
    paddingLeft: theme.spacing.unit * 2,
    paddingRight: theme.spacing.unit * 2,

    [theme.breakpoints.up('sm')]: {
      paddingLeft: theme.spacing.unit * 3,
      paddingRight: theme.spacing.unit * 3,
    },
  },
});

export default withRoot(withStyles(styles)(Page));
