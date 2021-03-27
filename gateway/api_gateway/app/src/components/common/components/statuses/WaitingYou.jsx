import React from "react";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import PropTypes from "prop-types";

import {acceptFriendRequest, declineFriendRequest} from "../../../../app/actionCreators";
import {Chip} from "@material-ui/core";


class WaitingYou extends React.Component {

  constructor(props) {
    super(props);
    this.handleAccept = this.handleAccept.bind(this);
    this.handleDecline = this.handleDecline.bind(this);
    this.getFriendRequest = this.getFriendRequest.bind(this);
  }

  getFriendRequest() {
    const {userData, user} = this.props;
    return userData.friendRequests.find(req => {
      return req.to_user === userData.user.id && req.from_user === user.id;
    })
  }

  handleAccept(friendRequest) {
    this.props.acceptFriendRequest(friendRequest.id);
  }

  handleDecline(friendRequest) {
    this.props.declineFriendRequest(friendRequest.id);
  }

  render() {
    const friendRequest = this.getFriendRequest();

    return <Chip
      label='Accept'
      onDelete={() => this.handleDecline(friendRequest)}
      onClick={() => this.handleAccept(friendRequest)}
      color='secondary'
    />
  }
}

WaitingYou.propTypes = {
  user: PropTypes.object.isRequired,
}

const mapStateToProps = state => ({
  userData: state.userData
});


const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    acceptFriendRequest, declineFriendRequest
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(WaitingYou);
