import React from 'react';
import PropTypes from 'prop-types';

import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';
import Fade from '@material-ui/core/Fade';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';
import IconButton from '@material-ui/core/IconButton';
import Input from '@material-ui/core/Input';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Paper from '@material-ui/core/Paper';
import Tab from '@material-ui/core/Tab';
import Tabs from '@material-ui/core/Tabs';
import Toolbar from '@material-ui/core/Toolbar';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';

import { withStyles } from '@material-ui/core/styles';

import DownloadIcon from '@material-ui/icons/CloudDownload';
import AnalyticsIcon from '@material-ui/icons/ShowChart';
import EditIcon from '@material-ui/icons/Edit';
import MoreIcon from '@material-ui/icons/MoreVert';
import EmbedIcon from '@material-ui/icons/PictureInPicture';
import BackIcon from '@material-ui/icons/ArrowBack';

import Page from '../containers/Page';
import BodySection from '../components/BodySection';
import RenderedMarkdown from '../components/RenderedMarkdown';

import FetchMediaItem from '../containers/FetchMediaItem';
import IfOwnsChannel from "../containers/IfOwnsChannel";

import CollapsingPaperSection from '../components/CollapsingPaperSection';

/**
 * The media item page
 */
const MediaPage = ({ match: { params: { pk } }, classes }) => (
  <Page>
    <FetchMediaItem id={ pk } component={ ConnectedMediaPageContents } />
  </Page>
);

MediaPage.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      pk: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
};

/** Given a list of sources, return the "best" source. */
const bestSource = sources => {
  const videos = sources
    .filter(item => item.mimeType === 'video/mp4')
    .sort((a, b) => {
      if(a.width > b.width) { return -1; }
      if(a.width < b.width) { return 1; }
      return 0;
    });

  if(videos.length > 0) { return videos[0]; }

  const audios = sources.filter(item => item.mimeType === 'audio/mp4');

  if(audios.length > 0) { return audios[0]; }

  return null;
};

class MediaPageContents extends React.Component {
  state = { }

  render() {
    const { resource: item, classes } = this.props;
    const { embedShown } = this.state;
    const source =
      (item && item.sources) ? bestSource(item.sources) : null;

    const embedCode = '<iframe> ... </iframe>';

    return (
      <div className={ classes.root }>
        <section className={ classes.playerSection }>
          <div className={ classes.playerWrapper }>
            <iframe
              src={ item ? item.embedUrl : '' }
              className={ classes.player }
              frameBorder="0"
              allowFullScreen>
            </iframe>
          </div>
        </section>
        <section className={ classes.headingSection }>
          <AppBar position="static">
            <Toolbar>
              <div className={ classes.headingTitle }>
                <Typography color="inherit" variant="headline" gutterBottom>
                  { item && item.title }
                </Typography>
                {
                  item && item.channel &&
                  <Typography color="inherit" variant="caption" gutterBottom>
                    <div className={ classes.channelBanner }>
                      <a href={`/channels/${item.channel.id}`}>{ item.channel.title }</a>
                    </div>
                  </Typography>
                }
              </div>
            </Toolbar>
            <Toolbar variant="dense" classes={{ root: classes.actions }}>
              <Tooltip title="Copy embed code">
                <IconButton color="inherit">
                  <EmbedIcon />
                </IconButton>
              </Tooltip>
              {
                source &&
                <Tooltip title="Download media">
                  <IconButton color="inherit" href={ source.url } download={true} target="_blank">
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
              }
              {
                item &&
                <Tooltip title="Analytics">
                  <IconButton
                    color="inherit" component='a' href={ '/media/' + item.id + '/analytics' }
                  >
                    <AnalyticsIcon />
                  </IconButton>
                </Tooltip>
              }
            </Toolbar>
          </AppBar>
        </section>
        {
          (item && item.channel)
          &&
          <IfOwnsChannel channel={ item.channel }>
            <Button
              variant="fab" color="secondary" aria-label="Edit"
              component="a" href={ '/media/' + item.id + '/edit' }
              classes={{ root: classes.fab }}
            >
              <EditIcon />
            </Button>
          </IfOwnsChannel>
        }
        <Grid container justify="center">
          {
            item && item.description && item.description.trim() !== '' &&
            <Grid item xs={12} md={10} lg={8} xl={6}>
              <CollapsingPaperSection>
                <BodySection>
                  <div className={ classes.description }>
                    <RenderedMarkdown source={ item.description } />
                  </div>
                </BodySection>
              </CollapsingPaperSection>
            </Grid>
          }
        </Grid>
      </div>
    );
  }
}

MediaPageContents.propTypes = {
  classes: PropTypes.object.isRequired,
  item: PropTypes.object,
};

/* tslint:disable object-literal-sort-keys */
var styles = theme => ({
  root: {
    [theme.breakpoints.up('md')]: {
      paddingBottom: theme.spacing.unit * 3,
    },
  },

  actions: {
    backgroundColor: theme.palette.primary.dark,

    '& > *:first-child': {
      marginLeft: -1.5 * theme.spacing.unit,
    },

    '& > *:last-child': {
      marginRight: -1.5 * theme.spacing.unit,
    },
  },

  headingTitle: {
    flexGrow: 1,
    paddingBottom: theme.spacing.unit * 2,
    paddingTop: theme.spacing.unit * 2,

    '& a': {
      color: 'inherit',
      textDecoration: 'inherit',
    },

    '& a:hover': {
      textDecoration: 'underline',
    },

    [theme.breakpoints.up('md')]: {
      paddingBottom: theme.spacing.unit * 3,
      paddingTop: theme.spacing.unit * 3,
    },
  },

  headingSection: {
    [theme.breakpoints.up('md')]: {
      marginBottom: theme.spacing.unit * 2,
    },
  },

  description: {
    marginBottom: -theme.spacing.unit,
    paddingBottom: 1, // HACK: fix odd margin spacing for description
    paddingTop: theme.spacing.unit * 2,

    [theme.breakpoints.up('md')]: {
      paddingBottom: theme.spacing.unit,
      paddingTop: theme.spacing.unit * 3,
    },
  },

  innerSection: {
    marginLeft: 'auto',
    marginRight: 'auto',
    maxWidth: theme.spacing.unit * 120,
  },

  channelBanner: {
    alignContent: 'center',
    alignItems: 'flex-start',
    display: 'flex',
    opacity: 0.54,
  },

  fab: {
    bottom: theme.spacing.unit * 2,
    position: 'absolute',
    right: theme.spacing.unit * 2,
  },

  // The following rules specify that the player keep itself in 16:9 aspect ratio but is never
  // larger than 54% of the screen height. (We'll come back to why this isn't a rounder number in a
  // bit.) Our trick here is to use the fact that padding values are relative to an element's
  // *width*. We can force a particular aspect ratio by specifying a height of zero and a padding
  // based on the reciprocal of the aspect ratio. We also want the video to have a maximum height
  // of 54vh (see above). Since the padding value is a function of the width, we need to limit the
  // maximum *width* of the element, not the height. Fortunately we're doing all this
  // jiggery-pokery to keep a constant aspect ratio and so a maximum *height* of 54vh implies a
  // maximum width of 54vh * 16 / 9 = 96vh.
  //
  // The use of a 54% maximum height lets us keep the nice round figure for the maximum height.
  playerSection: {
    backgroundColor: 'black',
    maxHeight: '54vh',
    overflow: 'hidden',  // since the player wrapper below can sometimes overhang
  },
  playerWrapper: {
    height: 0,
    margin: [[0, 'auto']],
    maxWidth: '96vh',
    paddingTop: '56.25%', // 16:9
    position: 'relative',
    width: '100%',
  },
  player: {
    height: '100%',
    left: 0,
    position: 'absolute',
    top: 0,
    width: '100%',
  },
  link: {
    color: theme.palette.text.secondary,
  },
  rightIcon: {
    marginLeft: theme.spacing.unit,
  },
  buttonStack: {
    '& a': {
      marginBottom: theme.spacing.unit,
    },
  },
  fullWidth: {
    width: '100%',
  }
});
/* tslint:enable */

const ConnectedMediaPageContents = withStyles(styles)(MediaPageContents);

export default MediaPage;
