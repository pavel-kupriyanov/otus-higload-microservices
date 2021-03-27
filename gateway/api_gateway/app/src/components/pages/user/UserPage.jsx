import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import {bindActionCreators} from 'redux';
import {Form} from "react-final-form";
import {Card, Grid, Typography, FormControlLabel, Checkbox, Paper, Tabs, Tab} from '@material-ui/core';

import {getUser, getFriends, clearUser, clearUsers, getNews, clearNews, addNew} from '../../../app/actionCreators';
import {Hobbies, UserInfo, UserCard} from '../../common';
import EditableHobbies from './EditableHobbies';
import FriendRequests from './FriendRequests';
import New from "../../common/components/New";
import AddNewForm from "./AddNewForm";

const PAGE_LIMIT = 10;

const cardStyle = {
  padding: '20px',
  height: '100%',
  marginTop: '10px'
}

const gridStyle = {
  marginTop: '40px',
  padding: '20px'
}

const TABS = {
  FRIENDS: 'FRIENDS',
  POSTS: 'POSTS'
}

class UserPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {showDeclinedFriendRequests: true, tab: TABS.POSTS};
    this.addNew = this.addNew.bind(this);
  }

  componentDidMount() {
    const {id, getUser, getFriends, getNews} = this.props;
    getUser(id);
    getFriends(id);
    getNews(id, 1, PAGE_LIMIT);
  }

  componentWillUnmount() {
    const {clearUser, clearUsers, clearNews} = this.props;
    clearUser();
    clearUsers();
    clearNews();
  }

  addNew(form){
    this.props.addNew(form.text);
  }


  render() {
    const {id, user, users, userData, news} = this.props;
    const {showDeclinedFriendRequests, tab} = this.state;
    const isMyPage = Number(id) === userData.user.id;
    const friends = isMyPage ? userData.friends : users;

    return <Grid item container spacing={2} justify='space-between' direction='row'>
      <Grid item xs={6}>
        <Card style={cardStyle}>
          <Typography variant='h5' component='h2'>
            Common info
          </Typography>
          {user && user.id && <UserInfo user={user}/>}
        </Card>
      </Grid>
      <Grid item xs={6}>
        <Card style={cardStyle}>
          <Typography variant='h5' component='h2'>
            Hobbies
          </Typography>
          {isMyPage ? <EditableHobbies hobbies={userData.user.hobbies}/> :
            <Hobbies hobbies={user ? user.hobbies : []}/>}
        </Card>
      </Grid>
      {(isMyPage && !!userData.friendRequests.length) && <>
        <Grid item xs={12} style={gridStyle}>
          <Typography variant='h5' component='h2' style={
            {justifyContent: 'space-between', display: 'flex'}}
          >
            Friend requests
            <FormControlLabel
              control={
                <Checkbox
                  checked={showDeclinedFriendRequests}
                  onChange={() => this.setState({
                    showDeclinedFriendRequests: !showDeclinedFriendRequests
                  })}
                  name='showDeclined'
                  color='primary'
                />
              }
              label='Show declined requests'
            />
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <FriendRequests showDeclined={showDeclinedFriendRequests}/>
        </Grid>
      </>}
      <Grid item xs={12} style={{marginTop: 70}}>
        <Paper square>
          <Tabs
            value={tab}
            indicatorColor="primary"
            textColor="primary"
            onChange={(e, value) => this.setState({...this.state, tab: value})}
            aria-label="disabled tabs example"
          >
            <Tab label="Friends" value={TABS.FRIENDS}/>
            <Tab label="Latest posts" value={TABS.POSTS}/>
          </Tabs>
        </Paper>
      </Grid>
      <Grid item xs={12} container spacing={2} justify='space-between' direction='row'>
        {tab === TABS.FRIENDS && friends.map(user => <Grid item xs={6} key={'friend_' + user.id}>
            <UserCard user={user}/>
          </Grid>
        )}
        {tab === TABS.POSTS && isMyPage && <Grid item xs={12}>
          <Form onSubmit={this.addNew} component={AddNewForm}/>
        </Grid>}
        {tab === TABS.POSTS && news.map(newItem => <Grid item xs={12} key={'new_' + newItem.id}>
            <New newItem={newItem}/>
          </Grid>
        )}
      </Grid>
    </Grid>
  }
}

UserPage.propTypes = {
  id: PropTypes.string.isRequired,
  user: PropTypes.object,
  accessToken: PropTypes.object,
  getUser: PropTypes.func.isRequired,
  getFriends: PropTypes.func.isRequired,
  clearUser: PropTypes.func.isRequired,
  clearUsers: PropTypes.func.isRequired,
}

const mapStateToProps = state => ({
  user: state.user,
  userData: state.userData,
  users: state.users,
  news: state.news
});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    getUser, getFriends, clearUser, clearUsers, getNews, clearNews, addNew
  }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(UserPage);
