import React from 'react';
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import {Container, Grid, Typography} from "@material-ui/core";

import {getFeed, clearNews} from "../../../app/actionCreators";
import {createFeedWebsocket} from "../../../app/ws";
import New from "../../common/components/New";
import PaginateButtons from "../../common/components/PaginateButtons";


const PAGE_LIMIT = 100;


class FeedPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {page: 1, isAll: false};
    this.ws = null;
    this.handlePage = this.handlePage.bind(this);
  }


  componentDidMount() {
    this.props.getFeed(1, PAGE_LIMIT);
    createFeedWebsocket().then(ws => {this.ws = ws});
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    const {news} = this.props;
    if (prevProps.news.length === news.length) {
      return
    }
    const isAll = news.length < PAGE_LIMIT;
    this.setState({...this.state, isAll});
  }

  componentWillUnmount() {
    this.props.clearNews();
    if (this.ws){
      this.ws.close();
    }
  }


  async handlePage(page) {
    this.props.getFeed(page, PAGE_LIMIT);
    this.setState({...this.state, page: page});
  }

  render() {
    const {news} = this.props;
    const {page, isAll} = this.state;

    return <Container>
      <Grid item container spacing={2} justify="space-between" direction="row">
        {news.map(newItem => <Grid item xs={12} key={'new_' + newItem.id}>
            <New newItem={newItem}/>
          </Grid>
        )}
        {!news.length && <Typography variant="h5" component="h2" style={{marginBottom: "10px"}}>
          News not found
        </Typography>}
      </Grid>
      <PaginateButtons page={page} isAll={isAll} handlePage={this.handlePage}/>
    </Container>
  }
}

const mapStateToProps = state => ({news: state.news});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({getFeed, clearNews}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(FeedPage);
