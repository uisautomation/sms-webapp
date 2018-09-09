import React from 'react';

import Paper from '@material-ui/core/Paper';
import { withStyles } from '@material-ui/core/styles';

const CollapsingPaperSection = ({ classes, children }) => (
  <Paper classes={{ root: classes.paperRoot, rounded: classes.paperRounded }}>
    { children }
  </Paper>
);

const styles = theme => ({
  paperRoot: {
    [theme.breakpoints.up('md')]: {
      margin: theme.spacing.unit,
    },
  },

  paperRounded: {
    [theme.breakpoints.down('sm')]: {
      borderRadius: 0,
    },
  },
});

export default withStyles(styles)(CollapsingPaperSection);
