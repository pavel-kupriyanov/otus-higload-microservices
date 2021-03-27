import React from "react";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import PropTypes from "prop-types";

import {deleteFriendRequest} from "../../../../app/actionCreators";
import {REQUEST_STATUSES} from "../../../../app/utils";
import {Chip} from "@material-ui/core";


class WaitingUser extends React.Component {

  constructor(props) {
    super(props);
    this.handleDelete = this.handleDelete.bind(this);
    this.getFriendRequest = this.getFriendRequest.bind(this);
  }

  getFriendRequest() {
    const {userData, user} = this.props;
    return userData.friendRequests.find(req => {
      return req.from_user === userData.user.id && req.to_user === user.id;
    })
  }


  handleDelete(friendRequest) {
    this.props.deleteFriendRequest(friendRequest.id);
  }

  render() {
    const friendRequest = this.getFriendRequest();
    const isWaiting = friendRequest.status === REQUEST_STATUSES.WAITING;
    const text = isWaiting ? 'Waiting user response' : 'User decline your request';
    return <Chip
      label={text}
      onDelete={() => this.handleDelete(friendRequest)}
      color='secondary'
    />
  }
}

WaitingUser.propTypes = {
  user: PropTypes.object.isRequired,
}

const mapStateToProps = state => ({
  userData: state.userData
});


const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    deleteFriendRequest
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(WaitingUser);
