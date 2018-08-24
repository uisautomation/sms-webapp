import React from 'react';
import PropTypes from 'prop-types';

import { Link } from 'react-router-dom'

import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ListSubheader from '@material-ui/core/ListSubheader';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import CreateChannelIcon from '@material-ui/icons/AddToQueue';
import ChannelIcon from '@material-ui/icons/VideoLibrary';
import LatestMediaIcon from '@material-ui/icons/NewReleases';
import HomeIcon from '@material-ui/icons/Home';
import PopularIcon from '@material-ui/icons/TrendingUp';
import FeedbackIcon from '@material-ui/icons/Feedback';
import HelpIcon from '@material-ui/icons/Help';
import SettingsIcon from '@material-ui/icons/Settings';

/** Side panel for the current user providing navigation links. */
const NavigationPanel = ({ profile, classes }) => <div className={ classes.root }>
  <div className={ classes.profileBar }>
  {
    profile && !profile.isAnonymous
    ?
    <div>
      <Avatar
        alt={ profile.displayName }
        classes={{ root: classes.avatar }}
        src={ profile.avatarImageUrl }
      >
        { profile.avatarImageUrl ? null : profile.displayName[0] }
      </Avatar>
      <Typography variant='title'>{ profile.displayName }</Typography>
      <Typography variant='caption'>{ profile.username }</Typography>
    </div>
    :
    null
  }
  {
    profile && profile.isAnonymous
    ?
    <div>
      <Button
        color='primary' variant='outlined' fullWidth component='a' href='/accounts/login'
      >
        Sign in with Raven
      </Button>
    </div>
    :
    null
  }
  </div>
  <div className={classes.main}>
    <Divider />
    <List>
      <ListItem button component={Link} to='/'>
        <ListItemIcon><HomeIcon /></ListItemIcon>
        <ListItemText primary="Home" />
      </ListItem>
      <ListItem button component={Link} to='/'>
        <ListItemIcon><PopularIcon /></ListItemIcon>
        <ListItemText primary="Popular" />
      </ListItem>
    </List>
    <Divider />
    <List subheader={<ListSubheader>Channels</ListSubheader>}>
      <ListItem button>
        <ListItemAvatar><Avatar>G</Avatar></ListItemAvatar>
        <ListItemText classes={{ root: classes.listItemRoot }}
          secondary="47 items" primary="Philosophers of Greece" />
      </ListItem>
      <ListItem button>
        <ListItemAvatar><Avatar src="https://randomuser.me/api/portraits/thumb/women/65.jpg" /></ListItemAvatar>
        <ListItemText classes={{ root: classes.listItemRoot }}
          secondary="1 item" primary="Smith Lectures" />
      </ListItem>
      <ListItem button>
        <ListItemAvatar><Avatar
src="http://www.sjcchoir.co.uk/sites/default/files/styles/main_content_small_image/public/images/125_col_small_st_johns_choir_17x15_c_b_ealovega.jpg?itok=8Y3mjZ1I" /></ListItemAvatar>
        <ListItemText classes={{ root: classes.listItemRoot }} 
          secondary="341 items" primary="St John's Choir" />
      </ListItem>
    </List>
    <Divider />
    <List>
      <ListItem button>
        <ListItemIcon><ChannelIcon /></ListItemIcon>
        <ListItemText primary="Manage channels" />
      </ListItem>
      <ListItem button>
        <ListItemIcon><HelpIcon /></ListItemIcon>
        <ListItemText primary="Help" />
      </ListItem>
      <ListItem button>
        <ListItemIcon><FeedbackIcon /></ListItemIcon>
        <ListItemText primary="Feedback" />
      </ListItem>
    </List>
  </div>
  {
    profile && !profile.isAnonymous
    ?
    <div className={classes.bottom}>
      <Divider />
      <div className={classes.bottomPanel}>
        <Typography gutterBottom variant='caption'>
          <a href="/account/logout">Sign out</a>
        </Typography>
        <Typography variant='caption'>
          <a href="/about">About</a>{' '}
          <a href="#">Contact</a>{' '}
          <a href="https://github.com/uisautomation/sms-webapp">Developers</a>{' '}
        </Typography>
        <Typography variant='caption'>
          &copy; 2018 University of Cambridge
        </Typography>
      </div>
    </div>
    :
    null
  }
</div>;

NavigationPanel.propTypes = {
  /** User profile. */
  profile: PropTypes.shape({
    avatarImageUrl: PropTypes.string,
    displayName: PropTypes.string,
    isAnonymous: PropTypes.bool.isRequired,
    username: PropTypes.string.isRequired,
  }),
};

const styles = theme => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },

  main: {
    flexGrow: 1,
  },

  avatar: {
    marginBottom: theme.spacing.unit * 2,
  },

  bottomPanel: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    paddingBottom: theme.spacing.unit * 2,
    paddingLeft: theme.spacing.unit * 3,
    paddingRight: theme.spacing.unit * 3,
    paddingTop: theme.spacing.unit * 2,

    '& a': {
      color: 'inherit',
      textDecoration: 'inherit',
    },

    '& a:hover': {
      textDecoration: 'underline',
    },
  },

  profileBar: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: theme.spacing.unit * 2,

    [theme.breakpoints.up('sm')]: {
      paddingLeft: theme.spacing.unit * 3,
      paddingRight: theme.spacing.unit * 3,
    },
  },

  listItemRoot: {
    '& *': {
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
    },
  },
});

export default withStyles(styles)(NavigationPanel);
