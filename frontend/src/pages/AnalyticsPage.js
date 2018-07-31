import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';

import {Chart} from "react-google-charts";
import Page from "../components/Page";
import Grid from '@material-ui/core/Grid';
import {mediaGet} from "../api";
import Typography from '@material-ui/core/Typography';

/**
 * The media item's analytics page
 */
class AnalyticsPage extends Component {

  constructor() {
    super();

    this.state = {
      // The media item response from the API, if any.
      mediaItemResponse: null,
    }
  }

  componentWillMount() {
    // As soon as the page mounts, fetch the media item.
    const { match: { params: { pk } } } = this.props;
    mediaGet(pk).then(
      response => this.setState({ mediaItemResponse: response }),
      error => this.setState({ mediaItemResponse: null })
    );
  }

  render() {
    const { mediaItemResponse } = this.state;
    const { chartData, classes, match: { params: { pk } } } = this.props;

    let chart = <Typography variant="subheading">
      There is no data available for the media
    </Typography>;

    if (chartData.length > 1) {
      chart = (
        <Typography variant='body1' component='div' className={ classes.chartContainer }>
          <Chart
            chartType="AnnotationChart"
            data={chartData}
            options={{fill: 100, colors: ['#EF2E31']}}
          />
        </Typography>
      );
    }

    return (
      <Page>
        <section>
          <Grid container spacing={16} className={ classes.gridContainer }>
            <Grid item xs={12}>
              <Typography variant="headline" component="div">
                Viewing history (views per day)
              </Typography>
            </Grid>
            <Grid item xs={12}>{ chart }</Grid>
            <Grid item xs={12}>
              <Typography variant="headline" component="div">
                { mediaItemResponse && mediaItemResponse.title }
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="subheading">
                <a className={ classes.link } href={'/media/' + pk}>
                  Media Item
                </a>
              </Typography>
            </Grid>
            <Grid item xs={6} style={{textAlign: 'right'}}>
              <Typography variant="subheading">
                <a className={ classes.link } href={ mediaItemResponse && mediaItemResponse.legacy.statisticsUrl }>
                  Legacy Statistics
                </a>
              </Typography>
            </Grid>
          </Grid>
        </section>
      </Page>
    );
  }
}

AnalyticsPage.propTypes = {
  chartData: PropTypes.array.isRequired,
  classes: PropTypes.object.isRequired,
};

/**
 * A higher-order component wrapper which retrieves the media item's analytics (resolved from
 * global data), generates the chart data for AnnotationChart, and passes it along.
 */
const withChartData = WrappedComponent => props => {

  const chartData = [["Date", "Views"]];

  let minDate = new Date("9999-12-31");
  let maxDate = new Date("0000-01-01");

  const summedByDate = {};

  if (window.mediaItemAnalytics.length > 0) {
    // Here we sum up all views for a particular day (irrespective of other variable) and
    // calculate the min and max dates.
    for (let i = 0; i < window.mediaItemAnalytics.length; i ++) {
      const date = new Date(window.mediaItemAnalytics[i]['date']);
      const views = date in summedByDate ? summedByDate[date] : 0;
      summedByDate[date] = views + window.mediaItemAnalytics[i]['views'];
      minDate = Math.min(minDate, date);
      maxDate = Math.max(maxDate, date);
    }

    // Here we provide an ordered list of the views fill out missing days with zero views.

    // Note we also add a zero data-point at either end of the data which makes the graph
    // look better in case of a single data-point.
    maxDate = addDays(new Date(maxDate), 1);
    let date = addDays(new Date(minDate), -1);

    while (date <= maxDate) {
      chartData.push(
        [date, date in summedByDate ? summedByDate[date] : 0]
      );
      date = addDays(date, 1);
    }
  }

  return (<WrappedComponent chartData={chartData} {...props} />);
};

/**
 * A helper function to return a new date displaced from a given date by given number of days.
 */
const addDays = (date, days) => {
    const result = new Date(date.valueOf());
    result.setUTCDate(result.getUTCDate() + days);
    return result;
};

/* tslint:disable object-literal-sort-keys */
var styles = _ => ({
  gridContainer: {
    maxWidth: 1260,
    margin: '0 auto'
  },
  chartContainer: {
    /* Missing bottom border */
    '& .rangeControl': {
      borderBottom: [['1px', '#888888', 'solid']]
    },
    /**
     * Hide the useless displayZoomButtons
     *
     * HACK: it is noted here that this approach is brittle - keep an eye on Google Charts in case
     * they provide a way of configuring these buttons in the future (alternatively we could make
     * our own buttons using setVisibleChartRange()).
     */
    '& #reactgooglegraph-1_AnnotationChart_zoomControlContainer_1-hour': {
      display: 'none'
    },
    '& #reactgooglegraph-1_AnnotationChart_zoomControlContainer_1-day': {
      display: 'none'
    },
    '& #reactgooglegraph-1_AnnotationChart_zoomControlContainer_5-days': {
      display: 'none'
    },
  }
});
/* tslint:enable */

export default withChartData(withStyles(styles)(AnalyticsPage));
