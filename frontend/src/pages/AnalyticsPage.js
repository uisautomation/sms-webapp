import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';

import {Chart} from "react-google-charts";
import Page from "../components/Page";
import Grid from '@material-ui/core/Grid';

/**
 * The media item's analytics page
 */
const AnalyticsPage = ({ chartData, classes }) => (
  <Page>
    <section>
      <Grid container spacing={16} className={ classes.gridContainer }>
        <Grid item xs={12}>
          <Chart
            chartType="AnnotationChart"
            data={chartData}
            options={{fill: 100, colors: ['#106470']}}
          />
        </Grid>
      </Grid>
    </section>
  </Page>
);

AnalyticsPage.propTypes = {
  chartData: PropTypes.array.isRequired,
  classes: PropTypes.object.isRequired,
};

/**
 * A higher-order component wrapper which retrieves the media item's analytics (resolved from
 * global data), generates the chart data for AnnotationChart, and passes it along.
 */
const withChartData = WrappedComponent => props => {

  var chartData = [["Date", "Views"]];

  for (var i = 0; i < window.mediaItemAnalytics.length; i ++) {
    chartData.push(
      [new Date(window.mediaItemAnalytics[i].date * 1000), window.mediaItemAnalytics[i].views]
    );
  }

  return (<WrappedComponent chartData={chartData} {...props} />);
};

/* tslint:disable object-literal-sort-keys */
var styles = theme => ({
  gridContainer: {
    maxWidth: 1260,
    margin: '0 auto'
  },
});
/* tslint:enable */

export default withChartData(withStyles(styles)(AnalyticsPage));
