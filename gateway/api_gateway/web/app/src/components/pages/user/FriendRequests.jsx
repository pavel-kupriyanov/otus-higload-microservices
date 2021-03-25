import React from 'react';

import {bindActionCreators} from "redux";
import {getFriendRequestUsers} from "../../../app/actionCreators";
import {connect} from "react-redux";
import {REQUEST_STATUSES} from "../../../app/utils";
import UserCard from "../../common/components/UserCard";
import PropTypes from "prop-types";
import {Grid} from "@material-ui/core";


class FriendRequests extends React.Component {


  componentDidMount() {
    const {userData} = this.props;
    const friendRequests = userData.friendRequests;
    const ids = friendRequests.map(req =>
      req.from_user === userData.user.id ? req.to_user : req.from_user
    )
    this.props.getFriendRequestUsers(ids);
  }

  render() {
    const {friendRequestUsers, friendRequests, user} = this.props.userData;
    let users = friendRequestUsers;
    if (!this.props.showDeclined) {
      const declinedIds = friendRequests
        .filter(req => req.status !== REQUEST_STATUSES.DECLINED)
        .map(req => req.from_user === user.id ? req.to_user : req.from_user)
      users = users.filter(user => declinedIds.find(id => id === user.id))
    }

    return <Grid item container spacing={2} justify="space-between" direction="row">
      {users.map(user => <Grid item xs={6} key={'friend_request_user_' + user.id}>
          <UserCard user={user}/>
        </Grid>
      )}
    </Grid>
  }
}

FriendRequests.propTypes = {
  showDeclined: PropTypes.bool.isRequired
}

const mapStateToProps = state => ({
  userData: state.userData,
});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({getFriendRequestUsers}, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(FriendRequests);






