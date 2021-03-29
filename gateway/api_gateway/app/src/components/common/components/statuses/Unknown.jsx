import React from "react";
import {bindActionCreators} from "redux";
import {addFriendRequest} from "../../../../app/actionCreators";
import {connect} from "react-redux";
import PropTypes from "prop-types";
import {Chip} from "@material-ui/core";


class Unknown extends React.Component {

  constructor(props) {
    super(props);
    this.handleAdd = this.handleAdd.bind(this);
  }

  handleAdd() {
    const {user, addFriendRequest} = this.props;
    addFriendRequest(user.id);
  }

  render() {
    return <Chip label="Add Friend" onClick={this.handleAdd}/>
  }
}

Unknown.propTypes = {
  user: PropTypes.object.isRequired,
}

const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    addFriendRequest,
  }, dispatch)
}

export default connect(null, mapDispatchToProps)(Unknown);
